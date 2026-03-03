"""
Extended unit tests for OfflineModeHandler.

This test file complements test_offline_mode_handler.py with additional
edge cases and scenarios:
- Edge cases for analyze command with various symbol formats
- Futures command with all valid timeframes
- Menu generation and button callbacks
- Additional error scenarios

Feature: dual-mode-offline-online
Task: 5.3
Requirements: 2.6
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Set dummy environment variables to avoid database connection errors
os.environ['SUPABASE_URL'] = 'https://dummy.supabase.co'
os.environ['SUPABASE_KEY'] = 'dummy_key'

# Mock database module before importing handler
mock_db = MagicMock()
sys.modules['app.dual_mode_db'] = mock_db

# Now we can import the handler
from app.dual_mode.offline_mode_handler import (
    OfflineModeHandler,
    AnalysisResult,
    SignalResult
)


class TestAnalyzeCommandEdgeCases:
    """Test edge cases for analyze command with various symbol formats."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    @pytest.mark.anyio
    async def test_analyze_lowercase_symbol(self, handler):
        """Test analyze command with lowercase symbol."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_analyze_command(12345, "btc")
        
        # Should convert to uppercase and add USDT
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "BTCUSDT"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_analyze_mixed_case_symbol(self, handler):
        """Test analyze command with mixed case symbol."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_analyze_command(12345, "EtH")
        
        # Should normalize to uppercase
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "ETHUSDT"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_analyze_symbol_with_whitespace(self, handler):
        """Test analyze command with symbol containing whitespace."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_analyze_command(12345, "  BTC  ")
        
        # Should strip whitespace
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "BTCUSDT"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_analyze_symbol_already_with_usdt(self, handler):
        """Test analyze command with symbol already containing USDT."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_analyze_command(12345, "BTCUSDT")
        
        # Should not add USDT twice
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "BTCUSDT"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_analyze_symbol_with_usdt_lowercase(self, handler):
        """Test analyze command with lowercase usdt suffix."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_analyze_command(12345, "btcusdt")
        
        # Should normalize to uppercase
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "BTCUSDT"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_analyze_uncommon_symbol(self, handler):
        """Test analyze command with less common trading symbol."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Test with various symbols
        symbols = ["SOL", "AVAX", "MATIC", "DOT", "LINK"]
        
        for symbol in symbols:
            result = await handler.handle_analyze_command(12345, symbol)
            assert result.success is True
            
            # Verify correct symbol format
            call_args = handler.signal_generator.generate_signal.call_args
            assert call_args[0][0] == f"{symbol}USDT"
    
    @pytest.mark.anyio
    async def test_analyze_very_long_symbol(self, handler):
        """Test analyze command with unusually long symbol."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Some tokens have long names
        result = await handler.handle_analyze_command(12345, "SHIB")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "SHIBUSDT"
    
    @pytest.mark.anyio
    async def test_analyze_numeric_in_symbol(self, handler):
        """Test analyze command with symbol containing numbers."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Some tokens have numbers (e.g., 1INCH)
        result = await handler.handle_analyze_command(12345, "1INCH")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "1INCHUSDT"


class TestFuturesCommandAllTimeframes:
    """Test futures command with all valid timeframes."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    @pytest.mark.anyio
    async def test_futures_1m_timeframe(self, handler):
        """Test futures command with 1m timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "1m")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "1m"
    
    @pytest.mark.anyio
    async def test_futures_5m_timeframe(self, handler):
        """Test futures command with 5m timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "5m")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "5m"
    
    @pytest.mark.anyio
    async def test_futures_15m_timeframe(self, handler):
        """Test futures command with 15m timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "15m")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "15m"
    
    @pytest.mark.anyio
    async def test_futures_30m_timeframe(self, handler):
        """Test futures command with 30m timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "30m")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "30m"
    
    @pytest.mark.anyio
    async def test_futures_1h_timeframe(self, handler):
        """Test futures command with 1h timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "1h")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "1h"
    
    @pytest.mark.anyio
    async def test_futures_4h_timeframe(self, handler):
        """Test futures command with 4h timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "4h")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "4h"
    
    @pytest.mark.anyio
    async def test_futures_1d_timeframe(self, handler):
        """Test futures command with 1d timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "1d")
        
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "1d"
    
    @pytest.mark.anyio
    async def test_futures_uppercase_timeframe(self, handler):
        """Test futures command with uppercase timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "4H")
        
        # Should normalize to lowercase
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "4h"
    
    @pytest.mark.anyio
    async def test_futures_timeframe_with_whitespace(self, handler):
        """Test futures command with timeframe containing whitespace."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        result = await handler.handle_futures_command(12345, "BTCUSDT", "  1h  ")
        
        # Should strip whitespace
        assert result.success is True
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "1h"
    
    @pytest.mark.anyio
    async def test_futures_invalid_timeframe_format(self, handler):
        """Test futures command with invalid timeframe format."""
        # Test various invalid formats that should be rejected
        # Note: Some timeframes like "1M" might be valid in Binance API but not in our list
        invalid_timeframes = ["2h", "3h", "6h", "12h", "1w", "invalid", "xyz", ""]
        
        for timeframe in invalid_timeframes:
            result = await handler.handle_futures_command(12345, "BTCUSDT", timeframe)
            # Empty timeframe will fail validation
            if timeframe == "":
                assert result.success is False
                assert "timeframe" in result.error.lower()
            # Other invalid formats should also fail
            elif timeframe in ["invalid", "xyz"]:
                assert result.success is False
                assert "timeframe" in result.error.lower()


