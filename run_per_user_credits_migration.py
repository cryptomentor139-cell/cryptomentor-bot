#!/usr/bin/env python3
"""
Run OpenClaw Per-User Credits Migration
Migrates to per-user credit tracking system
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services import get_database


def run_migration():
    """Run the per-user credits migration"""
    print("🔄 Starting OpenClaw Per-User Credits Migration...")
    
    try:
        db = get_database()
        
        # Read migration file
        migration_file = os.path.join(
            os.path.dirname(__file__),
            'migrations',
            '013_openclaw_per_user_credits.sql'
        )
        
        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print(f"📄 Read migration file: {migration_file}")
        
        # Check if using PostgreSQL or SQLite
        is_postgres = hasattr(db, 'conn') and hasattr(db.conn, 'server_version')
        
        if not is_postgres:
            print("⚠️ Local SQLite detected - migration designed for PostgreSQL")
            print("   This migration should be run on Railway (PostgreSQL)")
            print("   Skipping local migration...")
            return True
        
        # Execute migration (PostgreSQL)
        cursor = db.conn.cursor()
        
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  Executing statement {i}/{len(statements)}...")
                cursor.execute(statement)
        
        db.conn.commit()
        cursor.close()
        
        print("✅ Migration completed successfully!")
        print("\n📊 New tables created:")
        print("  • openclaw_user_credits - Per-user credit balances")
        print("  • openclaw_credit_allocations - Admin allocation log")
        print("  • openclaw_credit_usage - Per-message usage log")
        print("  • openclaw_balance_snapshots - System balance tracking")
        
        print("\n🎯 Next steps:")
        print("  1. Deploy to Railway")
        print("  2. Use /admin_add_credits to allocate credits to users")
        print("  3. Use /admin_system_status to monitor balance")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)

