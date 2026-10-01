import re
import logging
from typing import Optional, Dict

logger = logging.getLogger("boostx.platform_mapper")

# Platform Keyword Patterns
PLATFORM_PATTERNS = [
    ("Instagram", [
        r"\binstagram\b", r"\binstagram\.com\b", r"\big\b", r"\binsta\b", r"\big\s", r"instagram profiles"
    ]),
    ("TikTok", [
        r"\btiktok\b", r"\btiktok\.com\b", r"\btt\b", r"\btt\s"
    ]),
    ("Facebook", [
        r"\bfacebook\b", r"\bfacebook\.com\b", r"\bfb\b", r"\bfb\s", r"facebook page"
    ]),
    ("Telegram", [
        r"\btelegram\b", r"\btelegram\.me\b", r"\bt\.me\b", r"\btg\b", r"\btg\s"
    ]),
    ("X", [
        r"\btwitter\b", r"\btwitter\.com\b", r"\bretweet\b", r"\btweet\b", r"\bx\.com\b", r"\bx\b"
    ])
]

# Map aliases passed from frontend/queries to canonical platform names
CANONICAL_PLATFORM_MAP = {
    "instagram": "Instagram",
    "ig": "Instagram",
    "insta": "Instagram",
    "tiktok": "TikTok",
    "facebook": "Facebook",
    "fb": "Facebook",
    "telegram": "Telegram",
    "tg": "Telegram",
    "x": "X",
    "twitter": "X"
}


def normalize_platform_name(query_name: Optional[str]) -> Optional[str]:
    """Map any input string (e.g. 'ig', 'twitter', 'instagram') to canonical platform name."""
    if not query_name:
        return None
    clean = query_name.strip().lower()
    if clean in CANONICAL_PLATFORM_MAP:
        return CANONICAL_PLATFORM_MAP[clean]
    # Check title case match
    for canonical in ["TikTok", "Instagram", "Facebook", "X", "Telegram"]:
        if clean == canonical.lower():
            return canonical
    return None


def classify_platform(name: str = "", category: str = "", type_: str = "") -> Optional[str]:
    """
    Centralized platform classifier for BaloonBoost services.
    Inspects name, category, and type together using text normalization.
    """
    combined = f"{category} {name} {type_}".lower()
    clean_combined = re.sub(r"[^\w\s\.\-]", " ", combined)

    # 1. Direct platform keyword search
    for platform_name, patterns in PLATFORM_PATTERNS:
        for pat in patterns:
            if re.search(pat, clean_combined):
                return platform_name

    # 2. Check for Twitter / X retweets / tweet terms specifically for X
    if any(kw in clean_combined for kw in ["twitter", "retweet", "tweet"]):
        return "X"

    # 3. Check for IG / Insta terms
    if any(kw in clean_combined for kw in ["instagram", "insta", "ig"]):
        return "Instagram"

    # 4. Check for FB terms
    if any(kw in clean_combined for kw in ["facebook", "fb"]):
        return "Facebook"

    # 5. Check for TG terms
    if any(kw in clean_combined for kw in ["telegram", "tg"]):
        return "Telegram"

    # 6. Check for TikTok terms
    if "tiktok" in clean_combined:
        return "TikTok"

    return None


def log_platform_mapping_diagnostics(services_list: list) -> Dict[str, int]:
    """
    Production-safe diagnostic logger (does NOT log API keys or secrets).
    Logs summary statistics of provider catalog mapping.
    """
    counts = {
        "Instagram": 0,
        "TikTok": 0,
        "Facebook": 0,
        "X": 0,
        "Telegram": 0,
        "Unmapped": 0
    }

    sample_items = []
    for item in services_list[:5]:
        s_id = getattr(item, "service_id", item.get("service") if isinstance(item, dict) else None)
        s_name = getattr(item, "name", item.get("name") if isinstance(item, dict) else "")
        s_cat = getattr(item, "category", item.get("category") if isinstance(item, dict) else "")
        s_type = getattr(item, "type", item.get("type") if isinstance(item, dict) else "")
        sample_items.append(f"ID {s_id}: [{s_cat}] {s_name} ({s_type})")

    for item in services_list:
        s_name = getattr(item, "name", item.get("name") if isinstance(item, dict) else "")
        s_cat = getattr(item, "category", item.get("category") if isinstance(item, dict) else "")
        s_type = getattr(item, "type", item.get("type") if isinstance(item, dict) else "")
        
        plat = classify_platform(name=s_name, category=s_cat, type_=s_type)
        if plat in counts:
            counts[plat] += 1
        else:
            counts["Unmapped"] += 1

    logger.info(f"BaloonBoost catalog returned {len(services_list)} services.")
    logger.info(f"Sample BaloonBoost items: {sample_items}")
    logger.info(f"Platform Mapping Counts: {counts}")
    return counts
