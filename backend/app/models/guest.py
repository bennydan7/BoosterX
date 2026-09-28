from datetime import datetime, timezone, timedelta
from backend.app.db import db

class GuestSession(db.Model):
    __tablename__ = "guest_sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_id_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_active_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(days=30))
