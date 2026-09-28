import logging
from decimal import Decimal
import requests
from flask import current_app
from backend.app.db import db
from backend.app.models import Setting

logger = logging.getLogger("boostx.fx_worker")

SANITY_BAND_MAX_CHANGE = Decimal("0.20")  # 20% max allowed single change

def refresh_fx_rate_worker(app=None) -> dict:
    if app:
        with app.app_context():
            return _do_refresh()
    else:
        return _do_refresh()

def _do_refresh() -> dict:
    fx_url = current_app.config.get("FX_API_URL")
    if not fx_url:
        return {"status": "skipped", "reason": "No FX_API_URL configured"}

    try:
        resp = requests.get(fx_url, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        new_rate = Decimal(str(data.get("rate") or data.get("GHS") or data.get("usd_to_ghs")))
    except Exception as exc:
        logger.warning(f"Failed to fetch live FX rate: {exc}")
        return {"status": "error", "message": str(exc)}

    setting = Setting.query.filter_by(key="usd_to_ghs_rate").first()
    if setting:
        old_rate = Decimal(setting.value)
        # Sanity band check
        diff = abs(new_rate - old_rate) / old_rate
        if diff > SANITY_BAND_MAX_CHANGE:
            logger.warning(f"FX rate jump of {diff * 100:.1f}% rejected by sanity band check (old={old_rate}, new={new_rate})")
            return {"status": "rejected", "reason": f"Jump of {diff * 100:.1f}% exceeded sanity band limit"}
        setting.value = str(new_rate)
    else:
        db.session.add(Setting(key="usd_to_ghs_rate", value=str(new_rate)))

    db.session.commit()
    logger.info(f"Updated USD/GHS rate to {new_rate}")
    return {"status": "success", "rate": str(new_rate)}
