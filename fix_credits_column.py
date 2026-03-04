"""
Fix credits column in openclaw_user_credits table
Add missing 'credits' column and migrate data from 'balance'
"""

import sqlite3
import os

def fix_credits_column():
    """Add credits column and migrate data"""
    
    db_path = os.getenv('DATABASE_PATH', 'cryptomentor.db')
    
    print(f"🔧 Fixing credits column in: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        print("\n1️⃣ Checking current table structure...")
        cursor.execute("PRAGMA table_info(openclaw_user_credits)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        print(f"   Current columns: {column_names}")
        
        # Add credits column if not exists
        if 'credits' not in column_names:
            print("\n2️⃣ Adding 'credits' column...")
            cursor.execute("""
                ALTER TABLE openclaw_user_credits 
                ADD COLUMN credits REAL NOT NULL DEFAULT 0.0
            """)
            print("   ✅ credits column added")
        else:
            print("\n2️⃣ credits column already exists")
        
        # Add total_allocated if not exists
        if 'total_allocated' not in column_names:
            print("\n3️⃣ Adding 'total_allocated' column...")
            cursor.execute("""
                ALTER TABLE openclaw_user_credits 
                ADD COLUMN total_allocated REAL NOT NULL DEFAULT 0.0
            """)
            print("   ✅ total_allocated column added")
        else:
            print("\n3️⃣ total_allocated column already exists")
        
        # Add total_used if not exists
        if 'total_used' not in column_names:
            print("\n4️⃣ Adding 'total_used' column...")
            cursor.execute("""
                ALTER TABLE openclaw_user_credits 
                ADD COLUMN total_used REAL NOT NULL DEFAULT 0.0
            """)
            print("   ✅ total_used column added")
        else:
            print("\n4️⃣ total_used column already exists")
        
        # Migrate data from balance to credits if balance exists
        if 'balance' in column_names and 'credits' in column_names:
            print("\n5️⃣ Migrating data from 'balance' to 'credits'...")
            cursor.execute("""
                UPDATE openclaw_user_credits 
                SET credits = CAST(balance AS REAL) / 1000000.0
                WHERE credits = 0 AND balance > 0
            """)
            rows_updated = cursor.rowcount
            print(f"   ✅ Migrated {rows_updated} rows")
        
        # Migrate data from total_purchased to total_allocated
        if 'total_purchased' in column_names and 'total_allocated' in column_names:
            print("\n6️⃣ Migrating 'total_purchased' to 'total_allocated'...")
            cursor.execute("""
                UPDATE openclaw_user_credits 
                SET total_allocated = CAST(total_purchased AS REAL) / 1000000.0
                WHERE total_allocated = 0 AND total_purchased > 0
            """)
            rows_updated = cursor.rowcount
            print(f"   ✅ Migrated {rows_updated} rows")
        
        # Migrate data from total_spent to total_used
        if 'total_spent' in column_names and 'total_used' in column_names:
            print("\n7️⃣ Migrating 'total_spent' to 'total_used'...")
            cursor.execute("""
                UPDATE openclaw_user_credits 
                SET total_used = CAST(total_spent AS REAL) / 1000000.0
                WHERE total_used = 0 AND total_spent > 0
            """)
            rows_updated = cursor.rowcount
            print(f"   ✅ Migrated {rows_updated} rows")
        
        conn.commit()
        
        # Verify final structure
        print("\n8️⃣ Verifying final structure...")
        cursor.execute("PRAGMA table_info(openclaw_user_credits)")
        columns = cursor.fetchall()
        
        print("   Final columns:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Show sample data
        print("\n9️⃣ Sample data:")
        cursor.execute("""
            SELECT user_id, credits, total_allocated, total_used 
            FROM openclaw_user_credits 
            LIMIT 5
        """)
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"   User {row[0]}: credits=${row[1]:.4f}, allocated=${row[2]:.4f}, used=${row[3]:.4f}")
        else:
            print("   No data yet")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ CREDITS COLUMN FIXED!")
        print("=" * 60)
        print("\n🚀 Now you can use:")
        print("   /admin_add_credits <user_id> <amount> <reason>")
        print("\n💡 Example:")
        print("   /admin_add_credits 1087836223 0.3 coba")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = fix_credits_column()
    sys.exit(0 if success else 1)
