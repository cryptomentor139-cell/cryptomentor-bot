"""
Test Task 5.4: Command Aliases
Test that /signal and /signals work identically to /analyze and /futures_signals
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.handlers_manual_signals import (
    cmd_analyze, cmd_futures_signals,
    cmd_signal, cmd_signals
)


def test_signal_alias():
    """Test that /signal is an alias for /analyze"""
    print("\n" + "="*60)
    print("TEST: /signal alias verification")
    print("="*60)
    
    # Check that cmd_signal points to cmd_analyze
    if cmd_signal is cmd_analyze:
        print("✅ PASS: cmd_signal is correctly aliased to cmd_analyze")
        print(f"   cmd_signal function: {cmd_signal.__name__}")
        print(f"   cmd_analyze function: {cmd_analyze.__name__}")
        return True
    else:
        print("❌ FAIL: cmd_signal is NOT aliased to cmd_analyze")
        print(f"   cmd_signal: {cmd_signal}")
        print(f"   cmd_analyze: {cmd_analyze}")
        return False


def test_signals_alias():
    """Test that /signals is an alias for /futures_signals"""
    print("\n" + "="*60)
    print("TEST: /signals alias verification")
    print("="*60)
    
    # Check that cmd_signals points to cmd_futures_signals
    if cmd_signals is cmd_futures_signals:
        print("✅ PASS: cmd_signals is correctly aliased to cmd_futures_signals")
        print(f"   cmd_signals function: {cmd_signals.__name__}")
        print(f"   cmd_futures_signals function: {cmd_futures_signals.__name__}")
        return True
    else:
        print("❌ FAIL: cmd_signals is NOT aliased to cmd_futures_signals")
        print(f"   cmd_signals: {cmd_signals}")
        print(f"   cmd_futures_signals: {cmd_futures_signals}")
        return False


def test_alias_registration_in_bot():
    """Test that aliases are registered in bot.py"""
    print("\n" + "="*60)
    print("TEST: Alias registration in bot.py")
    print("="*60)
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        checks = []
        
        # Check if cmd_signal is imported
        if 'cmd_signal' in bot_content:
            print("✅ cmd_signal imported in bot.py")
            checks.append(True)
        else:
            print("❌ cmd_signal NOT imported in bot.py")
            checks.append(False)
        
        # Check if cmd_signals is imported
        if 'cmd_signals' in bot_content:
            print("✅ cmd_signals imported in bot.py")
            checks.append(True)
        else:
            print("❌ cmd_signals NOT imported in bot.py")
            checks.append(False)
        
        # Check if /signal command is registered
        if 'CommandHandler("signal", cmd_signal)' in bot_content:
            print("✅ /signal command registered in bot.py")
            checks.append(True)
        else:
            print("❌ /signal command NOT registered in bot.py")
            checks.append(False)
        
        # Check if /signals command is registered
        if 'CommandHandler("signals", cmd_signals)' in bot_content:
            print("✅ /signals command registered in bot.py")
            checks.append(True)
        else:
            print("❌ /signals command NOT registered in bot.py")
            checks.append(False)
        
        return all(checks)
        
    except Exception as e:
        print(f"❌ Error reading bot.py: {e}")
        return False


def test_alias_docstrings():
    """Test that aliases have proper documentation"""
    print("\n" + "="*60)
    print("TEST: Alias documentation")
    print("="*60)
    
    checks = []
    
    # Check cmd_analyze docstring (which cmd_signal inherits)
    if cmd_analyze.__doc__:
        print("✅ cmd_analyze has docstring:")
        print(f"   {cmd_analyze.__doc__.strip()[:80]}...")
        checks.append(True)
    else:
        print("❌ cmd_analyze missing docstring")
        checks.append(False)
    
    # Check cmd_futures_signals docstring (which cmd_signals inherits)
    if cmd_futures_signals.__doc__:
        print("✅ cmd_futures_signals has docstring:")
        print(f"   {cmd_futures_signals.__doc__.strip()[:80]}...")
        checks.append(True)
    else:
        print("❌ cmd_futures_signals missing docstring")
        checks.append(False)
    
    return all(checks)


def test_alias_behavior_equivalence():
    """Test that aliases have identical behavior to original commands"""
    print("\n" + "="*60)
    print("TEST: Alias behavior equivalence")
    print("="*60)
    
    checks = []
    
    # Test 1: cmd_signal should have same attributes as cmd_analyze
    print("\n1. Checking cmd_signal attributes:")
    if hasattr(cmd_signal, '__name__') and hasattr(cmd_analyze, '__name__'):
        if cmd_signal.__name__ == cmd_analyze.__name__:
            print(f"   ✅ Both have same __name__: {cmd_signal.__name__}")
            checks.append(True)
        else:
            print(f"   ❌ Different __name__: {cmd_signal.__name__} vs {cmd_analyze.__name__}")
            checks.append(False)
    
    # Test 2: cmd_signals should have same attributes as cmd_futures_signals
    print("\n2. Checking cmd_signals attributes:")
    if hasattr(cmd_signals, '__name__') and hasattr(cmd_futures_signals, '__name__'):
        if cmd_signals.__name__ == cmd_futures_signals.__name__:
            print(f"   ✅ Both have same __name__: {cmd_signals.__name__}")
            checks.append(True)
        else:
            print(f"   ❌ Different __name__: {cmd_signals.__name__} vs {cmd_futures_signals.__name__}")
            checks.append(False)
    
    # Test 3: Check that they're callable
    print("\n3. Checking if aliases are callable:")
    if callable(cmd_signal):
        print("   ✅ cmd_signal is callable")
        checks.append(True)
    else:
        print("   ❌ cmd_signal is NOT callable")
        checks.append(False)
    
    if callable(cmd_signals):
        print("   ✅ cmd_signals is callable")
        checks.append(True)
    else:
        print("   ❌ cmd_signals is NOT callable")
        checks.append(False)
    
    return all(checks)


def test_handlers_file_structure():
    """Test that handlers_manual_signals.py has correct structure"""
    print("\n" + "="*60)
    print("TEST: handlers_manual_signals.py structure")
    print("="*60)
    
    try:
        with open('app/handlers_manual_signals.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        
        # Check for alias definitions
        if 'cmd_signal = cmd_analyze' in content:
            print("✅ cmd_signal alias defined correctly")
            checks.append(True)
        else:
            print("❌ cmd_signal alias NOT defined correctly")
            checks.append(False)
        
        if 'cmd_signals = cmd_futures_signals' in content:
            print("✅ cmd_signals alias defined correctly")
            checks.append(True)
        else:
            print("❌ cmd_signals alias NOT defined correctly")
            checks.append(False)
        
        # Check for comments explaining aliases
        if '# /signal is alias for /analyze' in content or 'alias for /analyze' in content:
            print("✅ cmd_signal alias has explanatory comment")
            checks.append(True)
        else:
            print("⚠️  cmd_signal alias missing explanatory comment")
            checks.append(True)  # Not critical
        
        if '# /signals is alias for /futures_signals' in content or 'alias for /futures_signals' in content:
            print("✅ cmd_signals alias has explanatory comment")
            checks.append(True)
        else:
            print("⚠️  cmd_signals alias missing explanatory comment")
            checks.append(True)  # Not critical
        
        return all(checks)
        
    except Exception as e:
        print(f"❌ Error reading handlers_manual_signals.py: {e}")
        return False


def run_all_tests():
    """Run all alias tests"""
    print("\n" + "="*70)
    print("TASK 5.4: COMMAND ALIASES TEST SUITE")
    print("="*70)
    print("\nTesting that /signal and /signals work identically to their base commands")
    print("Expected: Aliases should be direct references to original functions")
    
    results = []
    
    # Run all tests
    results.append(("Signal alias verification", test_signal_alias()))
    results.append(("Signals alias verification", test_signals_alias()))
    results.append(("Alias registration in bot.py", test_alias_registration_in_bot()))
    results.append(("Alias documentation", test_alias_docstrings()))
    results.append(("Alias behavior equivalence", test_alias_behavior_equivalence()))
    results.append(("Handlers file structure", test_handlers_file_structure()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nVerification complete:")
        print("✅ /signal is correctly aliased to /analyze")
        print("✅ /signals is correctly aliased to /futures_signals")
        print("✅ Both aliases registered in bot.py")
        print("✅ Aliases will work identically to original commands")
        print("\nTask 5.4 Status: ✅ COMPLETE")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the failures above and fix the issues.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
