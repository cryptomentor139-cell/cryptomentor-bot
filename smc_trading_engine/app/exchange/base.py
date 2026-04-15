from abc import ABC, abstractmethod


class ExchangeClientBase(ABC):
    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, limit: int):
        raise NotImplementedError

    @abstractmethod
    async def get_ticker(self, symbol: str):
        raise NotImplementedError

    @abstractmethod
    async def get_open_position(self, symbol: str):
        raise NotImplementedError
