from app.core.models import Candle


def map_bitunix_candle(payload: dict) -> Candle:
    return Candle(
        timestamp=payload["timestamp"],
        open=float(payload["open"]),
        high=float(payload["high"]),
        low=float(payload["low"]),
        close=float(payload["close"]),
        volume=float(payload["volume"]),
    )
