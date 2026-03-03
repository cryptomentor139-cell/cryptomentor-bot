#!/usr/bin/env python3
"""
Force Test Broadcast Count
Test directly without cache
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct():
    """Test broadcast count directly"""
    print("="*60)
    print("🧪 DIRECT BROADCAST COUNT TEST")
    print("="*60)
    
    try:
        # Import fresh
        import importlib
        
        # Clear any cached modules
        if 'services' in sys.modules:
            del sys.modules['services']
        if 'database' in sys.modules:
            del sys.modules['database']
        
        # Import fresh
        from services import get_database
        
        print("\n📊 Getting database instance...")
        db = get_database()
        
        print("📊 Calling get_all_broadcast_users()...")
        broadcast_data = db.get_all_broadcast_users()
        
        stats = broadcast_data['stats']
        
        print("\n" + "="*60)
        print("📈 RESULTS")
        print("="*60)
        
        print(f"\n📁 Local DB: {stats['local_count']} users")
        print(f"☁️  Supabase: {stats['supabase_count']} users")
        print(f"🎯 Total Unique: {stats['total_unique']} users")
        print(f"🔄 Duplicates: {stats['duplicates']}")
        
        print("\n" + "="*60)
        print(f"✅ BROADCAST WILL REACH: {stats['total_unique']} USERS")
        print("="*60)
        
        # Check if this matches what bot shows
        if stats['total_unique'] == 665:
            print("\n⚠️  WARNING: Still showing 665 users")
            print("\nPossible causes:")
            print("1. Supabase not connected (check env variables)")
            print("2. Database actually has 665 valid users")
            print("3. Railway not restarted yet")
            
            if stats['supabase_count'] == 0:
                print("\n❌ ISSUE FOUND: Supabase not connected!")
                print("   Supabase count is 0")
                print("\n   Solution:")
                print("   1. Check SUPABASE_URL in .env")
                print("   2. Check SUPABASE_SERVICE_KEY in .env")
                print("   3. Restart bot")
        else:
            print(f"\n✅ SUCCESS: Showing {stats['total_unique']} users")
            print("   This should match what you see in bot")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_supabase_connection():
    """Check if Supabase is connected"""
    print("\n" + "="*60)
    print("🔍 CHECKING SUPABASE CONNECTION")
    print("="*60)
    
    try:
        from supabase_client import supabase
        
        if not supabase:
            print("\n❌ Supabase NOT configured")
            print("\nCheck these environment variables:")
            print("  - SUPABASE_URL")
            print("  - SUPABASE_SERVICE_KEY")
            return False
        
        print("\n✅ Supabase client exists")
        
        # Try to query
        print("📊 Testing query...")
        result = supabase.table('users')\
            .select('telegram_id', count='exact')\
            .limit(1)\
            .execute()
        
        total_count = result.count if hasattr(result, 'count') else 0
        
        print(f"✅ Supabase connected!")
        print(f"   Total users in Supabase: {total_count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Supabase connection failed: {e}")
        return False

def check_env_variables():
    """Check environment variables"""
    print("\n" + "="*60)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("="*60)
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY',
        'SUPABASE_ANON_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first 20 chars only
            masked = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("\n🚀 Starting Force Broadcast Count Test\n")
    
    # Check env
    check_env_variables()
    
    # Check Supabase
    supabase_ok = check_supabase_connection()
    
    # Test broadcast count
    test_ok = test_direct()
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Supabase connection: {'✅ OK' if supabase_ok else '❌ FAILED'}")
    print(f"Broadcast count test: {'✅ OK' if test_ok else '❌ FAILED'}")
    print("="*60)
    
    if not supabase_ok:
        print("\n⚠️  SUPABASE NOT CONNECTED")
        print("This is why you're seeing 665 users (local DB only)")
        print("\nTo fix:")
        print("1. Check .env file has SUPABASE_URL and SUPABASE_SERVICE_KEY")
        print("2. Restart bot")
        print("3. Test again")
