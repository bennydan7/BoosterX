from dataclasses import dataclass
from typing import Optional
import hashlib
from backend.app.db import db
from backend.app.models import Order, Payment, LedgerTransaction, GuestSession
from backend.app.utils.phone import normalize_phone

@dataclass(frozen=True)
class ClaimResult:
    orders_claimed: int
    payments_claimed: int
    public_order_ids: list[str]

class ClaimService:
    @staticmethod
    def claim_current_guest_session(*, user_id: int, raw_guest_session_token: Optional[str], claim_by_contact_enabled: bool = False, email: Optional[str] = None, phone: Optional[str] = None) -> ClaimResult:
        """
        Moves guest orders, payments, and ledger entries associated with the
        CURRENT guest session (verified by cookie possession) to user_id in ONE transaction.
        If claim_by_contact_enabled is True, also claims unclaimed orders matching email/phone (orders ONLY, NEVER money).
        """
        if not raw_guest_session_token and not (claim_by_contact_enabled and (email or phone)):
            return ClaimResult(orders_claimed=0, payments_claimed=0, public_order_ids=[])

        session_id_hash = hashlib.sha256(raw_guest_session_token.encode("utf-8")).hexdigest() if raw_guest_session_token else None

        claimed_orders = 0
        claimed_payments = 0
        public_ids = []

        with db.session.begin_nested():
            # 1. Claim current guest session (Orders, Payments, Ledger rows)
            if session_id_hash:
                orders = Order.query.filter_by(session_id=session_id_hash, user_id=None).all()
                for o in orders:
                    o.user_id = user_id
                    public_ids.append(o.public_order_id)
                    claimed_orders += 1

                payments = Payment.query.filter_by(session_id=session_id_hash, user_id=None).all()
                for p in payments:
                    p.user_id = user_id
                    claimed_payments += 1

                ledgers = LedgerTransaction.query.filter_by(session_id=session_id_hash, user_id=None).all()
                for l in ledgers:
                    l.user_id = user_id

            # 2. Contact-based claiming (OFF by default). Moves orders ONLY, NEVER payments/ledger.
            if claim_by_contact_enabled and (email or phone):
                norm_phone = normalize_phone(phone) if phone else None
                clean_email = email.strip().lower() if email else None

                matched_guest_hashes = set()
                if clean_email:
                    guests = GuestSession.query.filter_by(email=clean_email).all()
                    for g in guests:
                        matched_guest_hashes.add(g.session_id_hash)
                if norm_phone:
                    guests = GuestSession.query.filter_by(phone=norm_phone).all()
                    for g in guests:
                        matched_guest_hashes.add(g.session_id_hash)

                if matched_guest_hashes:
                    contact_orders = Order.query.filter(Order.session_id.in_(matched_guest_hashes), Order.user_id == None).all()
                    for o in contact_orders:
                        o.user_id = user_id
                        if o.public_order_id not in public_ids:
                            public_ids.append(o.public_order_id)
                            claimed_orders += 1

        db.session.commit()
        return ClaimResult(orders_claimed=claimed_orders, payments_claimed=claimed_payments, public_order_ids=public_ids)
