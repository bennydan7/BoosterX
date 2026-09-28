from decimal import Decimal
from flask import Blueprint, jsonify, request, current_app, make_response
from backend.app.db import db
from backend.app.models import Order, OrderStatus, OrderEvent, LedgerTransaction, LedgerStatus, LedgerType, Payment, PaymentStatus, Refill, Service, Notification
from backend.app.auth.session import get_current_user, get_or_create_guest_session, hash_token
from backend.app.orders.order_service import create_and_submit_order, refund_order, OrderExecutionError
from backend.app.services.ledger_service import get_owner_balance
from backend.app.providers.factory import get_provider_client
from backend.app.providers.provider_client import ProviderError

orders_bp = Blueprint("orders", __name__, url_prefix="/api")

def _resolve_caller_identity():
    user = get_current_user()
    if user:
        return user.id, None, None
    raw_cookie = request.cookies.get(current_app.config["GUEST_COOKIE_NAME"])
    new_cookie = None
    if not raw_cookie:
        raw_cookie, session_id_hash = get_or_create_guest_session()
        new_cookie = raw_cookie
    else:
        session_id_hash = hash_token(raw_cookie)
    return None, session_id_hash, new_cookie

def _serialize_order(order: Order, include_events: bool = False) -> dict:
    start_c = order.start_count if order.start_count is not None else 0
    remains_c = order.remains if order.remains is not None else order.quantity
    
    if order.quantity > 0:
        delivered_units = max(0, order.quantity - remains_c)
        progress_pct = min(100, int((delivered_units / order.quantity) * 100))
    else:
        progress_pct = 0

    if order.status in (OrderStatus.COMPLETED,):
        progress_pct = 100

    data = {
        "id": order.id,
        "public_order_id": order.public_order_id,
        "platform": order.platform,
        "service_id": order.service_id,
        "service_name": order.service_name,
        "target": order.target,
        "quantity": order.quantity,
        "charge_ghs": f"{order.charge_ghs:.2f}",
        "status": order.status,
        "start_count": start_c,
        "remains": remains_c,
        "progress_percent": progress_pct,
        "needs_attention": order.needs_attention,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
    }

    if include_events:
        events = OrderEvent.query.filter_by(order_id=order.id).order_by(OrderEvent.id.asc()).all()
        data["events"] = [{
            "id": e.id,
            "event_type": e.event_type,
            "description": e.description,
            "created_at": e.created_at.isoformat() if e.created_at else None
        } for e in events]

    return data


