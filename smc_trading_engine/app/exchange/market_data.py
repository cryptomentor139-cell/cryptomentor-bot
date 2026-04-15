from app.exchange.bitunix_client import BitunixClient


async def fetch_candles(symbol: str, timeframe: str, limit: int):
    return await BitunixClient().get_candles(symbol=symbol, timeframe=timeframe, limit=limit)
