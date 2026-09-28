import re
from typing import Optional

def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """
    Normalize Ghanaian and international phone numbers to E.164 format (+233XXXXXXXXX).
    Examples:
      '0202979378'    -> '+233202979378'
      '233202979378'  -> '+233202979378'
      '+233202979378' -> '+233202979378'
    """
    if not phone:
        return None
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone.strip())
    if not cleaned:
        return None
    
    if cleaned.startswith("+"):
        return cleaned
    
    if cleaned.startswith("0") and len(cleaned) == 10:
        return "+233" + cleaned[1:]
    
    if cleaned.startswith("233") and len(cleaned) == 12:
        return "+" + cleaned
        
    return "+" + cleaned if not cleaned.startswith("+") else cleaned
