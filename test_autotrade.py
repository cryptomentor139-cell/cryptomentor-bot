#!/usr/bin/env python3
"""
Test AutoTrade Handler
Quick test to verify autotrade functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_autotrade_import():
    """Test if autotrade handler can be imported"""
    try:
        from app.handlers_autotrade import register_autotrade_handlers
        print("✅ AutoTrade handler imported successfully")
        return True
    except Exception as e:
        print(f"❌ AutoTrade import failed: {e}")
        return False

def test_autotrade_database():
    """Test autotrade database initialization"""
    try:
        from app.handlers_autotrade import init_autotrade_db, save_autotrade_user, get_autotrade_user
        
        # Initialize database
        init_autotrade_db()
        print("✅ AutoTrade database initialized")
        
        # Test user operations
        test_user_id = 123456789
        save_autotrade_user(test_user_id, 100.0, "0x1234567890abcdef")
        user_data = get_autotrade_user(test_user_id)
        
        if user_data:
            print(f"✅ User data saved and retrieved: {user_data[1]} with ${user_data[3]} deposit")
        else:
            print("❌ User data not found")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_profit_simulation():
    """Test profit simulation function"""
    try:
        from app.handlers_autotrade import simulate_trading_profit
        
        profit_data = simulate_trading_profit(100.0, 30)  # $100 for 30 days
        
        print(f"✅ Profit simulation working:")
        print(f"   Initial: $100.00")
        print(f"   Current: ${profit_data['current_balance']:.2f}")
        print(f"   Profit: ${profit_data['profit']:.2f} ({profit_data['profit_percentage']:+.2f}%)")
        
        return True
    except Exception as e:
        print(f"❌ Profit simulation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AutoTrade System...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_autotrade_import),
        ("Database Test", test_autotrade_database),
        ("Profit Simulation Test", test_profit_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed!")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! AutoTrade system is ready.")
        print("\n🚀 Next steps:")
        print("1. Restart your bot")
        print("2. Use /autotrade command")
        print("3. Start earning with AI trading!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)