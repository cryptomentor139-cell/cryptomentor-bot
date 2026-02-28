#!/usr/bin/env python3
"""
Backup Supabase Users Table to JSON
Run this BEFORE migration 003
"""

import json
import os
from datetime import datetime

def backup_users_table():
    """Backup users table from Supabase to JSON file"""
    try:
        # Import Supabase client
        from supabase_client import supabase_service
        
        print("🔄 Connecting to Supabase...")
        
        # Get client
        client = supabase_service()
        if not client:
            print("❌ Failed to connect to Supabase")
            return False
        
        # Fetch all users
        print("📥 Fetching all users from Supabase...")
        result = client.table('users').select('*').execute()
        
        if not result.data:
            print("⚠️ No users found in database")
            return False
        
        users = result.data
        total_users = len(users)
        
        print(f"✅ Fetched {total_users} users")
        
        # Count premium users
        premium_count = sum(1 for u in users if u.get('is_premium'))
        lifetime_count = sum(1 for u in users if u.get('is_premium') and u.get('subscription_end') is None)
        
        print(f"📊 Premium users: {premium_count}")
        print(f"📊 Lifetime users: {lifetime_count}")
        
        # Create backup object
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'total_users': total_users,
            'premium_users': premium_count,
            'lifetime_users': lifetime_count,
            'users': users
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_users_before_automaton_{timestamp}.json'
        
        # Save to file
        print(f"💾 Saving backup to {filename}...")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Verify file
        file_size = os.path.getsize(filename)
        print(f"✅ Backup saved: {filename} ({file_size:,} bytes)")
        
        # Create summary
        print("\n" + "=" * 60)
        print("📋 BACKUP SUMMARY")
        print("=" * 60)
        print(f"Backup file: {filename}")
        print(f"Total users: {total_users}")
        print(f"Premium users: {premium_count}")
        print(f"Lifetime users: {lifetime_count}")
        print(f"File size: {file_size:,} bytes")
        print(f"Backup date: {backup_data['backup_date']}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Supabase Users Backup")
    print("=" * 60)
    success = backup_users_table()
    print("=" * 60)
    if success:
        print("✅ Backup completed successfully!")
        print("\n⚠️ IMPORTANT: Keep this backup file safe!")
        print("   You can use it to restore data if migration fails.")
    else:
        print("❌ Backup failed!")
        print("   DO NOT proceed with migration until backup succeeds.")
