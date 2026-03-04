"""
OpenClaw Enhanced Message Handler
Supports:
1. Real-time Binance API data
2. Image/chart analysis with GPT-4 Vision
3. Crypto market data integration
"""

import logging
import re
from typing import Optional, Tuple
from telegram import Update, File
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class OpenClawEnhancedHandler:
    """Enhanced handler with crypto data and vision capabilities"""
    
    def __init__(self, openclaw_manager):
        """
        Initialize enhanced handler
        
        Args:
            openclaw_manager: OpenClawManager instance
        """
        self.manager = openclaw_manager
        self.crypto_tools = None
        self.vision_tools = None
    
    def _get_crypto_tools(self):
        """Lazy load crypto tools"""
        if self.crypto_tools is None:
            from app.openclaw_crypto_data_tools import get_crypto_data_tools
            self.crypto_tools = get_crypto_data_tools()
        return self.crypto_tools
    
    def _get_vision_tools(self):
        """Lazy load vision tools"""
        if self.vision_tools is None:
            from app.openclaw_vision_tools import get_vision_tools
            self.vision_tools = get_vision_tools()
        return self.vision_tools
    
    async def enhance_message_with_data(
        self,
        message: str,
        photo: Optional[File] = None
    ) -> Tuple[str, dict]:
        """
        Enhance user message with real-time data and image analysis
        
        Args:
            message: User's message text
            photo: Optional Telegram photo
            
        Returns:
            Tuple of (enhanced_message, context_data)
        """
        enhanced_message = message
        context_data = {}
        
        # 1. Handle image/chart analysis
        if photo:
            vision_result = await self._analyze_photo(photo, message)
            if vision_result['success']:
                context_data['image_analysis'] = vision_result['analysis']
                enhanced_message = f"""[IMAGE ANALYSIS]
{vision_result['analysis']}

[USER QUESTION]
{message if message else 'What do you see in this chart?'}"""
            else:
                logger.error(f"Image analysis failed: {vision_result.get('error')}")
        
        # 2. Detect crypto symbols and fetch real-time data
        symbols = self._extract_crypto_symbols(message)
        if symbols:
            crypto_data = await self._fetch_crypto_data(symbols)
            if crypto_data:
                context_data['crypto_data'] = crypto_data
                enhanced_message = self._inject_crypto_data(enhanced_message, crypto_data)
        
        # 3. Detect requests for market data
        if self._is_market_data_request(message):
            market_data = await self._fetch_market_overview()
            if market_data:
                context_data['market_data'] = market_data
                enhanced_message = self._inject_market_data(enhanced_message, market_data)
        
        return enhanced_message, context_data
    
    async def _analyze_photo(self, photo: File, user_question: str) -> dict:
        """Analyze photo using vision tools"""
        try:
            vision_tools = self._get_vision_tools()
            return await vision_tools.analyze_telegram_photo(photo, user_question)
        except Exception as e:
            logger.error(f"Error analyzing photo: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_crypto_symbols(self, message: str) -> list:
        """
        Extract crypto symbols from message
        
        Examples:
        - "BTC price" -> ["BTCUSDT"]
        - "ETH and SOL" -> ["ETHUSDT", "SOLUSDT"]
        - "BTCUSDT chart" -> ["BTCUSDT"]
        """
        symbols = []
        message_upper = message.upper()
        
        # Common crypto symbols
        crypto_map = {
            'BTC': 'BTCUSDT',
            'BITCOIN': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'ETHEREUM': 'ETHUSDT',
            'BNB': 'BNBUSDT',
            'SOL': 'SOLUSDT',
            'SOLANA': 'SOLUSDT',
            'XRP': 'XRPUSDT',
            'RIPPLE': 'XRPUSDT',
            'ADA': 'ADAUSDT',
            'CARDANO': 'ADAUSDT',
            'DOGE': 'DOGEUSDT',
            'DOGECOIN': 'DOGEUSDT',
            'DOT': 'DOTUSDT',
            'POLKADOT': 'DOTUSDT',
            'MATIC': 'MATICUSDT',
            'POLYGON': 'MATICUSDT',
            'AVAX': 'AVAXUSDT',
            'AVALANCHE': 'AVAXUSDT',
            'LINK': 'LINKUSDT',
            'CHAINLINK': 'LINKUSDT',
            'UNI': 'UNIUSDT',
            'UNISWAP': 'UNIUSDT',
            'ATOM': 'ATOMUSDT',
            'COSMOS': 'ATOMUSDT',
            'LTC': 'LTCUSDT',
            'LITECOIN': 'LTCUSDT',
            'TRX': 'TRXUSDT',
            'TRON': 'TRXUSDT',
            'NEAR': 'NEARUSDT',
            'APT': 'APTUSDT',
            'ARB': 'ARBUSDT',
            'OP': 'OPUSDT',
            'OPTIMISM': 'OPUSDT'
        }
        
        # Check for direct USDT pairs
        usdt_pattern = r'\b([A-Z]{2,10})USDT\b'
        usdt_matches = re.findall(usdt_pattern, message_upper)
        for match in usdt_matches:
            symbols.append(f"{match}USDT")
        
        # Check for common crypto names
        for crypto, symbol in crypto_map.items():
            if re.search(r'\b' + crypto + r'\b', message_upper):
                if symbol not in symbols:
                    symbols.append(symbol)
        
        return symbols[:5]  # Limit to 5 symbols
    
    async def _fetch_crypto_data(self, symbols: list) -> dict:
        """Fetch real-time data for symbols"""
        try:
            crypto_tools = self._get_crypto_tools()
            data = {}
            
            for symbol in symbols:
                stats = await crypto_tools.get_24h_stats(symbol)
                if stats['success']:
                    data[symbol] = stats
            
            return data
        except Exception as e:
            logger.error(f"Error fetching crypto data: {e}")
            return {}
    
    def _inject_crypto_data(self, message: str, crypto_data: dict) -> str:
        """Inject real-time crypto data into message"""
        if not crypto_data:
            return message
        
        data_section = "\n\n[REAL-TIME MARKET DATA]\n"
        
        for symbol, data in crypto_data.items():
            data_section += f"""
{symbol}:
• Price: ${data['price']:,.2f}
• 24h Change: {data['change_percent_24h']:+.2f}%
• 24h High: ${data['high_24h']:,.2f}
• 24h Low: ${data['low_24h']:,.2f}
• 24h Volume: ${data['quote_volume_24h']:,.0f}
"""
        
        return message + data_section
    
    def _is_market_data_request(self, message: str) -> bool:
        """Check if message requests market overview"""
        keywords = [
            'market overview', 'market summary', 'top gainers',
            'trending', 'hot coins', 'market update',
            'crypto market', 'market status'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
    
    async def _fetch_market_overview(self) -> dict:
        """Fetch market overview data"""
        try:
            crypto_tools = self._get_crypto_tools()
            
            # Get top gainers
            gainers = await crypto_tools.get_top_gainers(limit=5)
            
            # Get major coins
            major_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
            major_data = await crypto_tools.get_market_summary(major_symbols)
            
            return {
                'gainers': gainers,
                'major_coins': major_data
            }
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {}
    
    def _inject_market_data(self, message: str, market_data: dict) -> str:
        """Inject market overview data into message"""
        if not market_data:
            return message
        
        data_section = "\n\n[MARKET OVERVIEW]\n"
        
        # Major coins
        if 'major_coins' in market_data and market_data['major_coins'].get('success'):
            data_section += "\n📊 Major Coins:\n"
            for symbol, data in market_data['major_coins'].get('markets', {}).items():
                data_section += f"• {symbol}: ${data['price']:,.2f} ({data['change_percent_24h']:+.2f}%)\n"
        
        # Top gainers
        if 'gainers' in market_data and market_data['gainers'].get('success'):
            data_section += "\n🚀 Top Gainers (24h):\n"
            for gainer in market_data['gainers'].get('gainers', [])[:5]:
                data_section += f"• {gainer['symbol']}: {gainer['change_percent']:+.2f}% (${gainer['price']:,.4f})\n"
        
        return message + data_section


# Singleton instance
_enhanced_handler_instance = None

def get_enhanced_handler(openclaw_manager):
    """Get singleton instance of enhanced handler"""
    global _enhanced_handler_instance
    if _enhanced_handler_instance is None:
        _enhanced_handler_instance = OpenClawEnhancedHandler(openclaw_manager)
    return _enhanced_handler_instance
