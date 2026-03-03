#!/usr/bin/env python3
"""
Run OpenClaw Skills Migration
Adds skill system to OpenClaw AI Assistants
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the OpenClaw skills migration"""
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        sys.exit(1)
    
    print("🔄 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print("🔄 Running migration 011_openclaw_skills.sql...")
        
        # Read migration file
        with open('migrations/011_openclaw_skills.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify tables created
        print("\n📊 Verifying tables...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'openclaw_skill%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Count default skills
        cursor.execute("SELECT COUNT(*) FROM openclaw_skills_catalog")
        skill_count = cursor.fetchone()[0]
        print(f"\n✅ Loaded {skill_count} default skills")
        
        # Show skill categories
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM openclaw_skills_catalog
            GROUP BY category
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        print(f"\n📦 Skills by category:")
        for cat, count in categories:
            print(f"   • {cat}: {count} skills")
        
        # Show free vs premium
        cursor.execute("""
            SELECT 
                CASE WHEN is_premium THEN 'Premium' ELSE 'Free' END as type,
                COUNT(*) as count
            FROM openclaw_skills_catalog
            GROUP BY is_premium
        """)
        
        types = cursor.fetchall()
        print(f"\n💰 Skills by type:")
        for skill_type, count in types:
            print(f"   • {skill_type}: {count} skills")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ OpenClaw Skills System Ready!")
        print("="*60)
        print("\n📚 Available Commands:")
        print("   • /openclaw_skills - Browse available skills")
        print("   • /openclaw_myskills - View installed skills")
        print("   • /openclaw_skill <skill_id> - View skill details")
        print("   • /openclaw_install <skill_id> - Install a skill")
        print("   • /openclaw_toggle <skill_id> - Enable/disable skill")
        print("\n💡 Example:")
        print("   /openclaw_install skill_crypto_analysis")
        print("\n🚀 Start your bot and try the new skill system!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
