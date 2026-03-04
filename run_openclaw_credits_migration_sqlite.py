#!/usr/bin/env python3
"""
Run OpenClaw Per-User Credits Migration for SQLite
Creates tables if they don't exist
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Run the migration"""
    
    # Connect to database
    db_path = os.getenv('DATABASE_PATH', 'cryptomentor.db')
    print(f"📂 Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n🔧 Creating OpenClaw per-user credits tables...")
        
        # 1. Per-user credit balances
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openclaw_user_credits (
                user_id INTEGER PRIMARY KEY,
                credits REAL NOT NULL DEFAULT 0.0,
                total_allocated REAL NOT NULL DEFAULT 0.0,
                total_used REAL NOT NULL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created openclaw_user_credits table")
        
        # 2. Credit allocation log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openclaw_credit_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                admin_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                reason TEXT,
                openrouter_balance_before REAL,
                openrouter_balance_after REAL,
                total_allocated_before REAL,
                total_allocated_after REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created openclaw_credit_allocations table")
        
        # 3. Credit usage log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openclaw_credit_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assistant_id TEXT,
                conversation_id TEXT,
                message_id TEXT,
                credits_used REAL NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                model_used TEXT,
                balance_before REAL,
                balance_after REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created openclaw_credit_usage table")
        
        # 4. System balance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openclaw_balance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openrouter_balance REAL NOT NULL,
                total_allocated REAL NOT NULL,
                total_used REAL NOT NULL,
                available_to_allocate REAL NOT NULL,
                user_count INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created openclaw_balance_snapshots table")
        
        # Create indexes
        print("\n🔧 Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_openclaw_user_credits_user ON openclaw_user_credits(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_user ON openclaw_credit_allocations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_admin ON openclaw_credit_allocations(admin_id)",
            "CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_created ON openclaw_credit_allocations(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_openclaw_usage_user ON openclaw_credit_usage(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_openclaw_usage_created ON openclaw_credit_usage(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_openclaw_snapshots_created ON openclaw_balance_snapshots(created_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ Created all indexes")
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Verifying tables...")
        
        # Verify tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'openclaw_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Found {len(tables)} OpenClaw tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   • {table[0]}: {count} rows")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("OpenClaw Per-User Credits Migration (SQLite)")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\n🎯 Next steps:")
        print("  1. Restart bot or Railway service")
        print("  2. Test /admin_system_status")
        print("  3. Test /admin_add_credits <user_id> <amount>")
        print("  4. All OpenClaw commands should work now!")
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED!")
        print("=" * 60)
        print("\nCheck error messages above and fix issues.")
