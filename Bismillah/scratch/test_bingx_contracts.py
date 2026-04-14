import sys
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('D:/cryptomentorAI/Bismillah')
from app.bingx_autotrade_client import BingXAutoTradeClient

def test_bingx():
    c = BingXAutoTradeClient()
    # Try public contracts endpoint
    endpoints = [
        '/openApi/swap/v2/quote/contracts',
        '/openApi/swap/v2/quote/ticker' # ticker often has precision info
    ]
    for ep in endpoints:
        print(f"Trying {ep}...")
        res = c._request('GET', ep)
        if res.get('success'):
            print(f'SUCCESS at {ep}')
            data = res.get('data', [])
            if isinstance(data, list):
                for sym in data[:5]:
                    print(f"{sym.get('symbol')}: p_prec={sym.get('pricePrecision')} tick={sym.get('tickSize')} q_prec={sym.get('quantityPrecision') or sym.get('qtyPrecision')}")
            else:
                print(f"Data: {str(data)[:200]}")
            return
        else:
            print(f'FAILED at {ep}', res)

if __name__ == '__main__':
    test_bingx()
