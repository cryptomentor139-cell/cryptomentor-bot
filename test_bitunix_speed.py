import sys
import os
import time

# Inject Bismillah path
_BISMILLAH_PATH = r'/root/cryptomentor-bot/Bismillah'
if _BISMILLAH_PATH not in sys.path:
    sys.path.insert(0, _BISMILLAH_PATH)

from app.bitunix_autotrade_client import BitunixAutoTradeClient

def test_speed():
    client = BitunixAutoTradeClient()
    print("Testing connection speed to Bitunix...")
    start = time.time()
    try:
        # Use a real endpoint that doesn't need keys if possible, or just index
        res = client._request('GET', '/fapi/index')
        end = time.time()
        print(f"Time taken: {end - start:.2f}s")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_speed()
