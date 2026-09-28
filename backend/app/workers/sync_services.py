import logging
from decimal import Decimal
from typing import Optional
from backend.app.db import db
from backend.app.models import Service, Platform
from backend.app.providers.factory import get_provider_client

logger = logging.getLogger("boostx.sync_services")

KEYWORD_MAP = {
    "TikTok": ["tiktok"],
    "Instagram": ["instagram", "ig follower", "ig like", "ig view"],
    "Facebook": ["facebook", "fb follower", "fb page", "fb like"],
    "X": ["twitter", "x post", "x follower", "x like", "x ("],
    "Telegram": ["telegram", "tg member", "tg channel"]
}

def classify_platform(category: str, name: str) -> Optional[str]:
    combined = f"{category} {name}".lower()
    for platform_name, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in combined:
                return platform_name
    return None

def sync_services_worker(app=None) -> dict:
    """
    Background worker: fetches provider catalog, classifies into 5 platforms,
    upserts into services table, deactivates vanished services.
    """
    if app:
        with app.app_context():
            return _do_sync()
    else:
        return _do_sync()

def _do_sync() -> dict:
    logger.info("Starting service catalog sync worker...")
    provider = get_provider_client()
    try:
        raw_services = provider.get_services()
    except Exception as exc:
        logger.error(f"Failed to fetch services from provider: {exc}")
        return {"status": "error", "message": str(exc)}

    active_platforms = set(p.name for p in Platform.query.filter_by(active=True).all())
    
    synced_count = 0
    updated_count = 0
    fetched_provider_ids = set()

    for item in raw_services:
        # Ignore non-Default types
        if item.type and item.type != "Default":
            continue

        platform = classify_platform(item.category, item.name)
        if not platform or platform not in active_platforms:
            continue

        fetched_provider_ids.add(item.service_id)
        
        service = Service.query.filter_by(provider_service_id=item.service_id).first()
        if not service:
            service = Service(
                provider_service_id=item.service_id,
                platform=platform,
                category=item.category,
                name=item.name,
                type=item.type or "Default",
                description=item.description,
                rate_usd_per_1000=Decimal(str(item.rate_usd_per_1000)),
                min_qty=item.min_qty,
                max_qty=item.max_qty,
                refill_available=item.refill_available,
                enabled=False  # New services start disabled per spec
            )
            db.session.add(service)
            synced_count += 1
        else:
            service.platform = platform
            service.category = item.category
            service.name = item.name
            service.description = item.description
            service.rate_usd_per_1000 = Decimal(str(item.rate_usd_per_1000))
            service.min_qty = item.min_qty
            service.max_qty = item.max_qty
            service.refill_available = item.refill_available
            updated_count += 1

    # Deactivate vanished services
    vanished_count = 0
    existing_services = Service.query.all()
    for s in existing_services:
        if s.provider_service_id not in fetched_provider_ids:
            if s.enabled:
                s.enabled = False
                vanished_count += 1

    db.session.commit()
    logger.info(f"Sync complete: {synced_count} added, {updated_count} updated, {vanished_count} deactivated.")
    return {
        "status": "success",
        "added": synced_count,
        "updated": updated_count,
        "deactivated": vanished_count
    }
