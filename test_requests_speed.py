import sys
import os
import time
import requests

# Inject Bismillah path
_BISMILLAH_PATH = r'/root/cryptomentor-bot/Bismillah'
if _BISMILLAH_PATH not in sys.path:
    sys.path.insert(0, _BISMILLAH_PATH)

def test_speed():
    url = "https://fapi.bitunix.com/fapi/index"
    print("Testing connection speed to Bitunix using plain requests...")
    start = time.time()
    try:
        r = requests.get(url, timeout=15)
        end = time.time()
        print(f"Time taken: {end - start:.2f}s")
        print(f"Response: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_speed()
