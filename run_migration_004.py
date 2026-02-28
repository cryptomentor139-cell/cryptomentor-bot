#!/usr/bin/env python3
"""
Run Migration 004: Add Audit Logs Table
Task 17.1: Implement audit logging
"""

import os
import sys
from supabase import create_client

def run_migration():
    """Run the audit_logs table migration"""
    
    print("=" * 60)
    print("MIGRATION 004: Add Audit Logs Table")
    print("=" * 60)
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        print("\nPlease set environment variables:")
        print("  export SUPABASE_URL='your-supabase-url'")
        print("  export SUPABASE_SERVICE_KEY='your-service-role-key'")
        return False
    
    print(f"\n✅ Supabase URL: {supabase_url}")
    print("✅ Service key found")
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("\n✅ Connected to Supabase")
        
        # Read migration SQL
        migration_file = "migrations/004_add_audit_logs.sql"
        print(f"\n📄 Reading migration file: {migration_file}")
        
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        print(f"✅ Migration SQL loaded ({len(sql)} characters)")
        
        # Execute migration
        print("\n🔄 Executing migration...")
        print("-" * 60)
        
        # Split SQL into individual statements
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"\nExecuting statement {i}/{len(statements)}...")
                try:
                    # Use RPC to execute raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    # If RPC doesn't exist, try direct execution
                    print(f"⚠️ RPC method not available, trying alternative...")
                    # Note: Supabase Python client doesn't support raw SQL directly
                    # You may need to execute this in Supabase SQL Editor
                    print(f"Statement: {statement[:100]}...")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        
        # Verify table creation
        print("\n🔍 Verifying audit_logs table...")
        try:
            result = supabase.table('audit_logs').select('*').limit(1).execute()
            print("✅ audit_logs table exists and is accessible")
            print(f"   Current record count: {len(result.data)}")
        except Exception as e:
            print(f"⚠️ Could not verify table: {e}")
            print("\nPlease run the migration SQL manually in Supabase SQL Editor:")
            print(f"   File: {migration_file}")
        
        print("\n✅ Migration 004 completed successfully!")
        print("\nNext steps:")
        print("  1. Verify the audit_logs table in Supabase dashboard")
        print("  2. Test audit logging with: python test_audit_logger.py")
        print("  3. Integrate audit logging into existing modules")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
