#!/usr/bin/env python3
"""
Verify manual signal generation in production
Check Railway deployment and test with lifetime premium user
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.supabase_conn import get_supabase_client

def check_lifetime_premium_user(user_id: int):
    """Check if user is lifetime premium"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("users").select(
            "telegram_id, username, is_premium, premium_until, credits"
        ).eq(
            "telegram_id", user_id
        ).execute()
        
        if result.data:
            user = result.data[0]
            print(f"\n✅ User Found:")
            print(f"  User ID: {user['telegram_id']}")
            print(f"  Username: @{user.get('username', 'N/A')}")
            print(f"  Is Premium: {user['is_premium']}")
            print(f"  Premium Until: {user['premium_until']}")
            print(f"  Credits: {user.get('credits', 0)}")
            
            is_lifetime = user['is_premium'] and user['premium_until'] is None
            
            if is_lifetime:
                print(f"\n✅ User is LIFETIME PREMIUM")
                print(f"  → Should NOT be charged credits for manual signals")
            else:
                print(f"\n⚠️  User is NOT lifetime premium")
                print(f"  → Will be charged credits for manual signals")
            
            return user, is_lifetime
        else:
            print(f"\n❌ User {user_id} not found in database")
            return None, False
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None, False


def verify_handlers_registered():
    """Verify that manual signal handlers are registered"""
    print("\n" + "="*60)
    print("Checking Handler Registration")
    print("="*60)
    
    try:
        # Check if handlers file exists
        handlers_path = "app/handlers_manual_signals.py"
        if os.path.exists(handlers_path):
            print(f"✅ Handlers file exists: {handlers_path}")
        else:
            print(f"❌ Handlers file NOT found: {handlers_path}")
            return False
        
        # Check if premium checker exists
        checker_path = "app/premium_checker.py"
        if os.path.exists(checker_path):
            print(f"✅ Premium checker exists: {checker_path}")
        else:
            print(f"❌ Premium checker NOT found: {checker_path}")
            return False
        
        # Check if bot.py has handler registration
        with open("bot.py", "r", encoding="utf-8") as f:
            bot_content = f.read()
            
            if "handlers_manual_signals" in bot_content:
                print(f"✅ Manual signal handlers imported in bot.py")
            else:
                print(f"❌ Manual signal handlers NOT imported in bot.py")
                return False
            
            if 'CommandHandler("analyze"' in bot_content:
                print(f"✅ /analyze command registered")
            else:
                print(f"❌ /analyze command NOT registered")
                return False
            
            if 'CommandHandler("futures"' in bot_content:
                print(f"✅ /futures command registered")
            else:
                print(f"❌ /futures command NOT registered")
                return False
            
            if 'CommandHandler("futures_signals"' in bot_content:
                print(f"✅ /futures_signals command registered")
            else:
                print(f"❌ /futures_signals command NOT registered")
                return False
        
        print(f"\n✅ All handlers properly registered!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying handlers: {e}")
        return False


def check_railway_deployment():
    """Check Railway deployment status"""
    print("\n" + "="*60)
    print("Railway Deployment Check")
    print("="*60)
    
    # Check if Railway environment variables are set
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    if railway_env:
        print(f"✅ Running in Railway environment: {railway_env}")
    else:
        print(f"⚠️  Not running in Railway (local environment)")
    
    # Check critical environment variables
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "BINANCE_API_KEY",
        "BINANCE_API_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is MISSING")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print(f"\n✅ All required environment variables are set")
        return True


def test_premium_checker():
    """Test premium checker module"""
    print("\n" + "="*60)
    print("Testing Premium Checker Module")
    print("="*60)
    
    try:
        from app.premium_checker import is_lifetime_premium, check_and_deduct_credits
        
        print(f"✅ Premium checker module imported successfully")
        
        # Test with known lifetime premium user
        test_user_id = 1766523174  # @ceteline
        
        is_lifetime = is_lifetime_premium(test_user_id)
        print(f"\n✅ is_lifetime_premium({test_user_id}) = {is_lifetime}")
        
        if is_lifetime:
            print(f"✅ Correctly identified as lifetime premium")
        else:
            print(f"❌ Should be lifetime premium but returned False")
            return False
        
        # Test credit check (should bypass for lifetime premium)
        success, msg = check_and_deduct_credits(test_user_id, 20)
        print(f"\n✅ check_and_deduct_credits({test_user_id}, 20)")
        print(f"  Success: {success}")
        print(f"  Message: {msg}")
        
        if success and "Lifetime Premium" in msg:
            print(f"✅ Correctly bypassed credit check for lifetime premium")
        else:
            print(f"❌ Should bypass credit check but didn't")
            return False
        
        print(f"\n✅ Premium checker module working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing premium checker: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("PRODUCTION VERIFICATION - Manual Signal Generation")
    print("="*60)
    
    # Step 1: Check Railway deployment
    railway_ok = check_railway_deployment()
    
    # Step 2: Verify handlers registered
    handlers_ok = verify_handlers_registered()
    
    # Step 3: Test premium checker
    checker_ok = test_premium_checker()
    
    # Step 4: Check test user
    print("\n" + "="*60)
    print("Checking Test User")
    print("="*60)
    
    test_user_id = 1766523174  # @ceteline
    user, is_lifetime = check_lifetime_premium_user(test_user_id)
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_checks = [
        ("Railway Environment", railway_ok),
        ("Handlers Registration", handlers_ok),
        ("Premium Checker Module", checker_ok),
        ("Test User Available", user is not None and is_lifetime)
    ]
    
    for check_name, check_result in all_checks:
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    all_passed = all(result for _, result in all_checks)
    
    if all_passed:
        print("\n" + "="*60)
        print("✅ ALL CHECKS PASSED - READY FOR PRODUCTION TESTING")
        print("="*60)
        print("\n📋 Next Steps:")
        print("1. Contact test user @ceteline (ID: 1766523174)")
        print("2. Ask them to test these commands:")
        print("   - /analyze BTCUSDT")
        print("   - /futures ETHUSDT 4h")
        print("   - /futures_signals")
        print("3. Monitor Railway logs for any errors")
        print("4. Verify no credit deduction in database")
        print("\n📊 Expected Results:")
        print("   - Signal generated and delivered < 5 seconds")
        print("   - No credit deduction (lifetime premium)")
        print("   - No errors in Railway logs")
        print("   - Signal format matches CryptoMentor AI 3.0")
        return 0
    else:
        print("\n" + "="*60)
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE TESTING")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
