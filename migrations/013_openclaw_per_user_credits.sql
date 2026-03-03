-- OpenClaw Per-User Credit Tracking System
-- Each user has their own credit balance allocated by admin
-- Total allocated credits must not exceed OpenRouter balance

-- Per-user credit balances
CREATE TABLE IF NOT EXISTS openclaw_user_credits (
    user_id BIGINT PRIMARY KEY,
    credits DECIMAL(10, 4) NOT NULL DEFAULT 0.0000,
    total_allocated DECIMAL(10, 4) NOT NULL DEFAULT 0.0000,
    total_used DECIMAL(10, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit allocation log (admin adds credits to users)
CREATE TABLE IF NOT EXISTS openclaw_credit_allocations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    admin_id BIGINT NOT NULL,
    amount DECIMAL(10, 4) NOT NULL,
    reason VARCHAR(255),
    openrouter_balance_before DECIMAL(10, 4),
    openrouter_balance_after DECIMAL(10, 4),
    total_allocated_before DECIMAL(10, 4),
    total_allocated_after DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit usage log (per message deduction)
CREATE TABLE IF NOT EXISTS openclaw_credit_usage (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    assistant_id VARCHAR(255),
    conversation_id VARCHAR(255),
    message_id VARCHAR(255),
    credits_used DECIMAL(10, 4) NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    model_used VARCHAR(100),
    balance_before DECIMAL(10, 4),
    balance_after DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System balance tracking (OpenRouter vs Allocated)
CREATE TABLE IF NOT EXISTS openclaw_balance_snapshots (
    id SERIAL PRIMARY KEY,
    openrouter_balance DECIMAL(10, 4) NOT NULL,
    total_allocated DECIMAL(10, 4) NOT NULL,
    total_used DECIMAL(10, 4) NOT NULL,
    available_to_allocate DECIMAL(10, 4) NOT NULL,
    user_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_openclaw_user_credits_user ON openclaw_user_credits(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_user ON openclaw_credit_allocations(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_admin ON openclaw_credit_allocations(admin_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_allocations_created ON openclaw_credit_allocations(created_at);
CREATE INDEX IF NOT EXISTS idx_openclaw_usage_user ON openclaw_credit_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_usage_created ON openclaw_credit_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_openclaw_snapshots_created ON openclaw_balance_snapshots(created_at);

-- Comments
COMMENT ON TABLE openclaw_user_credits IS 'Per-user credit balances allocated by admin from OpenRouter balance';
COMMENT ON TABLE openclaw_credit_allocations IS 'Log of admin credit allocations to users';
COMMENT ON TABLE openclaw_credit_usage IS 'Log of credit deductions per message';
COMMENT ON TABLE openclaw_balance_snapshots IS 'Periodic snapshots of OpenRouter vs allocated balance';

COMMENT ON COLUMN openclaw_user_credits.credits IS 'Current available credits for user';
COMMENT ON COLUMN openclaw_user_credits.total_allocated IS 'Total credits ever allocated to user';
COMMENT ON COLUMN openclaw_user_credits.total_used IS 'Total credits used by user';
COMMENT ON COLUMN openclaw_credit_allocations.openrouter_balance_before IS 'OpenRouter balance before allocation';
COMMENT ON COLUMN openclaw_credit_allocations.total_allocated_before IS 'Total allocated to all users before this allocation';
COMMENT ON COLUMN openclaw_balance_snapshots.available_to_allocate IS 'OpenRouter balance minus total allocated';
