
import os
import sys
sys.path.append('.')

from database import Database

def test_referral_system():
    """Test complete referral system functionality"""
    print("🔍 Testing Referral System...")
    
    try:
        db = Database()
        
        # Test user IDs (use existing or create test users)
        referrer_id = 1296391564  # Your admin ID as referrer
        referred_id = 1234567890  # Test referred user
        
        print("\n1️⃣ Testing Free Referral Code Generation...")
        
        # Get referral codes for referrer
        referral_codes = db.get_user_referral_codes(referrer_id)
        if referral_codes:
            print(f"✅ Free Referral Code: {referral_codes['free_referral_code']}")
            print(f"✅ Premium Referral Code: {referral_codes['premium_referral_code']}")
        else:
            print("❌ No referral codes found")
            return
        
        print("\n2️⃣ Testing Referral Code Lookup...")
        
        # Test free referral code lookup
        found_referrer = db.get_user_by_referral_code(referral_codes['free_referral_code'])
        print(f"Free code lookup: {'✅ Success' if found_referrer == referrer_id else '❌ Failed'}")
        
        # Test premium referral code lookup
        found_premium_referrer = db.get_user_by_premium_referral_code(referral_codes['premium_referral_code'])
        print(f"Premium code lookup: {'✅ Success' if found_premium_referrer == referrer_id else '❌ Failed'}")
        
        print("\n3️⃣ Testing Free Referral Statistics...")
        
        # Get free referral stats
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (referrer_id,))
        free_referrals = db.cursor.fetchone()[0]
        print(f"Total free referrals: {free_referrals}")
        
        print("\n4️⃣ Testing Premium Referral Statistics...")
        
        # Get premium referral stats
        premium_stats = db.get_premium_referral_stats(referrer_id)
        print(f"Premium referrals: {premium_stats['total_referrals']}")
        print(f"Premium earnings: Rp {premium_stats['total_earnings']:,}")
        
        print("\n5️⃣ Testing Premium Referral Reward System...")
        
        # Test recording premium referral reward
        success = db.record_premium_referral_reward(
            referrer_id, referred_id, "1month", 320000
        )
        print(f"Premium reward recording: {'✅ Success' if success else '❌ Failed'}")
        
        if success:
            # Check updated stats
            updated_stats = db.get_premium_referral_stats(referrer_id)
            print(f"Updated earnings: Rp {updated_stats['total_earnings']:,}")
        
        print("\n6️⃣ Testing Database Integrity...")
        
        # Check tables exist
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='premium_referrals'")
        table_exists = db.cursor.fetchone() is not None
        print(f"Premium referrals table: {'✅ Exists' if table_exists else '❌ Missing'}")
        
        # Check required columns
        if table_exists:
            db.cursor.execute("PRAGMA table_info(premium_referrals)")
            columns = [col[1] for col in db.cursor.fetchall()]
            required_cols = ['referrer_id', 'referred_id', 'subscription_type', 'earnings', 'status']
            missing_cols = [col for col in required_cols if col not in columns]
            
            if not missing_cols:
                print("✅ All required columns present")
            else:
                print(f"❌ Missing columns: {missing_cols}")
        
        print("\n✅ Referral system test completed!")
        
    except Exception as e:
        print(f"❌ Error testing referral system: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_referral_system()
