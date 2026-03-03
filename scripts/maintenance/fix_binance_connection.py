#!/usr/bin/env python3
"""
Script untuk memperbaiki dan memastikan koneksi Binance API
"""
import os
import sys

print("="*60)
print("🔧 Fixing Binance API Connection")
print("="*60)

# Step 1: Check dependencies
print("\n1️⃣ Checking dependencies...")
required_packages = ['httpx', 'requests']
missing = []

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package} installed")
    except ImportError:
        print(f"   ❌ {package} NOT installed")
        missing.append(package)

if missing:
    print(f"\n⚠️  Installing missing packages: {', '.join(missing)}")
    import subprocess
    for pkg in missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    print("✅ All dependencies installed")

# Step 2: Test direct Binance API
print("\n2️⃣ Testing direct Binance API...")
try:
    import requests
    
    response = requests.get(
        "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        price = float(data['lastPrice'])
        print(f"   ✅ Binance API accessible")
        print(f"   ✅ BTC Price: ${price:,.2f}")
    else:
        print(f"   ❌ Status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n⚠️  Possible issues:")
    print("   - Internet connection problem")
    print("   - Firewall blocking Binance")
    print("   - Binance API temporarily down")

# Step 3: Test crypto_api module
print("\n3️⃣ Testing crypto_api module...")
try:
    from crypto_api import CryptoAPI
    
    api = CryptoAPI()
    result = api.get_crypto_price('BTC', force_refresh=True)
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    elif result.get('price'):
        print(f"   ✅ crypto_api working")
        print(f"   ✅ BTC: ${result['price']:,.2f}")
    else:
        print(f"   ⚠️  Unexpected response: {result}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Test binance_provider
print("\n4️⃣ Testing binance_provider...")
try:
    from app.providers.binance_provider import get_price
    
    price = get_price('BTC', futures=False)
    
    if price and price > 0:
        print(f"   ✅ binance_provider working")
        print(f"   ✅ BTC: ${price:,.2f}")
    else:
        print(f"   ❌ Invalid price: {price}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Recommendations
print("\n" + "="*60)
print("📋 RECOMMENDATIONS")
print("="*60)

print("""
✅ If all tests passed:
   - Binance API is working correctly
   - Bot should be able to fetch data

❌ If tests failed:
   1. Check internet connection
   2. Check if Binance is blocked by firewall
   3. Try using VPN if Binance is blocked in your region
   4. Check if httpx and requests are installed
   5. Restart the bot after fixing issues

💡 Common Issues:
   - Firewall blocking api.binance.com
   - Rate limiting (too many requests)
   - Network timeout
   - Missing dependencies
""")

print("="*60)
print("✅ Diagnostic Complete")
print("="*60)
