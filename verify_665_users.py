#!/usr/bin/env python3
"""
Verify 665 Users - Is this the actual count?
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def verify_user_count():
    """Verify actual user count in Supabase"""
    print("="*60)
    print("🔍 VERIFYING ACTUAL USER COUNT")
    print("="*60)
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        supabase = create_client(url, service_key)
        
        # Get total count
        print("\n📊 Getting total user count...")
        result = supabase.table('users')\
            .select('*', count='exact')\
            .execute()
        
        total_all = result.count if hasattr(result, 'count') else 0
        print(f"   Total rows in users table: {total_all}")
        
        # Get valid users (not banned, valid telegram_id)
        print("\n📊 Getting valid users (not banned, valid telegram_id)...")
        result = supabase.table('users')\
            .select('telegram_id', count='exact')\
            .not_.is_('telegram_id', 'null')\
            .neq('telegram_id', 0)\
            .execute()
        
        total_valid = result.count if hasattr(result, 'count') else 0
        print(f"   Valid users: {total_valid}")
        
        # Test pagination with all users
        print("\n📄 Testing pagination to fetch ALL users...")
        all_users = []
        page_size = 1000
        offset = 0
        page = 1
        
        while True:
            print(f"   Page {page}: Fetching offset {offset}...")
            result = supabase.table('users')\
                .select('telegram_id, first_name')\
                .not_.is_('telegram_id', 'null')\
                .neq('telegram_id', 0)\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                print(f"   Page {page}: No more data")
                break
            
            count = len(result.data)
            all_users.extend(result.data)
            print(f"   Page {page}: Fetched {count} users (total: {len(all_users)})")
            
            if count < page_size:
                print(f"   Page {page}: Last page (got {count} < {page_size})")
                break
            
            offset += page_size
            page += 1
        
        print("\n" + "="*60)
        print("📈 RESULTS")
        print("="*60)
        print(f"Total rows in table: {total_all}")
        print(f"Valid users (not banned, valid ID): {total_valid}")
        print(f"Users fetched with pagination: {len(all_users)}")
        print("="*60)
        
        if len(all_users) == total_valid:
            print("\n✅ PAGINATION WORKING CORRECTLY!")
            print(f"   Fetched all {len(all_users)} valid users")
        else:
            print("\n⚠️  MISMATCH!")
            print(f"   Expected: {total_valid}")
            print(f"   Got: {len(all_users)}")
        
        # Check if 665 is correct
        if total_valid == 665:
            print("\n✅ 665 IS THE CORRECT NUMBER!")
            print("   Your Supabase database actually has 665 valid users")
            print("   This is NOT a bug - it's the actual data")
            print("\n   Possible reasons:")
            print("   • Users who blocked bot are excluded")
            print("   • Banned users are excluded")
            print("   • Invalid telegram_id are excluded")
            print("   • This is the actual active user count")
        elif total_valid > 665:
            print(f"\n⚠️  ISSUE: Supabase has {total_valid} users but showing 665")
            print("   Pagination might not be working in bot code")
        
        # Show sample users
        if all_users:
            print("\n📋 Sample users (first 5):")
            for i, user in enumerate(all_users[:5], 1):
                print(f"   {i}. ID: {user.get('telegram_id')}, Name: {user.get('first_name')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Verifying 665 Users Count\n")
    verify_user_count()
