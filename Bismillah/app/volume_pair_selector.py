"""
Global volume-ranked pair selector for Bitunix futures.

Provides a cached top-volume symbol list (USDT pairs) used by both
autotrade (swing) and scalping engines.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

BITUNIX_BASE_URL = (
    os.getenv("BITUNIX_GATEWAY_URL", "").rstrip("/")
    or os.getenv("BITUNIX_BASE_URL", "https://fapi.bitunix.com").rstrip("/")
)
TICKERS_PATH = "/api/v1/futures/market/tickers"
REFRESH_TTL_SECONDS = 300
DEFAULT_LIMIT = 10

# Legacy fallback universe (stable, known tradable set in current engines).
DEFAULT_BOOTSTRAP_PAIRS: List[str] = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "AVAXUSDT",
    "DOTUSDT",
    "LINKUSDT",
]

_lock = threading.Lock()
_state: Dict[str, object] = {
    "pairs": [],
    "last_refresh_ts": 0.0,
    "source": "bootstrap",
    "error": None,
    "requested_limit": DEFAULT_LIMIT,
}


def _safe_float(v) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def _fetch_ranked_pairs(limit: int) -> List[str]:
    url = f"{BITUNIX_BASE_URL}{TICKERS_PATH}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    payload = resp.json() or {}

    if int(payload.get("code", -1)) != 0:
        raise RuntimeError(f"Bitunix ticker error: code={payload.get('code')} msg={payload.get('msg')}")

    rows = payload.get("data") or []
    ranked = []
    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol.endswith("USDT"):
            continue
        vol = _safe_float(row.get("quoteVol"))
        if vol <= 0:
            continue
        ranked.append((symbol, vol))

    if not ranked:
        raise RuntimeError("Bitunix ticker returned empty/invalid volume rows")

    ranked.sort(key=lambda x: x[1], reverse=True)
    top = []
    seen = set()
    for symbol, _ in ranked:
        if symbol in seen:
            continue
        seen.add(symbol)
        top.append(symbol)
        if len(top) >= limit:
            break
    return top


def get_ranked_top_volume_pairs(limit: int = DEFAULT_LIMIT) -> List[str]:
    limit = max(1, int(limit or DEFAULT_LIMIT))
    now = time.time()

    with _lock:
        cached_pairs = list(_state.get("pairs") or [])
        cache_age = now - float(_state.get("last_refresh_ts", 0.0) or 0.0)
        if cached_pairs and cache_age < REFRESH_TTL_SECONDS:
            return cached_pairs[:limit]

    try:
        top = _fetch_ranked_pairs(limit)
        with _lock:
            _state["pairs"] = top
            _state["last_refresh_ts"] = now
            _state["source"] = "fresh"
            _state["error"] = None
            _state["requested_limit"] = limit

        logger.info(
            "[VolumeSelector] refresh_success ts=%s source=fresh pair_count=%s pairs=%s",
            int(now),
            len(top),
            ",".join(top),
        )
        return top
    except Exception as e:
        with _lock:
            cached_pairs = list(_state.get("pairs") or [])
            if cached_pairs:
                _state["source"] = "cache_fallback"
                _state["error"] = str(e)
                logger.warning(
                    "[VolumeSelector] refresh_failed ts=%s source=cache_fallback pair_count=%s error=%s",
                    int(now),
                    len(cached_pairs),
                    e,
                )
                return cached_pairs[:limit]

            bootstrap = DEFAULT_BOOTSTRAP_PAIRS[:limit]
            _state["pairs"] = bootstrap
            _state["last_refresh_ts"] = now
            _state["source"] = "bootstrap_fallback"
            _state["error"] = str(e)
            _state["requested_limit"] = limit

            logger.warning(
                "[VolumeSelector] refresh_failed ts=%s source=bootstrap_fallback pair_count=%s error=%s",
                int(now),
                len(bootstrap),
                e,
            )
            return bootstrap


def get_selector_health() -> Dict[str, object]:
    with _lock:
        return {
            "last_refresh_ts": _state.get("last_refresh_ts"),
            "source": _state.get("source"),
            "pair_count": len(_state.get("pairs") or []),
            "pairs": list(_state.get("pairs") or []),
            "error": _state.get("error"),
            "requested_limit": _state.get("requested_limit"),
            "refresh_ttl_seconds": REFRESH_TTL_SECONDS,
        }

