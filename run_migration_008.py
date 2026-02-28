"""
Run Migration 008: Isolated AI Instances
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def run_migration():
    """Apply migration 008 to add isolated AI instance support"""
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print("🔄 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Connected to database")
        print("📝 Reading migration file...")
        
        # Read migration SQL
        with open('migrations/008_isolated_ai_instances.sql', 'r') as f:
            migration_sql = f.read()
        
        print("🚀 Applying migration 008...")
        
        # Execute migration
        cursor.execute(migration_sql)
        
        # Verify tables were updated
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'automaton_agents' 
            AND column_name IN ('user_id', 'parent_agent_id', 'generation', 'isolated_balance', 'total_earnings')
        """)
        
        columns = cursor.fetchall()
        print(f"\n✅ Added {len(columns)} new columns to automaton_agents:")
        for col in columns:
            print(f"   - {col['column_name']}")
        
        # Verify view was created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_name = 'user_ai_hierarchy'
        """)
        
        view = cursor.fetchone()
        if view:
            print(f"✅ Created view: {view['table_name']}")
        
        # Verify function was created
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_name = 'get_user_ai_portfolio'
        """)
        
        func = cursor.fetchone()
        if func:
            print(f"✅ Created function: {func['routine_name']}")
        
        # Commit transaction
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ Migration 008 applied successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Test with: python test_isolated_ai.py")
        print("2. Integrate with bot handlers")
        print("3. Deploy to Railway")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("="*60)
    print("MIGRATION 008: ISOLATED AI INSTANCES")
    print("="*60)
    print("\nThis migration adds support for:")
    print("- User-specific AI instances")
    print("- Fair profit distribution")
    print("- Independent child spawning per user")
    print("- Multi-generation agent hierarchy")
    print("\n" + "="*60)
    
    confirm = input("\nApply migration? (yes/no): ")
    
    if confirm.lower() == 'yes':
        success = run_migration()
        exit(0 if success else 1)
    else:
        print("❌ Migration cancelled")
        exit(1)
