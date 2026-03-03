"""
OfflineModeHandler - Manual trading features without LLM.

This module provides the OfflineModeHandler class responsible for:
- Processing manual trading requests without LLM
- Technical analysis using Binance API
- Futures signal generation
- Manual signal handling
- Offline mode menu and response formatting

Feature: dual-mode-offline-online
Task: 5.1
Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.7
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Import existing signal generator (uses Binance API, no LLM)
from futures_signal_generator import FuturesSignalGenerator


@dataclass
class AnalysisResult:
    """Result of technical analysis operation."""
    success: bool
    signal_text: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SignalResult:
    """Result of signal generation operation."""
    success: bool
    signal_text: Optional[str] = None
    error: Optional[str] = None


class OfflineModeHandler:
    """
    Handles manual trading features in offline mode without LLM.
    
    This class provides:
    - Technical analysis using Binance market data
    - Futures signal generation
    - Manual signal handling
    - Offline mode menu and response formatting
    
    All operations use Binance API only - NO LLM processing.
    """
    
    # Response prefix for offline mode
    OFFLINE_PREFIX = "[OFFLINE] 📊"
    
    def __init__(self):
        """Initialize OfflineModeHandler."""
        self.signal_generator = FuturesSignalGenerator()
    
    async def handle_analyze_command(self, user_id: int, symbol: str) -> AnalysisResult:
        """
        Handle technical analysis command for a single symbol.
        
        Uses existing Binance integration to generate trading signals
        without any LLM processing. This is a cost-effective manual
        trading feature.
        
        Args:
            user_id: Telegram user ID
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            AnalysisResult with signal text or error
            
        Requirements: 2.1, 2.3, 2.4
        """
        try:
            # Validate symbol format
            if not symbol:
                return AnalysisResult(
                    success=False,
                    error="Symbol cannot be empty"
                )
            
            # Clean and format symbol
            cleaned_symbol = symbol.upper().strip()
            if not cleaned_symbol.endswith('USDT'):
                cleaned_symbol += 'USDT'
            
            # Generate signal using Binance API (no LLM)
            signal_text = await self.signal_generator.generate_signal(
                cleaned_symbol, 
                '1h'  # Default timeframe
            )
            
            # Format with offline prefix
            formatted_signal = self.format_offline_response({
                'type': 'analysis',
                'symbol': cleaned_symbol,
                'content': signal_text
            })
            
            return AnalysisResult(
                success=True,
                signal_text=formatted_signal
            )
            
        except Exception as e:
            error_msg = f"Error analyzing {symbol}: {str(e)}"
            print(f"❌ {error_msg}")
            return AnalysisResult(
                success=False,
                error=error_msg
            )
    
    async def handle_futures_command(self, user_id: int, symbol: str, 
                                    timeframe: str = '1h') -> SignalResult:
        """
        Handle futures signal generation command.
        
        Generates futures trading signals using Binance market data
        with custom timeframe. No LLM processing involved.
        
        Args:
            user_id: Telegram user ID
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Chart timeframe (e.g., '1h', '4h', '1d')
            
        Returns:
            SignalResult with signal text or error
            
        Requirements: 2.1, 2.2, 2.3, 2.4
        """
        try:
            # Validate inputs
            if not symbol:
                return SignalResult(
                    success=False,
                    error="Symbol cannot be empty"
                )
            
            # Clean and format symbol
            cleaned_symbol = symbol.upper().strip()
            if not cleaned_symbol.endswith('USDT'):
                cleaned_symbol += 'USDT'
            
            # Validate timeframe
            valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
            cleaned_timeframe = timeframe.lower().strip()
            
            if cleaned_timeframe not in valid_timeframes:
                return SignalResult(
                    success=False,
                    error=f"Invalid timeframe. Valid options: {', '.join(valid_timeframes)}"
                )
            
            # Generate futures signal using Binance API (no LLM)
            signal_text = await self.signal_generator.generate_signal(
                cleaned_symbol,
                cleaned_timeframe
            )
            
            # Format with offline prefix
            formatted_signal = self.format_offline_response({
                'type': 'futures',
                'symbol': cleaned_symbol,
                'timeframe': cleaned_timeframe,
                'content': signal_text
            })
            
            return SignalResult(
                success=True,
                signal_text=formatted_signal
            )
            
        except Exception as e:
            error_msg = f"Error generating futures signal for {symbol}: {str(e)}"
            print(f"❌ {error_msg}")
            return SignalResult(
                success=False,
                error=error_msg
            )
    
    async def handle_manual_signal(self, user_id: int, params: Dict[str, Any]) -> SignalResult:
        """
        Handle manual trading signal request with custom parameters.
        
        This method provides flexible signal generation based on
        user-provided parameters. Uses Binance API only.
        
        Args:
            user_id: Telegram user ID
            params: Dictionary with signal parameters:
                - symbol: Trading symbol (required)
                - timeframe: Chart timeframe (optional, default: '1h')
                - type: Signal type (optional: 'spot', 'futures')
                
        Returns:
            SignalResult with signal text or error
            
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.6
        """
        try:
            # Extract parameters
            symbol = params.get('symbol')
            timeframe = params.get('timeframe', '1h')
            signal_type = params.get('type', 'futures')
            
            if not symbol:
                return SignalResult(
                    success=False,
                    error="Symbol is required"
                )
            
            # Use futures command handler for signal generation
            result = await self.handle_futures_command(user_id, symbol, timeframe)
            
            return result
            
        except Exception as e:
            error_msg = f"Error generating manual signal: {str(e)}"
            print(f"❌ {error_msg}")
            return SignalResult(
                success=False,
                error=error_msg
            )
    
    def get_offline_menu(self) -> InlineKeyboardMarkup:
        """
        Get offline mode inline keyboard menu.
        
        Provides menu options for:
        - Technical analysis
        - Futures signals
        - Return to main menu
        
        Returns:
            InlineKeyboardMarkup with offline mode options
            
        Requirements: 2.5
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 Technical Analysis",
                    callback_data="offline_analyze"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔮 Futures Signals",
                    callback_data="offline_futures"
                )
            ],
            [
                InlineKeyboardButton(
                    "📈 Multi-Coin Signals",
                    callback_data="offline_multi"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Main Menu",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def format_offline_response(self, data: Dict[str, Any]) -> str:
        """
        Format response with [OFFLINE] prefix and consistent styling.
        
        All offline mode responses are prefixed with [OFFLINE] 📊
        to clearly indicate manual trading mode without LLM.
        
        Args:
            data: Dictionary with response data:
                - type: Response type ('analysis', 'futures', 'error')
                - content: Main content text
                - symbol: Trading symbol (optional)
                - timeframe: Chart timeframe (optional)
                
        Returns:
            Formatted response string with offline prefix
            
        Requirements: 2.7
        """
        response_type = data.get('type', 'general')
        content = data.get('content', '')
        symbol = data.get('symbol', '')
        timeframe = data.get('timeframe', '')
        
        # Build header with offline prefix
        header = f"{self.OFFLINE_PREFIX}\n"
        
        # Add context based on type
        if response_type == 'analysis':
            header += f"📊 Technical Analysis: {symbol}\n"
            header += "━━━━━━━━━━━━━━━━━━━━\n"
        elif response_type == 'futures':
            header += f"🔮 Futures Signal: {symbol} ({timeframe.upper()})\n"
            header += "━━━━━━━━━━━━━━━━━━━━\n"
        elif response_type == 'error':
            header += "❌ Error\n"
            header += "━━━━━━━━━━━━━━━━━━━━\n"
        
        # Combine header and content
        formatted = header + content
        
        # Add footer note
        footer = "\n\n💡 Manual Trading Mode (No AI)"
        
        return formatted + footer
    
    def get_welcome_message(self) -> str:
        """
        Get welcome message for offline mode.
        
        Returns:
            Welcome message explaining offline mode features
        """
        return (
            f"{self.OFFLINE_PREFIX}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Welcome to Offline Mode!\n\n"
            "📊 Manual Trading Features:\n"
            "• Technical Analysis\n"
            "• Futures Signals\n"
            "• Multi-Coin Scanning\n\n"
            "💰 Cost-Effective:\n"
            "Uses Binance API only - No LLM processing\n\n"
            "🎯 Available Commands:\n"
            "• /analyze <symbol> - Single coin analysis\n"
            "• /futures <symbol> <timeframe> - Futures signal\n"
            "• /futures_signals - Multi-coin signals\n\n"
            "💡 Switch to Online Mode:\n"
            "Use /online for AI-powered trading with Automaton"
        )
    
    def get_help_text(self) -> str:
        """
        Get help text for offline mode commands.
        
        Returns:
            Help text with command usage examples
        """
        return (
            f"{self.OFFLINE_PREFIX}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Offline Mode Commands:\n\n"
            "📊 /analyze <symbol>\n"
            "   Generate technical analysis for a symbol\n"
            "   Example: /analyze BTCUSDT\n\n"
            "🔮 /futures <symbol> [timeframe]\n"
            "   Generate futures signal with custom timeframe\n"
            "   Example: /futures ETHUSDT 4h\n"
            "   Valid timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d\n\n"
            "📈 /futures_signals\n"
            "   Generate multi-coin signals (top 10 coins)\n\n"
            "💡 All commands use Binance API only - No LLM processing"
        )
