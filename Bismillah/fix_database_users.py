
#!/usr/bin/env python3
"""
Fix common database user issues for CryptoMentor AI
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
except ImportError as e:
    print(f"❌ Failed to import Database: {e}")
    sys.exit(1)

def fix_database_users():
    """Fix common database user issues"""
    print("🔧 CryptoMentor AI - Database User Fix")
    print("=" * 50)

    try:
        # Initialize database
        db = Database()
        print("✅ Database connection established")

        # Check current status
        print("\n📊 Current Database Status:")

        # Total users
        db.cursor.execute("SELECT COUNT(*) FROM users")
        total_users = db.cursor.fetchone()[0]
        print(f"👥 Total users: {total_users}")

        # Users with NULL telegram_id
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NULL OR telegram_id = 0")
        null_telegram_id = db.cursor.fetchone()[0]
        print(f"❌ NULL telegram_id: {null_telegram_id}")

        # Users with NULL credits
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE credits IS NULL")
        null_credits = db.cursor.fetchone()[0]
        print(f"💳 NULL credits: {null_credits}")

        # Users with negative credits
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE credits < 0")
        negative_credits = db.cursor.fetchone()[0]
        print(f"➖ Negative credits: {negative_credits}")

        # Start fixing issues
        print("\n🔧 Fixing database issues...")

        # Fix NULL credits
        if null_credits > 0:
            db.cursor.execute("UPDATE users SET credits = 100 WHERE credits IS NULL")
            db.connection.commit()
            print(f"✅ Fixed {null_credits} users with NULL credits (set to 100)")

        # Fix negative credits
        if negative_credits > 0:
            db.cursor.execute("UPDATE users SET credits = 10 WHERE credits < 0")
            db.connection.commit()
            print(f"✅ Fixed {negative_credits} users with negative credits (set to 10)")

        # Remove users with invalid telegram_id
        if null_telegram_id > 0:
            db.cursor.execute("DELETE FROM users WHERE telegram_id IS NULL OR telegram_id = 0")
            db.connection.commit()
            print(f"✅ Removed {null_telegram_id} users with invalid telegram_id")

        # Final status check
        print("\n📊 Final Database Status:")
        
        db.cursor.execute("SELECT COUNT(*) FROM users")
        final_total = db.cursor.fetchone()[0]
        
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
        premium_users = db.cursor.fetchone()[0]
        
        db.cursor.execute("SELECT SUM(credits) FROM users")
        total_credits = db.cursor.fetchone()[0] or 0

        print(f"📊 Final total users: {final_total}")
        print(f"👥 Valid users: {final_total}")
        print(f"⭐ Premium users: {premium_users}")
        print(f"💰 Total credits: {total_credits}")

        print("\n✅ Database user issues fixed successfully!")

        # Close database connection
        db.close()

    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_database_users()
