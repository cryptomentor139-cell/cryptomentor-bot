#!/usr/bin/env python3
"""
Test script untuk cek koneksi Binance API
"""
import sys
import traceback

print("="*60)
print("🔍 Testing Binance API Connection")
print("="*60)

# Test 1: Import modules
print("\n1️⃣ Testing imports...")
try:
    from crypto_api import CryptoAPI
    print("   ✅ crypto_api imported")
except Exception as e:
    print(f"   ❌ Failed to import crypto_api: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Initialize CryptoAPI
print("\n2️⃣ Initializing CryptoAPI...")
try:
    crypto_api = CryptoAPI()
    print("   ✅ CryptoAPI initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Get BTC price
print("\n3️⃣ Testing get_crypto_price('BTC')...")
try:
    result = crypto_api.get_crypto_price('BTC', force_refresh=True)
    print(f"   Result: {result}")
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    elif result.get('success'):
        price = result.get('price', 0)
        change = result.get('change_24h', 0)
        print(f"   ✅ BTC Price: ${price:,.2f}")
        print(f"   ✅ 24h Change: {change:+.2f}%")
    else:
        print(f"   ⚠️  Unexpected response format")
except Exception as e:
    print(f"   ❌ Exception: {e}")
    traceback.print_exc()

# Test 4: Get ETH price
print("\n4️⃣ Testing get_crypto_price('ETH')...")
try:
    result = crypto_api.get_crypto_price('ETH', force_refresh=True)
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    elif result.get('success'):
        price = result.get('price', 0)
        change = result.get('change_24h', 0)
        print(f"   ✅ ETH Price: ${price:,.2f}")
        print(f"   ✅ 24h Change: {change:+.2f}%")
    else:
        print(f"   ⚠️  Unexpected response format")
except Exception as e:
    print(f"   ❌ Exception: {e}")
    traceback.print_exc()

# Test 5: Get futures data
print("\n5️⃣ Testing get_futures_data('BTC')...")
try:
    result = crypto_api.get_futures_data('BTC')
    print(f"   Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    elif result.get('success'):
        print(f"   ✅ Futures data retrieved successfully")
        if 'data' in result:
            data = result['data']
            print(f"   Data keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
    else:
        print(f"   ⚠️  Unexpected response format")
except Exception as e:
    print(f"   ❌ Exception: {e}")
    traceback.print_exc()

# Test 6: Direct Binance API test
print("\n6️⃣ Testing direct Binance API call...")
try:
    import requests
    
    # Test Binance spot price
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    response = requests.get(url, timeout=10)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        price = float(data.get('lastPrice', 0))
        change = float(data.get('priceChangePercent', 0))
        print(f"   ✅ Direct API works!")
        print(f"   BTC Price: ${price:,.2f}")
        print(f"   24h Change: {change:+.2f}%")
    else:
        print(f"   ❌ API returned status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Test Complete")
print("="*60)
