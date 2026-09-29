import secrets
from functools import wraps
from flask import request, jsonify, session, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.app.auth.session import get_current_user
from backend.app.models.user import UserRole

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://"
)

def get_csrf_token() -> str:
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]

def validate_csrf():
    """Validate CSRF token header on state-changing requests."""
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        # Exclude public session initialization endpoint
        if request.path.endswith("/api/session"):
            return None
        sent_token = request.headers.get("X-CSRF-Token") or request.headers.get("X-CSRF-TOKEN")
        expected_token = session.get("csrf_token")
        if not expected_token or not sent_token or not secrets.compare_digest(sent_token, expected_token):
            return jsonify({"error": "Invalid or missing CSRF token."}), 403
    return None

def admin_required(f):
    """
    Security guard: /api/admin/* endpoints return a generic 404 to non-admins.
    No role hint, no 401/403 leakage.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != UserRole.ADMIN:
            return jsonify({"error": "Resource not found"}), 404
        return f(*args, **kwargs)
    return decorated_function
