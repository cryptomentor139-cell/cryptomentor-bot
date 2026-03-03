-- Migration 009: Dual Mode Offline-Online System
-- Purpose: Enable users to switch between offline (manual trading) and online (AI agent) modes
-- Feature: dual-mode-offline-online
-- Requirements: 1.7, 4.4, 10.2

-- ============================================================================
-- Table 1: user_mode_states
-- Purpose: Track user's current mode and mode transition history
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_mode_states (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    current_mode VARCHAR(20) NOT NULL CHECK (current_mode IN ('offline', 'online')),
    previous_mode VARCHAR(20) CHECK (previous_mode IN ('offline', 'online')),
    last_transition TIMESTAMP NOT NULL DEFAULT NOW(),
    transition_count INTEGER NOT NULL DEFAULT 0,
    offline_state JSONB DEFAULT '{}',
    online_session_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for user_mode_states
CREATE INDEX IF NOT EXISTS idx_user_mode_states_user_id ON user_mode_states(user_id);
CREATE INDEX IF NOT EXISTS idx_user_mode_states_current_mode ON user_mode_states(current_mode);
CREATE INDEX IF NOT EXISTS idx_user_mode_states_last_transition ON user_mode_states(last_transition DESC);

-- Comments for user_mode_states
COMMENT ON TABLE user_mode_states IS 'Tracks user mode state (offline/online) and transition history';
COMMENT ON COLUMN user_mode_states.user_id IS 'Telegram user ID';
COMMENT ON COLUMN user_mode_states.current_mode IS 'Active mode: offline (manual) or online (AI agent)';
COMMENT ON COLUMN user_mode_states.previous_mode IS 'Previous mode before last transition';
COMMENT ON COLUMN user_mode_states.last_transition IS 'Timestamp of last mode change';
COMMENT ON COLUMN user_mode_states.transition_count IS 'Total number of mode transitions';
COMMENT ON COLUMN user_mode_states.offline_state IS 'Preserved offline mode context (JSON)';
COMMENT ON COLUMN user_mode_states.online_session_id IS 'Reference to active online session';

-- ============================================================================
-- Table 2: online_sessions
-- Purpose: Manage isolated AI agent sessions for online mode
-- ============================================================================
CREATE TABLE IF NOT EXISTS online_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP NOT NULL DEFAULT NOW(),
    message_count INTEGER NOT NULL DEFAULT 0,
    credits_used INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed', 'expired')),
    closed_at TIMESTAMP
);

-- Indexes for online_sessions
CREATE INDEX IF NOT EXISTS idx_online_sessions_user_id ON online_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_online_sessions_agent_id ON online_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_online_sessions_status ON online_sessions(status);
CREATE INDEX IF NOT EXISTS idx_online_sessions_created_at ON online_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_online_sessions_last_activity ON online_sessions(last_activity DESC);

-- Comments for online_sessions
COMMENT ON TABLE online_sessions IS 'Manages isolated AI agent sessions for online mode users';
COMMENT ON COLUMN online_sessions.session_id IS 'Unique session identifier';
COMMENT ON COLUMN online_sessions.user_id IS 'Telegram user ID';
COMMENT ON COLUMN online_sessions.agent_id IS 'Isolated AI agent identifier';
COMMENT ON COLUMN online_sessions.created_at IS 'Session creation timestamp';
COMMENT ON COLUMN online_sessions.last_activity IS 'Last user interaction timestamp';
COMMENT ON COLUMN online_sessions.message_count IS 'Total messages in this session';
COMMENT ON COLUMN online_sessions.credits_used IS 'Automaton credits consumed in this session';
COMMENT ON COLUMN online_sessions.status IS 'Session status: active, closed, or expired';
COMMENT ON COLUMN online_sessions.closed_at IS 'Session closure timestamp';

-- ============================================================================
-- Table 3: isolated_ai_agents
-- Purpose: Store isolated AI agent instances per user
-- ============================================================================
CREATE TABLE IF NOT EXISTS isolated_ai_agents (
    agent_id VARCHAR(255) PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    genesis_prompt TEXT NOT NULL,
    conversation_history JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used TIMESTAMP NOT NULL DEFAULT NOW(),
    total_messages INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deleted'))
);

