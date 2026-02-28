#!/usr/bin/env python3
"""
Run migration 003: Add automaton_access field to users table
"""

import sqlite3
import os

def run_migration():
    """Run the migration to add automaton_access column"""
    db_path = "cryptomentor.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'automaton_access' in columns:
            print("⚠️ Column 'automaton_access' already exists")
        else:
            # Add the column
            cursor.execute("ALTER TABLE users ADD COLUMN automaton_access INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Column 'automaton_access' added successfully")
        
        # Update existing lifetime users to have automatic access
        cursor.execute("""
            UPDATE users 
            SET automaton_access = 1 
            WHERE subscription_end IS NULL AND is_premium = 1
        """)
        affected = cursor.rowcount
        conn.commit()
        print(f"✅ Updated {affected} lifetime users with automatic Automaton access")
        
        # Verify the changes
        cursor.execute("""
            SELECT COUNT(*) FROM users WHERE automaton_access = 1
        """)
        count = cursor.fetchone()[0]
        print(f"📊 Total users with Automaton access: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running migration 003: Add automaton_access field")
    print("=" * 60)
    success = run_migration()
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
