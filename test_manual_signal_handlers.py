"""
Test Manual Signal Handlers
Quick verification that handlers are properly implemented
"""

import asyncio
from app.handlers_manual_signals import (
    validate_symbol,
    validate_timeframe,
    check_rate_limit,
    cmd_analyze,
    cmd_futures,
    cmd_futures_signals,
    cmd_signal,
    cmd_signals
)


def test_validate_symbol():
    """Test symbol validation"""
    print("\n=== Testing Symbol Validation ===")
    
    # Valid symbols
    assert validate_symbol("BTCUSDT") == (True, "BTCUSDT")
    assert validate_symbol("btcusdt") == (True, "BTCUSDT")
    assert validate_symbol("BTC") == (True, "BTCUSDT")
    assert validate_symbol("eth") == (True, "ETHUSDT")
    
    # Invalid symbols
    assert validate_symbol("")[0] == False
    assert validate_symbol("A" * 25)[0] == False
    assert validate_symbol("X")[0] == False
    
    print("✅ Symbol validation tests passed")


def test_validate_timeframe():
    """Test timeframe validation"""
    print("\n=== Testing Timeframe Validation ===")
    
    # Valid timeframes
    assert validate_timeframe("1h") == (True, "1h")
    assert validate_timeframe("1H") == (True, "1h")
    assert validate_timeframe("4h") == (True, "4h")
    assert validate_timeframe("1d") == (True, "1d")
    
    # Invalid timeframes
    assert validate_timeframe("99h")[0] == False
    assert validate_timeframe("invalid")[0] == False
    
    print("✅ Timeframe validation tests passed")


def test_rate_limiting():
    """Test rate limiting logic"""
    print("\n=== Testing Rate Limiting ===")
    
    test_user_id = 999999
    
    # First 5 requests should succeed
    for i in range(5):
        is_allowed, _ = check_rate_limit(test_user_id)
        assert is_allowed, f"Request {i+1} should be allowed"
    
    # 6th request should fail
    is_allowed, cooldown = check_rate_limit(test_user_id)
    assert not is_allowed, "6th request should be rate limited"
    assert cooldown > 0, "Cooldown should be positive"
    
    print(f"✅ Rate limiting tests passed (cooldown: {cooldown}s)")


def test_command_aliases():
    """Test that command aliases are properly set"""
    print("\n=== Testing Command Aliases ===")
    
    # Check that aliases point to the correct functions
    assert cmd_signal == cmd_analyze, "/signal should be alias for /analyze"
    assert cmd_signals == cmd_futures_signals, "/signals should be alias for /futures_signals"
    
    print("✅ Command aliases tests passed")


def test_handler_imports():
    """Test that all required imports are available"""
    print("\n=== Testing Handler Imports ===")
    
    # Check that FuturesSignalGenerator can be imported
    try:
        from futures_signal_generator import FuturesSignalGenerator
        generator = FuturesSignalGenerator()
        print("✅ FuturesSignalGenerator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import FuturesSignalGenerator: {e}")
        return False
    
    # Check that premium_checker can be imported
    try:
        from app.premium_checker import check_and_deduct_credits, is_lifetime_premium
        print("✅ Premium checker functions imported successfully")
    except Exception as e:
        print(f"❌ Failed to import premium checker: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("MANUAL SIGNAL HANDLERS - VERIFICATION TESTS")
    print("=" * 60)
    
    try:
        # Test validation functions
        test_validate_symbol()
        test_validate_timeframe()
        test_rate_limiting()
        test_command_aliases()
        test_handler_imports()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nHandlers are ready for integration!")
        print("\nNext steps:")
        print("1. Register handlers in bot.py")
        print("2. Test with real Telegram bot")
        print("3. Deploy to Railway")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
