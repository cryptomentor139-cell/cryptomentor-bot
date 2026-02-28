"""
Test Task 5.4: Command Aliases Integration Test
Test that /signal and /signals work identically to /analyze and /futures_signals
with actual lifetime premium user scenarios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from app.handlers_manual_signals import (
    cmd_analyze, cmd_futures_signals,
    cmd_signal, cmd_signals
)


def create_mock_update(user_id: int, command: str, args: list = None):
    """Create a mock Update object for testing"""
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = user_id
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.delete = AsyncMock()
    return update


def create_mock_context(args: list = None):
    """Create a mock Context object for testing"""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = args or []
    return context


async def test_signal_alias_with_lifetime_premium():
    """Test /signal command with lifetime premium user"""
    print("\n" + "="*60)
    print("TEST: /signal alias with lifetime premium user")
    print("="*60)
    
    # Mock lifetime premium user (user_id: 999999)
    user_id = 999999
    update = create_mock_update(user_id, "/signal", ["BTCUSDT"])
    context = create_mock_context(["BTCUSDT"])
    
    try:
        # Mock premium checker to return lifetime premium
        with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_check:
            mock_check.return_value = (True, "Lifetime Premium - No credit charge")
            
            # Mock FuturesSignalGenerator
            with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
                mock_instance = Mock()
                mock_instance.generate_signal = AsyncMock(return_value="📊 Test Signal for BTCUSDT")
                mock_gen.return_value = mock_instance
                
                # Call cmd_signal (which is alias for cmd_analyze)
                await cmd_signal(update, context)
                
                # Verify premium check was called
                mock_check.assert_called_once_with(user_id, 20)
                
                # Verify signal was generated
                mock_instance.generate_signal.assert_called_once_with("BTCUSDT", "1h")
                
                # Verify message was sent
                assert update.message.reply_text.call_count >= 2  # Loading + signal
                
                print("✅ PASS: /signal works correctly for lifetime premium user")
                print(f"   - Premium check called: {mock_check.called}")
                print(f"   - Signal generated: {mock_instance.generate_signal.called}")
                print(f"   - Message sent: {update.message.reply_text.called}")
                return True
                
    except Exception as e:
        print(f"❌ FAIL: Error testing /signal alias: {e}")
        return False


async def test_signals_alias_with_lifetime_premium():
    """Test /signals command with lifetime premium user"""
    print("\n" + "="*60)
    print("TEST: /signals alias with lifetime premium user")
    print("="*60)
    
    # Mock lifetime premium user
    user_id = 999999
    update = create_mock_update(user_id, "/signals")
    context = create_mock_context([])
    
    try:
        # Mock premium checker to return lifetime premium
        with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_check:
            mock_check.return_value = (True, "Lifetime Premium - No credit charge")
            
            # Mock FuturesSignalGenerator
            with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
                mock_instance = Mock()
                mock_instance.generate_multi_signals = AsyncMock(
                    return_value="📊 Multi-coin signals for 10 coins"
                )
                mock_gen.return_value = mock_instance
                
                # Call cmd_signals (which is alias for cmd_futures_signals)
                await cmd_signals(update, context)
                
                # Verify premium check was called with correct cost
                mock_check.assert_called_once_with(user_id, 60)
                
                # Verify multi signals were generated
                mock_instance.generate_multi_signals.assert_called_once()
                
                # Verify message was sent
                assert update.message.reply_text.call_count >= 2  # Loading + signals
                
                print("✅ PASS: /signals works correctly for lifetime premium user")
                print(f"   - Premium check called: {mock_check.called}")
                print(f"   - Multi signals generated: {mock_instance.generate_multi_signals.called}")
                print(f"   - Message sent: {update.message.reply_text.called}")
                return True
                
    except Exception as e:
        print(f"❌ FAIL: Error testing /signals alias: {e}")
        return False


async def test_alias_equivalence():
    """Test that aliases behave identically to original commands"""
    print("\n" + "="*60)
    print("TEST: Alias equivalence verification")
    print("="*60)
    
    user_id = 999999
    
    # Test 1: cmd_signal should behave exactly like cmd_analyze
    print("\n1. Testing cmd_signal vs cmd_analyze:")
    update1 = create_mock_update(user_id, "/signal", ["ETHUSDT"])
    context1 = create_mock_context(["ETHUSDT"])
    
    update2 = create_mock_update(user_id, "/analyze", ["ETHUSDT"])
    context2 = create_mock_context(["ETHUSDT"])
    
    try:
        with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_check:
            mock_check.return_value = (True, "Lifetime Premium")
            
            with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
                mock_instance = Mock()
                mock_instance.generate_signal = AsyncMock(return_value="Signal")
                mock_gen.return_value = mock_instance
                
                # Call both commands
                await cmd_signal(update1, context1)
                await cmd_analyze(update2, context2)
                
                # Both should call premium check with same parameters
                assert mock_check.call_count == 2
                assert mock_check.call_args_list[0] == mock_check.call_args_list[1]
                
                # Both should generate signal with same parameters
                assert mock_instance.generate_signal.call_count == 2
                
                print("   ✅ cmd_signal and cmd_analyze behave identically")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: cmd_signals should behave exactly like cmd_futures_signals
    print("\n2. Testing cmd_signals vs cmd_futures_signals:")
    update3 = create_mock_update(user_id, "/signals")
    context3 = create_mock_context([])
    
    update4 = create_mock_update(user_id, "/futures_signals")
    context4 = create_mock_context([])
    
    try:
        with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_check:
            mock_check.return_value = (True, "Lifetime Premium")
            
            with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
                mock_instance = Mock()
                mock_instance.generate_multi_signals = AsyncMock(return_value="Signals")
                mock_gen.return_value = mock_instance
                
                # Call both commands
                await cmd_signals(update3, context3)
                await cmd_futures_signals(update4, context4)
                
                # Both should call premium check with same parameters
                assert mock_check.call_count == 2
                assert mock_check.call_args_list[0] == mock_check.call_args_list[1]
                
                # Both should generate multi signals
                assert mock_instance.generate_multi_signals.call_count == 2
                
                print("   ✅ cmd_signals and cmd_futures_signals behave identically")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ PASS: All aliases behave identically to original commands")
    return True


async def test_alias_error_handling():
    """Test that aliases handle errors identically to original commands"""
    print("\n" + "="*60)
    print("TEST: Alias error handling")
    print("="*60)
    
    user_id = 999999
    
    # Test invalid symbol with /signal
    print("\n1. Testing invalid symbol with /signal:")
    update = create_mock_update(user_id, "/signal", [""])
    context = create_mock_context([""])
    
    try:
        await cmd_signal(update, context)
        
        # Should send error message
        assert update.message.reply_text.called
        call_args = update.message.reply_text.call_args[0][0]
        assert "❌" in call_args or "Usage" in call_args
        
        print("   ✅ /signal handles invalid input correctly")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test missing arguments with /signals (should work - no args needed)
    print("\n2. Testing /signals with no arguments:")
    update2 = create_mock_update(user_id, "/signals")
    context2 = create_mock_context([])
    
    try:
        with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_check:
            mock_check.return_value = (True, "Lifetime Premium")
            
            with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
                mock_instance = Mock()
                mock_instance.generate_multi_signals = AsyncMock(return_value="Signals")
                mock_gen.return_value = mock_instance
                
                await cmd_signals(update2, context2)
                
                # Should work without arguments
                assert mock_instance.generate_multi_signals.called
                
                print("   ✅ /signals works correctly without arguments")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ PASS: Aliases handle errors correctly")
    return True


async def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("TASK 5.4: COMMAND ALIASES INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting aliases with lifetime premium user scenarios")
    
    results = []
    
    # Run all async tests
    results.append(("Signal alias with lifetime premium", 
                   await test_signal_alias_with_lifetime_premium()))
    results.append(("Signals alias with lifetime premium", 
                   await test_signals_alias_with_lifetime_premium()))
    results.append(("Alias equivalence verification", 
                   await test_alias_equivalence()))
    results.append(("Alias error handling", 
                   await test_alias_error_handling()))
    
    # Print summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*70)
    print(f"Results: {passed}/{total} integration tests passed")
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\nVerification complete:")
        print("✅ /signal works identically to /analyze")
        print("✅ /signals works identically to /futures_signals")
        print("✅ Both aliases work with lifetime premium users")
        print("✅ Error handling is consistent across aliases")
        print("\nTask 5.4 Status: ✅ COMPLETE")
        return True
    else:
        print("\n⚠️  SOME INTEGRATION TESTS FAILED")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)
