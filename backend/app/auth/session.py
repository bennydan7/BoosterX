import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from flask import request, session, current_app, make_response
from backend.app.db import db
from backend.app.models import User, UserRole, UserStatus, GuestSession

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def get_or_create_guest_session() -> Tuple[str, str]:
    """
    Returns (raw_guest_token, session_id_hash).
    Sets the boostx_guest HttpOnly cookie if not present.
    """
    guest_cookie = request.cookies.get(current_app.config["GUEST_COOKIE_NAME"])
    if guest_cookie:
        session_id_hash = hash_token(guest_cookie)
        guest = GuestSession.query.filter_by(session_id_hash=session_id_hash).first()
        if guest:
            guest.last_active_at = datetime.now(timezone.utc)
            db.session.commit()
            return guest_cookie, session_id_hash

    # Create new guest session
    raw_token = generate_token()
    session_id_hash = hash_token(raw_token)
    guest = GuestSession(
        session_id_hash=session_id_hash,
        created_at=datetime.now(timezone.utc),
        last_active_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.session.add(guest)
    db.session.commit()
    return raw_token, session_id_hash

def get_current_user() -> Optional[User]:
    """
    Loads current authenticated user from Flask session / cookies.
    Enforces active status check and session_version invalidation.
    """
    user_id = session.get("user_id")
    token_version = session.get("session_version")
    if not user_id:
        return None

    user = db.session.get(User, user_id)
    if not user or user.status != UserStatus.ACTIVE:
        session.clear()
        return None

    if token_version is not None and token_version != user.session_version:
        session.clear()
        return None

    return user
