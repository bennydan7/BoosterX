"""
models.py — BoostX account model.

One login page serves both customers and admins. The two are told apart
purely by the `role` column on this table — never by anything the frontend
shows. There is no "admin" link, toggle, or hint anywhere on the public
login/register screens (see routes.py for how the redirect after login
stays silent about this).
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


@dataclass
class User:
    """
    A single account table for both roles.

    Security notes:
      - `password_hash` is never the raw password — see set_password().
      - `role` is set once at creation and is never editable through any
        customer-facing endpoint. Only an existing admin (via an internal,
        already-authenticated admin route) can create another admin.
      - `failed_login_attempts` / `locked_until` implement a basic lockout
        so the shared login page can't be brute-forced — this matters more
        here than on a normal site, because this same page can reach an
        admin account.
    """

    id: int
    public_user_id: str
    email: Optional[str]
    phone: Optional[str]
    password_hash: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

    # ------------------------------------------------------------------ #

    @staticmethod
    def new_public_id(role: UserRole) -> str:
        # Customer-facing IDs look like BoostX order/payment IDs (BX-USR-xxxxx).
        # Admin IDs are never generated through the public registration path.
        prefix = "BX-USR" if role == UserRole.CUSTOMER else "BX-ADM"
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password, method="pbkdf2:sha256")

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def is_locked(self, *, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.locked_until is not None and self.locked_until > now


def validate_password_policy(raw_password: str) -> Optional[str]:
    """Returns an error message, or None if the password is acceptable."""
    if len(raw_password) < 8:
        return "Password must be at least 8 characters."
    if raw_password.isdigit() or raw_password.isalpha():
        return "Password must mix letters and numbers."
    return None


def validate_identifier(email: Optional[str], phone: Optional[str]) -> Optional[str]:
    """At least one of email/phone is required; email, if given, must look valid."""
    if not email and not phone:
        return "An email or phone number is required."
    if email and not EMAIL_RE.match(email):
        return "That doesn't look like a valid email address."
    return None
