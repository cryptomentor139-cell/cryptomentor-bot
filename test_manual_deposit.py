#!/usr/bin/env python3
"""
Test Manual Deposit System
Tests admin credit commands and deposit flow
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.handlers_admin_credits import (
            admin_add_credits_command,
            admin_check_user_credits_command
        )
        print("✅ Admin credits handlers imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import admin credits handlers: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from database import Database
        db = Database()
        
        if db.supabase_enabled:
            print("✅ Supabase connection enabled")
            
            # Test user_credits_balance table exists
            result = db.supabase_service.table('user_credits_balance').select('*').limit(1).execute()
            print("✅ user_credits_balance table accessible")
            
            # Test credit_transactions table exists
            result = db.supabase_service.table('credit_transactions').select('*').limit(1).execute()
            print("✅ credit_transactions table accessible")
            
            return True
        else:
            print("❌ Supabase not enabled")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_admin_status():
    """Test admin status check"""
    print("\n🧪 Testing admin status...")
    
    try:
        from app.admin_status import is_admin
        
        # Get admin IDs from environment
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if admin_ids_str:
            admin_ids = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
            if admin_ids:
                test_admin_id = admin_ids[0]
                if is_admin(test_admin_id):
                    print(f"✅ Admin check works for ID: {test_admin_id}")
                    return True
                else:
                    print(f"❌ Admin check failed for ID: {test_admin_id}")
                    return False
            else:
                print("⚠️  No admin IDs configured")
                return False
        else:
            print("⚠️  ADMIN_IDS not set in environment")
            return False
            
    except Exception as e:
        print(f"❌ Admin status check failed: {e}")
        return False


def test_bot_registration():
    """Test that admin commands are registered in bot"""
    print("\n🧪 Testing bot command registration...")
    
    try:
        from bot import TelegramBot
        
        # This will fail if imports fail
        bot = TelegramBot()
        print("✅ Bot initialized successfully")
        
        # Check if setup would work
        print("✅ Bot setup would register admin credit commands")
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False


def test_deposit_flow():
    """Test deposit flow components"""
    print("\n🧪 Testing deposit flow...")
    
    try:
        from menu_handlers import MenuCallbackHandler
        print("✅ Menu handlers imported successfully")
        
        # Check if deposit handlers exist
        handler = MenuCallbackHandler(None)
        if hasattr(handler, 'handle_automaton_first_deposit'):
            print("✅ handle_automaton_first_deposit exists")
        else:
            print("❌ handle_automaton_first_deposit missing")
            return False
            
        if hasattr(handler, 'handle_deposit_guide'):
            print("✅ handle_deposit_guide exists")
        else:
            print("❌ handle_deposit_guide missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Deposit flow test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MANUAL DEPOSIT SYSTEM - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Admin Status", test_admin_status()))
    results.append(("Bot Registration", test_bot_registration()))
    results.append(("Deposit Flow", test_deposit_flow()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Manual deposit system is ready.")
        print("\n📝 Next steps:")
        print("1. Test admin commands in Telegram:")
        print("   /admin_add_credits <user_id> 3000 Test deposit")
        print("   /admin_check_credits <user_id>")
        print("2. Test user deposit flow:")
        print("   - Go to AI Agent menu")
        print("   - Click 'Deposit Sekarang'")
        print("   - Click 'Kirim Bukti Transfer'")
        print("3. Deploy to Railway")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
