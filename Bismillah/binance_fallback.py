
import time
import httpx
import asyncio

BINANCE_URL = "https://api.binance.com"

async def get_klines(symbol="BNBUSDT", interval="5m", limit=300, timeout=10):
    """
    Binance fallback for when CoinAPI fails
    Returns unified format compatible with existing analyzers
    """
    url = f"{BINANCE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        
        # Map to unified rows format
        rows = []
        for k in data:
            rows.append({
                "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(k[6]//1000)),  # close time
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            })
        return rows
    except Exception as e:
        print(f"❌ Binance fallback failed for {symbol}: {e}")
        return []

async def get_price(symbol="BNBUSDT", timeout=10):
    """
    Get current price from Binance as fallback
    """
    url = f"{BINANCE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        return float(data["price"])
    except Exception as e:
        print(f"❌ Binance price fallback failed for {symbol}: {e}")
        return 0.0
