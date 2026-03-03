#!/usr/bin/env python3
"""
Run OpenClaw Migration via Railway Shell
This script will be executed on Railway where database is accessible
"""

import os
import sys

def run_migration():
    """Run migration on Railway"""
    try:
        # Import psycopg2 (should be available on Railway)
        import psycopg2
        
        # Get DATABASE_URL from Railway environment
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            # Build from PG variables
            host = os.getenv('PGHOST')
            port = os.getenv('PGPORT', '5432')
            database = os.getenv('PGDATABASE')
            user = os.getenv('PGUSER')
            password = os.getenv('PGPASSWORD')
            
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
        
        print("🔗 Connecting to Railway database...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("📖 Reading migration SQL...")
        migration_sql = """
-- OpenClaw Payment System Tables
-- Manages deposits, credits, and platform fees

-- User credits table
CREATE TABLE IF NOT EXISTS openclaw_credits (
    user_id BIGINT PRIMARY KEY,
    credits DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_deposited DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_spent DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table (deposits)
CREATE TABLE IF NOT EXISTS openclaw_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    transaction_hash VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    platform_fee DECIMAL(10, 2) NOT NULL,
    user_credits DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- Usage log table (credit deductions)
CREATE TABLE IF NOT EXISTS openclaw_usage_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    reason VARCHAR(255),
    model_used VARCHAR(100),
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pending deposits table (awaiting confirmation)
CREATE TABLE IF NOT EXISTS openclaw_pending_deposits (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    deposit_wallet VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- Platform revenue table (admin earnings)
CREATE TABLE IF NOT EXISTS openclaw_platform_revenue (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    admin_wallet VARCHAR(255),
    transferred BOOLEAN DEFAULT FALSE,
    transferred_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat monitoring table (track all attempts)
CREATE TABLE IF NOT EXISTS openclaw_chat_monitor (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(255),
    message TEXT,
    has_credits BOOLEAN DEFAULT FALSE,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    success BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_openclaw_transactions_user ON openclaw_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_transactions_status ON openclaw_transactions(status);
CREATE INDEX IF NOT EXISTS idx_openclaw_transactions_hash ON openclaw_transactions(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_openclaw_usage_user ON openclaw_usage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_pending_user ON openclaw_pending_deposits(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_pending_status ON openclaw_pending_deposits(status);
CREATE INDEX IF NOT EXISTS idx_openclaw_revenue_transferred ON openclaw_platform_revenue(transferred);
CREATE INDEX IF NOT EXISTS idx_openclaw_monitor_user ON openclaw_chat_monitor(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_monitor_credits ON openclaw_chat_monitor(has_credits);
CREATE INDEX IF NOT EXISTS idx_openclaw_monitor_created ON openclaw_chat_monitor(created_at);
"""
        
        print("🚀 Running migration...")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'openclaw%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 OpenClaw tables ({len(tables)}):")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
