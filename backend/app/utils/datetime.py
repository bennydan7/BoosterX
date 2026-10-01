from datetime import datetime, timezone

def utc_now() -> datetime:
    """Return current UTC time as a timezone-naive datetime object for DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
