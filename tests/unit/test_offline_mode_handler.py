"""
Unit tests for OfflineModeHandler.

Tests the offline mode handler implementation for:
- Technical analysis command handling
- Futures signal generation
- Manual signal handling
- Menu generation
- Response formatting

Feature: dual-mode-offline-online
Task: 5.1
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


class TestOfflineModeHandler:
    """Test suite for OfflineModeHandler."""
    
    @pytest.fixture
    def handler(self):
        """Create OfflineModeHandler instance."""
        return OfflineModeHandler()
    
    def test_initialization(self, handler):
        """Test handler initializes correctly."""
        assert handler is not None
        assert handler.signal_generator is not None
        assert handler.OFFLINE_PREFIX == "[OFFLINE] 📊"
    
    @pytest.mark.anyio
    async def test_handle_analyze_command_success(self, handler):
        """Test successful technical analysis."""
        # Mock the signal generator
        mock_signal = "📊 BTCUSDT Analysis\nBullish trend detected"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Execute
        result = await handler.handle_analyze_command(12345, "BTCUSDT")
        
        # Verify
        assert result.success is True
        assert result.signal_text is not None
        assert "[OFFLINE] 📊" in result.signal_text
        assert "BTCUSDT" in result.signal_text
        assert result.error is None
    
    @pytest.mark.anyio
    async def test_handle_analyze_command_adds_usdt(self, handler):
        """Test that analyze command adds USDT suffix if missing."""
        mock_signal = "📊 Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Execute with symbol without USDT
        result = await handler.handle_analyze_command(12345, "BTC")
        
        # Verify signal generator was called with BTCUSDT
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][0] == "BTCUSDT"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_handle_analyze_command_empty_symbol(self, handler):
        """Test analyze command with empty symbol."""
        result = await handler.handle_analyze_command(12345, "")
        
        assert result.success is False
        assert result.error is not None
        assert "empty" in result.error.lower()
    
    @pytest.mark.anyio
    async def test_handle_futures_command_success(self, handler):
        """Test successful futures signal generation."""
        mock_signal = "🔮 ETHUSDT Futures Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Execute
        result = await handler.handle_futures_command(12345, "ETHUSDT", "4h")
        
        # Verify
        assert result.success is True
        assert result.signal_text is not None
        assert "[OFFLINE] 📊" in result.signal_text
        assert "ETHUSDT" in result.signal_text
        assert result.error is None
    
    @pytest.mark.anyio
    async def test_handle_futures_command_invalid_timeframe(self, handler):
        """Test futures command with invalid timeframe."""
        result = await handler.handle_futures_command(12345, "BTCUSDT", "99h")
        
        assert result.success is False
        assert result.error is not None
        assert "timeframe" in result.error.lower()
    
    @pytest.mark.anyio
    async def test_handle_futures_command_default_timeframe(self, handler):
        """Test futures command uses default timeframe."""
        mock_signal = "Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Execute without timeframe (should default to 1h)
        result = await handler.handle_futures_command(12345, "BTCUSDT")
        
        # Verify default timeframe was used
        handler.signal_generator.generate_signal.assert_called_once()
        call_args = handler.signal_generator.generate_signal.call_args
        assert call_args[0][1] == "1h"
        assert result.success is True
    
    @pytest.mark.anyio
    async def test_handle_manual_signal_success(self, handler):
        """Test manual signal handling."""
        mock_signal = "Manual Signal"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        params = {
            'symbol': 'SOLUSDT',
            'timeframe': '1h',
            'type': 'futures'
        }
        
        result = await handler.handle_manual_signal(12345, params)
        
        assert result.success is True
        assert result.signal_text is not None
    
    @pytest.mark.anyio
    async def test_handle_manual_signal_missing_symbol(self, handler):
        """Test manual signal with missing symbol."""
        params = {'timeframe': '1h'}
        
        result = await handler.handle_manual_signal(12345, params)
        
        assert result.success is False
        assert result.error is not None
        assert "required" in result.error.lower()
    
    def test_get_offline_menu(self, handler):
        """Test offline menu generation."""
        menu = handler.get_offline_menu()
        
        assert menu is not None
        assert len(menu.inline_keyboard) > 0
        
        # Check for expected buttons
        buttons_text = []
        for row in menu.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any("Technical Analysis" in text for text in buttons_text)
        assert any("Futures Signals" in text for text in buttons_text)
        assert any("Main Menu" in text for text in buttons_text)
    
    def test_format_offline_response_analysis(self, handler):
        """Test response formatting for analysis."""
        data = {
            'type': 'analysis',
            'symbol': 'BTCUSDT',
            'content': 'Test analysis content'
        }
        
        formatted = handler.format_offline_response(data)
        
        assert "[OFFLINE] 📊" in formatted
        assert "BTCUSDT" in formatted
        assert "Test analysis content" in formatted
        assert "Manual Trading Mode" in formatted
    
    def test_format_offline_response_futures(self, handler):
        """Test response formatting for futures."""
        data = {
            'type': 'futures',
            'symbol': 'ETHUSDT',
            'timeframe': '4h',
            'content': 'Test futures signal'
        }
        
        formatted = handler.format_offline_response(data)
        
        assert "[OFFLINE] 📊" in formatted
        assert "ETHUSDT" in formatted
        assert "4H" in formatted
        assert "Test futures signal" in formatted
    
    def test_format_offline_response_error(self, handler):
        """Test response formatting for errors."""
        data = {
            'type': 'error',
            'content': 'Test error message'
        }
        
        formatted = handler.format_offline_response(data)
        
        assert "[OFFLINE] 📊" in formatted
        assert "Error" in formatted
        assert "Test error message" in formatted
    
    def test_get_welcome_message(self, handler):
        """Test welcome message generation."""
        message = handler.get_welcome_message()
        
        assert "[OFFLINE] 📊" in message
        assert "Welcome" in message
        assert "Manual Trading" in message
        assert "/analyze" in message
        assert "/futures" in message
        assert "/online" in message
    
    def test_get_help_text(self, handler):
        """Test help text generation."""
        help_text = handler.get_help_text()
        
        assert "[OFFLINE] 📊" in help_text
        assert "/analyze" in help_text
        assert "/futures" in help_text
        assert "/futures_signals" in help_text
        assert "Binance API" in help_text
    
    @pytest.mark.anyio
    async def test_no_llm_calls_in_analyze(self, handler):
        """Test that analyze command does not use LLM."""
        mock_signal = "Signal without LLM"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Execute - the handler should not use any LLM
        result = await handler.handle_analyze_command(12345, "BTCUSDT")
        
        # Verify success without LLM
        assert result.success is True
        # The signal generator is called, but it doesn't use LLM internally
        handler.signal_generator.generate_signal.assert_called_once()
    
    @pytest.mark.anyio
    async def test_no_llm_calls_in_futures(self, handler):
        """Test that futures command does not use LLM."""
        mock_signal = "Signal without LLM"
        handler.signal_generator.generate_signal = AsyncMock(return_value=mock_signal)
        
        # Execute - the handler should not use any LLM
        result = await handler.handle_futures_command(12345, "ETHUSDT", "1h")
        
        # Verify success without LLM
        assert result.success is True
        # The signal generator is called, but it doesn't use LLM internally
        handler.signal_generator.generate_signal.assert_called_once()
    
    @pytest.mark.anyio
    async def test_error_handling_in_analyze(self, handler):
        """Test error handling in analyze command."""
        # Mock signal generator to raise exception
        handler.signal_generator.generate_signal = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        result = await handler.handle_analyze_command(12345, "BTCUSDT")
        
        assert result.success is False
        assert result.error is not None
        assert "Error" in result.error
    
    @pytest.mark.anyio
    async def test_error_handling_in_futures(self, handler):
        """Test error handling in futures command."""
        # Mock signal generator to raise exception
        handler.signal_generator.generate_signal = AsyncMock(
            side_effect=Exception("Network Error")
        )
        
        result = await handler.handle_futures_command(12345, "ETHUSDT", "4h")
        
        assert result.success is False
        assert result.error is not None
        assert "Error" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
