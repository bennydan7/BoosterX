from flask import current_app
from backend.app.providers.interface import ProviderInterface
from backend.app.providers.provider_client import ProviderAdapter
from backend.app.providers.fake_provider import FakeProvider

_fake_instance = None

def get_provider_client() -> ProviderInterface:
    global _fake_instance
    mode = current_app.config.get("PROVIDER_MODE", "fake").lower()
    if mode == "live":
        return ProviderAdapter(
            api_url=current_app.config["PROVIDER_API_URL"],
            api_key=current_app.config["PROVIDER_API_KEY"]
        )
    else:
        if _fake_instance is None:
            _fake_instance = FakeProvider()
        return _fake_instance
