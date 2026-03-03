#!/usr/bin/env python3
"""Quick test Binance API"""
import requests

print("Testing Binance API...")

# Test 1: Direct API call
try:
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        price = float(data['lastPrice'])
        change = float(data['priceChangePercent'])
        print(f"✅ BTC Price: ${price:,.2f}")
        print(f"✅ 24h Change: {change:+.2f}%")
        print("✅ Binance API is working!")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Using crypto_api
print("\nTesting crypto_api module...")
try:
    from crypto_api import CryptoAPI
    
    api = CryptoAPI()
    result = api.get_crypto_price('BTC', force_refresh=True)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ BTC: ${result.get('price', 0):,.2f}")
        print(f"✅ Change: {result.get('change_24h', 0):+.2f}%")
        print("✅ crypto_api is working!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
