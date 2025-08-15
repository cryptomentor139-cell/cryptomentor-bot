
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
    
    # Normalize symbol - ensure it ends with USDT
    if not symbol.upper().endswith('USDT'):
        symbol = symbol.upper() + 'USDT'
    
    # Handle special cases
    symbol_aliases = {
        'IOTAUSDT': 'IOTAUSDT',  # IOTA is supported on Binance
        'BTTUSDT': 'BTTCUSDT',   # BTT is now BTTC
        'BCHSVUSDT': 'BSVUSDT'   # BCHSV is now BSV
    }
    
    symbol = symbol_aliases.get(symbol, symbol)
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        
        if not data or len(data) == 0:
            print(f"⚠️ No data returned from Binance for {symbol}")
            return []
        
        # Map to unified rows format
        rows = []
        for k in data:
            try:
                rows.append({
                    "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(k[6]//1000)),  # close time
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                })
            except (ValueError, IndexError) as parse_error:
                print(f"⚠️ Error parsing candle data for {symbol}: {parse_error}")
                continue
        
        print(f"✅ Binance fallback successful for {symbol}: {len(rows)} candles")
        return rows
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            print(f"❌ Binance: Invalid symbol {symbol} (400 Bad Request)")
        else:
            print(f"❌ Binance HTTP error for {symbol}: {e.response.status_code}")
        return []
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
