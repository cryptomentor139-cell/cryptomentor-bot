#!/usr/bin/env python3
"""
Migrate Local Users to Supabase
Move all users from local SQLite to Supabase
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_users():
    """Migrate all local users to Supabase"""
    print("="*60)
    print("🚀 MIGRATING LOCAL USERS TO SUPABASE")
    print("="*60)
    
    try:
        from services import get_database
        from supabase import create_client
        from app.sb_repo import upsert_user_strict
        
        # Get databases
        db = get_database()
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(url, service_key)
        
        # Get local users
        print("\n📁 Getting LOCAL users...")
        local_users = db.get_all_users()
        local_ids = {u.get('telegram_id'): u for u in local_users if u.get('telegram_id')}
        print(f"   Found {len(local_ids)} users in local DB")
        
        # Get Supabase users
        print("\n☁️  Getting SUPABASE users...")
        result = supabase.table('users')\
            .select('telegram_id')\
            .not_.is_('telegram_id', 'null')\
            .neq('telegram_id', 0)\
            .execute()
        
        supabase_ids = set(u.get('telegram_id') for u in result.data if u.get('telegram_id'))
        print(f"   Found {len(supabase_ids)} users in Supabase")
        
        # Find users to migrate
        to_migrate_ids = set(local_ids.keys()) - supabase_ids
        print(f"\n🔄 Users to migrate: {len(to_migrate_ids)}")
        
        if not to_migrate_ids:
            print("\n✅ All users already in Supabase!")
            print("   No migration needed")
            return True
        
        # Confirm migration
        print(f"\n⚠️  This will migrate {len(to_migrate_ids)} users to Supabase")
        print("   Press Enter to continue, or Ctrl+C to cancel...")
        input()
        
        # Migrate users
        print("\n🚀 Starting migration...")
        success_count = 0
        fail_count = 0
        batch_size = 50
        
        to_migrate_list = list(to_migrate_ids)
        total = len(to_migrate_list)
        
        for i in range(0, total, batch_size):
            batch = to_migrate_list[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} users)...")
            
            for user_id in batch:
                user = local_ids[user_id]
                
                try:
                    # Use upsert_user_strict to migrate
                    result = upsert_user_strict(
                        tg_id=user_id,
                        username=user.get('username'),
                        first_name=user.get('first_name'),
                        last_name=user.get('last_name'),
                        referred_by=user.get('referred_by')
                    )
                    
                    success_count += 1
                    
                    # Show progress every 10 users
                    if success_count % 10 == 0:
                        progress = (success_count / total) * 100
                        print(f"   Progress: {success_count}/{total} ({progress:.1f}%)")
                    
                except Exception as e:
                    fail_count += 1
                    print(f"   ❌ Failed to migrate {user_id}: {e}")
                    
                    # Stop if too many failures
                    if fail_count > 10:
                        print("\n❌ Too many failures! Stopping migration...")
                        print(f"   Migrated: {success_count}")
                        print(f"   Failed: {fail_count}")
                        return False
        
        # Final report
        print("\n" + "="*60)
        print("📊 MIGRATION COMPLETE")
        print("="*60)
        print(f"✅ Successfully migrated: {success_count} users")
        print(f"❌ Failed: {fail_count} users")
        print(f"📈 Success rate: {(success_count/total*100):.1f}%")
        
        # Verify
        print("\n🔍 Verifying migration...")
        result = supabase.table('users')\
            .select('telegram_id', count='exact')\
            .execute()
        
        new_total = result.count if hasattr(result, 'count') else 0
        print(f"   Supabase users before: {len(supabase_ids)}")
        print(f"   Supabase users after: {new_total}")
        print(f"   Increase: +{new_total - len(supabase_ids)}")
        
        if new_total >= len(supabase_ids) + success_count:
            print("\n✅ MIGRATION SUCCESSFUL!")
            print(f"   All {success_count} users migrated to Supabase")
            return True
        else:
            print("\n⚠️  VERIFICATION WARNING")
            print("   Some users might not have been migrated")
            print("   Check Supabase dashboard manually")
            return False
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify migration results"""
    print("\n" + "="*60)
    print("🔍 VERIFYING MIGRATION RESULTS")
    print("="*60)
    
    try:
        from services import get_database
        from supabase import create_client
        
        db = get_database()
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(url, service_key)
        
        # Get counts
        local_users = db.get_all_users()
        local_count = len(local_users)
        
        result = supabase.table('users')\
            .select('telegram_id', count='exact')\
            .execute()
        supabase_count = result.count if hasattr(result, 'count') else 0
        
        print(f"\n📊 Final Counts:")
        print(f"   Local DB: {local_count} users")
        print(f"   Supabase: {supabase_count} users")
        
        if supabase_count >= local_count:
            print(f"\n✅ SUCCESS!")
            print(f"   Supabase has {supabase_count - local_count} more users than local")
            print(f"   (This is normal - Supabase may have users from Railway)")
        else:
            print(f"\n⚠️  WARNING")
            print(f"   Supabase has {local_count - supabase_count} fewer users than local")
            print(f"   Some users might not have been migrated")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        return False

