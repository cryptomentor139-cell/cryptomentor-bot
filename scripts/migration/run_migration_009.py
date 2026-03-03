#!/usr/bin/env python3
"""
Run migration 009: Dual Mode Offline-Online System

This script applies the database migration for the dual-mode feature.
It creates 5 tables with indexes and helper functions.

Usage:
    python run_migration_009.py

Requirements:
    - SUPABASE_URL environment variable
    - SUPABASE_KEY environment variable
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the dual-mode migration."""
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        sys.exit(1)
    
    print("🔄 Connecting to Supabase...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Read migration file
        migration_file = 'migrations/009_dual_mode_offline_online.sql'
        print(f"\n📖 Reading migration file: {migration_file}")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print(f"✅ Migration file loaded ({len(migration_sql)} characters)")
        
        # Execute migration
        print("\n🚀 Executing migration...")
        print("   This may take a few moments...")
        
        # Note: Supabase Python client doesn't support raw SQL execution directly
        # You need to run this migration through Supabase SQL Editor or psql
        print("\n" + "="*70)
        print("⚠️  IMPORTANT: Manual Migration Required")
        print("="*70)
        print("\nThe Supabase Python client doesn't support raw SQL execution.")
        print("Please run this migration using one of these methods:\n")
        
        print("METHOD 1: Supabase SQL Editor (Recommended)")
        print("-" * 70)
        print("1. Open Supabase Dashboard: https://app.supabase.com")
        print("2. Navigate to: SQL Editor")
        print("3. Open file: migrations/009_dual_mode_offline_online.sql")
        print("4. Copy all content")
        print("5. Paste in SQL Editor")
        print("6. Click 'Run' button")
        print("7. Verify success messages\n")
        
        print("METHOD 2: psql Command Line")
        print("-" * 70)
        print("1. Install psql if not already installed")
        print("2. Get your database connection string from Supabase")
        print("3. Run command:")
        print(f"   psql 'YOUR_CONNECTION_STRING' -f {migration_file}\n")
        
        print("METHOD 3: Supabase CLI")
        print("-" * 70)
        print("1. Install Supabase CLI: npm install -g supabase")
        print("2. Login: supabase login")
        print("3. Link project: supabase link --project-ref YOUR_PROJECT_REF")
        print("4. Run migration: supabase db push\n")
        
        print("="*70)
        print("\n📋 Migration Summary:")
        print("-" * 70)
        print("Tables to create: 5")
        print("  1. user_mode_states")
        print("  2. online_sessions")
        print("  3. isolated_ai_agents")
        print("  4. automaton_credit_transactions")
        print("  5. mode_transition_log")
        print("\nIndexes: 20+ for performance optimization")
        print("Functions: 4 helper functions")
        print("  - get_user_mode()")
        print("  - get_active_session()")
        print("  - get_user_credits()")
        print("  - get_mode_stats()")
        print("-" * 70)
        
        print("\n✅ Migration file is ready to be executed")
        print(f"📁 Location: {migration_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def verify_migration():
    """Verify that migration was applied successfully."""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("\n🔍 Verifying migration...")
        
        # Check if tables exist by trying to query them
        tables = [
            'user_mode_states',
            'online_sessions',
            'isolated_ai_agents',
            'automaton_credit_transactions',
            'mode_transition_log'
        ]
        
        tables_exist = 0
        for table in tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ Table '{table}' exists")
                tables_exist += 1
            except Exception as e:
                print(f"  ❌ Table '{table}' not found: {e}")
        
        if tables_exist == 5:
            print(f"\n✅ All {tables_exist} tables verified successfully!")
            return True
        else:
            print(f"\n⚠️  Only {tables_exist}/5 tables found")
            print("   Please run the migration using Supabase SQL Editor")
            return False
            
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        return False


if __name__ == '__main__':
    print("="*70)
    print("Migration 009: Dual Mode Offline-Online System")
    print("="*70)
    
    # Run migration preparation
    success = run_migration()
    
    if success:
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("1. Run the migration using Supabase SQL Editor (see instructions above)")
        print("2. After running, verify with: python run_migration_009.py --verify")
        print("3. Test the database utilities: python -c 'from app.dual_mode_db import *'")
        print("="*70)
    
    # Check if verification requested
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_migration()
