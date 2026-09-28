"""
auth_service.py — BoostX authentication.

Core design decision (per Enock's instruction):

    Customers and admins log in on the SAME page, through the SAME
    endpoint, with the SAME form. Nothing in the request or the response
    copy reveals that an admin path exists. The only place role is ever
    decided is server-side, by looking up the account's `role` column
    after the password check succeeds.

Three rules make that safe:

  1. Registration (`register_customer`) can ONLY ever create a
     UserRole.CUSTOMER account. There is no public parameter, header, or
     trick that produces an admin account through this path.
  2. Admin accounts are created exclusively by `create_admin_account`,
     which is never wired to a public route — only to a seed script or an
     internal endpoint that itself requires an already-authenticated
     admin session.
  3. `authenticate()` returns the SAME generic error for "no such
     account" and "wrong password" — this stops the login page being used
     to enumerate which emails/phones have accounts (an attacker
     targeting the admin login shouldn't be able to tell whether they
     guessed a real admin email).
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Protocol

from backend.app.models import User, UserRole, UserStatus
from .models import validate_identifier, validate_password_policy

LOCKOUT_THRESHOLD = 5          # failed attempts before a temporary lock
LOCKOUT_DURATION = timedelta(minutes=15)
GENERIC_LOGIN_ERROR = "Incorrect email/phone or password."


class AuthError(Exception):
    """Safe to show to the end user as-is."""


# --------------------------------------------------------------------- #
# Storage boundary — swap InMemoryUserRepository for a real one backed
# by PostgreSQL (e.g. SQLAlchemy) without touching AuthService itself.
# --------------------------------------------------------------------- #
class UserRepository(Protocol):
    def get_by_identifier(self, identifier: str) -> Optional[User]: ...
    def get_by_id(self, user_id: int) -> Optional[User]: ...
    def save(self, user: User) -> User: ...
    def exists(self, identifier: str) -> bool: ...


class InMemoryUserRepository:
    """Reference implementation for tests/demos — not for production."""

    def __init__(self) -> None:
        self._by_id: dict[int, User] = {}
        self._next_id = 1

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        identifier = identifier.strip().lower()
        for user in self._by_id.values():
            if (user.email and user.email.lower() == identifier) or (user.phone == identifier):
                return user
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._by_id.get(user_id)

    def exists(self, identifier: str) -> bool:
        return self.get_by_identifier(identifier) is not None

    def save(self, user: User) -> User:
        if user.id is None or user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._by_id[user.id] = user
        return user


@dataclass(frozen=True)
class AuthResult:
    user: User
    session_token: str
    redirect_path: str  # decided server-side; never trust a client-supplied redirect


class AuthService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    # ------------------------------------------------------------------ #
    # Registration — customers only, always
    # ------------------------------------------------------------------ #
    def register_customer(
        self, *, email: Optional[str], phone: Optional[str], password: str, full_name: Optional[str] = None
    ) -> User:
        id_error = validate_identifier(email, phone)
        if id_error:
            raise AuthError(id_error)

        pw_error = validate_password_policy(password)
        if pw_error:
            raise AuthError(pw_error)

        identifier = (email or phone or "").strip().lower()
        if self._repo.exists(identifier):
            # Same generic phrasing style as login — don't confirm which
            # field collided, just that the account can't be created.
            raise AuthError("An account with those details already exists.")

        user = User(
            public_user_id=User.new_public_id(UserRole.CUSTOMER),
            full_name=full_name,
            email=email.strip().lower() if email else None,
            phone=phone.strip() if phone else None,
            password_hash="",
            role=UserRole.CUSTOMER,   # <-- hardcoded; not derived from input
            status=UserStatus.ACTIVE,
        )
        user.set_password(password)
        return self._repo.save(user)

    # ------------------------------------------------------------------ #
    # Admin provisioning — deliberately NOT reachable from a public route.
    # Call this only from a seed/management script, or from an internal
    # endpoint that already requires an authenticated admin session.
    # ------------------------------------------------------------------ #
    def create_admin_account(
        self, *, email: str, password: str, created_by_admin_id: Optional[int] = None
    ) -> User:
        id_error = validate_identifier(email, None)
        if id_error:
            raise AuthError(id_error)
        pw_error = validate_password_policy(password)
        if pw_error:
            raise AuthError(pw_error)
        if self._repo.exists(email.strip().lower()):
            raise AuthError("An account with those details already exists.")

        user = User(
            public_user_id=User.new_public_id(UserRole.ADMIN),
            email=email.strip().lower(),
            phone=None,
            password_hash="",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        user.set_password(password)
        return self._repo.save(user)

    # ------------------------------------------------------------------ #
    # Unified login — the one endpoint both roles use
    # ------------------------------------------------------------------ #
    def authenticate(self, *, identifier: str, password: str) -> AuthResult:
        identifier = identifier.strip().lower()
        user = self._repo.get_by_identifier(identifier)

        now = datetime.now(timezone.utc)

        if user is None:
            # Do real work anyway so response timing doesn't leak whether
            # the account exists (a cheap but worthwhile mitigation).
            from werkzeug.security import check_password_hash
            check_password_hash("pbkdf2:sha256:1000$dummy$dummy", password)
            raise AuthError(GENERIC_LOGIN_ERROR)

        if user.is_locked(now=now):
            # Same generic message — don't tell an attacker they found a
            # valid identifier and just need to wait out a lock.
            raise AuthError(GENERIC_LOGIN_ERROR)

        if user.status != UserStatus.ACTIVE:
            raise AuthError(GENERIC_LOGIN_ERROR)

        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
                user.locked_until = now + LOCKOUT_DURATION
            self._repo.save(user)
            raise AuthError(GENERIC_LOGIN_ERROR)

        # Success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now
        self._repo.save(user)

        return AuthResult(
            user=user,
            session_token=self._issue_session_token(user),
            redirect_path=post_login_redirect(user.role),
        )

    @staticmethod
    def _issue_session_token(user: User) -> str:
        """
        Placeholder token issuance. In production this should be a signed,
        short-lived JWT or a server-side session ID (e.g. Flask-Login /
        itsdangerous), carrying `user.id` and `user.role` inside a payload
        the CLIENT CANNOT MODIFY. The role must never be re-derived from
        anything the browser sends after login.
        """
        return secrets.token_urlsafe(32)


def post_login_redirect(role: UserRole) -> str:
    """
    The only place role ever affects behavior visible to the browser —
    and even then, only as a destination URL after a successful login,
    never as a hint on the login page itself.
    """
    return "/admin" if role == UserRole.ADMIN else "/account/orders"
