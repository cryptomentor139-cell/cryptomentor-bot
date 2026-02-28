#!/usr/bin/env python3
"""
Test script to verify deposit button callback routing
"""

import re

def test_callback_patterns():
    """Test if automaton_first_deposit matches the correct pattern"""
    
    callback_data = "automaton_first_deposit"
    
    # Test admin pattern (should NOT match)
    admin_pattern = r'^admin_'
    admin_match = bool(re.match(admin_pattern, callback_data))
    print(f"Admin pattern (^admin_): {admin_match} (should be False)")
    
    # Test signal pattern (should NOT match)
    signal_pattern = r'^signal_tf_'
    signal_match = bool(re.match(signal_pattern, callback_data))
    print(f"Signal pattern (^signal_tf_): {signal_match} (should be False)")
    
    # Test spawn pattern (should NOT match)
    spawn_pattern = r'^spawn_(noparent|parent)_'
    spawn_match = bool(re.match(spawn_pattern, callback_data))
    print(f"Spawn pattern (^spawn_(noparent|parent)_): {spawn_match} (should be False)")
    
    # Test menu pattern (should MATCH)
    menu_pattern = r'^(?!admin_|signal_tf_|spawn_).*'
    menu_match = bool(re.match(menu_pattern, callback_data))
    print(f"Menu pattern (^(?!admin_|signal_tf_|spawn_).*): {menu_match} (should be True)")
    
    print("\n" + "="*60)
    if not admin_match and not signal_match and not spawn_match and menu_match:
        print("✅ PASS: automaton_first_deposit will be handled by menu handler")
        return True
    else:
        print("❌ FAIL: Pattern matching issue detected!")
        return False

def test_handler_exists():
    """Test if the handler function exists"""
    try:
        from menu_handlers import MenuCallbackHandler
        handler = MenuCallbackHandler(None)
        
        if hasattr(handler, 'handle_automaton_first_deposit'):
            print("✅ handle_automaton_first_deposit method exists")
            return True
        else:
            print("❌ handle_automaton_first_deposit method NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ Error importing handler: {e}")
        return False

def test_callback_routing():
    """Test if callback is properly routed in handle_callback_query"""
    try:
        with open('menu_handlers.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if automaton_first_deposit is in the routing
        if 'elif callback_data == "automaton_first_deposit":' in content:
            print("✅ automaton_first_deposit routing found in handle_callback_query")
            
            # Check if it calls the correct handler
            if 'await self.handle_automaton_first_deposit(query, context)' in content:
                print("✅ Correct handler method is called")
                return True
            else:
                print("❌ Handler method call NOT FOUND")
                return False
        else:
            print("❌ automaton_first_deposit routing NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("DEPOSIT BUTTON CALLBACK TEST")
    print("="*60)
    print()
    
    print("Test 1: Pattern Matching")
    print("-"*60)
    test1 = test_callback_patterns()
    print()
    
    print("Test 2: Handler Method Exists")
    print("-"*60)
    test2 = test_handler_exists()
    print()
    
    print("Test 3: Callback Routing")
    print("-"*60)
    test3 = test_callback_routing()
    print()
    
    print("="*60)
    print("FINAL RESULT")
    print("="*60)
    if test1 and test2 and test3:
        print("✅ ALL TESTS PASSED - Button should work correctly")
        print("\nIf button still not responding, check:")
        print("1. Railway deployment logs for errors")
        print("2. Database connection issues")
        print("3. Telegram API rate limits")
    else:
        print("❌ SOME TESTS FAILED - Issues detected")
        if not test1:
            print("  - Pattern matching issue")
        if not test2:
            print("  - Handler method missing")
        if not test3:
            print("  - Routing configuration issue")
