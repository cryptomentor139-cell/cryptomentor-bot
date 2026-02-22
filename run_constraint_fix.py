"""
Fix database constraint for user_automatons.status
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def fix_constraint():
    """Fix the status constraint in user_automatons table"""
    
    print("="*80)
    print("FIX: Database Constraint - user_automatons.status")
    print("="*80)
    
    # Connect to Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL or SUPABASE_SERVICE_KEY not set")
        return False
    
    print(f"\n✅ Connecting to Supabase: {supabase_url}")
    supabase = create_client(supabase_url, supabase_key)
    
    # Read SQL fix
    with open('fix_database_constraint.sql', 'r') as f:
        sql = f.read()
    
    print("\n📝 SQL to execute:")
    print("-" * 80)
    print(sql)
    print("-" * 80)
    
    try:
        # Execute SQL
        print("\n⏳ Executing SQL...")
        
        # Drop old constraint
        supabase.postgrest.rpc('exec_sql', {
            'sql': 'ALTER TABLE user_automatons DROP CONSTRAINT IF EXISTS user_automatons_status_check'
        }).execute()
        print("✅ Dropped old constraint")
        
        # Add new constraint
        supabase.postgrest.rpc('exec_sql', {
            'sql': "ALTER TABLE user_automatons ADD CONSTRAINT user_automatons_status_check CHECK (status IN ('active', 'paused', 'dead', 'inactive', 'suspended', 'pending'))"
        }).execute()
        print("✅ Added new constraint")
        
        print("\n" + "="*80)
        print("✅ CONSTRAINT FIXED!")
        print("="*80)
        print("""
Valid status values now:
- 'active'    : Agent is running
- 'paused'    : Agent is temporarily stopped  
- 'dead'      : Agent has no credits
- 'inactive'  : Agent is disabled by user
- 'suspended' : Agent is suspended by admin
- 'pending'   : Agent is being created

Next steps:
1. Deploy bot to Railway
2. Test /spawn_agent command
3. Should work without constraint error
        """)
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAlternative: Run SQL manually in Supabase SQL Editor")
        print("1. Go to Supabase Dashboard")
        print("2. SQL Editor")
        print("3. Copy-paste SQL from fix_database_constraint.sql")
        print("4. Execute")
        return False

if __name__ == '__main__':
    fix_constraint()
