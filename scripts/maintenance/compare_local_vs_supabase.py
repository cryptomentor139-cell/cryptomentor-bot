#!/usr/bin/env python3
"""
Compare Local DB vs Supabase
Find out why local has 1063 but Supabase has 665
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def compare_databases():
    """Compare local SQLite vs Supabase"""
    print("="*60)
    print("🔍 COMPARING LOCAL DB VS SUPABASE")
    print("="*60)
    
    try:
        from services import get_database
        from supabase import create_client
        
        # Get local users
        print("\n📁 Getting LOCAL database users...")
        db = get_database()
        local_users = db.get_all_users()
        local_ids = set(u.get('telegram_id') for u in local_users if u.get('telegram_id'))
        print(f"   Local users: {len(local_ids)}")
        
        # Get Supabase users
        print("\n☁️  Getting SUPABASE users...")
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(url, service_key)
        
        result = supabase.table('users')\
            .select('telegram_id')\
            .not_.is_('telegram_id', 'null')\
            .neq('telegram_id', 0)\
            .execute()
        
        supabase_ids = set(u.get('telegram_id') for u in result.data if u.get('telegram_id'))
        print(f"   Supabase users: {len(supabase_ids)}")
        
        # Compare
        print("\n" + "="*60)
        print("📊 COMPARISON")
        print("="*60)
        
        only_local = local_ids - supabase_ids
        only_supabase = supabase_ids - local_ids
        in_both = local_ids & supabase_ids
        
        print(f"\n✅ In BOTH databases: {len(in_both)} users")
        print(f"📁 ONLY in LOCAL: {len(only_local)} users")
        print(f"☁️  ONLY in SUPABASE: {len(only_supabase)} users")
        
        total_unique = len(local_ids | supabase_ids)
        print(f"\n🎯 TOTAL UNIQUE users: {total_unique}")
        
        # Show samples
        if only_local:
            print(f"\n📁 Sample users ONLY in LOCAL (first 10):")
            for uid in list(only_local)[:10]:
                print(f"   • {uid}")
        
        if only_supabase:
            print(f"\n☁️  Sample users ONLY in SUPABASE (first 10):")
            for uid in list(only_supabase)[:10]:
                print(f"   • {uid}")
        
        # Conclusion
        print("\n" + "="*60)
        print("💡 CONCLUSION")
        print("="*60)
        
        if len(only_local) > 0:
            print(f"\n📁 Local DB has {len(only_local)} users NOT in Supabase")
            print("   These users will receive broadcast (from local DB)")
        
        if len(only_supabase) > 0:
            print(f"\n☁️  Supabase has {len(only_supabase)} users NOT in local DB")
            print("   These users will receive broadcast (from Supabase)")
        
        print(f"\n🎯 BROADCAST WILL REACH: {total_unique} UNIQUE USERS")
        print(f"   = {len(local_ids)} (local) + {len(supabase_ids)} (supabase) - {len(in_both)} (duplicates)")
        
        if total_unique == 665:
            print("\n⚠️  WARNING: Total unique is still 665!")
            print("   This means local DB users are ALL duplicates of Supabase")
            print("   OR local DB is not being used in broadcast")
        elif total_unique == 1063:
            print("\n✅ Total unique is 1063!")
            print("   This means local DB has unique users not in Supabase")
            print("   Broadcast should reach 1063 users")
        elif total_unique > 1063:
            print(f"\n✅ Total unique is {total_unique}!")
            print("   This is MORE than local DB alone")
            print(f"   Broadcast should reach {total_unique} users")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Comparing Local DB vs Supabase\n")
    compare_databases()
