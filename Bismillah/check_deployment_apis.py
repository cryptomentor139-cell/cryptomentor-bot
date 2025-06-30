
#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_deployment_apis():
    """Quick API health check for deployment environment"""
    print("🚀 DEPLOYMENT API Health Check")
    print("=" * 50)
    
    # Environment detection
    is_deployment = (
        os.getenv('REPLIT_DEPLOYMENT') == '1' or 
        os.getenv('REPL_DEPLOYMENT') == '1'
    )
    print(f"🌍 Environment: {'🌐 DEPLOYMENT' if is_deployment else '🔧 DEVELOPMENT'}")
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    results = {}
    
    # 1. Binance API Test
    print("\n⚡ Testing Binance APIs...")
    try:
        # Test Binance Spot
        spot_response = requests.get("https://api.binance.com/api/v3/ping", timeout=10)
        if spot_response.status_code == 200:
            print("✅ Binance Spot API: ONLINE")
            results['binance_spot'] = True
        else:
            print("❌ Binance Spot API: OFFLINE")
            results['binance_spot'] = False
            
        # Test Binance Futures
        futures_response = requests.get("https://fapi.binance.com/fapi/v1/ping", timeout=10)
        if futures_response.status_code == 200:
            print("✅ Binance Futures API: ONLINE")
            results['binance_futures'] = True
        else:
            print("❌ Binance Futures API: OFFLINE")
            results['binance_futures'] = False
            
    except Exception as e:
        print(f"❌ Binance API Error: {e}")
        results['binance_spot'] = False
        results['binance_futures'] = False

    # 2. CoinGecko API Test
    print("\n🦎 Testing CoinGecko API...")
    try:
        cg_response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=10)
        if cg_response.status_code == 200:
            print("✅ CoinGecko Free API: ONLINE")
            results['coingecko'] = True
        else:
            print("❌ CoinGecko Free API: OFFLINE")
            results['coingecko'] = False
    except Exception as e:
        print(f"❌ CoinGecko API Error: {e}")
        results['coingecko'] = False

    # 3. CryptoNews API Test
    print("\n📰 Testing CryptoNews API...")
    cryptonews_key = os.getenv("CRYPTONEWS_API_KEY")
    if cryptonews_key:
        try:
            news_response = requests.get(
                "https://cryptonews-api.com/api/v1/category",
                params={"section": "general", "items": 1, "token": cryptonews_key},
                timeout=10
            )
            if news_response.status_code == 200:
                print("✅ CryptoNews API: ONLINE")
                results['cryptonews'] = True
            else:
                print("❌ CryptoNews API: OFFLINE")
                results['cryptonews'] = False
        except Exception as e:
            print(f"❌ CryptoNews API Error: {e}")
            results['cryptonews'] = False
    else:
        print("⚠️ CryptoNews API Key: NOT SET")
        results['cryptonews'] = False

    # 4. Test actual crypto data retrieval
    print("\n💰 Testing Data Retrieval...")
    try:
        from crypto_api import CryptoAPI
        crypto_api = CryptoAPI()
        
        # Test BTC price
        btc_price = crypto_api.get_binance_price('BTC')
        if 'error' not in btc_price:
            print(f"✅ BTC Price: ${btc_price.get('price', 0):,.2f}")
            results['data_retrieval'] = True
        else:
            print("❌ Data Retrieval: FAILED")
            results['data_retrieval'] = False
            
    except Exception as e:
        print(f"❌ Data Retrieval Error: {e}")
        results['data_retrieval'] = False

    # Summary
    print("\n" + "=" * 50)
    print("📋 DEPLOYMENT API STATUS SUMMARY")
    print("=" * 50)
    
    total_apis = len(results)
    working_apis = sum(results.values())
    health_score = (working_apis / total_apis) * 100 if total_apis > 0 else 0
    
    for api_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api_name.upper().replace('_', ' ')}: {'ONLINE' if status else 'OFFLINE'}")
    
    print(f"\n🎯 Overall Health: {health_score:.0f}% ({working_apis}/{total_apis})")
    
    if health_score >= 75:
        print("🟢 STATUS: EXCELLENT - Ready for production deployment")
        print("🚀 Bot can run with full features")
    elif health_score >= 50:
        print("🟡 STATUS: GOOD - Most APIs working")
        print("📊 Bot can run with minor limitations")
    elif health_score >= 25:
        print("🟠 STATUS: PARTIAL - Some APIs down")
        print("🔄 Bot will use fallback data")
    else:
        print("🔴 STATUS: CRITICAL - Major API issues")
        print("⚠️ Bot may run in simulation mode")

    # Deployment recommendations
    print(f"\n💡 Deployment Recommendations:")
    if not results.get('binance_spot', False):
        print("   • Check network connectivity for Binance")
    if not results.get('coingecko', False):
        print("   • Verify CoinGecko API access")
    if not results.get('cryptonews', False):
        print("   • Add CryptoNews API key to secrets")
    if health_score == 100:
        print("   • 🎉 All systems optimal for deployment!")
    
    return results

if __name__ == "__main__":
    check_deployment_apis()
