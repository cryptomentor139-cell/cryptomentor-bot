
#!/usr/bin/env python3
"""
Import premium users backup ke Supabase
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.supabase_conn import sb_client, _env, _headers

def import_premium_backup():
    """Import premium users from backup JSON to Supabase"""
    try:
        # Load backup JSON
        backup_file = "premium_users_backup_20250802_130229.json"
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        premium_users = backup_data.get('premium_users', [])
        print(f"Found {len(premium_users)} premium users in backup")
        
        url, key, rest = _env()
        if not url or not key:
            print("❌ Supabase credentials not found")
            return
        
        imported_count = 0
        updated_count = 0
        
        for user in premium_users:
            try:
                telegram_id = user['telegram_id']
                
                # Prepare user data for Supabase
                user_data = {
                    'telegram_id': telegram_id,
                    'first_name': user.get('first_name', ''),
                    'username': user.get('username', 'no_username'),
                    'is_premium': True,
                    'premium_until': user.get('subscription_end'),  # null for lifetime
                    'banned': False,
                    'created_at': user.get('created_at', datetime.now().isoformat())
                }
                
                # Upsert to Supabase
                import requests
                response = requests.post(
                    f"{rest}/users",
                    headers={
                        **_headers(key),
                        "Prefer": "resolution=merge-duplicates"
                    },
                    json=user_data,
                    timeout=20
                )
                
                if response.status_code in (200, 201):
                    imported_count += 1
                    if user.get('subscription_end') is None:
                        print(f"✅ Imported lifetime user: {telegram_id} ({user.get('first_name')})")
                    else:
                        print(f"✅ Imported timed user: {telegram_id} ({user.get('first_name')})")
                else:
                    print(f"❌ Failed to import {telegram_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error importing user {user.get('telegram_id')}: {e}")
        
        print(f"\n📊 Import Summary:")
        print(f"• Total processed: {len(premium_users)}")
        print(f"• Successfully imported: {imported_count}")
        print(f"• Failed: {len(premium_users) - imported_count}")
        
    except Exception as e:
        print(f"❌ Error during import: {e}")

if __name__ == "__main__":
    import_premium_backup()
