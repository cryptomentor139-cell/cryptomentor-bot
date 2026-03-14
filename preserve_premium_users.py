#!/usr/bin/env python3
"""
Preserve Premium Users - Backup and restore premium user data
"""

import json
import os
from datetime import datetime

def backup_premium_users():
    """Backup premium users to JSON file"""
    try:
        from database import Database
        db = Database()
        
        # Get all premium users
        db.cursor.execute("""
            SELECT telegram_id, username, is_premium, is_lifetime, credits, created_at 
            FROM users 
            WHERE is_premium = 1 OR is_lifetime = 1 OR is_admin = 1
        """)
        
        users = []
        for row in db.cursor.fetchall():
            user_data = {
                "telegram_id": row[0],
                "username": row[1] or "Unknown",
                "is_premium": bool(row[2]),
                "is_lifetime": bool(row[3]),
                "credits": row[4] or 0,
                "created_at": row[5] or datetime.now().isoformat()
            }
            users.append(user_data)
        
        db.close()
        
        # Create backup
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "total_users": len(users),
            "users": users
        }
        
        # Save backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"premium_users_backup_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Premium users backed up to: {filename}")
        print(f"📊 Total users: {len(users)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    backup_premium_users()
