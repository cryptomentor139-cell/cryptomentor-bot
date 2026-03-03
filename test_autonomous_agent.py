"""
Test Autonomous Agent Components
Run this to verify all components are working
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("\n🧪 Testing Imports...")
    print("-" * 60)
    
    try:
        from app.openclaw_agent_tools import OpenClawAgentTools, get_openclaw_agent_tools
        print("✅ openclaw_agent_tools imported successfully")
    except Exception as e:
        print(f"❌ Failed to import openclaw_agent_tools: {e}")
        return False
    
    try:
        from app.openclaw_agent_loop import OpenClawAgenticLoop, get_openclaw_agentic_loop
        print("✅ openclaw_agent_loop imported successfully")
    except Exception as e:
        print(f"❌ Failed to import openclaw_agent_loop: {e}")
        return False
    
    try:
        from app.openclaw_manager import OpenClawManager, get_openclaw_manager
        print("✅ openclaw_manager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import openclaw_manager: {e}")
        return False
    
    return True

def test_tool_registry():
    """Test tool registry"""
    print("\n🧪 Testing Tool Registry...")
    print("-" * 60)
    
    try:
        from app.openclaw_agent_tools import OpenClawAgentTools
        
        # Create mock db
        class MockDB:
            def __init__(self):
                self.conn = None
                self.cursor = None
        
        db = MockDB()
        tools = OpenClawAgentTools(db)
        
        # Check tools registered
        tool_count = len(tools.tools)
        print(f"✅ {tool_count} tools registered:")
        
        for tool_name in tools.tools.keys():
            print(f"   - {tool_name}")
        
        # Test schema generation
        schema = tools.get_tools_schema()
        print(f"\n✅ Generated schema for {len(schema)} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agentic_loop():
    """Test agentic loop initialization"""
    print("\n🧪 Testing Agentic Loop...")
    print("-" * 60)
    
    try:
        from app.openclaw_agent_loop import OpenClawAgenticLoop
        from app.openclaw_agent_tools import OpenClawAgentTools
        
        # Create mocks
        class MockDB:
            def __init__(self):
                self.conn = None
                self.cursor = None
        
        class MockManager:
            def __init__(self):
                self.api_key = "test_key"
                self.base_url = "https://test.com"
                self.MODEL = "test-model"
            
            def _is_admin(self, user_id):
                return True
        
        db = MockDB()
        manager = MockManager()
        tools = OpenClawAgentTools(db)
        
        # Create agentic loop
        loop = OpenClawAgenticLoop(manager, tools)
        
        print(f"✅ Agentic loop initialized")
        print(f"   - Max iterations: {loop.MAX_ITERATIONS}")
        print(f"   - Model: {loop.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agentic loop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_execution():
    """Test tool execution (mock)"""
    print("\n🧪 Testing Tool Execution...")
    print("-" * 60)
    
    try:
        from app.openclaw_agent_tools import OpenClawAgentTools
        
        # Create mock db
        class MockDB:
            def __init__(self):
                self.conn = None
                self.cursor = None
        
        db = MockDB()
        tools = OpenClawAgentTools(db)
        
        # Test get_current_prices (doesn't need db)
        result = tools.execute_tool("get_current_prices", {})
        
        if result['success']:
            print("✅ Tool execution successful")
            print(f"   Result: {result['result']}")
        else:
            print(f"❌ Tool execution failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_files():
    """Check if all required files exist"""
    print("\n🧪 Checking Files...")
    print("-" * 60)
    
    required_files = [
        'app/openclaw_agent_tools.py',
        'app/openclaw_agent_loop.py',
        'app/openclaw_manager.py',
        'FULL_AGENT_READY.md',
        'FULL_AGENT_IMPLEMENTATION_PLAN.md',
        'AUTONOMOUS_AGENT_SUMMARY.md',
        'activate_full_agent.py'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    print("\n" + "="*60)
    print("🤖 AUTONOMOUS AGENT - COMPONENT TEST")
    print("="*60)
    
    # Run tests
    tests = [
        ("File Check", check_files),
        ("Import Test", test_imports),
        ("Tool Registry", test_tool_registry),
        ("Agentic Loop", test_agentic_loop),
        ("Tool Execution", test_tool_execution),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Agent is ready for integration.")
        print("\nNext steps:")
        print("1. Run: python activate_full_agent.py")
        print("2. Follow integration steps")
        print("3. Test with admin account")
        print("4. Deploy to Railway")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
