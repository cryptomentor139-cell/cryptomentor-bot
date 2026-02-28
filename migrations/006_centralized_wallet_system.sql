-- Migration 006: Centralized Wallet System with Conway Integration
-- This migration creates tables for centralized wallet deposit tracking
-- All users deposit to one wallet: 0x63116672bef9f26fd906cd2a57550f7a13925822
-- Conway Dashboard sends webhook notifications for deposits

-- ============================================================================
-- 1. PENDING DEPOSITS TABLE
-- Tracks users waiting for deposit (before they actually deposit)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pending_deposits (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    telegram_username VARCHAR(255),
    telegram_first_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'waiting', -- 'waiting', 'deposited', 'expired'
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours'),
    notified_at TIMESTAMP,
    UNIQUE(user_id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_pending_deposits_user_id ON pending_deposits(user_id);
CREATE INDEX IF NOT EXISTS idx_pending_deposits_status ON pending_deposits(status);

-- ============================================================================
-- 2. DEPOSIT TRANSACTIONS TABLE
-- Tracks all deposits received via Conway webhook
-- ============================================================================
CREATE TABLE IF NOT EXISTS deposit_transactions (
    id BIGSERIAL PRIMARY KEY,
    
    -- Transaction Info
    tx_hash VARCHAR(66) NOT NULL UNIQUE,
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42) NOT NULL DEFAULT '0x63116672bef9f26fd906cd2a57550f7a13925822',
    
    -- Network & Token
    network VARCHAR(20) NOT NULL, -- 'polygon', 'base', 'arbitrum'
    token VARCHAR(10) NOT NULL, -- 'USDT', 'USDC'
    token_contract VARCHAR(42),
    
    -- Amount
    amount DECIMAL(18, 6) NOT NULL,
    amount_usd DECIMAL(18, 2),
    
    -- Conway Credits
    conway_credits DECIMAL(18, 2) DEFAULT 0,
    credit_conversion_rate DECIMAL(10, 2) DEFAULT 100, -- 1 USD = 100 credits
    
    -- User Attribution
    user_id BIGINT, -- NULL until matched
    attributed_at TIMESTAMP,
    attribution_method VARCHAR(50), -- 'webhook_user_id', 'pending_match', 'manual', 'admin'
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'confirmed', 'credited', 'failed'
    confirmations INT DEFAULT 0,
    required_confirmations INT DEFAULT 12,
    
    -- Webhook Data
    webhook_received_at TIMESTAMP DEFAULT NOW(),
    webhook_payload JSONB,
    conway_transaction_id VARCHAR(255),
    
    -- Processing
    processed_at TIMESTAMP,
    credited_at TIMESTAMP,
    error_message TEXT,
    
    -- Timestamps
    block_number BIGINT,
    block_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_deposit_tx_hash ON deposit_transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_deposit_user_id ON deposit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_deposit_status ON deposit_transactions(status);
CREATE INDEX IF NOT EXISTS idx_deposit_from_address ON deposit_transactions(from_address);
CREATE INDEX IF NOT EXISTS idx_deposit_created_at ON deposit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_deposit_conway_tx_id ON deposit_transactions(conway_transaction_id);

-- ============================================================================
-- 3. USER CREDITS BALANCE TABLE
-- Aggregated view of user credits from all deposits
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_credits_balance (
    user_id BIGINT PRIMARY KEY,
    
    -- Deposit Stats
    total_deposits_count INT DEFAULT 0,
    total_deposited_usdt DECIMAL(18, 6) DEFAULT 0,
    total_deposited_usdc DECIMAL(18, 6) DEFAULT 0,
    total_deposited_usd DECIMAL(18, 2) DEFAULT 0,
    
    -- Credits
    total_conway_credits DECIMAL(18, 2) DEFAULT 0,
    available_credits DECIMAL(18, 2) DEFAULT 0,
    spent_credits DECIMAL(18, 2) DEFAULT 0,
    reserved_credits DECIMAL(18, 2) DEFAULT 0, -- For active agents
    
    -- First & Last Deposit
    first_deposit_at TIMESTAMP,
    last_deposit_at TIMESTAMP,
    last_deposit_amount DECIMAL(18, 6),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for queries
CREATE INDEX IF NOT EXISTS idx_user_credits_balance_user_id ON user_credits_balance(user_id);
CREATE INDEX IF NOT EXISTS idx_user_credits_available ON user_credits_balance(available_credits DESC);

-- ============================================================================
-- 4. WEBHOOK LOGS TABLE
-- Logs all webhook calls from Conway Dashboard for debugging
-- ============================================================================
CREATE TABLE IF NOT EXISTS webhook_logs (
    id BIGSERIAL PRIMARY KEY,
    
    -- Webhook Info
    webhook_type VARCHAR(50), -- 'deposit', 'credit_update', 'error'
    webhook_source VARCHAR(50) DEFAULT 'conway_dashboard',
    
    -- Request Data
    request_method VARCHAR(10),
    request_headers JSONB,
    request_body JSONB,
    request_ip VARCHAR(45),
    
    -- Response
    response_status INT,
    response_body JSONB,
    
    -- Processing
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    
    -- Related Records
    deposit_transaction_id BIGINT REFERENCES deposit_transactions(id),
    user_id BIGINT,
    
    -- Timestamps
    received_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_webhook_logs_received_at ON webhook_logs(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_processed ON webhook_logs(processed);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook_type ON webhook_logs(webhook_type);

-- ============================================================================
-- 5. CREDIT TRANSACTIONS TABLE
-- Tracks all credit movements (deposits, spending, refunds)
-- ============================================================================
CREATE TABLE IF NOT EXISTS credit_transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    
    -- Transaction Type
    transaction_type VARCHAR(50) NOT NULL, -- 'deposit', 'spend', 'refund', 'bonus', 'admin_adjustment'
    
    -- Amount
    amount DECIMAL(18, 2) NOT NULL,
    balance_before DECIMAL(18, 2) NOT NULL,
    balance_after DECIMAL(18, 2) NOT NULL,
    
    -- Reference
    reference_type VARCHAR(50), -- 'deposit_transaction', 'agent_spawn', 'agent_action', 'admin'
    reference_id BIGINT,
    description TEXT,
    
    -- Related Deposit
    deposit_transaction_id BIGINT REFERENCES deposit_transactions(id),
    
    -- Metadata
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_credit_tx_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_tx_type ON credit_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_credit_tx_created_at ON credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_tx_deposit_id ON credit_transactions(deposit_transaction_id);

-- ============================================================================
-- 6. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update user_credits_balance when deposit is credited
CREATE OR REPLACE FUNCTION update_user_credits_on_deposit()
RETURNS TRIGGER AS $$
BEGIN
    -- Only process when status changes to 'credited'
    IF NEW.status = 'credited' AND OLD.status != 'credited' AND NEW.user_id IS NOT NULL THEN
        
        -- Insert or update user_credits_balance
        INSERT INTO user_credits_balance (
            user_id,
            total_deposits_count,
            total_deposited_usdt,
            total_deposited_usdc,
            total_deposited_usd,
            total_conway_credits,
            available_credits,
            first_deposit_at,
            last_deposit_at,
            last_deposit_amount,
            updated_at
        ) VALUES (
            NEW.user_id,
            1,
            CASE WHEN NEW.token = 'USDT' THEN NEW.amount ELSE 0 END,
            CASE WHEN NEW.token = 'USDC' THEN NEW.amount ELSE 0 END,
            NEW.amount_usd,
            NEW.conway_credits,
            NEW.conway_credits,
            NEW.credited_at,
            NEW.credited_at,
            NEW.amount,
            NOW()
        )
        ON CONFLICT (user_id) DO UPDATE SET
            total_deposits_count = user_credits_balance.total_deposits_count + 1,
            total_deposited_usdt = user_credits_balance.total_deposited_usdt + 
                CASE WHEN NEW.token = 'USDT' THEN NEW.amount ELSE 0 END,
            total_deposited_usdc = user_credits_balance.total_deposited_usdc + 
                CASE WHEN NEW.token = 'USDC' THEN NEW.amount ELSE 0 END,
            total_deposited_usd = user_credits_balance.total_deposited_usd + NEW.amount_usd,
            total_conway_credits = user_credits_balance.total_conway_credits + NEW.conway_credits,
            available_credits = user_credits_balance.available_credits + NEW.conway_credits,
            last_deposit_at = NEW.credited_at,
            last_deposit_amount = NEW.amount,
            updated_at = NOW();
        
        -- Create credit transaction record
        INSERT INTO credit_transactions (
            user_id,
            transaction_type,
            amount,
            balance_before,
            balance_after,
            reference_type,
            reference_id,
            deposit_transaction_id,
            description,
            created_at
        ) VALUES (
            NEW.user_id,
            'deposit',
            NEW.conway_credits,
            (SELECT available_credits - NEW.conway_credits FROM user_credits_balance WHERE user_id = NEW.user_id),
            (SELECT available_credits FROM user_credits_balance WHERE user_id = NEW.user_id),
            'deposit_transaction',
            NEW.id,
            NEW.id,
            format('Deposit %s %s on %s (tx: %s)', NEW.amount, NEW.token, NEW.network, LEFT(NEW.tx_hash, 10)),
            NOW()
        );
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update credits
DROP TRIGGER IF EXISTS trigger_update_credits_on_deposit ON deposit_transactions;
CREATE TRIGGER trigger_update_credits_on_deposit
    AFTER UPDATE ON deposit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_credits_on_deposit();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for deposit_transactions
DROP TRIGGER IF EXISTS trigger_deposit_transactions_updated_at ON deposit_transactions;
CREATE TRIGGER trigger_deposit_transactions_updated_at
    BEFORE UPDATE ON deposit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_credits_balance
DROP TRIGGER IF EXISTS trigger_user_credits_balance_updated_at ON user_credits_balance;
CREATE TRIGGER trigger_user_credits_balance_updated_at
    BEFORE UPDATE ON user_credits_balance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Recent deposits with user info
CREATE OR REPLACE VIEW v_recent_deposits AS
SELECT 
    dt.id,
    dt.tx_hash,
    dt.user_id,
    dt.amount,
    dt.token,
    dt.network,
    dt.conway_credits,
    dt.status,
    dt.confirmations,
    dt.created_at,
    dt.credited_at,
    ucb.available_credits as user_available_credits,
    ucb.total_deposited_usd as user_total_deposited
FROM deposit_transactions dt
LEFT JOIN user_credits_balance ucb ON dt.user_id = ucb.user_id
ORDER BY dt.created_at DESC;

-- View: User deposit summary
CREATE OR REPLACE VIEW v_user_deposit_summary AS
SELECT 
    user_id,
    COUNT(*) as total_deposits,
    SUM(amount) as total_amount,
    SUM(conway_credits) as total_credits,
    MIN(created_at) as first_deposit,
    MAX(created_at) as last_deposit,
    array_agg(DISTINCT network) as networks_used,
    array_agg(DISTINCT token) as tokens_used
FROM deposit_transactions
WHERE status = 'credited'
GROUP BY user_id;

-- ============================================================================
-- 8. COMMENTS
-- ============================================================================

COMMENT ON TABLE pending_deposits IS 'Users who clicked deposit button but haven''t deposited yet';
COMMENT ON TABLE deposit_transactions IS 'All deposits received to centralized wallet 0x6311...5822';
COMMENT ON TABLE user_credits_balance IS 'Aggregated Conway credits balance per user';
COMMENT ON TABLE webhook_logs IS 'Logs of all webhook calls from Conway Dashboard';
COMMENT ON TABLE credit_transactions IS 'Audit log of all credit movements';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Migration 006 applied successfully
-- No schema_migrations table needed
