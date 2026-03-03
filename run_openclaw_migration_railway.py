#!/usr/bin/env python3
"""
Run OpenClaw Payment System Migration on Railway
"""

import os
import psycopg2

def run_migration():
    """Run the OpenClaw payment system migration"""
    try:
        # Get database connection from environment
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            # Build from individual params
            host = os.getenv('PGHOST', 'ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech')
            port = os.getenv('PGPORT', '5432')
            database = os.getenv('PGDATABASE', 'neondb')
            user = os.getenv('PGUSER', 'neondb_owner')
            password = os.getenv('PGPASSWORD', 'npg_PXo7pTdgJ4ny')
            
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
        
        print(f"🔗 Connecting to database at {host}:{port}...")
        conn = psycopg2.connect(db_url, sslmode='require')
        cursor = conn.cursor()
        
        print("📖 Reading migration file...")
        with open('migrations/012_openclaw_payment_system.sql', 'r') as f:
            migration_sql = f.read()
        
        print("🚀 Running migration...")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name LIKE 'openclaw%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Created {len(tables)} OpenClaw tables:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
