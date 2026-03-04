"""
Fix OpenClaw Credits Database for SQLite
Creates all necessary tables for per-user credit system
"""

import sqlite3
import os
import sys

def fix_openclaw_credits_db():
    """Create OpenClaw credit tables in SQLite database"""
    
    # Get database path
    db_path = os.getenv('DATABASE_PATH', 'cryptomentor.db')
    
    print(f"🔧 Fixing OpenClaw Credits Database: {db_path}")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n1️⃣ Creating openclaw_user_credits table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openclaw_user_credits (
                user_id INTEGER PRIMARY KEY,
                credits REAL NOT NULL DEFAULT 0.0,
                total_allocated REAL NOT NULL DEFAULT 0.0,
                total_used REAL NOT NULL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ openclaw_user_credits table created")
        
        print("\n2️⃣ Creating openclaw_credit_allocations table...")
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ openclaw_credit_allocations table created")
        
        print("\n3️⃣ Creating openclaw_credit_usage table...")
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ openclaw_credit_usage table created")
        
        print("\n4️⃣ Creating openclaw_balance_snapshots table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openclaw_balance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openrouter_balance REAL NOT NULL,
                total_allocated REAL NOT NULL,
                total_used REAL NOT NULL,
                available_to_allocate REAL NOT NULL,
                user_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ openclaw_balance_snapshots table created")
        
        print("\n5️⃣ Creating indexes...")
        
        # Indexes for openclaw_user_credits
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_user_credits_user 
            ON openclaw_user_credits(user_id)
        """)
        
        # Indexes for openclaw_credit_allocations
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_user 
            ON openclaw_credit_allocations(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_admin 
            ON openclaw_credit_allocations(admin_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_created 
            ON openclaw_credit_allocations(created_at)
        """)
        
        # Indexes for openclaw_credit_usage
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_usage_user 
            ON openclaw_credit_usage(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_usage_created 
            ON openclaw_credit_usage(created_at)
        """)
        
        # Indexes for openclaw_balance_snapshots
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_openclaw_snapshots_created 
            ON openclaw_balance_snapshots(created_at)
        """)
        
        print("   ✅ All indexes created")
        
        # Commit changes
        conn.commit()
        
        print("\n6️⃣ Verifying tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'openclaw_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print(f"   Found {len(tables)} OpenClaw tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        print("\n7️⃣ Checking table structure...")
        cursor.execute("PRAGMA table_info(openclaw_user_credits)")
        columns = cursor.fetchall()
        
        print("   openclaw_user_credits columns:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE FIXED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Restart your bot")
        print("2. Test with: /admin_add_credits <user_id> <amount>")
        print("3. User can check: /openclaw_balance")
        print("\n💡 Example:")
        print("   /admin_add_credits 1087836223 0.3 coba")
        print("\n🚀 Ready to commercialize!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fix_openclaw_credits_db()
    sys.exit(0 if success else 1)
