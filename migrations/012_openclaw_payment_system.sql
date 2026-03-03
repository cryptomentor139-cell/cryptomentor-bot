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
    confirmed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES openclaw_credits(user_id) ON DELETE CASCADE
);

-- Usage log table (credit deductions)
CREATE TABLE IF NOT EXISTS openclaw_usage_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    reason VARCHAR(255),
    model_used VARCHAR(100),
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES openclaw_credits(user_id) ON DELETE CASCADE
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES openclaw_transactions(id) ON DELETE CASCADE
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

-- Comments
COMMENT ON TABLE openclaw_credits IS 'User credit balances for OpenClaw usage';
COMMENT ON TABLE openclaw_transactions IS 'Deposit transactions with platform fee split';
COMMENT ON TABLE openclaw_usage_log IS 'Log of credit usage and deductions';
COMMENT ON TABLE openclaw_pending_deposits IS 'Pending deposits awaiting blockchain confirmation';
COMMENT ON TABLE openclaw_platform_revenue IS 'Platform fees collected (20% of deposits)';
COMMENT ON TABLE openclaw_chat_monitor IS 'Logs all OpenClaw chat attempts for admin monitoring';

COMMENT ON COLUMN openclaw_transactions.platform_fee IS '20% platform fee from deposit';
COMMENT ON COLUMN openclaw_transactions.user_credits IS '80% credited to user account';
COMMENT ON COLUMN openclaw_platform_revenue.transferred IS 'Whether fee has been transferred to admin wallet';
COMMENT ON COLUMN openclaw_chat_monitor.has_credits IS 'Whether user had credits when attempting to use OpenClaw';
COMMENT ON COLUMN openclaw_chat_monitor.success IS 'Whether the chat request was successful';
