from typing import Iterable

from .models import Candle


def confirm_break_of_structure(candles: Iterable[Candle]) -> bool:
    candles = list(candles)
    if len(candles) < 10:
        return False
    recent = candles[-5:]
    prior = candles[-10:-5]
    return max(c.high for c in recent) > max(c.high for c in prior) or min(c.low for c in recent) < min(c.low for c in prior)
