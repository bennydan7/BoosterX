"""
order_history_service.py

Once a customer has an account (see auth/), their orders are attached to
`user_id` instead of (or in addition to) a guest `session_id` — this is
what lets them come back, log in, and see everything they've ever
ordered and whether it delivered, without re-entering a BoostX order ID
each time.

This does not replace guest checkout (spec §16 "Guest Customer Identity"
still applies for anyone who doesn't want to register) — it adds an
account-linked view on top of the same `orders` table.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol


# Mirrors the `status` values already defined in the BoostX orders table.
DELIVERED_STATUSES = {"Completed"}
IN_PROGRESS_STATUSES = {"Pending", "In Progress", "Partial"}
NOT_DELIVERED_STATUSES = {"Canceled", "Failed", "Refunded"}


@dataclass(frozen=True)
class OrderRecord:
    public_order_id: str      # e.g. BX-ORD-102948
    platform: str
    service_name: str
    target: str
    quantity: int
    charge_ghs: float
    status: str
    start_count: Optional[int]
    remains: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

    @property
    def delivered(self) -> bool:
        return self.status in DELIVERED_STATUSES


@dataclass(frozen=True)
class OrderSummary:
    total_orders: int
    delivered: int
    in_progress: int
    not_delivered: int  # canceled / failed / refunded


class OrderRepository(Protocol):
    def list_for_user(self, user_id: int, *, limit: int, offset: int) -> list[OrderRecord]: ...
    def count_for_user(self, user_id: int) -> int: ...


class OrderHistoryService:
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    def get_orders(
        self, user_id: int, *, page: int = 1, page_size: int = 20
    ) -> list[OrderRecord]:
        page = max(page, 1)
        offset = (page - 1) * page_size
        return self._repo.list_for_user(user_id, limit=page_size, offset=offset)

    def get_summary(self, user_id: int) -> OrderSummary:
        """
        "How many orders have I placed, and how many actually delivered?"
        Pulls every order for the account once and buckets it — fine at
        MVP scale; swap for a single aggregate SQL query if a customer's
        order count grows large.
        """
        all_orders = self._repo.list_for_user(user_id, limit=100_000, offset=0)
        delivered = sum(1 for o in all_orders if o.status in DELIVERED_STATUSES)
        in_progress = sum(1 for o in all_orders if o.status in IN_PROGRESS_STATUSES)
        not_delivered = sum(1 for o in all_orders if o.status in NOT_DELIVERED_STATUSES)
        return OrderSummary(
            total_orders=len(all_orders),
            delivered=delivered,
            in_progress=in_progress,
            not_delivered=not_delivered,
        )
