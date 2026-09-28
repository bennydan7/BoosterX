"""
routes.py — Flask blueprint for BoostX authentication.

Frontend contract (read this before wiring up the login page):
  - ONE template, ONE form: identifier (email or phone) + password.
  - No "Admin login" link, tab, checkbox, or query-param switch anywhere.
  - After POST /api/auth/login succeeds, redirect the browser to
    `redirect_path` from the JSON response. Do not branch on role in the
    frontend — the backend already decided where to send them.
  - The register page/form only ever calls POST /api/auth/register, which
    can only ever create a customer account (see auth_service.py).
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from .auth_service import AuthError, AuthService, UserRepository

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# In app factory: auth_bp.auth_service = AuthService(real_repo); app.register_blueprint(auth_bp)
_auth_service: AuthService | None = None


def init_auth_routes(auth_service: AuthService) -> Blueprint:
    global _auth_service
    _auth_service = auth_service
    return auth_bp


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = _auth_service.register_customer(
            email=data.get("email"),
            phone=data.get("phone"),
            password=data.get("password", ""),
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "user_id": user.public_user_id,
        "message": "Account created. Please sign in.",
    }), 201


@auth_bp.post("/login")
def login():
    """
    Single login endpoint for BOTH customers and admins. The request body
    and the success/error shape are identical regardless of which type of
    account is authenticating — that symmetry is the point.
    """
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier", "")
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "Email/phone and password are required."}), 400

    try:
        result = _auth_service.authenticate(identifier=identifier, password=password)
    except AuthError as exc:
        # Same status code, same shape, whether the account is a customer,
        # an admin, locked, disabled, or doesn't exist at all.
        return jsonify({"error": str(exc)}), 401

    # Server-side session — the browser never sees or sets the role itself.
    session["user_id"] = result.user.id
    session["session_token"] = result.session_token

    return jsonify({
        "redirect_path": result.redirect_path,
        # Deliberately no "role" field in the response body: the frontend
        # doesn't branch on it, it just follows redirect_path.
    }), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Signed out."}), 200


@auth_bp.get("/me")
def me():
    """
    Used by the frontend to know what to render post-login (e.g. show the
    admin shell vs. the customer order-tracking shell) WITHOUT exposing
    role on the public login page itself — this endpoint only answers
    once a session already exists.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not signed in."}), 401

    user = _auth_service._repo.get_by_id(user_id)  # noqa: SLF001 — internal use
    if user is None:
        session.clear()
        return jsonify({"error": "Not signed in."}), 401

    return jsonify({
        "user_id": user.public_user_id,
        "role": user.role.value,
        "email": user.email,
        "phone": user.phone,
    }), 200
