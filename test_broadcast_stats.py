"""
Test script untuk melihat database broadcast statistics
Jalankan ini untuk melihat berapa user yang akan dijangkau broadcast
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_stats():
    """Test database statistics untuk broadcast"""
    print("=" * 60)
    print("📊 DATABASE BROADCAST STATISTICS TEST")
    print("=" * 60)
    print()
    
    try:
        # Import database
        from database import Database
        
        print("✅ Database module loaded")
        print()
        
        # Initialize database
        db = Database()
        print("✅ Database initialized")
        print()
        
        # Test 1: Get all users from local database
        print("🗄️  TEST 1: Local Database")
        print("-" * 60)
        local_users = db.get_all_users()
        print(f"✅ Found {len(local_users)} users in local database")
        
        if local_users:
            print(f"\nSample users (first 3):")
            for i, user in enumerate(local_users[:3], 1):
                print(f"  {i}. ID: {user.get('telegram_id')}, "
                      f"Name: {user.get('first_name', 'N/A')}, "
                      f"Premium: {user.get('is_premium', 0)}")
        print()
        
        # Test 2: Get broadcast users (combined)
        print("🎯 TEST 2: Combined Broadcast Statistics")
        print("-" * 60)
        broadcast_data = db.get_all_broadcast_users()
        stats = broadcast_data['stats']
        
        print(f"📊 Statistics:")
        print(f"  • Local DB: {stats['local_count']} users")
        print(f"  • Supabase DB: {stats['supabase_count']} users")
        print(f"  • Supabase Unique: {stats['supabase_unique']} users")
        print(f"  • Duplicates: {stats['duplicates']} users")
        print(f"  • Total Unique: {stats['total_unique']} users")
        print()
        
        # Test 3: Show formatted stats
        print("📋 TEST 3: Formatted Statistics (Admin View)")
        print("-" * 60)
        from app.admin_status import format_database_stats
        formatted = format_database_stats()
        print(formatted)
        print()
        
        # Summary
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print(f"🎯 BROADCAST REACH: {stats['total_unique']} unique users")
        print()
        
        # Show improvement
        if stats['total_unique'] > 1100:
            improvement = stats['total_unique'] - 1100
            percentage = (improvement / 1100) * 100
            print(f"📈 IMPROVEMENT: +{improvement} users (+{percentage:.1f}%)")
            print(f"   Before: ~1100 users")
            print(f"   After:  {stats['total_unique']} users")
        
        print()
        print("💡 To broadcast a message:")
        print("   1. Start the bot")
        print("   2. Send /admin command")
        print("   3. Go to Settings → Broadcast")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_supabase_connection():
    """Test Supabase connection"""
    print("=" * 60)
    print("☁️  SUPABASE CONNECTION TEST")
    print("=" * 60)
    print()
    
    try:
        from supabase_client import supabase, get_live_user_count
        
        if not supabase:
            print("⚠️  Supabase not configured")
            print("   Bot will use local database only")
            return False
        
        print("✅ Supabase client initialized")
        
        # Test connection
        user_count = get_live_user_count()
        print(f"✅ Supabase connection successful")
        print(f"   Users in Supabase: {user_count}")
        print()
        
        return True
        
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {e}")
        print("   Bot will use local database only")
        return False


def show_broadcast_preview():
    """Show what a broadcast would look like"""
    print("=" * 60)
    print("📢 BROADCAST PREVIEW")
    print("=" * 60)
    print()
    
    print("When you broadcast, you'll see:")
    print()
    print("1️⃣ Initial Message:")
    print("-" * 40)
    print("""📤 Broadcasting...

📊 Target Users:
• Local DB: 1000
• Supabase: 800 (600 unique)
• Total Unique: 1600
• Duplicates: 200

⏳ Starting broadcast...""")
    print()
    
    print("2️⃣ Progress Updates (every ~3 seconds):")
    print("-" * 40)
    print("""📤 Broadcasting...

📊 Progress: 270/1600 (16.9%)
✉️ Sent: 265
🚫 Blocked: 3
❌ Failed: 2""")
    print()
    
    print("3️⃣ Final Report:")
    print("-" * 40)
    print("""✅ Broadcast Complete!

📊 Database Stats:
• Local DB: 1000 users
• Supabase: 800 users
• Supabase Unique: 600 users
• Duplicates Removed: 200
• Total Unique: 1600 users

📤 Delivery Results:
✉️ Successfully sent: 1450
🚫 Blocked bot: 120
❌ Other failures: 30
📊 Total attempts: 1600

📈 Success Rate: 90.6%

💡 Note: Users who blocked the bot or deleted their account cannot receive messages.""")
    print()


if __name__ == "__main__":
    print()
    print("🤖 CryptoMentor Bot - Broadcast System Test")
    print()
    
    # Test Supabase
    supabase_ok = test_supabase_connection()
    print()
    
    # Test Database Stats
    stats_ok = test_database_stats()
    print()
    
    # Show Preview
    if stats_ok:
        show_broadcast_preview()
    
    print("=" * 60)
    print("🎉 Testing Complete!")
    print("=" * 60)
    print()
    
    if stats_ok:
        print("✅ Broadcast system is ready to use!")
        print()
        print("📝 Next Steps:")
        print("   1. Start your bot: python bot.py")
        print("   2. Open Telegram and send: /admin")
        print("   3. Navigate to: Settings → Database Stats")
        print("   4. Then try: Settings → Broadcast")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print()
