from typing import Iterable

from .models import Candle


def classify_market_state(candles: Iterable[Candle]) -> str:
    candles = list(candles)
    if len(candles) < 5:
        return "unknown"
    trend = candles[-1].close - candles[-5].close
    if abs(trend) < 1e-8:
        return "sideways"
    return "trending_up" if trend > 0 else "trending_down"
