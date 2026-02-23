-- Migration 008: Isolated AI Instances Per User
-- Purpose: Enable fair profit distribution by giving each user their own AI instance

-- Add user_id to link agents to specific users
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);

-- Add parent_agent_id to track child agents
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS parent_agent_id TEXT REFERENCES automaton_agents(agent_id);

-- Add generation to track AI hierarchy depth
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS generation INTEGER DEFAULT 1;

-- Add isolated_balance to track per-user AI balance
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS isolated_balance DECIMAL(20,8) DEFAULT 0;

-- Add total_earnings to track when to spawn children
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS total_earnings DECIMAL(20,8) DEFAULT 0;

-- Add spawn_threshold (AI decides, but we track it)
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS spawn_threshold DECIMAL(20,8);

-- Link to initial deposit from centralized wallet
ALTER TABLE automaton_agents 
ADD COLUMN IF NOT EXISTS initial_deposit_id BIGINT REFERENCES deposit_transactions(id);

-- Create index for faster user agent lookups
CREATE INDEX IF NOT EXISTS idx_automaton_agents_user_id ON automaton_agents(user_id);
CREATE INDEX IF NOT EXISTS idx_automaton_agents_parent_id ON automaton_agents(parent_agent_id);
CREATE INDEX IF NOT EXISTS idx_automaton_agents_deposit_id ON automaton_agents(initial_deposit_id);

-- Create view for user AI hierarchy
CREATE OR REPLACE VIEW user_ai_hierarchy AS
SELECT 
    a.agent_id,
    a.user_id,
    u.username,
    a.parent_agent_id,
    a.generation,
    a.isolated_balance,
    a.total_earnings,
    a.status,
    a.created_at,
    COUNT(children.agent_id) as child_count
FROM automaton_agents a
LEFT JOIN users u ON a.user_id = u.id
LEFT JOIN automaton_agents children ON children.parent_agent_id = a.agent_id
GROUP BY a.agent_id, a.user_id, u.username, a.parent_agent_id, 
         a.generation, a.isolated_balance, a.total_earnings, a.status, a.created_at;

-- Create function to get user's total AI portfolio value
CREATE OR REPLACE FUNCTION get_user_ai_portfolio(p_user_id INTEGER)
RETURNS TABLE (
    total_balance DECIMAL(20,8),
    total_earnings DECIMAL(20,8),
    agent_count INTEGER,
    main_agent_id TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(isolated_balance), 0) as total_balance,
        COALESCE(SUM(total_earnings), 0) as total_earnings,
        COUNT(*)::INTEGER as agent_count,
        MIN(CASE WHEN generation = 1 THEN agent_id END) as main_agent_id
    FROM automaton_agents
    WHERE user_id = p_user_id AND status = 'active';
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE automaton_agents IS 'Stores AI agent instances - each user has isolated instances';
COMMENT ON COLUMN automaton_agents.user_id IS 'Owner of this AI instance';
COMMENT ON COLUMN automaton_agents.parent_agent_id IS 'Parent agent if this is a spawned child';
COMMENT ON COLUMN automaton_agents.generation IS 'Generation level: 1=main, 2=child, 3=grandchild, etc';
COMMENT ON COLUMN automaton_agents.isolated_balance IS 'Balance specific to this AI instance';
COMMENT ON COLUMN automaton_agents.total_earnings IS 'Total profit earned by this AI instance';
COMMENT ON COLUMN automaton_agents.spawn_threshold IS 'Earnings threshold to spawn child (AI decides)';
COMMENT ON COLUMN automaton_agents.initial_deposit_id IS 'Link to deposit_transactions for main agents (Gen 1)';
