"""
claim_service.py

Guest checkout still works (spec §16). This service is what lets someone
who ordered as a guest — before they ever created an account — see those
old orders once they register or log in, instead of starting from zero.

How linking works:
  - A guest order is always attached to a `guest_sessions` row, and that
    row optionally carries a phone/email the guest typed in at checkout
    (spec §16: "Optional: allow the customer to enter a phone number or
    email for order recovery/notifications").
  - When an account is created (or logged into) with a matching phone or
    email, every order under any guest session that shares that contact
    detail is re-attached to the new `user_id`.
  - This never happens silently in the background scanning all guests —
    it only fires for the contact details the person themselves just
    typed into the registration/login form, so it can't be used to pull
    in someone else's orders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class ClaimResult:
    orders_claimed: int
    public_order_ids: list[str]


class ClaimRepository(Protocol):
    def find_unclaimed_order_ids_by_contact(
        self, *, email: Optional[str], phone: Optional[str]
    ) -> list[tuple[int, str]]:
        """Returns [(order_id, public_order_id), ...] for guest orders
        (user_id IS NULL) whose guest_session matches this email/phone."""
        ...

    def attach_orders_to_user(self, order_ids: list[int], user_id: int) -> None: ...


class ClaimService:
    def __init__(self, repo: ClaimRepository):
        self._repo = repo

    def claim_guest_orders(
        self, *, user_id: int, email: Optional[str], phone: Optional[str]
    ) -> ClaimResult:
        """
        Call this once, right after register_customer() succeeds, and
        again on every login (cheap — it's a no-op once everything is
        already claimed). Safe to call with both email and phone, or
        either alone.
        """
        if not email and not phone:
            return ClaimResult(orders_claimed=0, public_order_ids=[])

        matches = self._repo.find_unclaimed_order_ids_by_contact(email=email, phone=phone)
        if not matches:
            return ClaimResult(orders_claimed=0, public_order_ids=[])

        order_ids = [row[0] for row in matches]
        public_ids = [row[1] for row in matches]
        self._repo.attach_orders_to_user(order_ids, user_id)

        return ClaimResult(orders_claimed=len(order_ids), public_order_ids=public_ids)
