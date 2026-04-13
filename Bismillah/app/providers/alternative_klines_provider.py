"""
Alternative Klines Provider
Multi-source OHLCV data provider dengan fallback chain untuk reliability maksimal.

Priority chain:
1. Bitunix (exchange utama) - Futures data langsung
2. Binance Futures (fallback terbaik) - Gratis, reliable, semua pair
3. CryptoCompare (jika ada API key) - Spot data
4. CoinGecko (last resort) - Spot data, limited pairs

Dengan 4 sources, kita pastikan data selalu tersedia untuk push trading volume.
"""
import os
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class AlternativeKlinesProvider:
    """Provider OHLCV data dengan fallback multi-source"""
    
    def __init__(self):
        self.bitunix_api      = os.getenv('BITUNIX_BASE_URL', 'https://fapi.bitunix.com')
        self.binance_api      = "https://fapi.binance.com"  # Binance Futures public API
        self.coingecko_api    = "https://api.coingecko.com/api/v3"
        self.cryptocompare_api = "https://min-api.cryptocompare.com/data/v2"
        self.cryptocompare_key = os.getenv('CRYPTOCOMPARE_API_KEY', '')
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CryptoMentorAI/4.0 market-data",
            "Accept": "application/json",
        })
        self._source_fail_count: Dict[str, int] = {}
        self._source_backoff_until: Dict[str, float] = {}

    def _is_source_available(self, source: str) -> bool:
        until = self._source_backoff_until.get(source, 0)
        return time.time() >= until

    def _mark_source_success(self, source: str):
        self._source_fail_count[source] = 0
        self._source_backoff_until[source] = 0

    def _mark_source_failure(self, source: str):
        fails = int(self._source_fail_count.get(source, 0)) + 1
        self._source_fail_count[source] = fails
        # Exponential cooldown to reduce API hammering during outages.
        cooldown = min(90, 3 * (2 ** min(fails, 5)))
        self._source_backoff_until[source] = time.time() + cooldown

    def _http_get(self, source: str, url: str, params: Dict, timeout: int = 10, retries: int = 2):
        if not self._is_source_available(source):
            return None

        for attempt in range(retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=timeout)
                if resp.status_code == 200:
                    self._mark_source_success(source)
                    return resp
                # Retry transient statuses.
                if resp.status_code in (408, 425, 429, 500, 502, 503, 504) and attempt < retries:
                    time.sleep(0.35 * (attempt + 1))
                    continue
                break
            except requests.RequestException:
                if attempt < retries:
                    time.sleep(0.35 * (attempt + 1))
                    continue
                break

        self._mark_source_failure(source)
        return None
        
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> List:
        """
        Get OHLCV data — prioritas Bitunix, fallback ke CryptoCompare/CoinGecko.
        Returns list of klines in Binance format: [timestamp, open, high, low, close, volume, ...]
        """
        clean_symbol = symbol.upper().replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        full_symbol  = clean_symbol + "USDT"

        # 1. Bitunix (prioritas utama — data futures langsung)
        klines = self._get_from_bitunix(full_symbol, interval, limit)
        if klines:
            return klines

        # 2. Binance Futures (fallback terbaik — gratis, reliable, semua pair)
        klines = self._get_from_binance(full_symbol, interval, limit)
        if klines:
            print(f"[OK] Got {len(klines)} candles from Binance for {symbol}")
            return klines

        # 3. CryptoCompare
        if self.cryptocompare_key:
            klines = self._get_from_cryptocompare(clean_symbol, interval, limit)
            if klines:
                print(f"[OK] Got {len(klines)} candles from CryptoCompare for {symbol}")
                return klines

        # 4. CoinGecko
        klines = self._get_from_coingecko(clean_symbol, interval, limit)
        if klines:
            print(f"[OK] Got {len(klines)} candles from CoinGecko for {symbol}")
            return klines

        print(f"[ERR] Failed to get klines for {symbol} [{interval}] from all sources")
        return []

    def _get_from_bitunix(self, symbol: str, interval: str, limit: int) -> List:
        """Get OHLCV dari Bitunix futures API — tidak perlu auth, public endpoint."""
        try:
            # Bitunix interval mapping (sudah sama dengan standar)
            # Supported: 1m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h',
                '8h': '8h', '12h': '12h', '1d': '1d', '1w': '1w',
            }
            bx_interval = interval_map.get(interval)
            if not bx_interval:
                return []

            # Bitunix max limit per request = 200
            fetch_limit = min(limit, 200)

            url = f"{self.bitunix_api}/api/v1/futures/market/kline"
            params = {
                'symbol':   symbol,
                'interval': bx_interval,
                'limit':    fetch_limit,
            }

            resp = self._http_get("bitunix", url, params, timeout=10, retries=1)
            if resp is None:
                return []

            data = resp.json()
            if data.get('code') != 0 or not data.get('data'):
                return []

            raw = data['data']
            # Bitunix response: [{open, high, low, close, time, quoteVol, baseVol, type}, ...]
            # Sort ascending by time
            raw.sort(key=lambda x: x.get('time', 0))

            klines = []
            for c in raw:
                ts     = int(c.get('time', 0))
                open_  = str(c.get('open', 0))
                high   = str(c.get('high', 0))
                low    = str(c.get('low', 0))
                close  = str(c.get('close', 0))
                vol    = str(c.get('baseVol', 0))   # coin volume
                qvol   = str(c.get('quoteVol', 0))  # USDT volume
                klines.append([
                    ts, open_, high, low, close, vol,
                    ts + 1, qvol, 0, "0", "0", "0"
                ])

            min_required = min(10, fetch_limit)
            if len(klines) >= min_required:
                print(f"[OK] Got {len(klines)} candles from Bitunix for {symbol}")
                return klines

            return []

        except Exception as e:
            print(f"Bitunix klines error ({symbol}): {e}")
            return []
    
    def _get_from_binance(self, symbol: str, interval: str, limit: int) -> List:
        """
        Get OHLCV dari Binance Futures public API — gratis, tidak perlu auth.
        Binance support semua pair yang kita trade dan sangat reliable.
        """
        try:
            # Binance interval mapping (sudah standar)
            # Supported: 1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
            interval_map = {
                '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h',
                '8h': '8h', '12h': '12h', '1d': '1d', '1w': '1w',
            }
            bn_interval = interval_map.get(interval)
            if not bn_interval:
                return []

            # Binance max limit per request = 1500
            fetch_limit = min(limit, 1500)

            url = f"{self.binance_api}/fapi/v1/klines"
            params = {
                'symbol':   symbol,
                'interval': bn_interval,
                'limit':    fetch_limit,
            }

            resp = self._http_get("binance", url, params, timeout=10, retries=2)
            if resp is None:
                return []

            klines = resp.json()
            
            # Binance response sudah dalam format yang kita butuhkan:
            # [timestamp, open, high, low, close, volume, close_time, quote_volume, ...]
            min_required = min(10, fetch_limit)
            if isinstance(klines, list) and len(klines) >= min_required:
                # Convert all values to string for consistency
                formatted_klines = []
                for k in klines:
                    formatted_klines.append([
                        int(k[0]),      # timestamp
                        str(k[1]),      # open
                        str(k[2]),      # high
                        str(k[3]),      # low
                        str(k[4]),      # close
                        str(k[5]),      # volume
                        int(k[6]),      # close_time
                        str(k[7]),      # quote_volume
                        int(k[8]),      # number of trades
                        str(k[9]),      # taker buy base volume
                        str(k[10]),     # taker buy quote volume
                        str(k[11])      # ignore
                    ])
                return formatted_klines

            return []

        except Exception as e:
            print(f"Binance klines error ({symbol}): {e}")
            return []
    
    def _get_from_cryptocompare(self, symbol: str, interval: str, limit: int) -> List:
        """Get OHLCV from CryptoCompare"""
        try:
            # Map interval to CryptoCompare format
            interval_map = {
                '3m': ('histominute', 3),
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
            
            response = self._http_get("cryptocompare", url, params, timeout=10, retries=1)
            if response is not None:
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
            # CoinGecko OHLC is not suitable for sub-15m trading intervals.
            if interval in ('1m', '3m', '5m'):
                return []

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
                'DOGE': 'dogecoin',
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
                '3m': 0.05,
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
            
            response = self._http_get("coingecko", url, params, timeout=10, retries=1)
            if response is not None:
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
