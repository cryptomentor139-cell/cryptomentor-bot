#!/usr/bin/env python3
"""
Verify production test user: 1187119989
Check lifetime premium status and prepare for testing
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.supabase_conn import get_supabase_client

def verify_test_user():
    """Verify user 1187119989 is lifetime premium"""
    try:
        supabase = get_supabase_client()
        
        user_id = 1187119989
        
        result = supabase.table("users").select(
            "telegram_id, username, is_premium, premium_until, credits"
        ).eq(
            "telegram_id", user_id
        ).execute()
        
        if result.data:
            user = result.data[0]
            print("\n" + "="*60)
            print("TEST USER VERIFICATION")
            print("="*60)
            print(f"\n✅ User Found:")
            print(f"  User ID: {user['telegram_id']}")
            print(f"  Username: @{user.get('username', 'N/A')}")
            print(f"  Is Premium: {user['is_premium']}")
            print(f"  Premium Until: {user['premium_until']}")
            print(f"  Credits: {user.get('credits', 0)}")
            
            is_lifetime = user['is_premium'] and user['premium_until'] is None
            
            if is_lifetime:
                print(f"\n✅ CONFIRMED: User is LIFETIME PREMIUM")
                print(f"  → Will NOT be charged credits for manual signals")
                print(f"  → Perfect for production testing!")
            else:
                print(f"\n⚠️  WARNING: User is NOT lifetime premium")
                print(f"  → Will be charged credits for manual signals")
                print(f"  → May not be ideal for testing")
            
            # Test premium checker
            print("\n" + "="*60)
            print("TESTING PREMIUM CHECKER MODULE")
            print("="*60)
            
            from app.premium_checker import is_lifetime_premium, check_and_deduct_credits
            
            is_lifetime_check = is_lifetime_premium(user_id)
            print(f"\n✅ is_lifetime_premium({user_id}) = {is_lifetime_check}")
            
            if is_lifetime_check:
                print(f"✅ Premium checker correctly identifies user as lifetime premium")
            else:
                print(f"❌ Premium checker failed to identify user as lifetime premium")
            
            # Test credit check
            success, msg = check_and_deduct_credits(user_id, 20)
            print(f"\n✅ check_and_deduct_credits({user_id}, 20)")
            print(f"  Success: {success}")
            print(f"  Message: {msg}")
            
            if success and "Lifetime Premium" in msg:
                print(f"✅ Credit check correctly bypassed for lifetime premium")
            else:
                print(f"⚠️  Credit check did not bypass as expected")
            
            # Get current credits for comparison
            print("\n" + "="*60)
            print("CREDITS BEFORE TESTING")
            print("="*60)
            print(f"\nCurrent Credits: {user.get('credits', 0)}")
            print(f"Expected After Testing: {user.get('credits', 0)} (no change)")
            
            return user, is_lifetime
        else:
            print(f"\n❌ User {user_id} not found in database")
            return None, False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        import traceback
        traceback.print_exc()
        return None, False


if __name__ == "__main__":
    print("="*60)
    print("PRODUCTION TEST USER VERIFICATION")
    print("Bot: @CryptoMentorAI_bot")
    print("User ID: 1187119989")
    print("="*60)
    
    user, is_lifetime = verify_test_user()
    
    if user and is_lifetime:
        print("\n" + "="*60)
        print("✅ READY FOR PRODUCTION TESTING")
        print("="*60)
        print("\n📋 Test Commands:")
        print("1. Open Telegram and find @CryptoMentorAI_bot")
        print("2. Send: /analyze BTCUSDT")
        print("3. Send: /futures ETHUSDT 4h")
        print("4. Send: /futures_signals")
        print("5. Send: /signal BTCUSDT (alias test)")
        print("6. Send: /signals (alias test)")
        print("\n⏱️ Expected Response Times:")
        print("  - Single signal: < 5 seconds")
        print("  - Multi-coin: < 15 seconds")
        print("\n💰 Expected Credits:")
        print(f"  - Before: {user.get('credits', 0)}")
        print(f"  - After: {user.get('credits', 0)} (no change)")
        print("\n✅ All commands should work without credit charge!")
    else:
        print("\n❌ User verification failed or not lifetime premium")
        print("Cannot proceed with production testing")
