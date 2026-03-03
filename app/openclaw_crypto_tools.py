"""
OpenClaw Crypto Tools - Real-time Market Data for GPT-4.1

This module provides crypto market data tools that can be used by GPT-4.1
to give accurate trading signals and market analysis.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class OpenClawCryptoTools:
    """Crypto market data tools for OpenClaw AI Assistant"""
    
    def __init__(self):
        """Initialize crypto tools with API keys"""
        self.cryptocompare_key = os.getenv('CRYPTOCOMPARE_API_KEY')
        self.helius_key = os.getenv('HELIUS_API_KEY')
        self.cryptonews_key = os.getenv('CRYPTONEWS_API_KEY')
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price for a cryptocurrency
        
        Args:
            symbol: Crypto symbol (e.g., BTC, ETH, SOL)
            
        Returns:
            Dict with price data
        """
        try:
            # Use CryptoCompare API
            url = f"https://min-api.cryptocompare.com/data/price"
            params = {
                'fsym': symbol.upper(),
                'tsyms': 'USD,USDT',
                'api_key': self.cryptocompare_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol.upper(),
                    'price_usd': data.get('USD', 0),
                    'price_usdt': data.get('USDT', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'CryptoCompare'
                }
            else:
                return {'error': f'Failed to fetch price: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_price_history(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Get historical price data
        
        Args:
            symbol: Crypto symbol
            days: Number of days of history (default 7)
            
        Returns:
            Dict with historical price data
        """
        try:
            url = f"https://min-api.cryptocompare.com/data/v2/histoday"
            params = {
                'fsym': symbol.upper(),
                'tsym': 'USD',
                'limit': days,
                'api_key': self.cryptocompare_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Response') == 'Success':
                    prices = data['Data']['Data']
                    
                    # Calculate price change
                    if len(prices) >= 2:
                        first_price = prices[0]['close']
                        last_price = prices[-1]['close']
                        change_pct = ((last_price - first_price) / first_price) * 100
                    else:
                        change_pct = 0
                    
                    return {
                        'symbol': symbol.upper(),
                        'days': days,
                        'current_price': prices[-1]['close'] if prices else 0,
                        'change_percent': round(change_pct, 2),
                        'high': max([p['high'] for p in prices]) if prices else 0,
                        'low': min([p['low'] for p in prices]) if prices else 0,
                        'avg_volume': sum([p['volumeto'] for p in prices]) / len(prices) if prices else 0,
                        'data_points': len(prices),
                        'source': 'CryptoCompare'
                    }
                else:
                    return {'error': 'No data available'}
            else:
                return {'error': f'Failed to fetch history: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_market_indicators(self, symbol: str) -> Dict[str, Any]:
        """
        Get technical indicators for a cryptocurrency
        
        Args:
            symbol: Crypto symbol
            
        Returns:
            Dict with technical indicators
        """
        try:
            # Get 30-day history for indicators
            history = self.get_price_history(symbol, days=30)
            
            if 'error' in history:
                return history
            
            # Simple technical analysis
            current_price = history['current_price']
            high_30d = history['high']
            low_30d = history['low']
            change_pct = history['change_percent']
            
            # Calculate RSI-like indicator (simplified)
            if change_pct > 10:
                momentum = 'STRONG_BULLISH'
                signal = 'BUY'
            elif change_pct > 5:
                momentum = 'BULLISH'
                signal = 'BUY'
            elif change_pct < -10:
                momentum = 'STRONG_BEARISH'
                signal = 'SELL'
            elif change_pct < -5:
                momentum = 'BEARISH'
                signal = 'SELL'
            else:
                momentum = 'NEUTRAL'
                signal = 'HOLD'
            
            # Price position in range
            price_range = high_30d - low_30d
            if price_range > 0:
                position_pct = ((current_price - low_30d) / price_range) * 100
            else:
                position_pct = 50
            
            return {
                'symbol': symbol.upper(),
                'current_price': current_price,
                'momentum': momentum,
                'signal': signal,
                'change_30d': f"{change_pct:+.2f}%",
                'price_position': f"{position_pct:.1f}% of 30d range",
                'support_level': low_30d,
                'resistance_level': high_30d,
                'analysis': self._generate_analysis(momentum, change_pct, position_pct),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting indicators for {symbol}: {e}")
            return {'error': str(e)}
    
    def _generate_analysis(self, momentum: str, change_pct: float, position_pct: float) -> str:
        """Generate human-readable analysis"""
        
        analysis = []
        
        # Momentum analysis
        if momentum == 'STRONG_BULLISH':
            analysis.append("Strong upward momentum detected.")
        elif momentum == 'BULLISH':
            analysis.append("Positive momentum with upward trend.")
        elif momentum == 'STRONG_BEARISH':
            analysis.append("Strong downward pressure observed.")
        elif momentum == 'BEARISH':
            analysis.append("Negative momentum with downward trend.")
        else:
            analysis.append("Market is consolidating.")
        
        # Position analysis
        if position_pct > 80:
            analysis.append("Price near resistance - potential reversal zone.")
        elif position_pct < 20:
            analysis.append("Price near support - potential bounce zone.")
        else:
            analysis.append("Price in mid-range - watch for breakout.")
        
        # Risk assessment
        if abs(change_pct) > 15:
            analysis.append("High volatility - use tight stop-loss.")
        elif abs(change_pct) > 8:
            analysis.append("Moderate volatility - normal risk management.")
        else:
            analysis.append("Low volatility - consider range trading.")
        
        return " ".join(analysis)
    
    def get_crypto_news(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get latest crypto news
        
        Args:
            limit: Number of news items to fetch
            
        Returns:
            Dict with news data
        """
        try:
            if not self.cryptonews_key:
                return {'error': 'CryptoNews API key not configured'}
            
            url = "https://cryptonews-api.com/api/v1/category"
            params = {
                'section': 'general',
                'items': limit,
                'token': self.cryptonews_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                news_items = []
                for item in data.get('data', [])[:limit]:
                    news_items.append({
                        'title': item.get('title', ''),
                        'text': item.get('text', '')[:200] + '...',
                        'source': item.get('source_name', ''),
                        'date': item.get('date', '')
                    })
                
                return {
                    'news_count': len(news_items),
                    'news': news_items,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': f'Failed to fetch news: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error getting crypto news: {e}")
            return {'error': str(e)}
    
    def get_trading_signal(self, symbol: str) -> Dict[str, Any]:
        """
        Generate comprehensive trading signal
        
        Args:
            symbol: Crypto symbol
            
        Returns:
            Dict with trading signal and analysis
        """
        try:
            # Get current price
            price_data = self.get_current_price(symbol)
            if 'error' in price_data:
                return price_data
            
            # Get indicators
            indicators = self.get_market_indicators(symbol)
            if 'error' in indicators:
                return indicators
            
            # Combine into trading signal
            signal = {
                'symbol': symbol.upper(),
                'current_price': price_data['price_usd'],
                'signal': indicators['signal'],
                'momentum': indicators['momentum'],
                'change_30d': indicators['change_30d'],
                'support': indicators['support_level'],
                'resistance': indicators['resistance_level'],
                'analysis': indicators['analysis'],
                'recommendation': self._generate_recommendation(indicators),
                'timestamp': datetime.now().isoformat()
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating trading signal for {symbol}: {e}")
            return {'error': str(e)}
    
    def _generate_recommendation(self, indicators: Dict) -> str:
        """Generate trading recommendation"""
        
        signal = indicators['signal']
        momentum = indicators['momentum']
        
        if signal == 'BUY':
            if momentum == 'STRONG_BULLISH':
                return "Strong BUY - Consider entering long position with 2-3% of portfolio. Set stop-loss at support level."
            else:
                return "BUY - Good entry point for long position. Use 1-2% of portfolio with stop-loss below support."
        
        elif signal == 'SELL':
            if momentum == 'STRONG_BEARISH':
                return "Strong SELL - Consider exiting long positions or entering short. Protect capital."
            else:
                return "SELL - Weak momentum. Consider taking profits or reducing exposure."
        
        else:
            return "HOLD - Wait for clearer signal. Monitor support/resistance levels for breakout."
    
    def format_for_llm(self, data: Dict[str, Any]) -> str:
        """
        Format crypto data for LLM consumption
        
        Args:
            data: Crypto data dict
            
        Returns:
            Formatted string for LLM
        """
        if 'error' in data:
            return f"Error: {data['error']}"
        
        # Format based on data type
        if 'signal' in data:
            # Trading signal format
            return f"""
📊 Trading Signal for {data['symbol']}

Current Price: ${data['current_price']:.2f}
Signal: {data['signal']} ({data['momentum']})
30-Day Change: {data['change_30d']}

Support Level: ${data['support']:.2f}
Resistance Level: ${data['resistance']:.2f}

Analysis: {data['analysis']}

Recommendation: {data['recommendation']}

Timestamp: {data['timestamp']}
"""
        
        elif 'news' in data:
            # News format
            news_text = "\n\n".join([
                f"• {item['title']}\n  {item['text']}\n  Source: {item['source']}"
                for item in data['news']
            ])
            return f"📰 Latest Crypto News:\n\n{news_text}"
        
        else:
            # Generic format
            return str(data)


# Global instance
_crypto_tools = None

def get_crypto_tools() -> OpenClawCryptoTools:
    """Get or create crypto tools instance"""
    global _crypto_tools
    if _crypto_tools is None:
        _crypto_tools = OpenClawCryptoTools()
    return _crypto_tools
