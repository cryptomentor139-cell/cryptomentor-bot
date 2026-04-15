-- Align user_verifications with referral-aware web onboarding flow.
ALTER TABLE IF EXISTS public.user_verifications
ADD COLUMN IF NOT EXISTS community_code text,
ADD COLUMN IF NOT EXISTS partner_telegram_id bigint,
ADD COLUMN IF NOT EXISTS bitunix_referral_url text,
ADD COLUMN IF NOT EXISTS ref_source text,
ADD COLUMN IF NOT EXISTS rejection_reason text;

CREATE INDEX IF NOT EXISTS idx_user_verifications_community_code
ON public.user_verifications (community_code);
