"""Test crypto data providers WL#1"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.providers.data_provider import inject_provider_env
inject_provider_env()

import requests

# ── CryptoCompare ──────────────────────────────────────────────────
print("=== CryptoCompare ===")
cc_key = os.getenv("CRYPTOCOMPARE_API_KEY", "")
print(f"Key: {'SET (' + cc_key[:6] + '...)' if cc_key else 'MISSING'}")
try:
    r = requests.get(
        "https://min-api.cryptocompare.com/data/v2/histohour",
        params={"fsym": "BTC", "tsym": "USDT", "limit": 5, "api_key": cc_key},
        timeout=10
    )
    data = r.json()
    if data.get("Response") == "Success":
        candles = data["Data"]["Data"]
        print(f"✅ CryptoCompare OK — got {len(candles)} candles, latest close: {candles[-1]['close']}")
    else:
        print(f"❌ CryptoCompare error: {data.get('Message')}")
except Exception as e:
    print(f"❌ CryptoCompare failed: {e}")

print()

# ── CoinGecko ──────────────────────────────────────────────────────
print("=== CoinGecko ===")
cg_key = os.getenv("COINGECKO_API_KEY", "")
print(f"Key: {'SET (' + cg_key[:6] + '...)' if cg_key else 'NOT SET (using free tier)'}")
try:
    headers = {"x-cg-demo-api-key": cg_key} if cg_key else {}
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "bitcoin", "vs_currencies": "usd"},
        headers=headers,
        timeout=10
    )
    data = r.json()
    if "bitcoin" in data:
        print(f"✅ CoinGecko OK — BTC price: ${data['bitcoin']['usd']:,}")
    else:
        print(f"❌ CoinGecko error: {data}")
except Exception as e:
    print(f"❌ CoinGecko failed: {e}")
