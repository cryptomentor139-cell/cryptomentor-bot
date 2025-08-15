
from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.providers import cmc, coingecko, binance
from app.utils.async_tools import gather_safe

def _now_wib():
    return datetime.now().strftime("%H:%M:%S WIB")

async def build_market_report(symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """Build comprehensive market report"""
    
    # Get global metrics with fallback
    global_metrics = None
    try:
        global_metrics = await cmc.get_global_metrics()
    except Exception:
        try:
            global_metrics = await coingecko.get_global_metrics()
        except Exception:
            # Ultimate fallback
            global_metrics = {
                'market_cap': 0,
                'market_cap_change_pct_24h': 0,
                'total_volume_24h': 0,
                'active_cryptocurrencies': 0,
                'btc_dominance': 0,
                'eth_dominance': 0
            }
    
    # Default symbols if none provided
    if not symbols:
        symbols = ["BTC", "ETH", "BNB", "SOL", "XRP"]
    
    return {
        "report_time": _now_wib(),
        "global": global_metrics,
        "symbols": symbols
    }
