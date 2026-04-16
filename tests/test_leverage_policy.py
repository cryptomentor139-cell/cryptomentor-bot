import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BISMILLAH = os.path.join(_ROOT, "Bismillah")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _BISMILLAH not in sys.path:
    sys.path.insert(0, _BISMILLAH)

try:
    from Bismillah.app.leverage_policy import get_auto_max_safe_leverage
except ImportError:
    from app.leverage_policy import get_auto_max_safe_leverage  # type: ignore


def test_known_symbol_returns_expected_max_safe_leverage():
    assert get_auto_max_safe_leverage("BTCUSDT") == 200
    assert get_auto_max_safe_leverage("ETHUSDT") == 100
    assert get_auto_max_safe_leverage("AVAXUSDT") == 50


def test_unknown_symbol_falls_back_safely():
    assert get_auto_max_safe_leverage("UNKNOWNUSDT") == 20
    assert get_auto_max_safe_leverage("") == 20


def test_baseline_does_not_override_effective_policy():
    # Baseline is metadata-only; effective leverage remains pair-policy based.
    assert get_auto_max_safe_leverage("BTCUSDT", baseline_leverage=5) == 200
    assert get_auto_max_safe_leverage("SOLUSDT", baseline_leverage=100) == 75

