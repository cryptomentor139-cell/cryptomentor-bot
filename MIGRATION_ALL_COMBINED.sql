-- ============================================================================
-- COMBINED MIGRATION: 002 + 005
-- ============================================================================
-- This script combines:
-- - Migration 002: Simplified Automaton tables
-- - Migration 005: Parent-Child Lineage System
--
-- Run this ONCE in Supabase SQL Editor if you haven't run any migrations yet
-- ============================================================================

-- ============================================================================
-- PART 1: MIGRATION 002 - Simplified Automaton Tables
-- ============================================================================

-- TABLE 1: user_automatons
CREATE TABLE IF NOT EXISTS user_automatons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT NOT NULL,
  agent_wallet TEXT UNIQUE NOT NULL,
  agent_name TEXT NOT NULL,
  conway_deposit_address TEXT UNIQUE NOT NULL,
  genesis_prompt TEXT,
  conway_credits DECIMAL(18, 2) DEFAULT 0,
  survival_tier TEXT DEFAULT 'normal' CHECK (
    survival_tier IN ('normal', 'low_compute', 'critical', 'dead')
  ),
  created_at TIMESTAMP DEFAULT NOW(),
  last_active TIMESTAMP DEFAULT NOW(),
  status TEXT DEFAULT 'active' CHECK (
    status IN ('active', 'paused', 'dead')
  ),
  total_earnings DECIMAL(18, 6) DEFAULT 0,
  total_expenses DECIMAL(18, 6) DEFAULT 0,
  
  CONSTRAINT positive_credits CHECK (conway_credits >= 0),
  CONSTRAINT positive_earnings CHECK (total_earnings >= 0),
  CONSTRAINT positive_expenses CHECK (total_expenses >= 0)
);

-- Indexes for user_automatons
CREATE INDEX IF NOT EXISTS idx_automaton_user_id ON user_automatons(user_id);
CREATE INDEX IF NOT EXISTS idx_automaton_wallet ON user_automatons(agent_wallet);
CREATE INDEX IF NOT EXISTS idx_automaton_deposit_address ON user_automatons(conway_deposit_address);
CREATE INDEX IF NOT EXISTS idx_automaton_status ON user_automatons(status);
CREATE INDEX IF NOT EXISTS idx_automaton_survival_tier ON user_automatons(survival_tier);
CREATE INDEX IF NOT EXISTS idx_automaton_created_at ON user_automatons(created_at);

-- TABLE 2: automaton_transactions
CREATE TABLE IF NOT EXISTS automaton_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  automaton_id UUID REFERENCES user_automatons(id) NOT NULL,
  type TEXT NOT NULL CHECK (
    type IN ('spawn', 'deposit', 'earn', 'spend', 'performance_fee', 'platform_fee')
  ),
  amount DECIMAL(18, 6) NOT NULL,
  description TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT non_zero_amount CHECK (amount != 0)
);

-- Indexes for automaton_transactions
CREATE INDEX IF NOT EXISTS idx_transaction_automaton_id ON automaton_transactions(automaton_id);
CREATE INDEX IF NOT EXISTS idx_transaction_type ON automaton_transactions(type);
CREATE INDEX IF NOT EXISTS idx_transaction_timestamp ON automaton_transactions(timestamp);

-- TABLE 3: platform_revenue
CREATE TABLE IF NOT EXISTS platform_revenue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (
    source IN ('deposit_fee', 'performance_fee', 'spawn_fee')
  ),
  amount DECIMAL(18, 6) NOT NULL,
  agent_id UUID REFERENCES user_automatons(id),
  user_id BIGINT,
  timestamp TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT positive_amount CHECK (amount > 0)
);

-- Indexes for platform_revenue
CREATE INDEX IF NOT EXISTS idx_revenue_source ON platform_revenue(source);
CREATE INDEX IF NOT EXISTS idx_revenue_timestamp ON platform_revenue(timestamp);
CREATE INDEX IF NOT EXISTS idx_revenue_agent_id ON platform_revenue(agent_id);
CREATE INDEX IF NOT EXISTS idx_revenue_user_id ON platform_revenue(user_id);

-- ============================================================================
-- PART 2: MIGRATION 005 - Parent-Child Lineage System
-- ============================================================================

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
      type IN ('spawn', 'deposit', 'earn', 'spend', 'performance_fee', 'platform_fee', 'lineage_share')
    );
END $$;

-- Add related_agent_id column to automaton_transactions for lineage tracking
ALTER TABLE automaton_transactions
ADD COLUMN IF NOT EXISTS related_agent_id UUID REFERENCES user_automatons(id);

-- Add index for related_agent_id
CREATE INDEX IF NOT EXISTS idx_transaction_related_agent ON automaton_transactions(related_agent_id);

-- Add comments to explain the lineage system
COMMENT ON TABLE lineage_transactions IS 'Tracks parent-child revenue sharing where parents receive 10% of children earnings';
COMMENT ON COLUMN user_automatons.parent_agent_id IS 'Reference to parent agent if this agent was spawned from another agent';
COMMENT ON COLUMN user_automatons.total_children_revenue IS 'Total credits received from all children via 10% revenue sharing';
COMMENT ON COLUMN user_automatons.autonomous_spawn_enabled IS 'Whether this agent can autonomously spawn children when it has sufficient credits';
COMMENT ON COLUMN user_automatons.last_autonomous_spawn_at IS 'Timestamp of last autonomous spawn for rate limiting';
COMMENT ON COLUMN user_automatons.autonomous_spawn_count IS 'Total number of children spawned autonomously by this agent';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check all tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'user_automatons',
  'automaton_transactions',
  'platform_revenue',
  'lineage_transactions'
)
ORDER BY table_name;

-- Check lineage columns added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_automatons' 
AND column_name IN (
  'parent_agent_id',
  'total_children_revenue',
  'autonomous_spawn_enabled',
  'last_autonomous_spawn_at',
  'autonomous_spawn_count'
)
ORDER BY column_name;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Expected Results:
-- - 4 tables created (user_automatons, automaton_transactions, platform_revenue, lineage_transactions)
-- - 5 lineage columns added to user_automatons
-- - All indexes and constraints created
--
-- Next Steps:
-- 1. Run: python test_lineage_system.py (should get 8/8 PASS)
-- 2. Update handlers for lineage support
-- 3. Update revenue_manager for 10% distribution
-- 4. Deploy to production
-- ============================================================================
