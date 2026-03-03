"""
Integration Test for Task 5.5: Error Scenarios
Tests error handling in realistic scenarios with actual bot context.
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, '.')

from app.handlers_manual_signals import (
    cmd_analyze,
    cmd_futures,
    cmd_futures_signals
)


def create_realistic_update(user_id: int, command: str, args: list = None):
    """Create a realistic mock Update object."""
    from telegram import Update, Message, User, Chat
    
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = user_id
    update.effective_user.first_name = "TestUser"
    
    update.message = AsyncMock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.delete = AsyncMock()
    update.message.text = command
    
    # Create context
    from telegram.ext import ContextTypes
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = args if args is not None else []
    
    return update, context


async def test_scenario_1_invalid_symbol():
    """Scenario 1: User tries to analyze non-existent symbol."""
    print("\n" + "="*60)
    print("SCENARIO 1: Invalid Symbol (INVALID)")
    print("="*60)
    
    update, context = create_realistic_update(12345, "/analyze INVALID", ["INVALID"])
    
    with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_credits:
        mock_credits.return_value = (True, "Lifetime Premium")
        
        with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
            mock_instance = AsyncMock()
            mock_instance.generate_signal = AsyncMock(
                side_effect=Exception("Symbol INVALIDUSDT not found")
            )
            mock_gen.return_value = mock_instance
            
            await cmd_analyze(update, context)
    
    calls = update.message.reply_text.call_args_list
    error_msg = calls[-1][0][0] if calls else ""
    
    print(f"User Input: /analyze INVALID")
    print(f"Error Message:\n{error_msg}")
    
    assert "❌" in error_msg
    assert "Error" in error_msg
    print("\n✅ Test passed: Clear error message shown")
    return True


async def test_scenario_2_missing_symbol():
    """Scenario 2: User forgets to provide symbol."""
    print("\n" + "="*60)
    print("SCENARIO 2: Missing Symbol Argument")
    print("="*60)
    
    update, context = create_realistic_update(12345, "/analyze", [])
    
    await cmd_analyze(update, context)
    
    calls = update.message.reply_text.call_args_list
    usage_msg = calls[0][0][0] if calls else ""
    
    print(f"User Input: /analyze")
    print(f"Response:\n{usage_msg}")
    
    assert "Usage:" in usage_msg
    assert "Example" in usage_msg
    print("\n✅ Test passed: Usage instructions shown")
    return True


async def test_scenario_3_invalid_timeframe():
    """Scenario 3: User provides invalid timeframe."""
    print("\n" + "="*60)
    print("SCENARIO 3: Invalid Timeframe (99h)")
    print("="*60)
    
    update, context = create_realistic_update(12345, "/futures BTCUSDT 99h", ["BTCUSDT", "99h"])
    
    await cmd_futures(update, context)
    
    calls = update.message.reply_text.call_args_list
    error_msg = calls[0][0][0] if calls else ""
    
    print(f"User Input: /futures BTCUSDT 99h")
    print(f"Error Message:\n{error_msg}")
    
    assert "Invalid timeframe" in error_msg
    assert "1h" in error_msg or "4h" in error_msg
    print("\n✅ Test passed: Valid timeframes shown")
    return True


async def main():
    """Run integration tests."""
    print("\n" + "="*70)
    print("🧪 TASK 5.5: ERROR SCENARIOS INTEGRATION TEST")
    print("="*70)
    
    results = []
    results.append(await test_scenario_1_invalid_symbol())
    results.append(await test_scenario_2_missing_symbol())
    results.append(await test_scenario_3_invalid_timeframe())
    
    print("\n" + "="*70)
    print(f"📊 RESULT: {sum(results)}/{len(results)} scenarios passed")
    print("="*70)
    
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