@orders_bp.post("/orders")
def create_order_endpoint():
    data = request.get_json(silent=True) or {}
    service_id = data.get("service_id")
    target = data.get("target")
    quantity = data.get("quantity")
    idempotency_key = request.headers.get("Idempotency-Key") or data.get("idempotency_key")

    if not service_id or not target or quantity is None:
        return jsonify({"error": "service_id, target, and quantity are required"}), 400

    try:
        service_id = int(service_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid service_id or quantity"}), 400

    user_id, session_id_hash, new_cookie = _resolve_caller_identity()

    try:
        order = create_and_submit_order(
            user_id=user_id,
            session_id=session_id_hash,
            service_id=service_id,
            target=target,
            quantity=quantity,
            idempotency_key=idempotency_key
        )
    except OrderExecutionError as exc:
        payload = {"error": str(exc)}
        if exc.details:
            payload["details"] = exc.details
        return jsonify(payload), exc.code

    resp = make_response(jsonify({"order": _serialize_order(order, include_events=True)}), 201)
    if new_cookie:
        resp.set_cookie(
            current_app.config["GUEST_COOKIE_NAME"],
            new_cookie,
            httponly=True,
            samesite="Lax",
            secure=current_app.config.get("SESSION_COOKIE_SECURE", False)
        )
    return resp


@orders_bp.get("/orders/<public_id>")
def get_order_detail(public_id: str):
    order = Order.query.filter_by(public_order_id=public_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    user_id, session_id_hash, _ = _resolve_caller_identity()

    # Ownership check: if caller possesses cookie or is owner, show full details
    # Otherwise if public track request, limit target string for privacy
    is_owner = False
    if user_id and order.user_id == user_id:
        is_owner = True
    elif not user_id and session_id_hash and order.session_id == session_id_hash:
        is_owner = True

    serialized = _serialize_order(order, include_events=is_owner)
    if not is_owner:
        # Sanitize target if tracking publicly
        t = order.target
        if len(t) > 6:
            serialized["target"] = t[:3] + "..." + t[-3:]

    return jsonify({"order": serialized}), 200


@orders_bp.get("/orders/<public_id>/status")
def get_order_status(public_id: str):
    order = Order.query.filter_by(public_order_id=public_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    start_c = order.start_count if order.start_count is not None else 0
    remains_c = order.remains if order.remains is not None else order.quantity
    if order.quantity > 0:
        delivered_units = max(0, order.quantity - remains_c)
        progress_pct = min(100, int((delivered_units / order.quantity) * 100))
    else:
        progress_pct = 0

    if order.status in (OrderStatus.COMPLETED,):
        progress_pct = 100

    return jsonify({
        "public_order_id": order.public_order_id,
        "status": order.status,
        "start_count": start_c,
        "remains": remains_c,
        "progress_percent": progress_pct
    }), 200


@orders_bp.post("/orders/<public_id>/refill")
def request_order_refill(public_id: str):
    order = Order.query.filter_by(public_order_id=public_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    user_id, session_id_hash, _ = _resolve_caller_identity()
    if (user_id and order.user_id != user_id) or (not user_id and order.session_id != session_id_hash):
        return jsonify({"error": "Order not found"}), 404

    if not order.provider_order_id:
        return jsonify({"error": "Order has not been submitted to provider"}), 400

    service = db.session.get(Service, order.service_id)
    if not service or not service.refill_available:
        return jsonify({"error": "Refill is not supported for this service"}), 400

    if order.status not in (OrderStatus.COMPLETED, OrderStatus.PARTIAL):
        return jsonify({"error": "Refill is only eligible for Completed or Partial orders"}), 400

    provider = get_provider_client()
    try:
        refill_id = provider.refill_order(order.provider_order_id)
    except ProviderError as exc:
        return jsonify({"error": f"Provider refill failed: {exc}"}), 400

    refill_record = Refill(
        order_id=order.id,
        provider_refill_id=str(refill_id),
        status="Pending"
    )
    db.session.add(refill_record)
    db.session.add(OrderEvent(order_id=order.id, event_type="REFILL_REQUESTED", description=f"Requested refill (Refill ID: {refill_id})"))
    db.session.commit()

    return jsonify({"message": "Refill request submitted", "refill_id": refill_id}), 200


@orders_bp.post("/orders/<public_id>/cancel")
def request_order_cancel(public_id: str):
    order = Order.query.filter_by(public_order_id=public_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    user_id, session_id_hash, _ = _resolve_caller_identity()
    if (user_id and order.user_id != user_id) or (not user_id and order.session_id != session_id_hash):
        return jsonify({"error": "Order not found"}), 404

    if order.status in (OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.REFUNDED, OrderStatus.FAILED):
        return jsonify({"error": f"Cannot cancel order in status '{order.status}'"}), 400

    if order.provider_order_id:
        provider = get_provider_client()
        try:
            res = provider.cancel_order(order.provider_order_id)
        except ProviderError as exc:
            return jsonify({"error": f"Provider cancellation failed: {exc}"}), 400

    order.status = OrderStatus.CANCELLED
    refunded_amt = refund_order(order, "Canceled_Full", "User requested order cancellation")
    db.session.commit()

    return jsonify({
        "message": "Order cancelled successfully",
        "refund_amount_ghs": f"{refunded_amt:.2f}"
    }), 200


@orders_bp.get("/account/orders")
def list_account_orders():
    user_id, session_id_hash, _ = _resolve_caller_identity()

    if user_id:
        query = Order.query.filter_by(user_id=user_id)
    elif session_id_hash:
        query = Order.query.filter_by(session_id=session_id_hash, user_id=None)
    else:
        return jsonify({"orders": [], "total": 0, "page": 1, "per_page": 20}), 200

    search_q = request.args.get("search")
    if search_q:
        q_like = f"%{search_q.strip()}%"
        query = query.filter(
            (Order.public_order_id.ilike(q_like)) |
            (Order.target.ilike(q_like)) |
            (Order.service_name.ilike(q_like))
        )

    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter(Order.status == status_filter)

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        page = 1
        per_page = 20

    total = query.count()
    orders = query.order_by(Order.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "orders": [_serialize_order(o) for o in orders],
        "total": total,
        "page": page,
        "per_page": per_page
    }), 200


@orders_bp.get("/account/wallet")
def get_account_wallet():
    user_id, session_id_hash, _ = _resolve_caller_identity()

    avail_bal = get_owner_balance(user_id, session_id_hash)

    # Calculate total spent (posted order debits)
    if user_id:
        spent_query = db.session.query(db.func.sum(LedgerTransaction.amount_ghs)).filter(
            LedgerTransaction.user_id == user_id,
            LedgerTransaction.type == LedgerType.ORDER_DEBIT,
            LedgerTransaction.status == LedgerStatus.POSTED
        )
        dep_query = db.session.query(db.func.sum(Payment.amount_ghs)).filter(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.VERIFIED
        )
    elif session_id_hash:
        spent_query = db.session.query(db.func.sum(LedgerTransaction.amount_ghs)).filter(
            LedgerTransaction.session_id == session_id_hash,
            LedgerTransaction.user_id == None,
            LedgerTransaction.type == LedgerType.ORDER_DEBIT,
            LedgerTransaction.status == LedgerStatus.POSTED
        )
        dep_query = db.session.query(db.func.sum(Payment.amount_ghs)).filter(
            Payment.session_id == session_id_hash,
            Payment.user_id == None,
            Payment.status == PaymentStatus.VERIFIED
        )
    else:
        spent_query = None
        dep_query = None

    total_spent = spent_query.scalar() if spent_query else 0
    total_spent_val = Decimal(str(total_spent or 0))

    total_dep = dep_query.scalar() if dep_query else 0
    total_dep_val = Decimal(str(total_dep or 0))

    return jsonify({
        "available_balance": f"{avail_bal:.2f}",
        "total_spent": f"{total_spent_val:.2f}",
        "total_deposited": f"{total_dep_val:.2f}"
    }), 200


@orders_bp.get("/account/transactions")
def list_account_transactions():
    user_id, session_id_hash, _ = _resolve_caller_identity()

    if user_id:
        query = LedgerTransaction.query.filter_by(user_id=user_id)
    elif session_id_hash:
        query = LedgerTransaction.query.filter_by(session_id=session_id_hash, user_id=None)
    else:
        return jsonify({"transactions": [], "total": 0, "page": 1, "per_page": 20}), 200

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        page = 1
        per_page = 20

    total = query.count()
    txs = query.order_by(LedgerTransaction.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "transactions": [{
            "id": t.id,
            "type": t.type,
            "amount_ghs": f"{t.amount_ghs:.2f}",
            "status": t.status,
            "reference": t.reference,
            "description": t.description,
            "balance_before": f"{t.balance_before:.2f}",
            "balance_after": f"{t.balance_after:.2f}",
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in txs],
        "total": total,
        "page": page,
        "per_page": per_page
    }), 200


@orders_bp.get("/notifications")
def list_notifications():
    user_id, session_id_hash, _ = _resolve_caller_identity()

    if user_id:
        notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.id.desc()).all()
    elif session_id_hash:
        notifs = Notification.query.filter_by(session_id=session_id_hash, user_id=None).order_by(Notification.id.desc()).all()
    else:
        notifs = []

    return jsonify({
        "notifications": [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "read": n.read,
            "created_at": n.created_at.isoformat() if n.created_at else None
        } for n in notifs]
    }), 200


@orders_bp.post("/notifications/<int:notif_id>/read")
def mark_notification_read(notif_id: int):
    user_id, session_id_hash, _ = _resolve_caller_identity()

    notif = db.session.get(Notification, notif_id)
    if not notif:
        return jsonify({"error": "Notification not found"}), 404

    if (user_id and notif.user_id != user_id) or (not user_id and notif.session_id != session_id_hash):
        return jsonify({"error": "Notification not found"}), 404

    notif.read = True
    db.session.commit()
    return jsonify({"message": "Notification marked as read"}), 200
