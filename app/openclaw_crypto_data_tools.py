"""
OpenClaw Crypto Data Tools
Real-time Binance API integration for OpenClaw AI Assistant
"""

import os
import logging
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenClawCryptoDataTools:
    """Tools for fetching real-time crypto data from Binance"""
    
    BINANCE_API_BASE = "https://api.binance.com/api/v3"
    
    def __init__(self):
        """Initialize crypto data tools"""
        self.session = None
        # SSL verification - set to False for development if needed
        self.verify_ssl = True
        try:
            import ssl
            import certifi
            self.verify_ssl = certifi.where()
        except:
            # Fallback: disable SSL verification (not recommended for production)
            logger.warning("SSL verification disabled - install certifi for production")
            self.verify_ssl = False
    
    async def get_current_price(self, symbol: str) -> Dict:
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            
        Returns:
            Dict with price data
        """
        try:
            symbol = symbol.upper().replace("/", "")
            
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=10.0) as client:
                response = await client.get(
                    f"{self.BINANCE_API_BASE}/ticker/price",
                    params={"symbol": symbol}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'symbol': data['symbol'],
                        'price': float(data['price']),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_24h_stats(self, symbol: str) -> Dict:
        """
        Get 24h statistics for a symbol
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            
        Returns:
            Dict with 24h stats
        """
        try:
            symbol = symbol.upper().replace("/", "")
            
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=10.0) as client:
                response = await client.get(
                    f"{self.BINANCE_API_BASE}/ticker/24hr",
                    params={"symbol": symbol}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'symbol': data['symbol'],
                        'price': float(data['lastPrice']),
                        'change_24h': float(data['priceChange']),
                        'change_percent_24h': float(data['priceChangePercent']),
                        'high_24h': float(data['highPrice']),
                        'low_24h': float(data['lowPrice']),
                        'volume_24h': float(data['volume']),
                        'quote_volume_24h': float(data['quoteVolume']),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 24
    ) -> Dict:
        """
        Get candlestick/kline data
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles (max 1000)
            
        Returns:
            Dict with kline data
        """
        try:
            symbol = symbol.upper().replace("/", "")
            
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=15.0) as client:
                response = await client.get(
                    f"{self.BINANCE_API_BASE}/klines",
                    params={
                        "symbol": symbol,
                        "interval": interval,
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse klines
                    klines = []
                    for k in data:
                        klines.append({
                            'timestamp': datetime.fromtimestamp(k[0] / 1000).isoformat(),
                            'open': float(k[1]),
                            'high': float(k[2]),
                            'low': float(k[3]),
                            'close': float(k[4]),
                            'volume': float(k[5])
                        })
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'interval': interval,
                        'klines': klines,
                        'count': len(klines)
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_orderbook(self, symbol: str, limit: int = 10) -> Dict:
        """
        Get order book depth
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            limit: Depth limit (5, 10, 20, 50, 100, 500, 1000)
            
        Returns:
            Dict with orderbook data
        """
        try:
            symbol = symbol.upper().replace("/", "")
            
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=10.0) as client:
                response = await client.get(
                    f"{self.BINANCE_API_BASE}/depth",
                    params={
                        "symbol": symbol,
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse bids and asks
                    bids = [[float(price), float(qty)] for price, qty in data['bids'][:limit]]
                    asks = [[float(price), float(qty)] for price, qty in data['asks'][:limit]]
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'bids': bids,
                        'asks': asks,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_top_gainers(self, limit: int = 10) -> Dict:
        """
        Get top gainers in last 24h
        
        Args:
            limit: Number of top gainers to return
            
        Returns:
            Dict with top gainers
        """
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=15.0) as client:
                response = await client.get(
                    f"{self.BINANCE_API_BASE}/ticker/24hr"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Filter USDT pairs and sort by price change percent
                    usdt_pairs = [
                        {
                            'symbol': item['symbol'],
                            'price': float(item['lastPrice']),
                            'change_percent': float(item['priceChangePercent']),
                            'volume': float(item['quoteVolume'])
                        }
                        for item in data
                        if item['symbol'].endswith('USDT') and float(item['quoteVolume']) > 1000000
                    ]
                    
                    # Sort by change percent descending
                    top_gainers = sorted(
                        usdt_pairs,
                        key=lambda x: x['change_percent'],
                        reverse=True
                    )[:limit]
                    
                    return {
                        'success': True,
                        'gainers': top_gainers,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_market_summary(self, symbols: List[str]) -> Dict:
        """
        Get market summary for multiple symbols
        
        Args:
            symbols: List of trading pairs
            
        Returns:
            Dict with market summary
        """
        try:
            results = {}
            
            for symbol in symbols:
                stats = await self.get_24h_stats(symbol)
                if stats['success']:
                    results[symbol] = stats
            
            return {
                'success': True,
                'markets': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching market summary: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_crypto_tools_instance = None

def get_crypto_data_tools() -> OpenClawCryptoDataTools:
    """Get singleton instance of crypto data tools"""
    global _crypto_tools_instance
    if _crypto_tools_instance is None:
        _crypto_tools_instance = OpenClawCryptoDataTools()
    return _crypto_tools_instance
