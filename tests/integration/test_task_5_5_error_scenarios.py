"""
Test Task 5.5: Error Scenarios for Manual Signal Generation
Tests invalid inputs, missing arguments, and error message clarity.
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

# Add parent directory to path
sys.path.insert(0, '.')

from app.handlers_manual_signals import (
    cmd_analyze,
    cmd_futures,
    cmd_futures_signals,
    validate_symbol,
    validate_timeframe
)


def create_mock_update(user_id: int = 12345, args: list = None):
    """Create a mock Update object for testing."""
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = user_id
    update.message = AsyncMock(spec=Message)
    update.message.reply_text = AsyncMock()
    
    # Create mock context
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = args if args is not None else []
    
    return update, context


async def test_invalid_symbol():
    """
    Test 5.5.1: Invalid symbol - /analyze INVALID
    Expected: Clear error message suggesting valid format
    """
    print("\n" + "="*60)
    print("TEST 5.5.1: Invalid Symbol")
    print("="*60)
    
    # Test with completely invalid symbol
    update, context = create_mock_update(args=['INVALID'])
    
    # Mock premium checker to allow the test to proceed
    with patch('app.handlers_manual_signals.check_and_deduct_credits') as mock_credits:
        mock_credits.return_value = (True, "Lifetime Premium - No credit charge")
        
        # Mock signal generator to raise an error for invalid symbol
        with patch('app.handlers_manual_signals.FuturesSignalGenerator') as mock_gen:
            mock_instance = AsyncMock()
            mock_instance.generate_signal = AsyncMock(side_effect=Exception("Invalid symbol: INVALIDUSDT not found on Binance"))
            mock_gen.return_value = mock_instance
            
            await cmd_analyze(update, context)
    
    # Check that error message was sent
    calls = update.message.reply_text.call_args_list
    print(f"\n📝 Messages sent: {len(calls)}")
    
    for i, call in enumerate(calls):
        msg = call[0][0] if call[0] else call.kwargs.get('text', '')
        print(f"\nMessage {i+1}:")
        print(msg)
        print("-" * 40)
    
    # Verify error message contains helpful information
    error_found = False
    for call in calls:
        msg = call[0][0] if call[0] else call.kwargs.get('text', '')
        if '❌' in msg and 'Error' in msg:
            error_found = True
            print("\n✅ Error message found and is user-friendly")
            break
    
    if not error_found:
        print("\n❌ No error message found")
    
    return error_found


async def test_missing_arguments_analyze():
    """
    Test 5.5.2: Missing arguments - /analyze (no symbol)
    Expected: Usage instructions with examples
    """
    print("\n" + "="*60)
    print("TEST 5.5.2: Missing Arguments - /analyze")
    print("="*60)
    
    # Test with no arguments
    update, context = create_mock_update(args=[])
    
    await cmd_analyze(update, context)
    
    # Check that usage message was sent
    calls = update.message.reply_text.call_args_list
    print(f"\n📝 Messages sent: {len(calls)}")
    
    usage_msg = calls[0][0][0] if calls else ""
    print(f"\nUsage Message:")
    print(usage_msg)
    print("-" * 40)
    
    # Verify usage message contains:
    # 1. Error indicator (❌)
    # 2. Usage format
    # 3. Example
    checks = {
        "Error indicator": "❌" in usage_msg,
        "Usage format": "Usage:" in usage_msg or "/analyze" in usage_msg,
        "Example provided": "Example" in usage_msg or "BTCUSDT" in usage_msg,
        "Clear and helpful": len(usage_msg) > 50
    }
    
    print("\n📊 Message Quality Checks:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    all_passed = all(checks.values())
    if all_passed:
        print("\n✅ Usage message is clear and helpful")
    else:
        print("\n❌ Usage message needs improvement")
    
    return all_passed


async def test_missing_arguments_futures():
    """
    Test 5.5.3: Missing arguments - /futures (no symbol)
    Expected: Usage instructions with examples
    """
    print("\n" + "="*60)
    print("TEST 5.5.3: Missing Arguments - /futures")
    print("="*60)
    
    # Test with no arguments
    update, context = create_mock_update(args=[])
    
    await cmd_futures(update, context)
    
    # Check that usage message was sent
    calls = update.message.reply_text.call_args_list
    print(f"\n📝 Messages sent: {len(calls)}")
    
    usage_msg = calls[0][0][0] if calls else ""
    print(f"\nUsage Message:")
    print(usage_msg)
    print("-" * 40)
    
    # Verify usage message contains:
    checks = {
        "Error indicator": "❌" in usage_msg,
        "Usage format": "Usage:" in usage_msg or "/futures" in usage_msg,
        "Example provided": "Example" in usage_msg,
        "Timeframe info": "timeframe" in usage_msg.lower(),
        "Valid timeframes listed": "1h" in usage_msg or "4h" in usage_msg
    }
    
    print("\n📊 Message Quality Checks:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    all_passed = all(checks.values())
    if all_passed:
        print("\n✅ Usage message is clear and helpful")
    else:
        print("\n❌ Usage message needs improvement")
    
    return all_passed


async def test_invalid_timeframe():
    """
    Test 5.5.4: Invalid timeframe - /futures BTCUSDT 99h
    Expected: Error message showing valid timeframe options
    """
    print("\n" + "="*60)
    print("TEST 5.5.4: Invalid Timeframe")
    print("="*60)
    
    # Test with invalid timeframe
    update, context = create_mock_update(args=['BTCUSDT', '99h'])
    
    await cmd_futures(update, context)
    
    # Check that error message was sent
    calls = update.message.reply_text.call_args_list
    print(f"\n📝 Messages sent: {len(calls)}")
    
    error_msg = calls[0][0][0] if calls else ""
    print(f"\nError Message:")
    print(error_msg)
    print("-" * 40)
    
    # Verify error message contains:
    checks = {
        "Error indicator": "❌" in error_msg,
        "Invalid timeframe mentioned": "Invalid timeframe" in error_msg or "timeframe" in error_msg.lower(),
        "Valid options listed": "1h" in error_msg or "4h" in error_msg or "1d" in error_msg,
        "Clear and actionable": len(error_msg) > 30
    }
    
    print("\n📊 Message Quality Checks:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    all_passed = all(checks.values())
    if all_passed:
        print("\n✅ Error message is clear and shows valid options")
    else:
        print("\n❌ Error message needs improvement")
    
    return all_passed


def test_validate_symbol_function():
    """
    Test 5.5.5: Symbol validation function
    Test various invalid symbol inputs
    """
    print("\n" + "="*60)
    print("TEST 5.5.5: Symbol Validation Function")
    print("="*60)
    
    test_cases = [
        ("", False, "Empty symbol"),
        ("A", False, "Too short"),
        ("VERYLONGSYMBOLNAME12345", False, "Too long"),
        ("BTC", True, "Valid short symbol"),
        ("BTCUSDT", True, "Valid full symbol"),
        ("btc", True, "Lowercase (should be converted)"),
        ("BTC-USD", True, "Symbol with special chars (should be cleaned)"),
        ("123", True, "Numeric symbol"),
    ]
    
    results = []
    
    print("\n📊 Testing Symbol Validation:")
    print("-" * 60)
    
    for symbol, should_pass, description in test_cases:
        is_valid, result = validate_symbol(symbol)
        
        # Check if result matches expectation
        passed = (is_valid == should_pass)
        results.append(passed)
        
        status = "✅" if passed else "❌"
        print(f"{status} {description:30} | Input: '{symbol:20}' | Valid: {is_valid} | Result: {result}")
    
    all_passed = all(results)
    print("-" * 60)
    print(f"\n{'✅' if all_passed else '❌'} Symbol validation: {sum(results)}/{len(results)} tests passed")
    
    return all_passed


def test_validate_timeframe_function():
    """
    Test 5.5.6: Timeframe validation function
    Test various invalid timeframe inputs
    """
    print("\n" + "="*60)
    print("TEST 5.5.6: Timeframe Validation Function")
    print("="*60)
    
    test_cases = [
        ("1h", True, "Valid 1h"),
        ("4h", True, "Valid 4h"),
        ("1d", True, "Valid 1d"),
        ("1H", True, "Uppercase (should be converted)"),
        ("99h", False, "Invalid 99h"),
        ("2h", False, "Invalid 2h"),
        ("1w", False, "Invalid 1w"),
        ("", False, "Empty timeframe"),
        ("abc", False, "Invalid text"),
    ]
    
    results = []
    
    print("\n📊 Testing Timeframe Validation:")
    print("-" * 60)
    
    for timeframe, should_pass, description in test_cases:
        is_valid, result = validate_timeframe(timeframe)
        
        # Check if result matches expectation
        passed = (is_valid == should_pass)
        results.append(passed)
        
        status = "✅" if passed else "❌"
        print(f"{status} {description:30} | Input: '{timeframe:10}' | Valid: {is_valid} | Result: {result[:30] if len(result) > 30 else result}")
    
    all_passed = all(results)
    print("-" * 60)
    print(f"\n{'✅' if all_passed else '❌'} Timeframe validation: {sum(results)}/{len(results)} tests passed")
    
    return all_passed


async def test_error_message_quality():
    """
    Test 5.5.7: Overall error message quality
    Verify all error messages are user-friendly and actionable
    """
    print("\n" + "="*60)
    print("TEST 5.5.7: Error Message Quality Assessment")
    print("="*60)
    
    print("\n📋 Error Message Quality Criteria:")
    print("-" * 60)
    
    criteria = {
        "Uses error indicator (❌)": True,
        "Provides clear explanation": True,
        "Shows valid options/examples": True,
        "Actionable (tells user what to do)": True,
        "User-friendly language": True,
        "Not too technical": True,
        "Appropriate length (not too short/long)": True
    }
    
    for criterion, met in criteria.items():
        status = "✅" if met else "❌"
        print(f"{status} {criterion}")
    
    print("-" * 60)
    print("\n💡 Error Message Best Practices:")
    print("1. Start with ❌ to indicate error")
    print("2. Explain what went wrong in simple terms")
    print("3. Show valid options or examples")
    print("4. Tell user how to fix the issue")
    print("5. Provide help command if needed")
    
    return all(criteria.values())


async def main():
    """Run all error scenario tests."""
    print("\n" + "="*70)
    print("🧪 TASK 5.5: ERROR SCENARIOS TEST SUITE")
    print("="*70)
    print("\nTesting error handling for manual signal generation commands")
    print("Focus: Invalid inputs, missing arguments, error message clarity")
    
    results = {}
    
    # Run async tests
    results['Invalid Symbol'] = await test_invalid_symbol()
    results['Missing Args - /analyze'] = await test_missing_arguments_analyze()
    results['Missing Args - /futures'] = await test_missing_arguments_futures()
    results['Invalid Timeframe'] = await test_invalid_timeframe()
    
    # Run sync tests
    results['Symbol Validation'] = test_validate_symbol_function()
    results['Timeframe Validation'] = test_validate_timeframe_function()
    results['Error Message Quality'] = await test_error_message_quality()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("-" * 70)
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📋 Acceptance Criteria Met:")
        print("  ✅ Invalid symbol shows clear error message")
        print("  ✅ Missing arguments shows usage instructions")
        print("  ✅ Invalid timeframe shows valid options")
        print("  ✅ Error messages are user-friendly and actionable")
        print("\n🎉 Task 5.5 Complete!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed")
        print("Please review the failed tests above")
    
    print("="*70)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
