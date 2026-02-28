"""
Run Migration 005: Add Lineage System

This script applies the lineage system migration which adds:
- parent_agent_id column to user_automatons
- total_children_revenue tracking
- autonomous spawning fields
- lineage_transactions table
- related_agent_id for transaction tracking
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.supabase_conn import get_supabase_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_migration():
    """Execute migration 005"""
    print("=" * 60)
    print("Migration 005: Add Lineage System")
    print("=" * 60)
    
    # Read migration SQL
    migration_file = Path(__file__).parent / "migrations" / "005_add_lineage_system.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    print(f"\n📄 Migration file: {migration_file}")
    print(f"📝 SQL length: {len(migration_sql)} characters")
    
    # Get Supabase client
    try:
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Execute migration
    print("\n🚀 Executing migration...")
    print("-" * 60)
    
    try:
        # Split SQL into individual statements
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"\n[{i}/{len(statements)}] Executing statement...")
                # Show first 100 chars of statement
                preview = statement[:100].replace('\n', ' ')
                print(f"   {preview}...")
                
                # Execute via RPC (Supabase doesn't support direct SQL execution)
                # We need to use the SQL editor or run this directly in Supabase
                print(f"   ⚠️  Please run this statement in Supabase SQL Editor")
        
        print("\n" + "=" * 60)
        print("✅ Migration 005 prepared successfully!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Open Supabase Dashboard → SQL Editor")
        print("2. Copy the SQL from migrations/005_add_lineage_system.sql")
        print("3. Execute the SQL in the editor")
        print("4. Verify tables and columns were created")
        print("\n💡 Or run the SQL directly using psql:")
        print(f"   psql $DATABASE_URL < {migration_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
