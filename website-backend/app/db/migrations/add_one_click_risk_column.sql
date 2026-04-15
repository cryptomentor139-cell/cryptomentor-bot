-- Adds dedicated risk column for 1-click execution path.
-- Safe to run multiple times.

ALTER TABLE autotrade_sessions
ADD COLUMN IF NOT EXISTS one_click_risk_per_trade DOUBLE PRECISION DEFAULT 0.5;
