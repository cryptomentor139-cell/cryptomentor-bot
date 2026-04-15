from datetime import datetime, timedelta, timezone


class PairCooldown:
    def __init__(self, minutes: int = 30):
        self.minutes = minutes
        self._last_trade = {}

    def mark(self, symbol: str) -> None:
        self._last_trade[symbol] = datetime.now(timezone.utc)

    def is_blocked(self, symbol: str) -> bool:
        last = self._last_trade.get(symbol)
        if not last:
            return False
        return datetime.now(timezone.utc) < last + timedelta(minutes=self.minutes)