class TestMenuGeneration:
    """Test menu generation and button structure."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    def test_menu_has_correct_structure(self, handler):
        """Test that menu has correct button structure."""
        menu = handler.get_offline_menu()
        
        # Should have 4 rows
        assert len(menu.inline_keyboard) == 4
        
        # Each row should have buttons
        for row in menu.inline_keyboard:
            assert len(row) > 0
    
    def test_menu_technical_analysis_button(self, handler):
        """Test technical analysis button in menu."""
        menu = handler.get_offline_menu()
        
        # First row should have technical analysis button
        button = menu.inline_keyboard[0][0]
        assert "Technical Analysis" in button.text
        assert button.callback_data == "offline_analyze"
    
    def test_menu_futures_signals_button(self, handler):
        """Test futures signals button in menu."""
        menu = handler.get_offline_menu()
        
        # Second row should have futures signals button
        button = menu.inline_keyboard[1][0]
        assert "Futures Signals" in button.text
        assert button.callback_data == "offline_futures"
    
    def test_menu_multi_coin_button(self, handler):
        """Test multi-coin signals button in menu."""
        menu = handler.get_offline_menu()
        
        # Third row should have multi-coin button
        button = menu.inline_keyboard[2][0]
        assert "Multi-Coin" in button.text
        assert button.callback_data == "offline_multi"
    
    def test_menu_back_button(self, handler):
        """Test back to main menu button."""
        menu = handler.get_offline_menu()
        
        # Last row should have back button
        button = menu.inline_keyboard[3][0]
        assert "Back" in button.text or "Main Menu" in button.text
        assert button.callback_data == "main_menu"
    
    def test_menu_callback_data_format(self, handler):
        """Test that all callback data follows consistent format."""
        menu = handler.get_offline_menu()
        
        callback_data_list = []
        for row in menu.inline_keyboard:
            for button in row:
                callback_data_list.append(button.callback_data)
        
        # All offline mode callbacks should start with "offline_" except main_menu
        for callback_data in callback_data_list:
            if callback_data != "main_menu":
                assert callback_data.startswith("offline_")
    
    def test_menu_button_emojis(self, handler):
        """Test that menu buttons have appropriate emojis."""
        menu = handler.get_offline_menu()
        
        # Collect all button texts
        button_texts = []
        for row in menu.inline_keyboard:
            for button in row:
                button_texts.append(button.text)
        
        # Check that buttons have emojis
        emoji_count = sum(1 for text in button_texts if any(char in text for char in "📊🔮📈🔙"))
        assert emoji_count >= 3  # At least 3 buttons should have emojis


class TestResponseFormatting:
    """Test response formatting edge cases."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    def test_format_response_with_empty_content(self, handler):
        """Test formatting response with empty content."""
        data = {
            'type': 'analysis',
            'symbol': 'BTCUSDT',
            'content': ''
        }
        
        formatted = handler.format_offline_response(data)
        
        # Should still have prefix and structure
        assert "[OFFLINE] 📊" in formatted
        assert "BTCUSDT" in formatted
    
    def test_format_response_with_long_content(self, handler):
        """Test formatting response with very long content."""
        long_content = "A" * 5000  # Very long content
        data = {
            'type': 'analysis',
            'symbol': 'BTCUSDT',
            'content': long_content
        }
        
        formatted = handler.format_offline_response(data)
        
        # Should handle long content without errors
        assert "[OFFLINE] 📊" in formatted
        assert long_content in formatted
    
    def test_format_response_with_special_characters(self, handler):
        """Test formatting response with special characters."""
        data = {
            'type': 'analysis',
            'symbol': 'BTCUSDT',
            'content': 'Signal with special chars: €£¥₿ and emojis: 🚀📈💰'
        }
        
        formatted = handler.format_offline_response(data)
        
        # Should preserve special characters
        assert "€£¥₿" in formatted
        assert "🚀📈💰" in formatted
    
    def test_format_response_with_newlines(self, handler):
        """Test formatting response with multiple newlines."""
        data = {
            'type': 'futures',
            'symbol': 'ETHUSDT',
            'timeframe': '4h',
            'content': 'Line 1\n\nLine 2\n\n\nLine 3'
        }
        
        formatted = handler.format_offline_response(data)
        
        # Should preserve newlines
        assert 'Line 1' in formatted
        assert 'Line 2' in formatted
        assert 'Line 3' in formatted
    
    def test_format_response_unknown_type(self, handler):
        """Test formatting response with unknown type."""
        data = {
            'type': 'unknown_type',
            'content': 'Test content'
        }
        
        formatted = handler.format_offline_response(data)
        
        # Should still format with prefix
        assert "[OFFLINE] 📊" in formatted
        assert "Test content" in formatted
    
    def test_format_response_missing_optional_fields(self, handler):
        """Test formatting response with missing optional fields."""
        data = {
            'content': 'Just content, no type or symbol'
        }
        
        formatted = handler.format_offline_response(data)
        
        # Should handle missing fields gracefully
        assert "[OFFLINE] 📊" in formatted
        assert "Just content" in formatted


