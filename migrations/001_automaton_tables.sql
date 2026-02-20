-- ============================================================================
-- AUTOMATON INTEGRATION - DATABASE MIGRATION SCRIPT
-- ============================================================================
-- This script creates 6 new tables for the Automaton integration feature
-- Run this script in Supabase SQL Editor
-- 
-- Tables created:
-- 1. custodial_wallets - User-specific Ethereum wallets for deposits
-- 2. wallet_deposits - USDT/USDC deposit tracking
-- 3. wallet_withdrawals - Withdrawal request management
-- 4. user_automatons - Autonomous trading agent records
-- 5. automaton_transactions - Agent transaction history
-- 6. platform_revenue - Revenue tracking and reporting
-- ============================================================================

-- ============================================================================
-- TABLE 1: custodial_wallets
-- Purpose: Store user-specific Ethereum wallets with encrypted private keys
-- ============================================================================
CREATE TABLE IF NOT EXISTS custodial_wallets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT NOT NULL UNIQUE,
  wallet_address TEXT UNIQUE NOT NULL,
  private_key_encrypted TEXT NOT NULL,
  balance_usdc DECIMAL(18, 6) DEFAULT 0,
  conway_credits DECIMAL(18, 2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  last_deposit_at TIMESTAMP,
  total_deposited DECIMAL(18, 6) DEFAULT 0,
  total_spent DECIMAL(18, 6) DEFAULT 0,
  
  CONSTRAINT positive_balances CHECK (
    balance_usdc >= 0 AND 
    conway_credits >= 0
  ),
  CONSTRAINT positive_totals CHECK (
    total_deposited >= 0 AND
    total_spent >= 0
  )
);

-- Indexes for custodial_wallets
CREATE INDEX IF NOT EXISTS idx_custodial_wallet_address ON custodial_wallets(wallet_address);
CREATE INDEX IF NOT EXISTS idx_custodial_user_id ON custodial_wallets(user_id);

-- ============================================================================
-- TABLE 2: wallet_deposits
-- Purpose: Track all USDC deposits to custodial wallets (Base network only)
-- ============================================================================
CREATE TABLE IF NOT EXISTS wallet_deposits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id UUID REFERENCES custodial_wallets(id) NOT NULL,
  user_id BIGINT NOT NULL,
  tx_hash TEXT UNIQUE NOT NULL,
  from_address TEXT NOT NULL,
  amount DECIMAL(18, 6) NOT NULL,
  token TEXT NOT NULL CHECK (token IN ('USDC')),
  network TEXT NOT NULL CHECK (network IN ('base')),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'failed')),
  confirmations INT DEFAULT 0,
  detected_at TIMESTAMP DEFAULT NOW(),
  confirmed_at TIMESTAMP,
  credited_conway DECIMAL(18, 2),
  platform_fee DECIMAL(18, 6),
  
  CONSTRAINT positive_amount CHECK (amount > 0),
  CONSTRAINT positive_confirmations CHECK (confirmations >= 0)
);

-- Indexes for wallet_deposits
CREATE INDEX IF NOT EXISTS idx_deposit_tx_hash ON wallet_deposits(tx_hash);
CREATE INDEX IF NOT EXISTS idx_deposit_wallet_id ON wallet_deposits(wallet_id);
CREATE INDEX IF NOT EXISTS idx_deposit_user_id ON wallet_deposits(user_id);
CREATE INDEX IF NOT EXISTS idx_deposit_status ON wallet_deposits(status);
CREATE INDEX IF NOT EXISTS idx_deposit_detected_at ON wallet_deposits(detected_at);

-- ============================================================================
-- TABLE 3: wallet_withdrawals
-- Purpose: Manage withdrawal requests from custodial wallets
-- ============================================================================
CREATE TABLE IF NOT EXISTS wallet_withdrawals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_id UUID REFERENCES custodial_wallets(id) NOT NULL,
  user_id BIGINT NOT NULL,
  amount DECIMAL(18, 6) NOT NULL,
  token TEXT NOT NULL CHECK (token IN ('USDC')),
  to_address TEXT NOT NULL,
  tx_hash TEXT,
  status TEXT DEFAULT 'pending' CHECK (
    status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')
  ),
  requested_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  fee DECIMAL(18, 6) DEFAULT 1.0,
  
  CONSTRAINT positive_amount CHECK (amount >= 10),
  CONSTRAINT valid_address CHECK (to_address ~ '^0x[a-fA-F0-9]{40}$'),
  CONSTRAINT positive_fee CHECK (fee >= 0)
);

-- Indexes for wallet_withdrawals
CREATE INDEX IF NOT EXISTS idx_withdrawal_wallet_id ON wallet_withdrawals(wallet_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_user_id ON wallet_withdrawals(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_status ON wallet_withdrawals(status);
CREATE INDEX IF NOT EXISTS idx_withdrawal_requested_at ON wallet_withdrawals(requested_at);

-- ============================================================================
-- TABLE 4: user_automatons
-- Purpose: Store autonomous trading agent records
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_automatons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id BIGINT NOT NULL,
  agent_wallet TEXT UNIQUE NOT NULL,
  agent_name TEXT NOT NULL,
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
CREATE INDEX IF NOT EXISTS idx_automaton_status ON user_automatons(status);
CREATE INDEX IF NOT EXISTS idx_automaton_survival_tier ON user_automatons(survival_tier);
CREATE INDEX IF NOT EXISTS idx_automaton_created_at ON user_automatons(created_at);

-- ============================================================================
-- TABLE 5: automaton_transactions
-- Purpose: Track all agent transactions (spawn, fund, earn, spend, fees)
-- ============================================================================
CREATE TABLE IF NOT EXISTS automaton_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  automaton_id UUID REFERENCES user_automatons(id) NOT NULL,
  type TEXT NOT NULL CHECK (
    type IN ('spawn', 'fund', 'earn', 'spend', 'performance_fee', 'platform_fee')
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
-- TABLE 6: platform_revenue
-- Purpose: Track platform revenue from fees
-- ============================================================================
CREATE TABLE IF NOT EXISTS platform_revenue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (
    source IN ('deposit_fee', 'performance_fee', 'withdrawal_fee')
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
  'custodial_wallets',
  'wallet_deposits', 
  'wallet_withdrawals',
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
  'custodial_wallets',
  'wallet_deposits',
  'wallet_withdrawals', 
  'user_automatons',
  'automaton_transactions',
  'platform_revenue'
)
ORDER BY tablename, indexname;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Next steps:
-- 1. Set up environment variables in Railway (see RAILWAY_ENV_SETUP.md)
-- 2. Configure Polygon RPC connection
-- 3. Generate and store wallet encryption key
-- ============================================================================
