"""
Canonical leverage policy for all execution paths.

Current policy:
- Auto max-safe leverage is pair-based (exchange max per supported symbol).
- Unknown symbols fall back to a conservative default.
"""

from __future__ import annotations

from typing import Optional

DEFAULT_UNKNOWN_SYMBOL_LEVERAGE = 20

SYMBOL_MAX_LEVERAGE = {
    "BTCUSDT": 200,
    "ETHUSDT": 100,
    "SOLUSDT": 75,
    "DOGEUSDT": 75,
    "XRPUSDT": 75,
    "ADAUSDT": 75,
    "BNBUSDT": 75,
    "AVAXUSDT": 50,
    "DOTUSDT": 50,
    "MATICUSDT": 50,
    "LINKUSDT": 50,
    "UNIUSDT": 50,
    "ATOMUSDT": 50,
    "XAUUSDT": 100,
    "CLUSDT": 100,
    "QQQUSDT": 100,
}


def get_auto_max_safe_leverage(
    symbol: str,
    entry_price: Optional[float] = None,
    sl_price: Optional[float] = None,
    baseline_leverage: Optional[int] = None,
) -> int:
    """
    Return leverage from canonical auto max-safe policy.

    Parameters are kept for forward compatibility. Current behavior is purely
    pair-based and does not override from baseline leverage.
    """
    _ = (entry_price, sl_price, baseline_leverage)
    try:
        sym = str(symbol or "").upper()
        if not sym:
            return DEFAULT_UNKNOWN_SYMBOL_LEVERAGE
        return max(1, int(SYMBOL_MAX_LEVERAGE.get(sym, DEFAULT_UNKNOWN_SYMBOL_LEVERAGE)))
    except Exception:
        return DEFAULT_UNKNOWN_SYMBOL_LEVERAGE

