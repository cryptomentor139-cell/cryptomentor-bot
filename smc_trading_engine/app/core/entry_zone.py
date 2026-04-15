from typing import Iterable, Tuple

from .models import Candle


def detect_entry_zone(candles: Iterable[Candle]) -> Tuple[float, float]:
    candles = list(candles)
    if not candles:
        return (0.0, 0.0)
    last = candles[-1]
    zone_half = abs(last.high - last.low) * 0.15
    mid = last.close
    return (mid - zone_half, mid + zone_half)
