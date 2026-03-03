#!/usr/bin/env python3
"""
Test Autonomous Agent Integration
Verify that all components are properly integrated
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.openclaw_agent_tools import get_openclaw_agent_tools, OpenClawAgentTools
        print("  ✅ openclaw_agent_tools")
    except Exception as e:
        print(f"  ❌ openclaw_agent_tools: {e}")
        return False
    
    try:
        from app.openclaw_agent_loop import get_openclaw_agentic_loop, OpenClawAgenticLoop
        print("  ✅ openclaw_agent_loop")
    except Exception as e:
        print(f"  ❌ openclaw_agent_loop: {e}")
        return False
    
    try:
        from app.openclaw_manager import get_openclaw_manager
        print("  ✅ openclaw_manager")
    except Exception as e:
        print(f"  ❌ openclaw_manager: {e}")
        return False
    
    try:
        from app.openclaw_message_handler import get_openclaw_message_handler
        print("  ✅ openclaw_message_handler")
    except Exception as e:
        print(f"  ❌ openclaw_message_handler: {e}")
        return False
    
    return True

def test_tool_registry():
    """Test that tools are properly registered"""
    print("\n🧪 Testing tool registry...")
    
    try:
        from app.openclaw_agent_tools import OpenClawAgentTools
        from services import get_database
        
        db = get_database()
        tools = OpenClawAgentTools(db, None)
        
        # Check tool count
        tool_count = len(tools.tools)
        print(f"  ✅ {tool_count} tools registered")
        
        # Check specific tools
        expected_tools = [
            'get_bot_stats',
            'get_current_prices',
            'update_price',
            'broadcast_message',
            'generate_deposit_wallet',
            'get_user_info',
            'add_credits',
            'execute_sql_query',
            'get_system_info'
        ]
        
        for tool_name in expected_tools:
            if tool_name in tools.tools:
                print(f"  ✅ {tool_name}")
            else:
                print(f"  ❌ {tool_name} - NOT FOUND")
                return False
        
        # Test schema generation
        schema = tools.get_tools_schema()
        print(f"  ✅ Schema generated ({len(schema)} tools)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_agentic_loop():
    """Test that agentic loop can be initialized"""
    print("\n🧪 Testing agentic loop...")
    
    try:
        from app.openclaw_agent_tools import get_openclaw_agent_tools
        from app.openclaw_agent_loop import get_openclaw_agentic_loop
        from app.openclaw_manager import get_openclaw_manager
        from services import get_database
        
        db = get_database()
        manager = get_openclaw_manager(db)
        tools = get_openclaw_agent_tools(db, None)
        loop = get_openclaw_agentic_loop(manager, tools)
        
        print(f"  ✅ Agentic loop initialized")
        print(f"  ✅ Max iterations: {loop.MAX_ITERATIONS}")
        print(f"  ✅ Model: {loop.model}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_message_handler():
    """Test that message handler can use agentic loop"""
    print("\n🧪 Testing message handler integration...")
    
    try:
        from app.openclaw_agent_tools import get_openclaw_agent_tools
        from app.openclaw_agent_loop import get_openclaw_agentic_loop
        from app.openclaw_manager import get_openclaw_manager
        from app.openclaw_message_handler import get_openclaw_message_handler
        from services import get_database
        
        db = get_database()
        manager = get_openclaw_manager(db)
        tools = get_openclaw_agent_tools(db, None)
        loop = get_openclaw_agentic_loop(manager, tools)
        handler = get_openclaw_message_handler(manager)
        
        # Inject agentic loop
        handler.agentic_loop = loop
        
        print(f"  ✅ Message handler initialized")
        print(f"  ✅ Agentic loop injected")
        print(f"  ✅ Has agentic_loop: {hasattr(handler, 'agentic_loop')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_bot_integration():
    """Test that bot.py has the integration code"""
    print("\n🧪 Testing bot.py integration...")
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_code = f.read()
        
        # Check for required imports
        if 'from app.openclaw_agent_tools import get_openclaw_agent_tools' in bot_code:
            print("  ✅ agent_tools import found")
        else:
            print("  ❌ agent_tools import NOT FOUND")
            return False
        
        if 'from app.openclaw_agent_loop import get_openclaw_agentic_loop' in bot_code:
            print("  ✅ agentic_loop import found")
        else:
            print("  ❌ agentic_loop import NOT FOUND")
            return False
        
        # Check for initialization
        if 'agent_tools = get_openclaw_agent_tools' in bot_code:
            print("  ✅ agent_tools initialization found")
        else:
            print("  ❌ agent_tools initialization NOT FOUND")
            return False
        
        if 'agentic_loop = get_openclaw_agentic_loop' in bot_code:
            print("  ✅ agentic_loop initialization found")
        else:
            print("  ❌ agentic_loop initialization NOT FOUND")
            return False
        
        # Check for injection
        if 'openclaw_handler.agentic_loop = agentic_loop' in bot_code:
            print("  ✅ agentic_loop injection found")
        else:
            print("  ❌ agentic_loop injection NOT FOUND")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🤖 AUTONOMOUS AGENT INTEGRATION TEST")
    print("=" * 60)
    
    # Change to Bismillah directory if needed
    if os.path.exists('Bismillah'):
        os.chdir('Bismillah')
        print("📁 Changed to Bismillah directory\n")
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Tool Registry", test_tool_registry),
        ("Agentic Loop", test_agentic_loop),
        ("Message Handler", test_message_handler),
        ("Bot Integration", test_bot_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Ready for deployment!")
        print("\nNext steps:")
        print("1. Commit changes: git add . && git commit -m 'Activate autonomous agent'")
        print("2. Push to GitHub: git push")
        print("3. Deploy to Railway: railway up")
        print("4. Test with admin account: /openclaw_start")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Fix issues before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
