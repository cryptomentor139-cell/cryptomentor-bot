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
import logging

logger = logging.getLogger(__name__)

class AlternativeKlinesProvider:
    """Provider OHLCV data dengan fallback multi-source"""
    
    def __init__(self):
        self.bitunix_api      = os.getenv('BITUNIX_BASE_URL', 'https://fapi.bitunix.com')
        self.binance_api      = "https://fapi.binance.com"  # Binance Futures public API
        self.coingecko_api    = "https://api.coingecko.com/api/v3"
        self.cryptocompare_api = "https://min-api.cryptocompare.com/data/v2"
        self.cryptocompare_key = os.getenv('CRYPTOCOMPARE_API_KEY', '')
        self.max_retries = max(1, int(os.getenv("KLINE_FETCH_RETRIES", "3")))
        self.backoff_base_ms = max(50, int(os.getenv("KLINE_RETRY_BASE_DELAY_MS", "250")))
        self.backoff_cap_ms = max(200, int(os.getenv("KLINE_RETRY_CAP_DELAY_MS", "2000")))
        self.max_staleness_multiplier = max(
            1.0,
            float(os.getenv("KLINE_MAX_STALENESS_MULTIPLIER", "3.0")),
        )

    def _resolve_source_order(self, preferred_sources: Optional[List[str]] = None) -> List[str]:
        default_order = ["bitunix", "binance", "cryptocompare", "coingecko"]
        source_order_raw = os.getenv("KLINE_SOURCE_ORDER", ",".join(default_order))
        configured = [s.strip().lower() for s in source_order_raw.split(",") if s.strip()]
        pool = preferred_sources if preferred_sources else configured

        valid = []
        for source in pool:
            if source in default_order and source not in valid:
                valid.append(source)

        for source in default_order:
            if source not in valid:
                valid.append(source)
        return valid

    def _min_required_candles(self, limit: int) -> int:
        if limit <= 0:
            return 1
        return max(1, min(limit, 10))

    def _interval_to_seconds(self, interval: str) -> int:
        mapping = {
            '1m': 60,
            '3m': 180,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '2h': 7200,
            '4h': 14400,
            '6h': 21600,
            '8h': 28800,
            '12h': 43200,
            '1d': 86400,
            '3d': 259200,
            '1w': 604800,
        }
        return int(mapping.get(str(interval).lower(), 0))

    def _normalize_ts_sec(self, raw_ts) -> Optional[float]:
        try:
            ts = float(raw_ts)
        except Exception:
            return None
        if ts <= 0:
            return None
        if ts > 1_000_000_000_000:  # milliseconds
            ts = ts / 1000.0
        return ts

    def _is_klines_fresh(
        self,
        klines: List,
        interval: str,
        now_ts: Optional[float] = None,
    ) -> bool:
        if not klines:
            return False
        interval_sec = self._interval_to_seconds(interval)
        if interval_sec <= 0:
            return True
        last_candle = klines[-1] if isinstance(klines[-1], (list, tuple)) and klines[-1] else None
        if not last_candle:
            return False
        last_ts_sec = self._normalize_ts_sec(last_candle[0] if len(last_candle) > 0 else None)
        if last_ts_sec is None:
            return False
        now = float(time.time() if now_ts is None else now_ts)
        max_age_sec = float(interval_sec) * float(self.max_staleness_multiplier)
        age_sec = max(0.0, now - last_ts_sec)
        return age_sec <= max_age_sec
        
    def get_klines(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100,
        preferred_sources: Optional[List[str]] = None
    ) -> List:
        """
        Get OHLCV data — prioritas Bitunix, fallback ke CryptoCompare/CoinGecko.
        Returns list of klines in Binance format: [timestamp, open, high, low, close, volume, ...]
        """
        clean_symbol = symbol.upper().replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        full_symbol  = clean_symbol + "USDT"
        source_order = self._resolve_source_order(preferred_sources)
        min_required = self._min_required_candles(limit)

        source_fetchers = {
            "bitunix": lambda: self._get_from_bitunix(full_symbol, interval, limit),
            "binance": lambda: self._get_from_binance(full_symbol, interval, limit),
            "cryptocompare": lambda: self._get_from_cryptocompare(clean_symbol, interval, limit) if self.cryptocompare_key else [],
            "coingecko": lambda: self._get_from_coingecko(clean_symbol, interval, limit),
        }

        for source in source_order:
            fetcher = source_fetchers.get(source)
            if fetcher is None:
                continue
            for attempt in range(1, self.max_retries + 1):
                try:
                    klines = fetcher()
                except Exception as e:
                    logger.warning(
                        f"[Klines] {source} exception {clean_symbol} {interval} attempt {attempt}/{self.max_retries}: {e}"
                    )
                    klines = []

                if klines and len(klines) >= min_required:
                    if not self._is_klines_fresh(klines, interval):
                        logger.warning(
                            f"[Klines] {source} stale data rejected: {clean_symbol} {interval} "
                            f"(candles={len(klines)})"
                        )
                        klines = []
                    else:
                        logger.debug(
                            f"[Klines] {source} success {clean_symbol} {interval}: "
                            f"{len(klines)} candles (attempt {attempt})"
                        )
                        return klines

                if attempt < self.max_retries:
                    backoff_ms = min(self.backoff_cap_ms, self.backoff_base_ms * (2 ** (attempt - 1)))
                    time.sleep(backoff_ms / 1000.0)
            logger.warning(
                f"[Klines] source failed: {source} {clean_symbol} {interval} "
                f"after {self.max_retries} attempts"
            )

        logger.error(f"[Klines] Failed all sources for {clean_symbol} {interval} limit={limit}")
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

            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
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

            if len(klines) >= self._min_required_candles(limit):
                return klines

            return []

        except Exception as e:
            logger.debug(f"[Klines] Bitunix error ({symbol} {interval}): {e}")
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
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
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

            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                return []

            klines = resp.json()
            
            # Binance response sudah dalam format yang kita butuhkan:
            # [timestamp, open, high, low, close, volume, close_time, quote_volume, ...]
            if isinstance(klines, list) and len(klines) >= self._min_required_candles(limit):
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
            logger.debug(f"[Klines] Binance error ({symbol} {interval}): {e}")
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
            logger.debug(f"[Klines] CryptoCompare error ({symbol} {interval}): {e}")
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
            logger.debug(f"[Klines] CoinGecko error ({symbol} {interval}): {e}")
            return []

# Global instance
alternative_klines_provider = AlternativeKlinesProvider()
