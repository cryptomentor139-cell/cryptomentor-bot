-- Migration 010: OpenClaw Claude AI Assistant
-- Purpose: Enable personal AI Assistant with Claude Sonnet 4.5
-- Platform Fee: 20% for sustainability, 80% for LLM usage

-- OpenClaw AI Assistants
CREATE TABLE IF NOT EXISTS openclaw_assistants (
    assistant_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    personality TEXT DEFAULT 'friendly',
    system_prompt TEXT,
    memory_context TEXT,
    total_tokens_used BIGINT DEFAULT 0,
    total_credits_spent DECIMAL(20,8) DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'deleted')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OpenClaw Conversations
CREATE TABLE IF NOT EXISTS openclaw_conversations (
    conversation_id TEXT PRIMARY KEY,
    assistant_id TEXT NOT NULL REFERENCES openclaw_assistants(assistant_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT,
    context_summary TEXT,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_credits_spent DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OpenClaw Messages
CREATE TABLE IF NOT EXISTS openclaw_messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES openclaw_conversations(conversation_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    credits_cost DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OpenClaw Credit Transactions (with 20% platform fee)
CREATE TABLE IF NOT EXISTS openclaw_credit_transactions (
    transaction_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount_usdc DECIMAL(20,8) NOT NULL,
    platform_fee DECIMAL(20,8) NOT NULL, -- 20% of amount_usdc
    net_credits INTEGER NOT NULL, -- 80% converted to credits (1 USDC = 100 credits)
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'bonus')),
    description TEXT,
    conversation_id TEXT REFERENCES openclaw_conversations(conversation_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Platform Revenue Tracking
CREATE TABLE IF NOT EXISTS platform_revenue (
    revenue_id TEXT PRIMARY KEY,
    source TEXT NOT NULL, -- 'openclaw_fee', 'automaton_fee', etc
    amount_usdc DECIMAL(20,8) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    transaction_id TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OpenClaw User Credits Balance
CREATE TABLE IF NOT EXISTS openclaw_user_credits (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    balance INTEGER DEFAULT 0,
    total_purchased INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_openclaw_assistants_user_id ON openclaw_assistants(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_assistants_status ON openclaw_assistants(status);
CREATE INDEX IF NOT EXISTS idx_openclaw_conversations_assistant_id ON openclaw_conversations(assistant_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_conversations_user_id ON openclaw_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_messages_conversation_id ON openclaw_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_messages_created_at ON openclaw_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_openclaw_credit_transactions_user_id ON openclaw_credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_credit_transactions_type ON openclaw_credit_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_platform_revenue_source ON platform_revenue(source);
CREATE INDEX IF NOT EXISTS idx_platform_revenue_created_at ON platform_revenue(created_at);

-- Views for analytics

-- User AI Assistant Portfolio
CREATE OR REPLACE VIEW openclaw_user_portfolio AS
SELECT 
    u.id as user_id,
    u.username,
    uc.balance as credits_balance,
    uc.total_purchased,
    uc.total_spent,
    COUNT(DISTINCT a.assistant_id) as assistant_count,
    COUNT(DISTINCT c.conversation_id) as conversation_count,
    COALESCE(SUM(c.message_count), 0) as total_messages,
    COALESCE(SUM(c.total_tokens), 0) as total_tokens,
    COALESCE(SUM(c.total_credits_spent), 0) as total_credits_spent
FROM users u
LEFT JOIN openclaw_user_credits uc ON u.id = uc.user_id
LEFT JOIN openclaw_assistants a ON u.id = a.user_id AND a.status = 'active'
LEFT JOIN openclaw_conversations c ON a.assistant_id = c.assistant_id
GROUP BY u.id, u.username, uc.balance, uc.total_purchased, uc.total_spent;

-- Platform Revenue Summary
CREATE OR REPLACE VIEW platform_revenue_summary AS
SELECT 
    source,
    COUNT(*) as transaction_count,
    SUM(amount_usdc) as total_revenue,
    AVG(amount_usdc) as avg_revenue,
    MIN(created_at) as first_transaction,
    MAX(created_at) as last_transaction
FROM platform_revenue
GROUP BY source;

-- OpenClaw Usage Statistics
CREATE OR REPLACE VIEW openclaw_usage_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_messages,
    SUM(input_tokens + output_tokens) as total_tokens,
    SUM(credits_cost) as total_credits_spent,
    AVG(input_tokens + output_tokens) as avg_tokens_per_message
FROM openclaw_messages
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Functions

-- Get user OpenClaw credits
CREATE OR REPLACE FUNCTION get_openclaw_credits(p_user_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_balance INTEGER;
BEGIN
    SELECT balance INTO v_balance
    FROM openclaw_user_credits
    WHERE user_id = p_user_id;
    
    IF v_balance IS NULL THEN
        -- Initialize user credits if not exists
        INSERT INTO openclaw_user_credits (user_id, balance)
        VALUES (p_user_id, 0)
        ON CONFLICT (user_id) DO NOTHING;
        RETURN 0;
    END IF;
    
    RETURN v_balance;
END;
$$ LANGUAGE plpgsql;

-- Add OpenClaw credits (with platform fee)
CREATE OR REPLACE FUNCTION add_openclaw_credits(
    p_user_id INTEGER,
    p_amount_usdc DECIMAL(20,8),
    p_platform_fee_pct DECIMAL(5,4) DEFAULT 0.20
)
RETURNS TABLE (
    net_credits INTEGER,
    platform_fee DECIMAL(20,8),
    transaction_id TEXT
) AS $$
DECLARE
    v_platform_fee DECIMAL(20,8);
    v_net_amount DECIMAL(20,8);
    v_net_credits INTEGER;
    v_transaction_id TEXT;
BEGIN
    -- Calculate platform fee (20%)
    v_platform_fee := p_amount_usdc * p_platform_fee_pct;
    v_net_amount := p_amount_usdc - v_platform_fee;
    v_net_credits := FLOOR(v_net_amount * 100); -- 1 USDC = 100 credits
    
    -- Generate transaction ID
    v_transaction_id := 'OCT-' || p_user_id || '-' || EXTRACT(EPOCH FROM NOW())::BIGINT;
    
    -- Insert credit transaction
    INSERT INTO openclaw_credit_transactions (
        transaction_id, user_id, amount_usdc, platform_fee,
        net_credits, transaction_type, description
    ) VALUES (
        v_transaction_id, p_user_id, p_amount_usdc, v_platform_fee,
        v_net_credits, 'purchase',
        'Credit purchase: ' || p_amount_usdc || ' USDC (20% platform fee)'
    );
    
    -- Record platform revenue
    INSERT INTO platform_revenue (
        revenue_id, source, amount_usdc, user_id, transaction_id, description
    ) VALUES (
        'REV-' || v_transaction_id,
        'openclaw_fee',
        v_platform_fee,
        p_user_id,
        v_transaction_id,
        '20% platform fee from OpenClaw credit purchase'
    );
    
    -- Update user credits
    INSERT INTO openclaw_user_credits (user_id, balance, total_purchased)
    VALUES (p_user_id, v_net_credits, v_net_credits)
    ON CONFLICT (user_id) DO UPDATE SET
        balance = openclaw_user_credits.balance + v_net_credits,
        total_purchased = openclaw_user_credits.total_purchased + v_net_credits,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN QUERY SELECT v_net_credits, v_platform_fee, v_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- Deduct OpenClaw credits
CREATE OR REPLACE FUNCTION deduct_openclaw_credits(
    p_user_id INTEGER,
    p_credits INTEGER,
    p_conversation_id TEXT,
    p_description TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_balance INTEGER;
    v_transaction_id TEXT;
BEGIN
    -- Get current balance
    v_current_balance := get_openclaw_credits(p_user_id);
    
    -- Check sufficient balance
    IF v_current_balance < p_credits THEN
        RAISE EXCEPTION 'Insufficient credits. Balance: %, Required: %', v_current_balance, p_credits;
    END IF;
    
    -- Generate transaction ID
    v_transaction_id := 'OCU-' || p_user_id || '-' || EXTRACT(EPOCH FROM NOW())::BIGINT;
    
    -- Insert usage transaction
    INSERT INTO openclaw_credit_transactions (
        transaction_id, user_id, amount_usdc, platform_fee,
        net_credits, transaction_type, description, conversation_id
    ) VALUES (
        v_transaction_id, p_user_id, p_credits / 100.0, 0,
        -p_credits, 'usage', p_description, p_conversation_id
    );
    
    -- Update user credits
    UPDATE openclaw_user_credits
    SET 
        balance = balance - p_credits,
        total_spent = total_spent + p_credits,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE openclaw_assistants IS 'Personal AI Assistants using Claude Sonnet 4.5';
COMMENT ON TABLE openclaw_conversations IS 'Conversation threads with AI Assistants';
COMMENT ON TABLE openclaw_messages IS 'Individual messages in conversations';
COMMENT ON TABLE openclaw_credit_transactions IS 'Credit transactions with 20% platform fee';
COMMENT ON TABLE platform_revenue IS 'Platform revenue from fees (20% OpenClaw, etc)';
COMMENT ON TABLE openclaw_user_credits IS 'User credit balances for OpenClaw';

COMMENT ON COLUMN openclaw_credit_transactions.platform_fee IS '20% platform fee for sustainability';
COMMENT ON COLUMN openclaw_credit_transactions.net_credits IS '80% of purchase converted to credits';
