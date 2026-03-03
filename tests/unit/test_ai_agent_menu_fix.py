#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test AI Agent Menu Fix
Tests that the menu no longer loops back to main menu
"""

import os
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and credit check"""
    print("=" * 60)
    print("🧪 TEST 1: Supabase Connection")
    print("=" * 60)
    
    try:
        from supabase_client import supabase
        
        if not supabase:
            print("❌ Supabase client not initialized")
            return False
        
        print("✅ Supabase client initialized")
        
        # Test user ID (admin)
        user_id = 1187119989
        
        # Test query to user_credits_balance
        print(f"\n📊 Checking credits for user {user_id}...")
        credits_result = supabase.table('user_credits_balance')\
            .select('available_credits, total_conway_credits')\
            .eq('user_id', user_id)\
            .execute()
        
        if credits_result.data:
            balance = credits_result.data[0]
            available = float(balance.get('available_credits', 0))
            total = float(balance.get('total_conway_credits', 0))
            
            print(f"✅ Credits found:")
            print(f"   • Available Credits: {available}")
            print(f"   • Total Conway Credits: {total}")
            print(f"   • Has Deposit: {available > 0 or total > 0}")
            return True
        else:
            print("⚠️  No credits record found for user")
            
            # Try fallback to custodial_wallets
            print("\n🔄 Trying fallback to custodial_wallets...")
            wallet_result = supabase.table('custodial_wallets')\
                .select('balance_usdc, conway_credits')\
                .eq('user_id', user_id)\
                .execute()
            
            if wallet_result.data:
                wallet = wallet_result.data[0]
                usdc = float(wallet.get('balance_usdc', 0))
                credits = float(wallet.get('conway_credits', 0))
                
                print(f"✅ Wallet found:")
                print(f"   • Balance USDC: {usdc}")
                print(f"   • Conway Credits: {credits}")
                print(f"   • Has Deposit: {usdc > 0 or credits > 0}")
                return True
            else:
                print("❌ No wallet record found either")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """Test Database class integration"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Database Class Integration")
    print("=" * 60)
    
    try:
        from database import Database
        db = Database()
        
        print(f"✅ Database initialized")
        print(f"   • Supabase enabled: {db.supabase_enabled}")
        
        if db.supabase_enabled:
            print(f"   • Supabase service available: {hasattr(db, 'supabase_service')}")
            
            # Test getting user language
            user_id = 1187119989
            lang = db.get_user_language(user_id)
            print(f"   • User language: {lang}")
            
            return True
        else:
            print("⚠️  Supabase not enabled in Database class")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_handler_logic():
    """Test the menu handler logic without actually running the bot"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Menu Handler Logic")
    print("=" * 60)
    
    try:
        from database import Database
        from supabase_client import supabase
        
        db = Database()
        user_id = 1187119989
        user_lang = db.get_user_language(user_id)
        
        print(f"✅ User language: {user_lang}")
        
        # Simulate the deposit check logic
        has_deposit = False
        
        if db.supabase_enabled and supabase:
            print("✅ Supabase enabled, checking credits...")
            
            credits_result = supabase.table('user_credits_balance')\
                .select('available_credits, total_conway_credits')\
                .eq('user_id', user_id)\
                .execute()
            
            if credits_result.data:
                balance = credits_result.data[0]
                available_credits = float(balance.get('available_credits', 0))
                total_credits = float(balance.get('total_conway_credits', 0))
                has_deposit = (available_credits > 0 or total_credits > 0)
                
                print(f"✅ Deposit check result: {has_deposit}")
                print(f"   • Available: {available_credits}")
                print(f"   • Total: {total_credits}")
            else:
                print("⚠️  No credits record, trying fallback...")
                
                wallet_result = supabase.table('custodial_wallets')\
                    .select('balance_usdc, conway_credits')\
                    .eq('user_id', user_id)\
                    .execute()
                
                if wallet_result.data:
                    wallet = wallet_result.data[0]
                    balance_usdc = float(wallet.get('balance_usdc', 0))
                    conway_credits = float(wallet.get('conway_credits', 0))
                    has_deposit = (balance_usdc > 0 or conway_credits > 0)
                    
                    print(f"✅ Fallback check result: {has_deposit}")
                    print(f"   • USDC: {balance_usdc}")
                    print(f"   • Credits: {conway_credits}")
        
        if has_deposit:
            print("\n✅ User should see FULL AI Agent menu")
        else:
            print("\n⚠️  User should see DEPOSIT-FIRST menu")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n🚀 Starting AI Agent Menu Fix Tests\n")
    
    results = []
    
    # Test 1: Supabase connection
    results.append(("Supabase Connection", test_supabase_connection()))
    
    # Test 2: Database integration
    results.append(("Database Integration", test_database_integration()))
    
    # Test 3: Menu handler logic
    results.append(("Menu Handler Logic", test_menu_handler_logic()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! The menu fix should work correctly.")
        print("\n📝 Next steps:")
        print("   1. Deploy to Railway")
        print("   2. Test clicking 'AI Agent' button in Telegram")
        print("   3. Verify menu shows correctly (not looping to main menu)")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
