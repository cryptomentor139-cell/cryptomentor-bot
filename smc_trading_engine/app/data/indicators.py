def atr(candles, period: int = 14) -> float:
    if not candles:
        return 0.0
    highs = [c.high for c in candles[-period:]]
    lows = [c.low for c in candles[-period:]]
    return (max(highs) - min(lows)) / max(1, len(highs))
