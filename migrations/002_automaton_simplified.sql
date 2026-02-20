-- ============================================================================
-- AUTOMATON INTEGRATION - SIMPLIFIED DATABASE MIGRATION
-- ============================================================================
-- This is the SIMPLIFIED version for Conway direct integration
-- Conway handles wallets, deposits, and withdrawals
-- We only track agents, transactions, and revenue
-- 
-- Tables created:
-- 1. user_automatons - Autonomous trading agent records
-- 2. automaton_transactions - Agent transaction history  
-- 3. platform_revenue - Revenue tracking and reporting
-- 
-- REMOVED (Conway handles these):
-- - custodial_wallets (Conway provides deposit addresses)
-- - wallet_deposits (Conway tracks deposits)
-- - wallet_withdrawals (Conway handles withdrawals)
-- ============================================================================

-- ============================================================================
-- TABLE 1: user_automatons
-- Purpose: Store autonomous trading agent records
-- ============================================================================
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

-- ============================================================================
-- TABLE 2: automaton_transactions
-- Purpose: Track all agent transactions (spawn, fund, earn, spend, fees)
-- ============================================================================
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

-- ============================================================================
-- TABLE 3: platform_revenue
-- Purpose: Track platform revenue from fees
-- ============================================================================
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
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these queries after migration to verify tables were created successfully

-- Check table existence
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'user_automatons',
  'automaton_transactions',
  'platform_revenue'
)
ORDER BY table_name;

-- Check index creation
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN (
  'user_automatons',
  'automaton_transactions',
  'platform_revenue'
)
ORDER BY tablename, indexname;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get all active agents for a user
-- SELECT * FROM user_automatons WHERE user_id = 1187119989 AND status = 'active';

-- Get agent transaction history
-- SELECT * FROM automaton_transactions 
-- WHERE automaton_id = '<agent_id>' 
-- ORDER BY timestamp DESC 
-- LIMIT 20;

-- Get platform revenue summary
-- SELECT 
--   source,
--   COUNT(*) as transaction_count,
--   SUM(amount) as total_revenue
-- FROM platform_revenue
-- GROUP BY source;

-- Get agents by survival tier
-- SELECT 
--   survival_tier,
--   COUNT(*) as agent_count,
--   SUM(conway_credits) as total_credits
-- FROM user_automatons
-- WHERE status = 'active'
-- GROUP BY survival_tier;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Next steps:
-- 1. Set up Conway API credentials in Railway
-- 2. Implement Conway API integration (app/conway_integration.py)
-- 3. Test deposit address generation
-- 4. Test credit balance checking
-- ============================================================================
