import sys
import os
import requests

sys.path.append('D:/cryptomentorAI/Bismillah')
from app.bitunix_autotrade_client import BitunixAutoTradeClient

import sys
sys.stdout.reconfigure(encoding='utf-8')

def test():
    c = BitunixAutoTradeClient('key', 'secret') # Dummy keys to avoid init print
    # Try public contracts endpoint
    # Endpoint might be /api/v1/futures/market/contracts or /api/v1/futures/quote/contracts
    endpoints = ['/api/v1/futures/market/contracts', '/api/v1/futures/quote/contracts']
    for ep in endpoints:
        print(f"Trying {ep}...")
        res = c._request('GET', ep)
        if res.get('success'):
            print(f'SUCCESS at {ep}')
            for sym in res.get('data', [])[:5]:
                print(f"{sym['symbol']}: p_prec={sym.get('pricePrecision')} tick={sym.get('tickSize')} q_prec={sym.get('qtyPrecision')}")
            return
        else:
            print(f'FAILED at {ep}', res)

if __name__ == '__main__':
    test()