-- Indexes for isolated_ai_agents
CREATE INDEX IF NOT EXISTS idx_isolated_ai_agents_user_id ON isolated_ai_agents(user_id);
CREATE INDEX IF NOT EXISTS idx_isolated_ai_agents_status ON isolated_ai_agents(status);
CREATE INDEX IF NOT EXISTS idx_isolated_ai_agents_last_used ON isolated_ai_agents(last_used DESC);
CREATE INDEX IF NOT EXISTS idx_isolated_ai_agents_created_at ON isolated_ai_agents(created_at DESC);

-- Comments for isolated_ai_agents
COMMENT ON TABLE isolated_ai_agents IS 'Stores isolated AI agent instances - one per user for fair resource allocation';
COMMENT ON COLUMN isolated_ai_agents.agent_id IS 'Unique agent identifier';
COMMENT ON COLUMN isolated_ai_agents.user_id IS 'Owner of this AI agent (unique constraint ensures one agent per user)';
COMMENT ON COLUMN isolated_ai_agents.genesis_prompt IS 'Base system prompt for trading operations';
COMMENT ON COLUMN isolated_ai_agents.conversation_history IS 'Agent conversation history (JSON array)';
COMMENT ON COLUMN isolated_ai_agents.created_at IS 'Agent creation timestamp';
COMMENT ON COLUMN isolated_ai_agents.last_used IS 'Last interaction timestamp';
COMMENT ON COLUMN isolated_ai_agents.total_messages IS 'Total messages processed by this agent';
COMMENT ON COLUMN isolated_ai_agents.status IS 'Agent status: active, inactive, or deleted';

-- ============================================================================
-- Table 4: automaton_credit_transactions
-- Purpose: Track all Automaton credit additions and deductions
-- ============================================================================
CREATE TABLE IF NOT EXISTS automaton_credit_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    admin_id BIGINT,
    session_id UUID REFERENCES online_sessions(session_id)
);

