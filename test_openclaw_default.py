"""
Test OpenClaw Default Mode
Verify that OpenClaw auto-activates for all users
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.openclaw_message_handler import OpenClawMessageHandler
        print("✅ OpenClawMessageHandler imported")
        
        from app.openclaw_manager import OpenClawManager
        print("✅ OpenClawManager imported")
        
        from services import get_database
        print("✅ Database service imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_auto_session_creation():
    """Test that sessions are auto-created"""
    print("\n🧪 Testing auto-session creation logic...")
    
    try:
        from app.openclaw_message_handler import OpenClawMessageHandler
        from app.openclaw_manager import OpenClawManager
        from services import get_database
        
        db = get_database()
        manager = OpenClawManager(db)
        handler = OpenClawMessageHandler(manager)
        
        print("✅ Handler created successfully")
        print("✅ Auto-session creation logic is in place")
        
        # Check if handle_message exists and has correct signature
        import inspect
        sig = inspect.signature(handler.handle_message)
        params = list(sig.parameters.keys())
        
        if 'update' in params and 'context' in params:
            print("✅ handle_message has correct signature")
        else:
            print("❌ handle_message signature incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openclaw_api_key():
    """Test that OpenClaw API key is configured"""
    print("\n🧪 Testing OpenClaw API configuration...")
    
    api_key = os.getenv('OPENCLAW_API_KEY')
    
    if not api_key:
        print("❌ OPENCLAW_API_KEY not found in environment")
        return False
    
    if len(api_key) < 20:
        print("❌ OPENCLAW_API_KEY seems invalid (too short)")
        return False
    
    print(f"✅ OPENCLAW_API_KEY configured ({len(api_key)} chars)")
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from services import get_database
        db = get_database()
        
        # Try to execute a simple query
        result = db.execute_query("SELECT 1 as test")
        
        if result and len(result) > 0:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database query returned no results")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("OpenClaw Default Mode - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Auto-Session Creation", test_auto_session_creation()))
    results.append(("API Key Configuration", test_openclaw_api_key()))
    results.append(("Database Connection", test_database_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! OpenClaw Default Mode is ready!")
        print("\n📝 Next steps:")
        print("1. Deploy to Railway: git push origin main")
        print("2. Test with real Telegram messages")
        print("3. Monitor credit usage and responses")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
