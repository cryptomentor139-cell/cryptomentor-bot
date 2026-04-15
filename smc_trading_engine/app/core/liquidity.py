from typing import Iterable

from .models import Candle


def detect_liquidity_sweep(candles: Iterable[Candle]) -> bool:
    candles = list(candles)
    if len(candles) < 3:
        return False
    prev_high = max(c.high for c in candles[:-1])
    prev_low = min(c.low for c in candles[:-1])
    last = candles[-1]
    swept_high = last.high > prev_high and last.close < prev_high
    swept_low = last.low < prev_low and last.close > prev_low
    return swept_high or swept_low
