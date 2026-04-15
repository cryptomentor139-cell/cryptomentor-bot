import os
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "website-backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def test_referral_code_sanitization():
    from app.routes.user import _sanitize_community_code

    assert _sanitize_community_code(" Navi-Crypto_2026!! ") == "navicrypto2026"
    assert _sanitize_community_code("   ") is None


def test_referral_fallback_url_env_override(monkeypatch):
    from app.routes.user import _fallback_referral_url

    monkeypatch.setenv("FALLBACK_REFERRAL_URL", "https://example.com/ref")
    assert _fallback_referral_url() == "https://example.com/ref"


def test_one_click_and_autotrade_risk_bounds_constants():
    from app.routes.dashboard import (
        ALLOWED_RISK_MAX,
        ONE_CLICK_RISK_MAX,
        ONE_CLICK_RISK_MIN,
    )
    from app.routes.signals import RISK_MAX_PCT

    assert ALLOWED_RISK_MAX == 10.0
    assert RISK_MAX_PCT == 10.0
    assert ONE_CLICK_RISK_MIN == 0.5
    assert ONE_CLICK_RISK_MAX == 100.0
