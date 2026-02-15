"""
Alternative Klines Provider
Menggunakan CoinGecko dan CryptoCompare sebagai alternatif Binance
Untuk mengatasi masalah network timeout ke Binance API
"""
import os
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class AlternativeKlinesProvider:
    """Provider alternatif untuk mendapatkan OHLCV data ketika Binance tidak accessible"""
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.cryptocompare_api = "https://min-api.cryptocompare.com/data/v2"
        self.cryptocompare_key = os.getenv('CRYPTOCOMPARE_API_KEY', '')
        
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List:
        """
        Get OHLCV data from alternative sources
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe ('1h', '4h', '1d')
            limit: Number of candles
            
        Returns:
            List of klines in Binance format: [timestamp, open, high, low, close, volume, ...]
        """
        # Clean symbol
        clean_symbol = symbol.upper().replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        
        # Try CryptoCompare first (more reliable for OHLCV)
        if self.cryptocompare_key:
            klines = self._get_from_cryptocompare(clean_symbol, interval, limit)
            if klines:
                print(f"✅ Got {len(klines)} candles from CryptoCompare for {symbol}")
                return klines
        
        # Fallback to CoinGecko
        klines = self._get_from_coingecko(clean_symbol, interval, limit)
        if klines:
            print(f"✅ Got {len(klines)} candles from CoinGecko for {symbol}")
            return klines
        
        print(f"❌ Failed to get klines for {symbol} from all sources")
        return []
    
    def _get_from_cryptocompare(self, symbol: str, interval: str, limit: int) -> List:
        """Get OHLCV from CryptoCompare"""
        try:
            # Map interval to CryptoCompare format
            interval_map = {
                '1h': ('histohour', 1),
                '4h': ('histohour', 4),
                '1d': ('histoday', 1),
                '15m': ('histominute', 15),
                '30m': ('histominute', 30)
            }
            
            if interval not in interval_map:
                return []
            
            endpoint, aggregate = interval_map[interval]
            
            url = f"{self.cryptocompare_api}/{endpoint}"
            params = {
                'fsym': symbol,
                'tsym': 'USD',
                'limit': limit,
                'aggregate': aggregate
            }
            
            if self.cryptocompare_key:
                params['api_key'] = self.cryptocompare_key
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Response') == 'Success' and 'Data' in data:
                    ohlcv_data = data['Data'].get('Data', [])
                    
                    # Convert to Binance format
                    klines = []
                    for candle in ohlcv_data:
                        # Binance format: [timestamp, open, high, low, close, volume, close_time, ...]
                        klines.append([
                            candle['time'] * 1000,  # timestamp in ms
                            str(candle['open']),
                            str(candle['high']),
                            str(candle['low']),
                            str(candle['close']),
                            str(candle['volumefrom']),
                            candle['time'] * 1000 + 3600000,  # close_time (approx)
                            str(candle['volumeto']),
                            0,  # number of trades (not available)
                            "0",  # taker buy base asset volume
                            "0",  # taker buy quote asset volume
                            "0"   # ignore
                        ])
                    
                    return klines
            
            return []
        
        except Exception as e:
            print(f"CryptoCompare error: {e}")
            return []
    
    def _get_from_coingecko(self, symbol: str, interval: str, limit: int) -> List:
        """Get OHLCV from CoinGecko"""
        try:
            # Map symbol to CoinGecko ID
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'SOL': 'solana',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'MATIC': 'matic-network',
                'AVAX': 'avalanche-2',
                'UNI': 'uniswap',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'ATOM': 'cosmos',
                'ICP': 'internet-computer',
                'NEAR': 'near',
                'APT': 'aptos',
                'FTM': 'fantom',
                'ALGO': 'algorand',
                'VET': 'vechain',
                'FLOW': 'flow'
            }
            
            coin_id = symbol_map.get(symbol.upper())
            if not coin_id:
                return []
            
            # Calculate days based on interval and limit
            interval_hours = {
                '1h': 1,
                '4h': 4,
                '1d': 24,
                '15m': 0.25,
                '30m': 0.5
            }
            
            hours = interval_hours.get(interval, 1)
            days = max(1, int((limit * hours) / 24))
            
            url = f"{self.coingecko_api}/coins/{coin_id}/ohlc"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 90)  # CoinGecko limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                ohlc_data = response.json()
                
                if isinstance(ohlc_data, list) and len(ohlc_data) > 0:
                    # Convert to Binance format
                    klines = []
                    for candle in ohlc_data[-limit:]:  # Get last 'limit' candles
                        # CoinGecko format: [timestamp, open, high, low, close]
                        timestamp = candle[0]
                        open_price = candle[1]
                        high_price = candle[2]
                        low_price = candle[3]
                        close_price = candle[4]
                        
                        # Estimate volume (not provided by CoinGecko OHLC)
                        volume = (high_price + low_price) / 2 * 1000  # Rough estimate
                        
                        klines.append([
                            timestamp,
                            str(open_price),
                            str(high_price),
                            str(low_price),
                            str(close_price),
                            str(volume),
                            timestamp + 3600000,  # close_time
                            str(volume * close_price),
                            0,
                            "0",
                            "0",
                            "0"
                        ])
                    
                    return klines
            
            return []
        
        except Exception as e:
            print(f"CoinGecko error: {e}")
            return []

# Global instance
alternative_klines_provider = AlternativeKlinesProvider()
