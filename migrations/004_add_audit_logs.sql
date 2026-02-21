-- Migration 004: Add Audit Logs Table
-- Creates audit_logs table for security and compliance logging
-- Task 17.1: Implement audit logging

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event identification
    event_type TEXT NOT NULL CHECK (
        event_type IN (
            'private_key_decryption',
            'admin_operation',
            'fee_collection',
            'withdrawal_request',
            'deposit_detection',
            'agent_spawn'
        )
    ),
    
    -- Timestamp (immutable)
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL,
    
    -- User/Admin identification
    user_id BIGINT,
    admin_id BIGINT,
    
    -- Private key decryption fields
    wallet_address TEXT,
    operation_type TEXT,
    
    -- Admin operation fields
    command TEXT,
    parameters JSONB,
    target_user_id BIGINT,
    
    -- Fee collection fields
    fee_type TEXT CHECK (
        fee_type IS NULL OR 
        fee_type IN ('deposit_fee', 'performance_fee', 'withdrawal_fee', 'spawn_fee')
    ),
    amount DECIMAL(18, 6),
    agent_id UUID,
    
    -- Withdrawal request fields
    to_address TEXT,
    token TEXT,
    status TEXT,
    withdrawal_id UUID,
    
    -- Deposit detection fields
    tx_hash TEXT,
    network TEXT,
    
    -- Agent spawn fields
    agent_name TEXT,
    credits_deducted DECIMAL(18, 2),
    
    -- Operation result
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Additional metadata (flexible JSON)
    metadata JSONB,
    description TEXT,
    
    -- Constraints
    CONSTRAINT positive_amount CHECK (amount IS NULL OR amount >= 0),
    CONSTRAINT positive_credits CHECK (credits_deducted IS NULL OR credits_deducted >= 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_id ON audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_agent_id ON audit_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_wallet_address ON audit_logs(wallet_address);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_timestamp ON audit_logs(event_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp DESC);

-- Add comment to table
COMMENT ON TABLE audit_logs IS 'Immutable audit trail for security and compliance logging';

-- Add comments to key columns
COMMENT ON COLUMN audit_logs.event_type IS 'Type of audited event';
COMMENT ON COLUMN audit_logs.timestamp IS 'Event timestamp (immutable)';
COMMENT ON COLUMN audit_logs.wallet_address IS 'Wallet address for private key operations';
COMMENT ON COLUMN audit_logs.operation_type IS 'Type of operation performed';
COMMENT ON COLUMN audit_logs.command IS 'Admin command executed';
COMMENT ON COLUMN audit_logs.parameters IS 'Sanitized command parameters (sensitive data redacted)';
COMMENT ON COLUMN audit_logs.fee_type IS 'Type of fee collected';
COMMENT ON COLUMN audit_logs.amount IS 'Fee or transaction amount';
COMMENT ON COLUMN audit_logs.metadata IS 'Additional event metadata';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT ON audit_logs TO authenticated;
-- GRANT INSERT ON audit_logs TO service_role;

-- Verification query
SELECT 
    'audit_logs table created successfully' AS status,
    COUNT(*) AS initial_count
FROM audit_logs;
