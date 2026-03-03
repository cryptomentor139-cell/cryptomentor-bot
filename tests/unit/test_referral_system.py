#!/usr/bin/env python3
"""
Test Referral System - Comprehensive Bug Check
Check all referral queries and functions for bugs
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_referral_code_generation():
    """Test referral code generation"""
    print("="*60)
    print("🧪 TEST 1: Referral Code Generation")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        # Test free referral code generation
        test_user_id = 999999999
        free_code = db._generate_free_referral_code(test_user_id)
        print(f"\n✅ Free referral code generated: {free_code}")
        
        # Verify format
        if free_code.startswith('F') and len(free_code) == 8:
            print(f"   ✅ Format correct: F + 7 chars")
        else:
            print(f"   ❌ Format incorrect: {free_code}")
            return False
        
        # Test premium referral code generation
        premium_code = db._generate_premium_referral_code(test_user_id)
        print(f"\n✅ Premium referral code generated: {premium_code}")
        
        # Verify format
        if premium_code.startswith('P') and len(premium_code) == 8:
            print(f"   ✅ Format correct: P + 7 chars")
        else:
            print(f"   ❌ Format incorrect: {premium_code}")
            return False
        
        # Test uniqueness
        if free_code != premium_code:
            print(f"\n✅ Codes are unique")
        else:
            print(f"\n❌ Codes are NOT unique!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_referral_lookup():
    """Test referral code lookup"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Referral Code Lookup")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        # Get a real user with referral code
        all_users = db.get_all_users()
        test_user = None
        
        for user in all_users:
            if user.get('referral_code'):
                test_user = user
                break
        
        if not test_user:
            print("\n⚠️  No users with referral codes found")
            print("   Creating test user...")
            
            # Create test user
            test_id = 888888888
            db.create_user(test_id, "test_user", "Test", "User", "id", None)
            test_user = db.get_user(test_id)
        
        if test_user:
            ref_code = test_user.get('referral_code')
            user_id = test_user.get('telegram_id')
            
            print(f"\n📊 Test User:")
            print(f"   ID: {user_id}")
            print(f"   Referral Code: {ref_code}")
            
            # Test lookup
            found_id = db.get_user_by_referral_code(ref_code)
            
            if found_id == user_id:
                print(f"\n✅ Lookup successful: {ref_code} → {found_id}")
                return True
            else:
                print(f"\n❌ Lookup failed: {ref_code} → {found_id} (expected {user_id})")
                return False
        else:
            print("\n❌ Could not create test user")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_referral_reward_processing():
    """Test referral reward processing"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Referral Reward Processing")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        # Create test referrer
        referrer_id = 777777777
        referred_id = 666666666
        
        # Clean up if exists
        db.cursor.execute("DELETE FROM users WHERE telegram_id IN (?, ?)", (referrer_id, referred_id))
        db.conn.commit()
        
        # Create referrer
        db.create_user(referrer_id, "referrer", "Referrer", "User", "id", None)
        
        # Get initial credits
        initial_credits = db.get_user_credits(referrer_id)
        print(f"\n📊 Initial credits: {initial_credits}")
        
        # Create referred user
        db.create_user(referred_id, "referred", "Referred", "User", "id", referrer_id)
        
        # Process reward
        success = db.process_referral_reward(referrer_id, referred_id)
        
        if success:
            print(f"✅ Reward processing successful")
            
            # Check credits increased
            final_credits = db.get_user_credits(referrer_id)
            print(f"📊 Final credits: {final_credits}")
            
            # Get tier info
            tier = db.get_user_tier(referrer_id)
            expected_reward = 5 + int(5 * (tier['bonus'] / 100))
            
            if final_credits >= initial_credits + expected_reward:
                print(f"✅ Credits increased correctly (+{final_credits - initial_credits})")
                print(f"   Expected: +{expected_reward} (base 5 + {tier['bonus']}% {tier['tier']} bonus)")
                return True
            else:
                print(f"❌ Credits did not increase correctly")
                print(f"   Expected: +{expected_reward}, Got: +{final_credits - initial_credits}")
                return False
        else:
            print(f"❌ Reward processing failed")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            db.cursor.execute("DELETE FROM users WHERE telegram_id IN (?, ?)", (referrer_id, referred_id))
            db.conn.commit()
        except:
            pass

def test_referral_stats():
    """Test referral statistics"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Referral Statistics")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        # Get a user with referrals
        all_users = db.get_all_users()
        test_user = None
        
        for user in all_users:
            stats = db.get_referral_stats(user.get('telegram_id'))
            if stats['total_referrals'] > 0:
                test_user = user
                break
        
        if not test_user:
            print("\n⚠️  No users with referrals found")
            print("   Testing with user 0 referrals...")
            test_user = all_users[0] if all_users else None
        
        if test_user:
            user_id = test_user.get('telegram_id')
            
            # Test basic stats
            stats = db.get_referral_stats(user_id)
            print(f"\n📊 Basic Stats for {user_id}:")
            print(f"   Total Referrals: {stats['total_referrals']}")
            print(f"   Total Earnings: Rp {stats['total_earnings']:,}")
            
            # Test detailed stats
            detailed = db.get_detailed_referral_stats(user_id)
            print(f"\n📊 Detailed Stats:")
            print(f"   Total Referrals: {detailed['total_referrals']}")
            print(f"   Active Referrals (30d): {detailed['active_referrals']}")
            print(f"   Total Earnings: Rp {detailed['total_earnings']:,}")
            print(f"   This Month: Rp {detailed['this_month_earnings']:,}")
            
            # Test tier info
            tier = db.get_user_tier(user_id)
            print(f"\n📊 Tier Info:")
            print(f"   Tier: {tier['tier']}")
            print(f"   Level: {tier['level']}")
            print(f"   Bonus: {tier['bonus']}%")
            print(f"   Money Multiplier: {tier['money_multiplier']}x")
            
            # Test earnings summary
            summary = db.get_referral_earnings_summary(user_id)
            print(f"\n📊 Earnings Summary:")
            print(f"   Total Referrals: {summary['total_referrals']}")
            print(f"   Free Referrals: {summary['free_referrals']}")
            print(f"   Premium Referrals: {summary['premium_referrals']}")
            print(f"   Credit Earnings: {summary['credit_earnings']} credits")
            print(f"   Money Earnings: Rp {summary['money_earnings']:,}")
            
            # Verify consistency
            if stats['total_referrals'] == detailed['total_referrals'] == summary['total_referrals']:
                print(f"\n✅ Stats are consistent across all functions")
                return True
            else:
                print(f"\n❌ Stats are INCONSISTENT!")
                print(f"   Basic: {stats['total_referrals']}")
                print(f"   Detailed: {detailed['total_referrals']}")
                print(f"   Summary: {summary['total_referrals']}")
                return False
        else:
            print("\n❌ No users found for testing")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_referral_tier_system():
    """Test referral tier system"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Referral Tier System")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        # Test tier thresholds
        test_cases = [
            (0, 'STARTER', 1, 5, 1.0),
            (5, 'STARTER', 1, 5, 1.0),
            (10, 'BRONZE', 2, 10, 1.5),
            (25, 'SILVER', 3, 15, 2.0),
            (50, 'GOLD', 4, 20, 2.5),
            (100, 'DIAMOND', 5, 30, 3.0),
        ]
        
        print("\n📊 Testing Tier Thresholds:")
        all_correct = True
        
        for referrals, expected_tier, expected_level, expected_bonus, expected_mult in test_cases:
            # Create test user with specific referral count
            test_id = 555555555
            
            # Clean up
            db.cursor.execute("DELETE FROM users WHERE telegram_id = ? OR referred_by = ?", (test_id, test_id))
            db.conn.commit()
            
            # Create referrer
            db.create_user(test_id, "test", "Test", "User", "id", None)
            
            # Create referrals
            for i in range(referrals):
                ref_id = 500000000 + i
                db.create_user(ref_id, f"ref{i}", f"Ref{i}", "User", "id", test_id)
            
            # Get tier
            tier = db.get_user_tier(test_id)
            
            # Verify
            if (tier['tier'] == expected_tier and 
                tier['level'] == expected_level and 
                tier['bonus'] == expected_bonus and 
                tier['money_multiplier'] == expected_mult):
                print(f"   ✅ {referrals} referrals → {tier['tier']} (Level {tier['level']}, {tier['bonus']}%, {tier['money_multiplier']}x)")
            else:
                print(f"   ❌ {referrals} referrals → Expected {expected_tier}, Got {tier['tier']}")
                all_correct = False
            
            # Cleanup
            db.cursor.execute("DELETE FROM users WHERE telegram_id = ? OR referred_by = ?", (test_id, test_id))
            db.conn.commit()
        
        return all_correct
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_premium_referral():
    """Test premium referral rewards"""
    print("\n" + "="*60)
    print("🧪 TEST 6: Premium Referral Rewards")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        # Create test users
        referrer_id = 444444444
        referred_id = 333333333
        
        # Clean up
        db.cursor.execute("DELETE FROM users WHERE telegram_id IN (?, ?)", (referrer_id, referred_id))
        db.cursor.execute("DELETE FROM premium_referrals WHERE referrer_id = ? OR referred_id = ?", (referrer_id, referred_id))
        db.conn.commit()
        
        # Create referrer (must be premium)
        db.create_user(referrer_id, "referrer", "Referrer", "User", "id", None)
        db.grant_premium(referrer_id, 30)
        
        # Get initial earnings
        initial_earnings = db.get_user(referrer_id).get('premium_earnings', 0)
        print(f"\n📊 Initial earnings: Rp {initial_earnings:,}")
        
        # Create referred user
        db.create_user(referred_id, "referred", "Referred", "User", "id", referrer_id)
        
        # Record premium referral reward
        success = db.record_premium_referral_reward(referrer_id, referred_id, '1_month', 50000)
        
        if success:
            print(f"✅ Premium reward recorded")
            
            # Check earnings increased
            final_earnings = db.get_user(referrer_id).get('premium_earnings', 0)
            print(f"📊 Final earnings: Rp {final_earnings:,}")
            
            # Get tier info
            tier = db.get_user_tier(referrer_id)
            base_earnings = 10000
            expected_earnings = int(base_earnings * tier['money_multiplier'])
            
            if final_earnings >= initial_earnings + expected_earnings:
                print(f"✅ Earnings increased correctly (+Rp {final_earnings - initial_earnings:,})")
                print(f"   Expected: +Rp {expected_earnings:,} (base Rp 10,000 × {tier['money_multiplier']}x {tier['tier']})")
                return True
            else:
                print(f"❌ Earnings did not increase correctly")
                print(f"   Expected: +Rp {expected_earnings:,}, Got: +Rp {final_earnings - initial_earnings:,}")
                return False
        else:
            print(f"❌ Premium reward recording failed")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            db.cursor.execute("DELETE FROM users WHERE telegram_id IN (?, ?)", (referrer_id, referred_id))
            db.cursor.execute("DELETE FROM premium_referrals WHERE referrer_id = ? OR referred_id = ?", (referrer_id, referred_id))
            db.conn.commit()
        except:
            pass

def run_all_tests():
    """Run all referral system tests"""
    print("\n🧪 REFERRAL SYSTEM - COMPREHENSIVE BUG CHECK\n")
    
    tests = [
        ("Referral Code Generation", test_referral_code_generation),
        ("Referral Code Lookup", test_referral_lookup),
        ("Referral Reward Processing", test_referral_reward_processing),
        ("Referral Statistics", test_referral_stats),
        ("Referral Tier System", test_referral_tier_system),
        ("Premium Referral Rewards", test_premium_referral),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
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
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Referral system is working correctly")
        return True
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("   Please review and fix issues above")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
