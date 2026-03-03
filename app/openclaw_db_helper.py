"""
OpenClaw Database Helper
Provides database connection for OpenClaw payment system
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


def get_openclaw_db_connection():
    """
    Get PostgreSQL database connection for OpenClaw
    
    Returns:
        Database connection object
    """
    try:
        # Get PostgreSQL connection details from environment
        db_url = os.getenv('DATABASE_URL')
        
        if db_url:
            # Parse DATABASE_URL (Railway format)
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            return conn
        else:
            # Fallback to individual parameters
            conn = psycopg2.connect(
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT', 5432),
                database=os.getenv('PGDATABASE'),
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                cursor_factory=RealDictCursor
            )
            return conn
            
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
    """
    Execute a database query
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch_one: Return single row
        fetch_all: Return all rows
        
    Returns:
        Query result or None
    """
    conn = None
    try:
        conn = get_openclaw_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
            conn.close()
            return result
        elif fetch_all:
            result = cursor.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected
            
    except Exception as e:
        logger.error(f"Database query error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise
