"""
Apply Lineage Migration to Supabase

This script reads the migration SQL and provides instructions for applying it.
Since Supabase Python client doesn't support raw SQL execution,
we'll provide the SQL for manual execution in Supabase Dashboard.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("=" * 70)
    print("LINEAGE SYSTEM MIGRATION - APPLY TO SUPABASE")
    print("=" * 70)
    
    # Read migration SQL
    migration_file = Path(__file__).parent / "migrations" / "005_add_lineage_system.sql"
    
    if not migration_file.exists():
        print(f"\n❌ Migration file not found: {migration_file}")
        return
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"\n✅ Migration file loaded: {migration_file.name}")
    print(f"📝 SQL length: {len(migration_sql)} characters")
    
    # Check if Supabase credentials are set
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("\n⚠️  Supabase credentials not found in .env")
        print("   This is OK - we'll provide manual instructions")
    else:
        print(f"\n✅ Supabase URL: {supabase_url[:30]}...")
        print("✅ Supabase credentials found")
    
    print("\n" + "=" * 70)
    print("MIGRATION SQL CONTENT")
    print("=" * 70)
    print("\n" + migration_sql)
    print("\n" + "=" * 70)
    
    print("\n📋 INSTRUCTIONS TO APPLY MIGRATION:")
    print("-" * 70)
    print("\nOption 1: Supabase Dashboard (RECOMMENDED)")
    print("1. Open Supabase Dashboard: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to SQL Editor (left sidebar)")
    print("4. Click 'New Query'")
    print("5. Copy the SQL above and paste it")
    print("6. Click 'Run' or press Ctrl+Enter")
    print("7. Verify success message")
    
    print("\nOption 2: Using psql (if you have direct database access)")
    print(f"   psql $DATABASE_URL < {migration_file}")
    
    print("\nOption 3: Using Supabase CLI")
    print("   supabase db push")
    
    print("\n" + "=" * 70)
    print("VERIFICATION STEPS")
    print("=" * 70)
    print("\nAfter running the migration, verify:")
    print("1. user_automatons table has new columns:")
    print("   - parent_agent_id")
    print("   - total_children_revenue")
    print("   - autonomous_spawn_enabled")
    print("   - last_autonomous_spawn_at")
    print("   - autonomous_spawn_count")
    print("\n2. lineage_transactions table exists with columns:")
    print("   - id, parent_agent_id, child_agent_id")
    print("   - child_earnings, parent_share, share_percentage")
    print("   - timestamp")
    print("\n3. automaton_transactions has new column:")
    print("   - related_agent_id")
    print("\n4. All indexes created successfully")
    
    print("\n" + "=" * 70)
    print("✅ Migration preparation complete!")
    print("=" * 70)
    
    # Save SQL to a separate file for easy copying
    output_file = Path(__file__).parent / "MIGRATION_005_TO_APPLY.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(migration_sql)
    
    print(f"\n💾 SQL also saved to: {output_file.name}")
    print("   You can copy from this file if needed")
    
    return True

if __name__ == "__main__":
    main()
