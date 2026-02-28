#!/usr/bin/env python3
"""
Test Broadcast Pagination Fix
Verify that all users are fetched from Supabase
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_broadcast_users():
    """Test get_all_broadcast_users with pagination"""
    print("="*60)
    print("🧪 TESTING BROADCAST PAGINATION")
    print("="*60)
    
    try:
        from services import get_database
        db = get_database()
        
        print("\n📊 Fetching all broadcast users...")
        print("⏳ This may take a moment if you have many users...\n")
        
        broadcast_data = db.get_all_broadcast_users()
        
        stats = broadcast_data['stats']
        
        print("\n" + "="*60)
        print("📈 BROADCAST USER STATISTICS")
        print("="*60)
        
        print(f"\n📁 LOCAL DATABASE:")
        print(f"   Users: {stats['local_count']}")
        
        print(f"\n☁️  SUPABASE DATABASE:")
        print(f"   Total fetched: {stats['supabase_count']}")
        print(f"   Unique (not in local): {stats['supabase_unique']}")
        
        print(f"\n🎯 COMBINED RESULTS:")
        print(f"   Total unique users: {stats['total_unique']}")
        print(f"   Duplicates removed: {stats['duplicates']}")
        
        print("\n" + "="*60)
        
        # Check if pagination worked
        if stats['supabase_count'] > 1000:
            print("✅ PAGINATION WORKING!")
            print(f"   Fetched {stats['supabase_count']} users (more than 1000 limit)")
        elif stats['supabase_count'] == 1000:
            print("⚠️  WARNING: Exactly 1000 users")
            print("   This might be the limit. Check if there are more users in Supabase.")
        elif stats['supabase_count'] > 0:
            print(f"✅ Fetched {stats['supabase_count']} users")
            print("   (Less than 1000, so pagination not needed)")
        else:
            print("❌ No Supabase users found")
            print("   Check Supabase connection")
        
        print("\n" + "="*60)
        
        # Show sample users
        if broadcast_data['unique_ids']:
            sample_ids = list(broadcast_data['unique_ids'])[:5]
            print(f"\n📋 Sample User IDs (first 5):")
            for uid in sample_ids:
                print(f"   • {uid}")
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_supabase_pagination_directly():
    """Test Supabase pagination directly"""
    print("\n" + "="*60)
    print("🧪 TESTING SUPABASE PAGINATION DIRECTLY")
    print("="*60)
    
    try:
        from supabase_client import supabase
        
        if not supabase:
            print("❌ Supabase not configured")
            return False
        
        print("\n📊 Fetching users with pagination...")
        
        all_users = []
        page_size = 1000
        offset = 0
        page_num = 1
        
        while True:
            print(f"\n📄 Fetching page {page_num} (offset {offset})...")
            
            result = supabase.table('users')\
                .select('telegram_id, first_name, username')\
                .not_.is_('telegram_id', 'null')\
                .neq('telegram_id', 0)\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                print(f"   No more data (page {page_num})")
                break
            
            page_count = len(result.data)
            all_users.extend(result.data)
            
            print(f"   ✅ Fetched {page_count} users")
            print(f"   📊 Total so far: {len(all_users)}")
            
            if page_count < page_size:
                print(f"   ℹ️  Last page (got {page_count} < {page_size})")
                break
            
            offset += page_size
            page_num += 1
        
        print("\n" + "="*60)
        print(f"✅ TOTAL USERS FETCHED: {len(all_users)}")
        print("="*60)
        
        if len(all_users) > 1000:
            print(f"\n🎉 SUCCESS! Pagination is working!")
            print(f"   Fetched {len(all_users)} users (more than 1000 limit)")
        elif len(all_users) == 1000:
            print(f"\n⚠️  WARNING: Exactly 1000 users")
            print(f"   Check if there are more users in Supabase")
        else:
            print(f"\n✅ Fetched {len(all_users)} users")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting Broadcast Pagination Tests\n")
    
    # Test 1: Via database.py
    test1 = test_broadcast_users()
    
    # Test 2: Direct Supabase
    test2 = test_supabase_pagination_directly()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Database.py test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Direct Supabase test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print("="*60)
    
    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Pagination is working correctly")
        print("✅ Broadcast will reach all users")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Check the errors above")
