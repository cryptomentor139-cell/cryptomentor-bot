-- Migration: add stackmentor preference flag and allow mixed trading_mode.

ALTER TABLE public.autotrade_sessions
ADD COLUMN IF NOT EXISTS stackmentor_enabled BOOLEAN DEFAULT TRUE;

UPDATE public.autotrade_sessions
SET stackmentor_enabled = TRUE
WHERE stackmentor_enabled IS NULL;

ALTER TABLE public.autotrade_sessions
ALTER COLUMN stackmentor_enabled SET DEFAULT TRUE;

ALTER TABLE public.autotrade_sessions
DROP CONSTRAINT IF EXISTS chk_trading_mode;

ALTER TABLE public.autotrade_sessions
ADD CONSTRAINT chk_trading_mode
CHECK (trading_mode IN ('scalping', 'swing', 'mixed'));

COMMENT ON COLUMN public.autotrade_sessions.stackmentor_enabled IS
'Web/UX preference flag for StackMentor controls (preference only in this release).';
