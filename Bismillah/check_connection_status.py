
#!/usr/bin/env python3
"""
Check connection status for all API integrations
"""

import os
import sys
import requests
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_binance_connection():
    """Check Binance API connection"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ping', timeout=10)
        if response.status_code == 200:
            print("✅ Binance API - Connected")
            return True
        else:
            print(f"❌ Binance API - Invalid - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Binance API - Failed: {e}")
        return False

def check_coinmarketcap_connection():
    """Check CoinMarketCap API connection"""
    try:
        cmc_key = os.getenv('CMC_API_KEY') or os.getenv('COINMARKETCAP_API_KEY')
        if not cmc_key:
            print("⚠️ CoinMarketCap API - No API key found")
            return False
            
        headers = {'X-CMC_PRO_API_KEY': cmc_key}
        response = requests.get(
            'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest',
            headers=headers,
            params={'limit': 1},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ CoinMarketCap API - Connected")
            return True
        else:
            print(f"❌ CoinMarketCap API - Invalid - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CoinMarketCap API - Failed: {e}")
        return False

def check_telegram_bot():
    """Check Telegram Bot connection"""
    try:
        bot_token = os.getenv('TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("⚠️ Telegram Bot - No token found")
            return False
            
        response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                username = data.get('result', {}).get('username', 'Unknown')
                print(f"✅ Telegram Bot - Connected (@{username})")
                return True
        
        print(f"❌ Telegram Bot - Invalid - HTTP {response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Telegram Bot - Failed: {e}")
        return False

def main():
    """Main connection check function"""
    print("🔍 CryptoMentor AI - Connection Status Check")
    print("=" * 50)
    print(f"🕐 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    connections = {
        'Binance API': check_binance_connection(),
        'CoinMarketCap API': check_coinmarketcap_connection(),
        'Telegram Bot': check_telegram_bot()
    }
    
    print("\n📊 Connection Summary:")
    working = sum(1 for status in connections.values() if status)
    total = len(connections)
    
    print(f"✅ Working: {working}/{total}")
    print(f"❌ Failed: {total - working}/{total}")
    
    if working == total:
        print("\n🚀 All systems operational!")
    else:
        print("\n⚠️ Some connections failed - check configuration")
    
    return working == total

if __name__ == "__main__":
    main()
