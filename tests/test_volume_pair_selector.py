import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BISMILLAH = os.path.join(_ROOT, "Bismillah")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _BISMILLAH not in sys.path:
    sys.path.insert(0, _BISMILLAH)

try:
    import Bismillah.app.volume_pair_selector as selector
except ImportError:
    import app.volume_pair_selector as selector  # type: ignore


class _Resp:
    def __init__(self, payload, code=200):
        self._payload = payload
        self.status_code = code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self):
        return self._payload


def _reset_state():
    selector._state["pairs"] = []
    selector._state["last_refresh_ts"] = 0.0
    selector._state["source"] = "bootstrap"
    selector._state["error"] = None
    selector._state["requested_limit"] = selector.DEFAULT_LIMIT


def test_selector_sorts_quote_volume_desc_and_filters_usdt(monkeypatch):
    _reset_state()

    payload = {
        "code": 0,
        "msg": "Success",
        "data": [
            {"symbol": "AAAUSDT", "quoteVol": "50"},
            {"symbol": "BBBUSDT", "quoteVol": "200"},
            {"symbol": "CCCUSDT", "quoteVol": "120"},
            {"symbol": "BTCUSD", "quoteVol": "999"},  # ignored (not USDT futures pair)
            {"symbol": "DDDUSDT", "quoteVol": "0"},   # ignored (no volume)
        ],
    }

    monkeypatch.setattr(selector.requests, "get", lambda *args, **kwargs: _Resp(payload))
    pairs = selector.get_ranked_top_volume_pairs(limit=3)
    assert pairs == ["BBBUSDT", "CCCUSDT", "AAAUSDT"]


def test_selector_uses_cache_fallback_when_refresh_fails(monkeypatch):
    _reset_state()
    selector._state["pairs"] = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    selector._state["last_refresh_ts"] = 0.0  # force refresh path

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(selector.requests, "get", _boom)
    pairs = selector.get_ranked_top_volume_pairs(limit=2)
    assert pairs == ["BTCUSDT", "ETHUSDT"]
    assert selector.get_selector_health()["source"] == "cache_fallback"


def test_selector_bootstrap_fallback_when_no_cache_and_refresh_fails(monkeypatch):
    _reset_state()

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(selector.requests, "get", _boom)
    pairs = selector.get_ranked_top_volume_pairs(limit=4)
    assert pairs == selector.DEFAULT_BOOTSTRAP_PAIRS[:4]
    assert selector.get_selector_health()["source"] == "bootstrap_fallback"

