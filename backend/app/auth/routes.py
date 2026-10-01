from flask import Blueprint, jsonify, request, session, current_app, make_response
from backend.app.db import db
from backend.app.models import User, UserRole, UserStatus
from backend.app.auth.repository import SQLAlchemyUserRepository
from backend.app.auth.auth_service import AuthService, AuthError
from backend.app.auth.session import get_current_user, get_or_create_guest_session, generate_token
from backend.app.middleware import get_csrf_token, limiter
from backend.app.orders.claim_service import ClaimService
from backend.app.utils.phone import normalize_phone

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

repo = SQLAlchemyUserRepository()
auth_service = AuthService(repo)


@auth_bp.post("/session")
def guest_session_endpoint():
    """Create or return guest session cookie & CSRF token."""
    raw_token, session_hash = get_or_create_guest_session()
    csrf_tok = get_csrf_token()
    
    resp = make_response(jsonify({
        "status": "ok",
        "csrf_token": csrf_tok,
        "is_guest": True
    }))
    
    cookie_name = current_app.config["GUEST_COOKIE_NAME"]
    resp.set_cookie(
        cookie_name,
        raw_token,
        httponly=True,
        secure=request.is_secure,
        samesite="Lax",
        max_age=30 * 24 * 3600
    )
    return resp, 200


@auth_bp.post("/auth/register")
@limiter.limit("5 per minute")
def register():
    data = request.get_json(silent=True) or {}
    full_name = data.get("full_name")
    identifier = data.get("identifier") or data.get("email") or data.get("phone", "")
    password = data.get("password", "")
    if not identifier:
        return jsonify({"error": "Email or phone number is required."}), 400

    email = None
    phone = None
    if "@" in identifier:
        email = identifier.strip().lower()
    else:
        try:
            phone = normalize_phone(identifier)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    try:
        user = auth_service.register_customer(
            email=email,
            phone=phone,
            password=password,
            full_name=full_name
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    # Auto-login after registration
    result = auth_service.authenticate(identifier=identifier, password=password)
    session["user_id"] = result.user.id
    session["session_version"] = result.user.session_version
    csrf_tok = get_csrf_token()

    # Claim guest session
    guest_cookie = request.cookies.get(current_app.config["GUEST_COOKIE_NAME"])
    claim_res = ClaimService.claim_current_guest_session(
        user_id=result.user.id,
        raw_guest_session_token=guest_cookie,
        claim_by_contact_enabled=current_app.config["CLAIM_BY_CONTACT_ENABLED"],
        email=result.user.email,
        phone=result.user.phone
    )

    return jsonify({
        "redirect_path": result.redirect_path,
        "csrf_token": csrf_tok,
        "orders_claimed": claim_res.orders_claimed
    }), 201


@auth_bp.post("/auth/login")
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier", "")
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "Email/phone and password are required."}), 400

    try:
        result = auth_service.authenticate(identifier=identifier, password=password)
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 401

    session["user_id"] = result.user.id
    session["session_version"] = result.user.session_version
    csrf_tok = get_csrf_token()

    # Claim guest session
    guest_cookie = request.cookies.get(current_app.config["GUEST_COOKIE_NAME"])
    claim_res = ClaimService.claim_current_guest_session(
        user_id=result.user.id,
        raw_guest_session_token=guest_cookie,
        claim_by_contact_enabled=current_app.config["CLAIM_BY_CONTACT_ENABLED"],
        email=result.user.email,
        phone=result.user.phone
    )

    return jsonify({
        "redirect_path": result.redirect_path,
        "csrf_token": csrf_tok,
        "orders_claimed": claim_res.orders_claimed
    }), 200


@auth_bp.post("/auth/logout")
def logout():
    session.clear()
    return jsonify({"message": "Signed out."}), 200


@auth_bp.get("/auth/me")
def me():
    user = get_current_user()
    csrf_tok = get_csrf_token()
    
    if not user:
        # Check if guest session exists
        raw_guest_cookie = request.cookies.get(current_app.config["GUEST_COOKIE_NAME"])
        return jsonify({
            "authenticated": False,
            "role": "guest",
            "csrf_token": csrf_tok
        }), 200

    return jsonify({
        "authenticated": True,
        "user_id": user.public_user_id,
        "full_name": user.full_name,
        "role": user.role,
        "email": user.email,
        "phone": user.phone,
        "csrf_token": csrf_tok
    }), 200


@auth_bp.post("/auth/change-password")
def change_password():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not user.check_password(current_password):
        return jsonify({"error": "Incorrect current password."}), 400

    from backend.app.auth.models import validate_password_policy
    err = validate_password_policy(new_password)
    if err:
        return jsonify({"error": err}), 400

    user.set_password(new_password)
    user.session_version += 1  # Invalidate all existing sessions
    db.session.commit()

    session["session_version"] = user.session_version
    return jsonify({"message": "Password updated successfully."}), 200
