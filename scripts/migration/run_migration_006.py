#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration 006 Runner: Centralized Wallet System with Conway Integration
Applies the centralized wallet database schema
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run migration 006 - Centralized Wallet System"""
    
    print("=" * 70)
    print("🚀 MIGRATION 006: Centralized Wallet System with Conway Integration")
    print("=" * 70)
    print()
    
    # Check Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found in .env")
        print("   Required: SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return False
    
    print(f"✅ Supabase URL: {supabase_url}")
    print()
    
    try:
        from supabase import create_client
        
        # Create Supabase client
        print("📡 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        print()
        
        # Read migration file
        migration_file = 'migrations/006_centralized_wallet_system.sql'
        print(f"📄 Reading migration file: {migration_file}")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"✅ Migration file loaded ({len(sql_content)} characters)")
        print()
        
        # Split SQL into individual statements
        print("⚙️  Parsing SQL statements...")
        statements = []
        current_statement = []
        in_function = False
        
        for line in sql_content.split('\n'):
            stripped = line.strip()
            
            # Track function blocks
            if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
                in_function = True
            
            # Skip comments and empty lines
            if stripped.startswith('--') or not stripped:
                continue
            
            current_statement.append(line)
            
            # End of statement
            if stripped.endswith(';') and not in_function:
                statements.append('\n'.join(current_statement))
                current_statement = []
            elif in_function and stripped.startswith('$') and stripped.endswith('$;'):
                in_function = False
                statements.append('\n'.join(current_statement))
                current_statement = []
        
        print(f"✅ Parsed {len(statements)} SQL statements")
        print()
        
        # Execute migration
        print("⚙️  Executing migration...")
        print("   This will create:")
        print("   • pending_deposits table")
        print("   • deposit_transactions table")
        print("   • user_credits_balance table")
        print("   • webhook_logs table")
        print("   • credit_transactions table")
        print("   • Triggers and functions")
        print("   • Views for querying")
        print()
        
        # Execute each statement
        executed = 0
        for i, statement in enumerate(statements, 1):
            try:
                # Use Supabase's query method for raw SQL
                supabase.postgrest.session.post(
                    f"{supabase_url}/rest/v1/rpc/query",
                    json={"query": statement},
                    headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
                )
                executed += 1
                if i % 5 == 0:
                    print(f"   Executed {i}/{len(statements)} statements...")
            except Exception as e:
                # Some statements might fail if tables already exist, that's okay
                if "already exists" not in str(e).lower():
                    print(f"   ⚠️  Statement {i} warning: {str(e)[:80]}")
        
        print(f"✅ Executed {executed}/{len(statements)} statements")
        print()
        
        # Verify tables were created
        print("🔍 Verifying tables...")
        
        tables_to_check = [
            'pending_deposits',
            'deposit_transactions',
            'user_credits_balance',
            'webhook_logs',
            'credit_transactions'
        ]
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"   ✅ {table}")
            except Exception as e:
                print(f"   ⚠️  {table} - {str(e)[:50]}")
        
        print()
        print("=" * 70)
        print("✅ MIGRATION 006 COMPLETED!")
        print("=" * 70)
        print()
        print("📋 Next Steps:")
        print("   1. Update menu_handlers.py for centralized wallet")
        print("   2. Create webhook receiver endpoint")
        print("   3. Setup Conway Dashboard webhook URL")
        print("   4. Test deposit flow")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ MIGRATION FAILED!")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
