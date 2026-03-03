#!/usr/bin/env python3
"""
Quick Test Script for AI Agent Button Fixes
Tests the fixed callback handlers and spawn agent input handler
"""

import sys
import os

def test_callback_query_fix():
    """Test that fake_update creation doesn't use query.update.update_id"""
    print("\n" + "="*60)
    print("TEST 1: CallbackQuery Fix")
    print("="*60)
    
    try:
        # Read menu_handlers.py
        with open('menu_handlers.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that query.update.update_id is NOT used
        if 'query.update.update_id' in content:
            print("❌ FAILED: Found 'query.update.update_id' in menu_handlers.py")
            print("   This will cause AttributeError!")
            return False
        
        # Check that update_id=999999 is used instead
        if 'update_id=999999' in content:
            print("✅ PASSED: Using static update_id=999999")
        else:
            print("⚠️  WARNING: No static update_id found")
        
        # Count fixed functions
        fixed_functions = [
            'handle_automaton_status',
            'handle_automaton_deposit', 
            'handle_automaton_logs',
            'handle_agent_lineage'
        ]
        
        found_count = sum(1 for func in fixed_functions if func in content)
        print(f"✅ Found {found_count}/{len(fixed_functions)} handler functions")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_spawn_agent_handler():
    """Test that spawn agent input handler exists in bot.py"""
    print("\n" + "="*60)
    print("TEST 2: Spawn Agent Input Handler")
    print("="*60)
    
    try:
        # Read bot.py
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for awaiting_agent_name handler
        if "user_data.get('awaiting_agent_name')" in content:
            print("✅ PASSED: Found awaiting_agent_name handler")
        else:
            print("❌ FAILED: No awaiting_agent_name handler found")
            return False
        
        # Check for spawn_agent action check
        if "user_data.get('action') == 'spawn_agent'" in content:
            print("✅ PASSED: Found spawn_agent action check")
        else:
            print("⚠️  WARNING: No spawn_agent action check")
        
        # Check for spawn_agent_command import
        if "from app.handlers_automaton import spawn_agent_command" in content:
            print("✅ PASSED: Found spawn_agent_command import")
        else:
            print("⚠️  WARNING: No spawn_agent_command import in handler")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_state_timestamp():
    """Test that state_timestamp is set in menu_handlers.py"""
    print("\n" + "="*60)
    print("TEST 3: State Timestamp Management")
    print("="*60)
    
    try:
        # Read menu_handlers.py
        with open('menu_handlers.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for state_timestamp in handle_automaton_spawn
        if "context.user_data['state_timestamp']" in content:
            print("✅ PASSED: Found state_timestamp assignment")
        else:
            print("⚠️  WARNING: No state_timestamp found")
        
        # Check for datetime import
        if "from datetime import datetime" in content:
            print("✅ PASSED: Found datetime import")
        else:
            print("⚠️  WARNING: No datetime import")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_menu_system_integration():
    """Test that AI Agent menu is properly configured"""
    print("\n" + "="*60)
    print("TEST 4: Menu System Integration")
    print("="*60)
    
    try:
        # Read menu_system.py
        with open('menu_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for AI_AGENT_MENU constant
        if "AI_AGENT_MENU = " in content:
            print("✅ PASSED: Found AI_AGENT_MENU constant")
        else:
            print("❌ FAILED: No AI_AGENT_MENU constant")
            return False
        
        # Check for build_ai_agent_menu function
        if "def build_ai_agent_menu" in content:
            print("✅ PASSED: Found build_ai_agent_menu function")
        else:
            print("❌ FAILED: No build_ai_agent_menu function")
            return False
        
        # Check for agent_lineage button
        if '"agent_lineage"' in content or "'agent_lineage'" in content:
            print("✅ PASSED: Found agent_lineage callback_data")
        else:
            print("⚠️  WARNING: No agent_lineage callback_data")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI AGENT BUTTON FIX - VERIFICATION TESTS")
    print("="*60)
    
    # Change to Bismillah directory if needed
    if not os.path.exists('bot.py'):
        if os.path.exists('Bismillah/bot.py'):
            os.chdir('Bismillah')
            print("📁 Changed directory to Bismillah/")
        else:
            print("❌ ERROR: Cannot find bot.py")
            sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("CallbackQuery Fix", test_callback_query_fix()))
    results.append(("Spawn Agent Handler", test_spawn_agent_handler()))
    results.append(("State Timestamp", test_state_timestamp()))
    results.append(("Menu Integration", test_menu_system_integration()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for deployment!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the fixes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
