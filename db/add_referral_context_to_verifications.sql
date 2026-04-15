-- Migration: Persist resolved referral context on UID submissions
-- Safe to run multiple times.

ALTER TABLE public.user_verifications
  ADD COLUMN IF NOT EXISTS ref_source TEXT,
  ADD COLUMN IF NOT EXISTS resolved_referral_url TEXT,
  ADD COLUMN IF NOT EXISTS resolved_partner_telegram_id BIGINT,
  ADD COLUMN IF NOT EXISTS resolved_partner_name TEXT;

CREATE INDEX IF NOT EXISTS idx_user_verifications_ref_source
  ON public.user_verifications(ref_source);

CREATE INDEX IF NOT EXISTS idx_user_verifications_resolved_partner_telegram_id
  ON public.user_verifications(resolved_partner_telegram_id);
