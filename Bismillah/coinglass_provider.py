
import requests
import os
import time
from datetime import datetime

class CoinGlassProvider:
    """CoinGlass V4 API Provider - Startup Plan"""
    
    def __init__(self):
        self.api_key = os.getenv("COINGLASS_API_KEY")
        self.base_url = "https://open-api-v4.coinglass.com/public/v4"
        self.headers = {
            'X-API-KEY': self.api_key,
            'accept': 'application/json'
        }
        
        if not self.api_key:
            print("⚠️ COINGLASS_API_KEY not found in environment variables")
        else:
            print("✅ CoinGlass V4 API initialized with Startup Plan")

    def _make_request(self, endpoint, params=None):
        """Make authenticated request to CoinGlass V4 API"""
        try:
            if not self.api_key:
                return {'error': 'COINGLASS_API_KEY not found'}
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params or {}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', True):
                    return data
                else:
                    return {'error': f"API Error: {data.get('msg', 'Unknown error')}"}
            else:
                return {'error': f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.Timeout:
            return {'error': 'CoinGlass API timeout'}
        except Exception as e:
            return {'error': f'CoinGlass API error: {str(e)}'}

    def get_long_short_ratio(self, symbol):
        """Get long/short ratio from CoinGlass V4"""
        try:
            clean_symbol = symbol.upper().replace('USDT', '').replace('USD', '')
            print(f"🔄 Getting long/short ratio for {clean_symbol} from CoinGlass V4...")
            
            result = self._make_request('futures/longShortRate', {'symbol': clean_symbol})
            
            if 'error' in result:
                print(f"❌ Long/Short ratio error: {result['error']}")
                return result
            
            # Parse CoinGlass V4 response
            data = result.get('data', [])
            if not data:
                return {'error': f'No long/short data for {clean_symbol}'}
            
            # Get latest data point
            latest = data[-1] if isinstance(data, list) else data
            
            long_ratio = float(latest.get('longRate', 50))
            short_ratio = 100 - long_ratio
            
            return {
                'symbol': clean_symbol,
                'long_ratio': long_ratio,
                'short_ratio': short_ratio,
                'timestamp': latest.get('time', int(time.time() * 1000)),
                'source': 'coinglass_v4',
                'raw_data': latest
            }
            
        except Exception as e:
            print(f"❌ Exception in get_long_short_ratio: {e}")
            return {'error': f'Long/short ratio error: {str(e)}'}

    def get_open_interest_chart(self, symbol):
        """Get open interest from CoinGlass V4"""
        try:
            clean_symbol = symbol.upper().replace('USDT', '').replace('USD', '')
            print(f"🔄 Getting open interest for {clean_symbol} from CoinGlass V4...")
            
            result = self._make_request('futures/openInterest', {'symbol': clean_symbol})
            
            if 'error' in result:
                print(f"❌ Open interest error: {result['error']}")
                return result
            
            data = result.get('data', [])
            if not data:
                return {'error': f'No open interest data for {clean_symbol}'}
            
            latest = data[-1] if isinstance(data, list) else data
            previous = data[-2] if isinstance(data, list) and len(data) > 1 else latest
            
            current_oi = float(latest.get('openInterest', 0))
            previous_oi = float(previous.get('openInterest', current_oi))
            
            oi_change_percent = ((current_oi - previous_oi) / max(previous_oi, 1)) * 100
            
            return {
                'symbol': clean_symbol,
                'open_interest': current_oi,
                'oi_change_percent': oi_change_percent,
                'timestamp': latest.get('time', int(time.time() * 1000)),
                'source': 'coinglass_v4',
                'raw_data': latest
            }
            
        except Exception as e:
            print(f"❌ Exception in get_open_interest_chart: {e}")
            return {'error': f'Open interest error: {str(e)}'}

    def get_funding_rate_chart(self, symbol):
        """Get funding rate from CoinGlass V4"""
        try:
            clean_symbol = symbol.upper().replace('USDT', '').replace('USD', '')
            print(f"🔄 Getting funding rate for {clean_symbol} from CoinGlass V4...")
            
            result = self._make_request('futures/fundingRate', {'symbol': clean_symbol})
            
            if 'error' in result:
                print(f"❌ Funding rate error: {result['error']}")
                return result
            
            data = result.get('data', [])
            if not data:
                return {'error': f'No funding rate data for {clean_symbol}'}
            
            latest = data[-1] if isinstance(data, list) else data
            
            funding_rate = float(latest.get('fundingRate', 0))
            
            return {
                'symbol': clean_symbol,
                'funding_rate': funding_rate,
                'funding_rate_percent': funding_rate * 100,
                'timestamp': latest.get('time', int(time.time() * 1000)),
                'source': 'coinglass_v4',
                'raw_data': latest
            }
            
        except Exception as e:
            print(f"❌ Exception in get_funding_rate_chart: {e}")
            return {'error': f'Funding rate error: {str(e)}'}

    def get_liquidation_map(self, symbol):
        """Get liquidation zones from CoinGlass V4"""
        try:
            clean_symbol = symbol.upper().replace('USDT', '').replace('USD', '')
            print(f"🔄 Getting liquidation zones for {clean_symbol} from CoinGlass V4...")
            
            result = self._make_request('futures/liquidationMap', {'symbol': clean_symbol})
            
            if 'error' in result:
                print(f"❌ Liquidation map error: {result['error']}")
                return result
            
            data = result.get('data', {})
            if not data:
                return {'error': f'No liquidation data for {clean_symbol}'}
            
            long_liquidation = float(data.get('longLiquidation', 0))
            short_liquidation = float(data.get('shortLiquidation', 0))
            total_liquidation = long_liquidation + short_liquidation
            
            return {
                'symbol': clean_symbol,
                'long_liquidation': long_liquidation,
                'short_liquidation': short_liquidation,
                'total_liquidation': total_liquidation,
                'long_percentage': (long_liquidation / max(total_liquidation, 1)) * 100,
                'short_percentage': (short_liquidation / max(total_liquidation, 1)) * 100,
                'dominant_side': 'Long' if long_liquidation > short_liquidation else 'Short',
                'zones': data.get('priceRanges', []),
                'source': 'coinglass_v4',
                'raw_data': data
            }
            
        except Exception as e:
            print(f"❌ Exception in get_liquidation_map: {e}")
            return {'error': f'Liquidation map error: {str(e)}'}

    def get_comprehensive_futures_data(self, symbol):
        """Get all futures data for a symbol"""
        try:
            clean_symbol = symbol.upper().replace('USDT', '').replace('USD', '')
            print(f"🔄 Getting comprehensive futures data for {clean_symbol}...")
            
            # Get all data
            ls_data = self.get_long_short_ratio(clean_symbol)
            oi_data = self.get_open_interest_chart(clean_symbol) 
            funding_data = self.get_funding_rate_chart(clean_symbol)
            liq_data = self.get_liquidation_map(clean_symbol)
            
            # Count successful calls
            successful_calls = 0
            for data in [ls_data, oi_data, funding_data, liq_data]:
                if 'error' not in data:
                    successful_calls += 1
            
            return {
                'symbol': clean_symbol,
                'long_short_data': ls_data,
                'open_interest_data': oi_data,
                'funding_rate_data': funding_data,
                'liquidation_data': liq_data,
                'successful_calls': successful_calls,
                'total_calls': 4,
                'data_quality': 'excellent' if successful_calls >= 3 else 'good' if successful_calls >= 2 else 'poor',
                'source': 'coinglass_v4_comprehensive'
            }
            
        except Exception as e:
            return {'error': f'Comprehensive data error: {str(e)}'}

print("✅ CoinGlassProvider V4 loaded successfully")
