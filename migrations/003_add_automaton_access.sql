-- ============================================================================
-- ADD AUTOMATON ACCESS FIELD TO USERS TABLE
-- ============================================================================
-- This migration adds automaton_access field to track who has paid for
-- Automaton feature access (Rp2,000,000 one-time fee)
-- 
-- Lifetime users get automatic access (no payment required)
-- ============================================================================

-- Add automaton_access column to users table
-- Note: This is for local SQLite database
-- For Supabase, run the equivalent PostgreSQL command in SQL Editor

-- SQLite version (for local testing)
ALTER TABLE users ADD COLUMN automaton_access INTEGER DEFAULT 0;

-- Update existing lifetime users to have automatic access
UPDATE users 
SET automaton_access = 1 
WHERE subscription_end IS NULL AND is_premium = 1;

-- ============================================================================
-- SUPABASE VERSION (Run this in Supabase SQL Editor)
-- ============================================================================
/*
-- Add column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS automaton_access BOOLEAN DEFAULT FALSE;

-- Grant access to existing lifetime users
UPDATE users 
SET automaton_access = TRUE 
WHERE subscription_end IS NULL AND is_premium = TRUE;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_automaton_access ON users(automaton_access);
*/

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check column was added
-- PRAGMA table_info(users);

-- Check lifetime users got access
-- SELECT telegram_id, first_name, is_premium, subscription_end, automaton_access 
-- FROM users 
-- WHERE is_premium = 1;

-- ============================================================================
-- NOTES
-- ============================================================================
-- automaton_access = 0/FALSE: No access (need to pay Rp2,000,000)
-- automaton_access = 1/TRUE: Has access (paid or lifetime user)
-- 
-- Lifetime users (subscription_end IS NULL) get automatic access
-- Regular premium users need to pay separately for Automaton access
-- ============================================================================
