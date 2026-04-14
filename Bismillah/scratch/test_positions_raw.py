import asyncio
import sys
sys.path.append('Bismillah/app')
from bitunix_autotrade_client import BitunixAutoTradeClient

async def test_positions():
    client = BitunixAutoTradeClient('f725ce96b020a1ce65123512a89045cb', 'a1945c7117f73db124ba22adbe58fc4d')
    res = client._request('GET', '/api/v1/futures/position', signed=True)
    if res.get('success'):
        print("Positions raw data:")
        for pos in res.get('data', []):
            print(f"symbol={pos.get('symbol')} positionSide={pos.get('positionSide')} side={pos.get('side')} qty={pos.get('positionAmt') or pos.get('qty') or pos.get('quantity')}")
    else:
        print("Failed:", res)

if __name__ == "__main__":
    asyncio.run(test_positions())
