"""
Test script untuk memverifikasi Binance klines/candle data
"""
import requests
from datetime import datetime

def test_binance_klines():
    """Test fetching klines from Binance"""
    print("=" * 60)
    print("🧪 TESTING BINANCE KLINES DATA")
    print("=" * 60)
    print()
    
    # Test symbols
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    
    for symbol in test_symbols:
        print(f"📊 Testing {symbol}...")
        print("-" * 60)
        
        # Test Spot API
        try:
            spot_url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': '1h',
                'limit': 10
            }
            
            response = requests.get(spot_url, params=params, timeout=10)
            
            if response.status_code == 200:
                klines = response.json()
                
                if isinstance(klines, list) and len(klines) > 0:
                    print(f"✅ Spot API: {len(klines)} candles fetched")
                    
                    # Show first candle
                    first_candle = klines[0]
                    timestamp = datetime.fromtimestamp(first_candle[0] / 1000)
                    open_price = float(first_candle[1])
                    high_price = float(first_candle[2])
                    low_price = float(first_candle[3])
                    close_price = float(first_candle[4])
                    volume = float(first_candle[5])
                    
                    print(f"   First candle: {timestamp}")
                    print(f"   O: ${open_price:,.2f} | H: ${high_price:,.2f} | L: ${low_price:,.2f} | C: ${close_price:,.2f}")
                    print(f"   Volume: {volume:,.2f}")
                else:
                    print(f"❌ Spot API: Empty response")
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Spot API: HTTP {response.status_code}")
                print(f"   Error: {error_data.get('msg', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Spot API Error: {e}")
        
        print()
    
    # Test SnD Zone Detector
    print("=" * 60)
    print("🧪 TESTING SND ZONE DETECTOR")
    print("=" * 60)
    print()
    
    try:
        from snd_zone_detector import detect_snd_zones
        
        result = detect_snd_zones('BTCUSDT', '1h', limit=100)
        
        if 'error' in result:
            print(f"❌ SnD Detector Error: {result['error']}")
        else:
            print(f"✅ SnD Detector Working!")
            print(f"   Symbol: {result.get('symbol')}")
            print(f"   Current Price: ${result.get('current_price', 0):,.2f}")
            print(f"   Demand Zones: {len(result.get('demand_zones', []))}")
            print(f"   Supply Zones: {len(result.get('supply_zones', []))}")
            print(f"   Entry Signal: {result.get('entry_signal', 'None')}")
    
    except Exception as e:
        print(f"❌ SnD Detector Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("📊 TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_binance_klines()