class TestWelcomeAndHelpMessages:
    """Test welcome and help message generation."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    def test_welcome_message_structure(self, handler):
        """Test welcome message has correct structure."""
        message = handler.get_welcome_message()
        
        assert "[OFFLINE] 📊" in message
        assert "Welcome" in message
        assert "Manual Trading" in message
    
    def test_welcome_message_mentions_commands(self, handler):
        """Test welcome message mentions available commands."""
        message = handler.get_welcome_message()
        
        # Should mention key commands
        assert "/analyze" in message
        assert "/futures" in message
        assert "/online" in message
    
    def test_welcome_message_mentions_features(self, handler):
        """Test welcome message mentions key features."""
        message = handler.get_welcome_message()
        
        # Should mention features
        assert "Technical Analysis" in message or "analysis" in message.lower()
        assert "Futures" in message or "futures" in message.lower()
    
    def test_help_text_structure(self, handler):
        """Test help text has correct structure."""
        help_text = handler.get_help_text()
        
        assert "[OFFLINE] 📊" in help_text
        assert "Commands" in help_text or "commands" in help_text.lower()
    
    def test_help_text_command_examples(self, handler):
        """Test help text includes command examples."""
        help_text = handler.get_help_text()
        
        # Should have examples
        assert "Example:" in help_text or "example:" in help_text.lower()
        assert "BTCUSDT" in help_text or "btcusdt" in help_text.lower()
    
    def test_help_text_timeframe_options(self, handler):
        """Test help text lists valid timeframe options."""
        help_text = handler.get_help_text()
        
        # Should mention timeframes
        assert "1h" in help_text
        assert "4h" in help_text or "timeframe" in help_text.lower()
    
    def test_help_text_no_llm_mention(self, handler):
        """Test help text mentions no LLM usage."""
        help_text = handler.get_help_text()
        
        # Should clarify no LLM usage
        assert "No LLM" in help_text or "Binance API" in help_text


class TestManualSignalEdgeCases:
    """Test manual signal handling edge cases."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    @pytest.mark.anyio
    async def test_manual_signal_with_all_params(self, handler):
        """Test manual signal with all parameters provided."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        params = {
            'symbol': 'BTCUSDT',
            'timeframe': '4h',
            'type': 'futures'
        }
        
        result = await handler.handle_manual_signal(12345, params)
        
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_manual_signal_with_minimal_params(self, handler):
        """Test manual signal with only required parameters."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        params = {
            'symbol': 'ETHUSDT'
        }
        
        result = await handler.handle_manual_signal(12345, params)
        
        # Should use defaults for optional params
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_manual_signal_empty_params(self, handler):
        """Test manual signal with empty parameters dict."""
        result = await handler.handle_manual_signal(12345, {})
        
        assert result.success is False
        assert "required" in result.error.lower()
    
    @pytest.mark.anyio
    async def test_manual_signal_none_symbol(self, handler):
        """Test manual signal with None as symbol."""
        params = {
            'symbol': None,
            'timeframe': '1h'
        }
        
        result = await handler.handle_manual_signal(12345, params)
        
        assert result.success is False
        assert "required" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
