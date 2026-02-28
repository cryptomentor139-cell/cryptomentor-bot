-- Migration 007: Add Autonomous Trading Support to Automaton Agents
-- Adds columns for Automaton AI integration and autonomous trading features

-- Add Automaton AI integration columns to user_automatons table
ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    automaton_ai_task_id TEXT;           -- Link to Automaton AI task ID

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    trading_enabled BOOLEAN DEFAULT false; -- Enable/disable autonomous trading

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    strategy TEXT DEFAULT 'conservative';  -- Trading strategy (conservative/moderate/aggressive)

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    risk_level TEXT DEFAULT 'low';        -- Risk level (low/medium/high)

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    max_trade_size_pct FLOAT DEFAULT 5.0; -- Max % of balance per trade

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    daily_loss_limit_pct FLOAT DEFAULT 20.0; -- Daily loss limit percentage

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    last_trade_at TIMESTAMP;              -- Last trade timestamp

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    total_trades INTEGER DEFAULT 0;       -- Total trades executed

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    winning_trades INTEGER DEFAULT 0;     -- Number of winning trades

ALTER TABLE user_automatons ADD COLUMN IF NOT EXISTS
    losing_trades INTEGER DEFAULT 0;      -- Number of losing trades

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_automatons_trading_enabled 
ON user_automatons(trading_enabled) WHERE trading_enabled = true;

CREATE INDEX IF NOT EXISTS idx_user_automatons_ai_task 
ON user_automatons(automaton_ai_task_id) WHERE automaton_ai_task_id IS NOT NULL;

-- Add comments
COMMENT ON COLUMN user_automatons.automaton_ai_task_id IS 'Link to Automaton AI dashboard task ID';
COMMENT ON COLUMN user_automatons.trading_enabled IS 'Whether autonomous trading is enabled for this agent';
COMMENT ON COLUMN user_automatons.strategy IS 'Trading strategy: conservative, moderate, or aggressive';
COMMENT ON COLUMN user_automatons.risk_level IS 'Risk level: low, medium, or high';
COMMENT ON COLUMN user_automatons.max_trade_size_pct IS 'Maximum percentage of balance per trade';
COMMENT ON COLUMN user_automatons.daily_loss_limit_pct IS 'Daily loss limit as percentage';
COMMENT ON COLUMN user_automatons.last_trade_at IS 'Timestamp of last executed trade';
COMMENT ON COLUMN user_automatons.total_trades IS 'Total number of trades executed';
COMMENT ON COLUMN user_automatons.winning_trades IS 'Number of profitable trades';
COMMENT ON COLUMN user_automatons.losing_trades IS 'Number of losing trades';

-- Migration complete
SELECT 'Migration 007: Autonomous Trading Support - COMPLETED' as status;
