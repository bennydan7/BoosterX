"""
pricing_service.py

BoostX pricing engine — GHS only.

Rule (per Enock's instruction):
    customer_price_ghs = (provider_rate_usd_per_1000 / 1000 * quantity * usd_to_ghs_rate)
                          + flat_markup_ghs

The flat markup defaults to GHS 5.00 and is added once per order — not per
unit — matching the spec's "Provider cost + BoostX markup = Customer price"
example. Everything here runs SERVER-SIDE ONLY. The frontend may preview a
price, but this function is the final authority (spec §9, §10, §51).

The provider's USD rate is NEVER returned to the customer — only the final
GHS figure. See `PricingService.quote_service` docstring.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


class PricingError(ValueError):
    """Raised when a quote request is invalid (quantity out of range, etc.)."""


@dataclass(frozen=True)
class PricingSettings:
    """
    Admin-configurable pricing settings.

    usd_to_ghs_rate:
        The FX rate BoostX uses to convert the provider's USD cost into GHS.
        USD/GHS moves fast (double-digit % swings within weeks) — do NOT
        hardcode this. Store it in the `settings` table, let the admin edit
        it, and/or refresh it from a live FX feed on a schedule. A stale
        rate here directly eats into your margin or overcharges customers.
    flat_markup_ghs:
        Flat amount added to every order's converted cost. Default GHS 5.00
        per Enock's instruction. Keep as Decimal to avoid float rounding
        drift on money.
    """

    usd_to_ghs_rate: Decimal
    flat_markup_ghs: Decimal = Decimal("5.00")
    currency: str = "GHS"


@dataclass(frozen=True)
class ServiceQuote:
    service_id: int
    quantity: int
    provider_cost_ghs: Decimal  # internal only — never send to the client
    markup_ghs: Decimal
    customer_price_ghs: Decimal
    currency: str


def _round_money(amount: Decimal) -> Decimal:
    """Round to 2dp, half-up — the way customers expect money to round."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class PricingService:
    """
    Stateless pricing engine. Takes provider rates (as loaded from the
    synced `services` table — see provider_client.ProviderService) and the
    admin's PricingSettings, and produces GHS quotes.
    """

    def __init__(self, settings: PricingSettings):
        if settings.usd_to_ghs_rate <= 0:
            raise PricingError("usd_to_ghs_rate must be a positive rate, configured by an admin")
        self._settings = settings

    def quote_service(
        self,
        *,
        service_id: int,
        provider_rate_usd_per_1000: Decimal,
        quantity: int,
        min_qty: int,
        max_qty: int,
    ) -> ServiceQuote:
        """
        Compute the GHS price for `quantity` units of a service.

        Only `customer_price_ghs` (and `currency`) should ever be sent to
        the frontend / customer. `provider_cost_ghs` and `markup_ghs` are
        for admin dashboards / internal accounting only — spec §10 is
        explicit that the wholesale cost must not be exposed.
        """
        if quantity < min_qty or quantity > max_qty:
            raise PricingError(
                f"Quantity {quantity} is outside the allowed range "
                f"[{min_qty}, {max_qty}] for service {service_id}"
            )
        if provider_rate_usd_per_1000 < 0:
            raise PricingError("provider_rate_usd_per_1000 cannot be negative")

        provider_cost_usd = (provider_rate_usd_per_1000 / Decimal(1000)) * Decimal(quantity)
        provider_cost_ghs = _round_money(provider_cost_usd * self._settings.usd_to_ghs_rate)

        customer_price_ghs = _round_money(provider_cost_ghs + self._settings.flat_markup_ghs)

        return ServiceQuote(
            service_id=service_id,
            quantity=quantity,
            provider_cost_ghs=provider_cost_ghs,
            markup_ghs=self._settings.flat_markup_ghs,
            customer_price_ghs=customer_price_ghs,
            currency=self._settings.currency,
        )

    def customer_facing_rate_per_1000(
        self, provider_rate_usd_per_1000: Decimal
    ) -> Decimal:
        """
        For display on the service-selection page ("GHS X.XX per 1000"),
        computed the same way as quote_service but WITHOUT the flat markup
        baked in per-1000 (the markup is applied once at order time, not
        per displayed unit rate). Useful for a "starting from" price label.
        """
        return _round_money(
            (provider_rate_usd_per_1000 / Decimal(1000)) * Decimal(1000) * self._settings.usd_to_ghs_rate
        )


# --------------------------------------------------------------------- #
# Example (remove/replace with real settings loaded from the DB/env)
# --------------------------------------------------------------------- #
if __name__ == "__main__":
    # Illustrative only — in the real app, usd_to_ghs_rate comes from the
    # admin settings table (see §43/§44 of the spec), not a hardcoded value.
    settings = PricingSettings(
        usd_to_ghs_rate=Decimal("10.70"),  # <-- update regularly; FX moves fast
        flat_markup_ghs=Decimal("5.00"),
    )
    pricing = PricingService(settings)

    quote = pricing.quote_service(
        service_id=1,
        provider_rate_usd_per_1000=Decimal("0.90"),  # TikTok Followers example from provider
        quantity=1000,
        min_qty=50,
        max_qty=10000,
    )
    print(quote)
    # ServiceQuote(service_id=1, quantity=1000, provider_cost_ghs=Decimal('9.63'),
    #              markup_ghs=Decimal('5.00'), customer_price_ghs=Decimal('14.63'),
    #              currency='GHS')
