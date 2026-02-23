# Apply Migration 008 to Supabase - Quick Guide

## Step 1: Open Supabase SQL Editor

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "SQL Editor" in left sidebar
4. Click "New query"

## Step 2: Copy & Paste This SQL

```sql
-- ============================================================================
-- MIGRATION 008: ISOLATED AI INSTANCES PER USER
-- Purpose: Enable fair profit distribution with isolated AI instances
-- ============================================================================

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

-- Add comments
COMMENT ON TABLE automaton_agents IS 'Stores AI agent instances - each user has isolated instances';
COMMENT ON COLUMN automaton_agents.user_id IS 'Owner of this AI instance';
COMMENT ON COLUMN automaton_agents.parent_agent_id IS 'Parent agent if this is a spawned child';
COMMENT ON COLUMN automaton_agents.generation IS 'Generation level: 1=main, 2=child, 3=grandchild, etc';
COMMENT ON COLUMN automaton_agents.isolated_balance IS 'Balance specific to this AI instance';
COMMENT ON COLUMN automaton_agents.total_earnings IS 'Total profit earned by this AI instance';
COMMENT ON COLUMN automaton_agents.spawn_threshold IS 'Earnings threshold to spawn child (AI decides)';
COMMENT ON COLUMN automaton_agents.initial_deposit_id IS 'Link to deposit_transactions for main agents (Gen 1)';

-- ============================================================================
-- MIGRATION 008 COMPLETE
-- ============================================================================
```

## Step 3: Execute

Click "Run" button (or press Ctrl+Enter)

## Step 4: Verify

Run this verification query:

```sql
-- Check columns added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'automaton_agents' 
AND column_name IN ('user_id', 'parent_agent_id', 'generation', 'isolated_balance', 'total_earnings', 'spawn_threshold', 'initial_deposit_id')
ORDER BY column_name;
```

Expected output: 7 rows

```sql
-- Check view created
SELECT * FROM user_ai_hierarchy LIMIT 1;
```

Should show columns: agent_id, user_id, username, parent_agent_id, generation, isolated_balance, total_earnings, status, created_at, child_count

```sql
-- Check function created
SELECT * FROM get_user_ai_portfolio(1);
```

Should return: total_balance, total_earnings, agent_count, main_agent_id

## Step 5: Done!

✅ Migration applied successfully!

Now the system will:
- Auto-create isolated AI instance when user deposits
- Track balance separately per user
- Enable fair profit distribution
- Support independent child spawning per user

## Rollback (If Needed)

If something goes wrong, run this:

```sql
-- Remove columns
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS user_id;
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS parent_agent_id;
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS generation;
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS isolated_balance;
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS total_earnings;
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS spawn_threshold;
ALTER TABLE automaton_agents DROP COLUMN IF EXISTS initial_deposit_id;

-- Drop view and function
DROP VIEW IF EXISTS user_ai_hierarchy;
DROP FUNCTION IF EXISTS get_user_ai_portfolio(INTEGER);

-- Drop indexes
DROP INDEX IF EXISTS idx_automaton_agents_user_id;
DROP INDEX IF EXISTS idx_automaton_agents_parent_id;
DROP INDEX IF EXISTS idx_automaton_agents_deposit_id;
```

## Support

If you encounter errors:
1. Check if `automaton_agents` table exists
2. Check if `users` table exists
3. Check if `deposit_transactions` table exists
4. Make sure you're connected to the correct database

## What This Enables

After migration:
- ✅ Each user gets isolated AI instance
- ✅ Fair profit distribution (proportional to deposit)
- ✅ Centralized wallet with database tracking
- ✅ Independent child spawning per user
- ✅ Complete audit trail per user

**System is now ready for production!** 🚀
