"""
OpenClaw Auto-Migration
Automatically creates tables if they don't exist
"""

import os
import logging

logger = logging.getLogger(__name__)


def auto_migrate_openclaw(db):
    """
    Auto-create OpenClaw tables if they don't exist
    
    Args:
        db: Database instance
        
    Returns:
        True if migration was run, False if tables already exist
    """
    try:
        cursor = db.cursor
        conn = db.conn
        
        logger.info("🔍 Checking OpenClaw tables...")
        
        # Check if openclaw_skills_catalog table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'openclaw_skills_catalog'
            )
        """)
        
        tables_exist = cursor.fetchone()[0]
        
        if tables_exist:
            logger.info("✅ OpenClaw tables already exist - skipping migration")
            return False
        
        logger.info("🔄 OpenClaw tables not found - running auto-migration...")
        
        # Get path to migration SQL file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(current_dir, '..', 'migrations', '011_openclaw_skills.sql')
        
        # Read migration SQL
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        logger.info("📄 Migration SQL loaded, executing...")
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        logger.info("✅ OpenClaw migration completed successfully!")
        
        # Verify tables created
        cursor.execute("""
            SELECT COUNT(*) FROM openclaw_skills_catalog
        """)
        skill_count = cursor.fetchone()[0]
        
        logger.info(f"✅ Verified: {skill_count} default skills loaded")
        
        return True
        
    except FileNotFoundError as e:
        logger.error(f"❌ Migration SQL file not found: {e}")
        logger.error("   Make sure migrations/011_openclaw_skills.sql exists")
        return False
        
    except Exception as e:
        logger.error(f"❌ OpenClaw auto-migration failed: {e}")
        logger.error("   Bot will continue but OpenClaw features may not work")
        try:
            conn.rollback()
        except:
            pass
        return False


def check_openclaw_ready(db):
    """
    Check if OpenClaw is ready to use
    
    Args:
        db: Database instance
        
    Returns:
        True if OpenClaw tables exist and are ready
    """
    try:
        cursor = db.cursor
        
        # Check if tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'openclaw_skills_catalog'
            )
        """)
        
        return cursor.fetchone()[0]
        
    except Exception as e:
        logger.error(f"Error checking OpenClaw status: {e}")
        return False
