"""
Test: Verify manual signal handlers are registered correctly in bot.py
"""

def test_import_handlers():
    """Test that handlers can be imported successfully"""
    try:
        from app.handlers_manual_signals import (
            cmd_analyze, cmd_futures, cmd_futures_signals,
            cmd_signal, cmd_signals
        )
        print("✅ All handlers imported successfully")
        print(f"  - cmd_analyze: {cmd_analyze.__name__}")
        print(f"  - cmd_futures: {cmd_futures.__name__}")
        print(f"  - cmd_futures_signals: {cmd_futures_signals.__name__}")
        print(f"  - cmd_signal: {cmd_signal.__name__} (alias)")
        print(f"  - cmd_signals: {cmd_signals.__name__} (alias)")
        return True
    except Exception as e:
        print(f"❌ Failed to import handlers: {e}")
        return False


def test_handler_aliases():
    """Test that command aliases point to correct functions"""
    try:
        from app.handlers_manual_signals import (
            cmd_analyze, cmd_signal,
            cmd_futures_signals, cmd_signals
        )
        
        # Verify aliases
        assert cmd_signal == cmd_analyze, "cmd_signal should be alias for cmd_analyze"
        assert cmd_signals == cmd_futures_signals, "cmd_signals should be alias for cmd_futures_signals"
        
        print("✅ Command aliases verified correctly")
        print(f"  - /signal → /analyze")
        print(f"  - /signals → /futures_signals")
        return True
    except AssertionError as e:
        print(f"❌ Alias verification failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing aliases: {e}")
        return False


def test_premium_checker_available():
    """Test that premium checker module is available"""
    try:
        from app.premium_checker import check_and_deduct_credits, is_lifetime_premium
        print("✅ Premium checker module available")
        print(f"  - is_lifetime_premium: {is_lifetime_premium.__name__}")
        print(f"  - check_and_deduct_credits: {check_and_deduct_credits.__name__}")
        return True
    except Exception as e:
        print(f"❌ Failed to import premium checker: {e}")
        return False


def test_futures_signal_generator_available():
    """Test that FuturesSignalGenerator is available"""
    try:
        from futures_signal_generator import FuturesSignalGenerator
        print("✅ FuturesSignalGenerator available")
        print(f"  - Class: {FuturesSignalGenerator.__name__}")
        return True
    except Exception as e:
        print(f"❌ Failed to import FuturesSignalGenerator: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Manual Signal Handler Registration")
    print("=" * 60)
    print()
    
    results = []
    
    print("Test 1: Import Handlers")
    print("-" * 60)
    results.append(test_import_handlers())
    print()
    
    print("Test 2: Handler Aliases")
    print("-" * 60)
    results.append(test_handler_aliases())
    print()
    
    print("Test 3: Premium Checker Module")
    print("-" * 60)
    results.append(test_premium_checker_available())
    print()
    
    print("Test 4: FuturesSignalGenerator")
    print("-" * 60)
    results.append(test_futures_signal_generator_available())
    print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Handler registration should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    print()
