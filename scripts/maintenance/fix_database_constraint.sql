-- ============================================================================
-- FIX: Database Constraint untuk user_automatons.status
-- ============================================================================
-- Error: violates check constraint "user_automatons_status_check"
-- 
-- Masalah: Constraint di database tidak match dengan code
-- Solusi: Update constraint untuk allow semua status yang digunakan code
-- ============================================================================

-- Drop existing constraint
ALTER TABLE user_automatons 
DROP CONSTRAINT IF EXISTS user_automatons_status_check;

-- Add new constraint with all valid statuses
ALTER TABLE user_automatons
ADD CONSTRAINT user_automatons_status_check 
CHECK (status IN ('active', 'paused', 'dead', 'inactive', 'suspended', 'pending'));

-- Verify constraint
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'user_automatons'::regclass
AND conname = 'user_automatons_status_check';

-- ============================================================================
-- EXPLANATION
-- ============================================================================
-- 
-- Valid status values:
-- - 'active'    : Agent is running
-- - 'paused'    : Agent is temporarily stopped
-- - 'dead'      : Agent has no credits
-- - 'inactive'  : Agent is disabled by user
-- - 'suspended' : Agent is suspended by admin
-- - 'pending'   : Agent is being created
-- 
-- ============================================================================
