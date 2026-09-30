import os
import sys
from decimal import Decimal

class Config:
    TESTING = os.getenv("TESTING", "false").lower() in ("true", "1") or "pytest" in sys.modules
    SECRET_KEY = os.getenv("SECRET_KEY", "boostx-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boostx.db')}"
    )
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Provider Settings
    PROVIDER_MODE = os.getenv("PROVIDER_MODE", "fake")  # 'live' or 'fake'
    PROVIDER_API_URL = os.getenv("PROVIDER_API_URL", "https://boostcenter2.com/api/v2")
    PROVIDER_API_KEY = os.getenv("PROVIDER_API_KEY", "mock-provider-key")
    
    # AI Vision Verification Settings (Gemini OpenAI-compatible API)
    AI_API_URL = os.getenv("AI_API_URL", os.getenv("OPENAI_API_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"))
    AI_API_KEY = os.getenv("AI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    AI_MODEL = os.getenv("AI_MODEL", os.getenv("OPENAI_VISION_MODEL", "gemini-2.0-flash-lite"))
    
    # FX Rate Settings
    FX_API_URL = os.getenv("FX_API_URL", "")
    DEFAULT_USD_TO_GHS = Decimal(os.getenv("USD_TO_GHS_RATE", os.getenv("DEFAULT_USD_TO_GHS", "10.70")))
    DEFAULT_FLAT_MARKUP_GHS = Decimal(os.getenv("FLAT_MARKUP_GHS", os.getenv("DEFAULT_FLAT_MARKUP_GHS", "5.00")))
    
    # Session & Claiming Settings
    SESSION_COOKIE_NAME = "boostx_session"
    GUEST_COOKIE_NAME = "boostx_guest"
    CLAIM_BY_CONTACT_ENABLED = os.getenv("CLAIM_BY_CONTACT_ENABLED", "false").lower() == "true"
    
    # Storage Settings
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
