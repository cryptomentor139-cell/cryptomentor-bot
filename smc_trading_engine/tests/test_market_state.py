from datetime import datetime, timezone

from app.core.market_state import classify_market_state
from app.core.models import Candle


def test_market_state_trending_up():
    candles = [
        Candle(timestamp=datetime.now(timezone.utc), open=1, high=2, low=0.5, close=v, volume=10)
        for v in [1.0, 1.1, 1.2, 1.3, 1.5]
    ]
    assert classify_market_state(candles) == "trending_up"
