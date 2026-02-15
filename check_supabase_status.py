"""
Script untuk mengecek status Supabase connection
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_supabase_config():
    """Check Supabase configuration"""
    print("=" * 60)
    print("☁️  SUPABASE CONNECTION STATUS")
    print("=" * 60)
    print()
    
    # Get environment variables
    supabase_url = os.getenv('SUPABASE_URL', '').strip()
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY', '').strip()
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '').strip()
    
    print("📋 Configuration Check:")
    print()
    
    # Check URL
    if not supabase_url or 'your_supabase' in supabase_url:
        print("❌ SUPABASE_URL: Not configured (placeholder)")
        print(f"   Current: {supabase_url}")
        url_ok = False
    else:
        print("✅ SUPABASE_URL: Configured")
        print(f"   Value: {supabase_url[:50]}...")
        url_ok = True
    
    print()
    
    # Check Service Key
    if not supabase_service_key or 'your_supabase' in supabase_service_key:
        print("❌ SUPABASE_SERVICE_KEY: Not configured (placeholder)")
        if supabase_service_key:
            print(f"   Current: {supabase_service_key[:30]}...")
        service_key_ok = False
    else:
        print("✅ SUPABASE_SERVICE_KEY: Configured")
        print(f"   Value: {supabase_service_key[:30]}...")
        service_key_ok = True
    
    print()
    
    # Check Anon Key (optional)
    if not supabase_anon_key or 'your_supabase' in supabase_anon_key:
        print("⚠️  SUPABASE_ANON_KEY: Not configured (optional)")
        if supabase_anon_key:
            print(f"   Current: {supabase_anon_key[:30]}...")
    else:
        print("✅ SUPABASE_ANON_KEY: Configured")
        print(f"   Value: {supabase_anon_key[:30]}...")
    
    print()
    print("=" * 60)
    
    # Overall status
    if url_ok and service_key_ok:
        print("✅ SUPABASE: FULLY CONFIGURED")
        print()
        print("🔌 Attempting connection test...")
        return True
    else:
        print("❌ SUPABASE: NOT CONFIGURED")
        print()
        print("📝 Missing configuration:")
        if not url_ok:
            print("   • SUPABASE_URL")
        if not service_key_ok:
            print("   • SUPABASE_SERVICE_KEY")
        print()
        return False


def test_supabase_connection():
    """Test actual connection to Supabase"""
    print()
    print("=" * 60)
    print("🔌 SUPABASE CONNECTION TEST")
    print("=" * 60)
    print()
    
    try:
        # Try to import and connect
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL', '').strip()
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY', '').strip()
        
        if not supabase_url or not supabase_key:
            print("❌ Cannot test: Missing credentials")
            return False
        
        print("⏳ Connecting to Supabase...")
        client = create_client(supabase_url, supabase_key)
        
        print("⏳ Testing query...")
        result = client.table('users').select('count', count='exact').limit(1).execute()
        
        user_count = result.count if hasattr(result, 'count') else 0
        
        print()
        print("✅ CONNECTION SUCCESSFUL!")
        print()
        print(f"📊 Users in Supabase: {user_count}")
        print()
        
        if user_count > 0:
            print("🎯 Supabase has users!")
            print(f"   You can reach {user_count} users from Supabase")
        else:
            print("⚠️  Supabase table is empty")
            print("   No additional users to broadcast to")
        
        return True
        
    except ImportError:
        print("❌ Supabase package not installed")
        print()
        print("📦 Install with:")
        print("   pip install supabase")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("💡 Possible issues:")
        print("   • Wrong URL or Key")
        print("   • Network connection problem")
        print("   • Supabase project not accessible")
        return False


def show_summary():
    """Show summary and recommendations"""
    print()
    print("=" * 60)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    print()
    
    # Check config
    supabase_url = os.getenv('SUPABASE_URL', '').strip()
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY', '').strip()
    
    is_configured = (supabase_url and 'your_supabase' not in supabase_url and
                     supabase_key and 'your_supabase' not in supabase_key)
    
    if is_configured:
        print("✅ Supabase is configured")
        print()
        print("🎯 Your broadcast system will use:")
        print("   • Local Database (SQLite)")
        print("   • Supabase Database")
        print("   • Automatic deduplication")
        print()
        print("📈 Expected reach: 1600+ users")
        
    else:
        print("⚠️  Supabase is NOT configured")
        print()
        print("🎯 Your broadcast system currently uses:")
        print("   • Local Database (SQLite) only")
        print("   • 1,063 users")
        print()
        print("📈 Current reach: 1,063 users")
        print()
        print("💡 To reach 1600+ users:")
        print()
        print("1. Get Supabase credentials:")
        print("   • Login to https://supabase.com")
        print("   • Open your project")
        print("   • Go to Settings → API")
        print("   • Copy Project URL and Service Role Key")
        print()
        print("2. Update .env file:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_SERVICE_KEY=your_actual_service_key")
        print()
        print("3. Install package:")
        print("   pip install supabase")
        print()
        print("4. Restart bot:")
        print("   python bot.py")
        print()
        print("5. Test broadcast:")
        print("   /admin → Settings → Database Stats")
    
    print()


if __name__ == "__main__":
    print()
    print("🤖 CryptoMentor Bot - Supabase Status Checker")
    print()
    
    # Check configuration
    is_configured = check_supabase_config()
    
    # Test connection if configured
    if is_configured:
        connection_ok = test_supabase_connection()
    else:
        connection_ok = False
    
    # Show summary
    show_summary()
    
    print("=" * 60)
    print("✅ Check Complete!")
    print("=" * 60)
    print()
    
    if is_configured and connection_ok:
        print("🎉 Supabase is ready to use!")
        print("   Your broadcast will reach users from both databases")
    elif is_configured and not connection_ok:
        print("⚠️  Supabase configured but connection failed")
        print("   Check your credentials and network")
    else:
        print("💡 Supabase not configured")
        print("   Bot will use local database only (1,063 users)")
    
    print()
