"""
Simple script to check broadcast reach
No external dependencies needed
"""
import sqlite3
import os

def check_local_database():
    """Check local SQLite database"""
    print("=" * 60)
    print("🗄️  LOCAL DATABASE (SQLite)")
    print("=" * 60)
    print()
    
    try:
        # Connect to database
        db_path = "cryptomentor.db"
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return 0
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total users
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE telegram_id IS NOT NULL 
            AND telegram_id != 0
            AND telegram_id != ''
        """)
        total = cursor.fetchone()[0]
        
        # Get valid users (not banned)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE telegram_id IS NOT NULL 
            AND telegram_id != 0
            AND telegram_id != ''
            AND (banned IS NULL OR banned = 0)
        """)
        valid = cursor.fetchone()[0]
        
        # Get banned users
        banned = total - valid
        
        # Get premium users
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE telegram_id IS NOT NULL 
            AND telegram_id != 0
            AND (banned IS NULL OR banned = 0)
            AND is_premium = 1
        """)
        premium = cursor.fetchone()[0]
        
        # Get sample users
        cursor.execute("""
            SELECT telegram_id, first_name, username, is_premium, created_at
            FROM users 
            WHERE telegram_id IS NOT NULL 
            AND telegram_id != 0
            AND (banned IS NULL OR banned = 0)
            ORDER BY created_at DESC
            LIMIT 5
        """)
        samples = cursor.fetchall()
        
        conn.close()
        
        # Display results
        print(f"📊 Statistics:")
        print(f"  • Total users: {total}")
        print(f"  • Valid users: {valid}")
        print(f"  • Banned users: {banned}")
        print(f"  • Premium users: {premium}")
        print(f"  • Free users: {valid - premium}")
        print()
        
        if samples:
            print(f"👥 Recent users (last 5):")
            for i, user in enumerate(samples, 1):
                tid, name, username, is_prem, created = user
                prem_badge = "👑" if is_prem else "👤"
                username_str = f"@{username}" if username else "No username"
                print(f"  {i}. {prem_badge} {name} ({username_str}) - ID: {tid}")
        print()
        
        return valid
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0


def check_supabase_env():
    """Check if Supabase is configured"""
    print("=" * 60)
    print("☁️  SUPABASE CONFIGURATION")
    print("=" * 60)
    print()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key and 'your_supabase' not in supabase_url:
        print("✅ Supabase is configured")
        print(f"   URL: {supabase_url[:30]}...")
        print(f"   Key: {supabase_key[:20]}...")
        print()
        print("⚠️  Note: To get exact Supabase user count, install supabase package:")
        print("   pip install supabase")
        print()
        return True
    else:
        print("⚠️  Supabase not configured or using placeholder values")
        print("   Bot will use local database only")
        print()
        return False


def show_broadcast_info(local_count):
    """Show broadcast information"""
    print("=" * 60)
    print("📢 BROADCAST INFORMATION")
    print("=" * 60)
    print()
    
    print(f"🎯 Current Broadcast Reach: {local_count} users")
    print()
    
    if local_count > 1100:
        improvement = local_count - 1100
        print(f"✅ Already improved from ~1100 to {local_count}")
        print(f"   Improvement: +{improvement} users")
    elif local_count < 1100:
        print(f"⚠️  Currently reaching {local_count} users")
        print(f"   Expected: 1600+ users with Supabase")
    
    print()
    print("💡 To reach MORE users:")
    print("   1. Configure Supabase (if you have 1600+ users there)")
    print("   2. Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
    print("   3. Install: pip install supabase")
    print("   4. Restart bot")
    print()
    
    print("📊 Expected with Supabase:")
    print("   • Local DB: ~1000 users")
    print("   • Supabase: ~800 users (600 unique)")
    print("   • Total: ~1600 users")
    print()


def show_how_to_broadcast():
    """Show how to use broadcast"""
    print("=" * 60)
    print("📝 HOW TO BROADCAST")
    print("=" * 60)
    print()
    
    print("Step 1: Start the bot")
    print("   python bot.py")
    print()
    
    print("Step 2: Open Telegram and send:")
    print("   /admin")
    print()
    
    print("Step 3: Click buttons:")
    print("   ⚙️ Settings → 📊 Database Stats")
    print("   (This will show you exact user count)")
    print()
    
    print("Step 4: Broadcast:")
    print("   ⚙️ Settings → 📢 Broadcast")
    print("   Type your message and send")
    print()
    
    print("✅ You'll see:")
    print("   • Real-time progress")
    print("   • Success/failure counts")
    print("   • Final detailed report")
    print()


if __name__ == "__main__":
    print()
    print("🤖 CryptoMentor Bot - Broadcast Reach Checker")
    print()
    
    # Check local database
    local_count = check_local_database()
    
    # Check Supabase config
    has_supabase = check_supabase_env()
    
    # Show broadcast info
    show_broadcast_info(local_count)
    
    # Show how to broadcast
    show_how_to_broadcast()
    
    print("=" * 60)
    print("✅ Check Complete!")
    print("=" * 60)
    print()
    
    if local_count > 0:
        print(f"🎯 You can broadcast to {local_count} users right now!")
        if has_supabase:
            print("   (Potentially more with Supabase - install package to verify)")
    else:
        print("⚠️  No users found. Add users first.")
    
    print()
