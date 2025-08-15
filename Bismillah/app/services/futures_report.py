
from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime

from app.services.market_report import build_market_report
from app.services.analysis import analyze_coin_futures
from app.utils.async_tools import gather_safe

def _now_wib():
    return datetime.now().strftime("%H:%M:%S WIB")

async def _scan_signals(coins: List[str], threshold: float = 75.0) -> List[Dict[str, Any]]:
    tasks = [analyze_coin_futures(c) for c in coins]
    results = await gather_safe(*tasks)
    out: List[Dict[str, Any]] = []
    for c, r in zip(coins, results):
        if isinstance(r, Exception):
            continue
        # gunakan field 'confidence' dari analyzer; kalau tidak ada, asumsikan 0
        conf = float(r.get("confidence", 0.0))
        if conf >= threshold:
            out.append(r)
    # urutkan confidence tertinggi
    out.sort(key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
    return out

async def build_futures_signals_report(coins: List[str] | None, threshold: float = 75.0) -> Dict[str, Any]:
    """
    - Global metrics (market_report)
    - Sinyal futures untuk daftar coins (atau default analyzer mu)
    - Filter confidence ≥ threshold
    """
    # 1) Global block (pakai default 5 top coins utk display di /market; tak mempengaruhi sinyal)
    global_rep = await build_market_report(symbols=None)

    # 2) Tentukan daftar coin untuk scan
    coins = [c.upper() for c in (coins or ["BTC","ETH","BNB","SOL","XRP"])]

    # 3) Scan sinyal
    signals = await _scan_signals(coins, threshold=threshold)

    return {
        "scan_time": _now_wib(),
        "threshold": threshold,
        "global": {
            "market_cap": global_rep["global"]["market_cap"],
            "change_pct_24h": global_rep["global"].get("market_cap_change_pct_24h", 0.0),
            "volume_24h": global_rep["global"]["total_volume_24h"],
            "active_cryptocurrencies": global_rep["global"].get("active_cryptocurrencies", 0),
            "btc_dominance": global_rep["global"].get("btc_dominance", 0.0),
            "eth_dominance": global_rep["global"].get("eth_dominance", 0.0),
        },
        "signals": signals
    }