def show_migration_summary():
    """Show summary before migration"""
    print("\n" + "="*60)
    print("📋 MIGRATION SUMMARY")
    print("="*60)
    
    try:
        from services import get_database
        from supabase import create_client
        
        db = get_database()
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(url, service_key)
        
        # Get local users
        local_users = db.get_all_users()
        local_ids = set(u.get('telegram_id') for u in local_users if u.get('telegram_id'))
        
        # Get Supabase users
        result = supabase.table('users')\
            .select('telegram_id')\
            .not_.is_('telegram_id', 'null')\
            .neq('telegram_id', 0)\
            .execute()
        supabase_ids = set(u.get('telegram_id') for u in result.data if u.get('telegram_id'))
        
        # Calculate
        only_local = local_ids - supabase_ids
        only_supabase = supabase_ids - local_ids
        in_both = local_ids & supabase_ids
        
        print(f"\n📊 Current Status:")
        print(f"   Local DB: {len(local_ids)} users")
        print(f"   Supabase: {len(supabase_ids)} users")
        print(f"   In both: {len(in_both)} users")
        print(f"   Only in local: {len(only_local)} users")
        print(f"   Only in Supabase: {len(only_supabase)} users")
        
        print(f"\n🎯 After Migration:")
        print(f"   Supabase will have: {len(supabase_ids) + len(only_local)} users")
        print(f"   Increase: +{len(only_local)} users")
        
        print(f"\n📈 Broadcast Impact:")
        print(f"   Before: {len(supabase_ids)} users")
        print(f"   After: {len(supabase_ids) + len(only_local)} users")
        print(f"   Improvement: +{len(only_local)} users ({(len(only_local)/len(supabase_ids)*100):.1f}% increase)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    print("\n🚀 Local to Supabase Migration Tool\n")
    
    # Show summary
    show_migration_summary()
    
    # Confirm
    print("\n" + "="*60)
    print("⚠️  IMPORTANT")
    print("="*60)
    print("This will migrate ALL local users to Supabase")
    print("This is a ONE-WAY operation")
    print("Make sure you have:")
    print("  1. Valid Supabase credentials in .env")
    print("  2. Backup of local database (optional)")
    print("  3. Stable internet connection")
    print("\nPress Enter to START migration, or Ctrl+C to CANCEL...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(0)
    
    # Run migration
    success = migrate_users()
    
    if success:
        # Verify
        verify_migration()
        
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Test broadcast in bot")
        print("2. Verify user count increased")
        print("3. Check Railway logs")
        print("\nBroadcast should now reach ALL users!")
    else:
        print("\n" + "="*60)
        print("❌ MIGRATION FAILED")
        print("="*60)
        print("\nPlease check errors above and try again")