-- Indexes for automaton_credit_transactions
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON automaton_credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_timestamp ON automaton_credit_transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_admin_id ON automaton_credit_transactions(admin_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_session_id ON automaton_credit_transactions(session_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_amount ON automaton_credit_transactions(amount);

-- Comments for automaton_credit_transactions
COMMENT ON TABLE automaton_credit_transactions IS 'Audit trail for all Automaton credit transactions';
COMMENT ON COLUMN automaton_credit_transactions.transaction_id IS 'Unique transaction identifier';
COMMENT ON COLUMN automaton_credit_transactions.user_id IS 'User receiving/spending credits';
COMMENT ON COLUMN automaton_credit_transactions.amount IS 'Credit amount (positive for additions, negative for deductions)';
COMMENT ON COLUMN automaton_credit_transactions.balance_after IS 'User credit balance after transaction';
COMMENT ON COLUMN automaton_credit_transactions.reason IS 'Transaction reason/description';
COMMENT ON COLUMN automaton_credit_transactions.timestamp IS 'Transaction timestamp';
COMMENT ON COLUMN automaton_credit_transactions.admin_id IS 'Admin who initiated transaction (if admin-initiated)';
COMMENT ON COLUMN automaton_credit_transactions.session_id IS 'Related online session (if applicable)';

-- ============================================================================
-- Table 5: mode_transition_log
-- Purpose: Log all mode transitions for monitoring and debugging
-- ============================================================================
CREATE TABLE IF NOT EXISTS mode_transition_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    from_mode VARCHAR(20) CHECK (from_mode IN ('offline', 'online')),
    to_mode VARCHAR(20) NOT NULL CHECK (to_mode IN ('offline', 'online')),
    success BOOLEAN NOT NULL,
    error_message TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for mode_transition_log
CREATE INDEX IF NOT EXISTS idx_mode_transition_log_user_id ON mode_transition_log(user_id);
CREATE INDEX IF NOT EXISTS idx_mode_transition_log_timestamp ON mode_transition_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mode_transition_log_success ON mode_transition_log(success);
CREATE INDEX IF NOT EXISTS idx_mode_transition_log_to_mode ON mode_transition_log(to_mode);

-- Comments for mode_transition_log
COMMENT ON TABLE mode_transition_log IS 'Audit log for all mode transitions (offline ↔ online)';
COMMENT ON COLUMN mode_transition_log.user_id IS 'User performing mode transition';
COMMENT ON COLUMN mode_transition_log.from_mode IS 'Mode before transition (null for first activation)';
COMMENT ON COLUMN mode_transition_log.to_mode IS 'Mode after transition';
COMMENT ON COLUMN mode_transition_log.success IS 'Whether transition completed successfully';
COMMENT ON COLUMN mode_transition_log.error_message IS 'Error details if transition failed';
COMMENT ON COLUMN mode_transition_log.duration_ms IS 'Transition duration in milliseconds';
COMMENT ON COLUMN mode_transition_log.timestamp IS 'Transition timestamp';

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function: Get user's current mode
CREATE OR REPLACE FUNCTION get_user_mode(p_user_id BIGINT)
RETURNS VARCHAR(20) AS $$
DECLARE
    v_mode VARCHAR(20);
BEGIN
    SELECT current_mode INTO v_mode
    FROM user_mode_states
    WHERE user_id = p_user_id;
    
    -- Default to offline if no record exists
    RETURN COALESCE(v_mode, 'offline');
END;
$$ LANGUAGE plpgsql;

-- Function: Get user's active online session
CREATE OR REPLACE FUNCTION get_active_session(p_user_id BIGINT)
RETURNS UUID AS $$
DECLARE
    v_session_id UUID;
BEGIN
    SELECT session_id INTO v_session_id
    FROM online_sessions
    WHERE user_id = p_user_id 
    AND status = 'active'
    ORDER BY last_activity DESC
    LIMIT 1;
    
    RETURN v_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get user's Automaton credit balance
CREATE OR REPLACE FUNCTION get_user_credits(p_user_id BIGINT)
RETURNS INTEGER AS $$
DECLARE
    v_balance INTEGER;
BEGIN
    SELECT balance_after INTO v_balance
    FROM automaton_credit_transactions
    WHERE user_id = p_user_id
    ORDER BY timestamp DESC
    LIMIT 1;
    
    -- Default to 0 if no transactions exist
    RETURN COALESCE(v_balance, 0);
END;
$$ LANGUAGE plpgsql;

-- Function: Get mode transition statistics
CREATE OR REPLACE FUNCTION get_mode_stats()
RETURNS TABLE (
    total_users BIGINT,
    offline_users BIGINT,
    online_users BIGINT,
    active_sessions BIGINT,
    total_transitions BIGINT,
    failed_transitions BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT ums.user_id) as total_users,
        COUNT(DISTINCT CASE WHEN ums.current_mode = 'offline' THEN ums.user_id END) as offline_users,
        COUNT(DISTINCT CASE WHEN ums.current_mode = 'online' THEN ums.user_id END) as online_users,
        COUNT(DISTINCT os.session_id) as active_sessions,
        COUNT(mtl.id) as total_transitions,
        COUNT(CASE WHEN NOT mtl.success THEN 1 END) as failed_transitions
    FROM user_mode_states ums
    LEFT JOIN online_sessions os ON os.user_id = ums.user_id AND os.status = 'active'
    LEFT JOIN mode_transition_log mtl ON mtl.user_id = ums.user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify all tables were created
DO $$
DECLARE
    v_table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'user_mode_states',
        'online_sessions',
        'isolated_ai_agents',
        'automaton_credit_transactions',
        'mode_transition_log'
    );
    
    IF v_table_count = 5 THEN
        RAISE NOTICE '✅ All 5 tables created successfully';
    ELSE
        RAISE WARNING '⚠️ Expected 5 tables, found %', v_table_count;
    END IF;
END $$;

-- Verify all indexes were created
DO $$
DECLARE
    v_index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND tablename IN (
        'user_mode_states',
        'online_sessions',
        'isolated_ai_agents',
        'automaton_credit_transactions',
        'mode_transition_log'
    );
    
    RAISE NOTICE '✅ Created % indexes for performance optimization', v_index_count;
END $$;

-- Verify helper functions were created
DO $$
DECLARE
    v_function_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN (
        'get_user_mode',
        'get_active_session',
        'get_user_credits',
        'get_mode_stats'
    );
    
    IF v_function_count = 4 THEN
        RAISE NOTICE '✅ All 4 helper functions created successfully';
    ELSE
        RAISE WARNING '⚠️ Expected 4 functions, found %', v_function_count;
    END IF;
END $$;

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Migration 009 completed successfully
-- Tables: 5 (user_mode_states, online_sessions, isolated_ai_agents, 
--            automaton_credit_transactions, mode_transition_log)
-- Indexes: 20+ for performance optimization
-- Functions: 4 helper functions for common operations
-- ============================================================================
