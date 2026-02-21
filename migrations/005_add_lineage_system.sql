-- Migration 005: Add Parent-Child Lineage System
-- This migration adds support for agent lineage with parent-child relationships
-- and 10% revenue sharing from children to parents

-- Add lineage-related columns to user_automatons table
ALTER TABLE user_automatons
ADD COLUMN IF NOT EXISTS parent_agent_id UUID REFERENCES user_automatons(id),
ADD COLUMN IF NOT EXISTS total_children_revenue DECIMAL(18, 6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS autonomous_spawn_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS last_autonomous_spawn_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS autonomous_spawn_count INT DEFAULT 0;

-- Add indexes for lineage queries
CREATE INDEX IF NOT EXISTS idx_automaton_parent ON user_automatons(parent_agent_id);
CREATE INDEX IF NOT EXISTS idx_automaton_autonomous_spawn ON user_automatons(last_autonomous_spawn_at);

-- Add constraint to ensure positive children revenue (drop first if exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'positive_children_revenue'
    ) THEN
        ALTER TABLE user_automatons
        ADD CONSTRAINT positive_children_revenue CHECK (total_children_revenue >= 0);
    END IF;
END $$;

-- Create lineage_transactions table for tracking parent-child revenue sharing
CREATE TABLE IF NOT EXISTS lineage_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_agent_id UUID REFERENCES user_automatons(id) NOT NULL,
  child_agent_id UUID REFERENCES user_automatons(id) NOT NULL,
  child_earnings DECIMAL(18, 6) NOT NULL,
  parent_share DECIMAL(18, 6) NOT NULL,
  share_percentage DECIMAL(5, 2) DEFAULT 10.00,
  timestamp TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT positive_amounts CHECK (
    child_earnings > 0 AND 
    parent_share > 0 AND
    parent_share = child_earnings * (share_percentage / 100)
  ),
  CONSTRAINT valid_lineage CHECK (parent_agent_id != child_agent_id)
);

-- Add indexes for lineage_transactions
CREATE INDEX IF NOT EXISTS idx_lineage_parent ON lineage_transactions(parent_agent_id);
CREATE INDEX IF NOT EXISTS idx_lineage_child ON lineage_transactions(child_agent_id);
CREATE INDEX IF NOT EXISTS idx_lineage_timestamp ON lineage_transactions(timestamp);

-- Update automaton_transactions type enum to include lineage_share
-- Drop the old constraint if it exists, then add new one
DO $$ 
BEGIN
    -- Drop old constraint if exists
    IF EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'automaton_transactions_type_check'
    ) THEN
        ALTER TABLE automaton_transactions DROP CONSTRAINT automaton_transactions_type_check;
    END IF;
    
    -- Add new constraint with lineage_share type
    ALTER TABLE automaton_transactions
    ADD CONSTRAINT automaton_transactions_type_check CHECK (
      type IN ('spawn', 'fund', 'earn', 'spend', 'performance_fee', 'platform_fee', 'lineage_share')
    );
END $$;

-- Add related_agent_id column to automaton_transactions for lineage tracking
ALTER TABLE automaton_transactions
ADD COLUMN IF NOT EXISTS related_agent_id UUID REFERENCES user_automatons(id);

-- Add index for related_agent_id
CREATE INDEX IF NOT EXISTS idx_transaction_related_agent ON automaton_transactions(related_agent_id);

-- Add comment to explain the lineage system
COMMENT ON TABLE lineage_transactions IS 'Tracks parent-child revenue sharing where parents receive 10% of children earnings';
COMMENT ON COLUMN user_automatons.parent_agent_id IS 'Reference to parent agent if this agent was spawned from another agent';
COMMENT ON COLUMN user_automatons.total_children_revenue IS 'Total credits received from all children via 10% revenue sharing';
COMMENT ON COLUMN user_automatons.autonomous_spawn_enabled IS 'Whether this agent can autonomously spawn children when it has sufficient credits';
COMMENT ON COLUMN user_automatons.last_autonomous_spawn_at IS 'Timestamp of last autonomous spawn for rate limiting';
COMMENT ON COLUMN user_automatons.autonomous_spawn_count IS 'Total number of children spawned autonomously by this agent';
