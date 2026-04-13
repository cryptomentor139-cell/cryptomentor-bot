-- Add explicit reviewer identity fields for UID approvals/rejections.
-- Run in Supabase SQL editor.

alter table public.user_verifications
  add column if not exists reviewed_by_actor_type text
    check (reviewed_by_actor_type in ('admin', 'partner'));

alter table public.user_verifications
  add column if not exists reviewed_by_telegram_id bigint;

alter table public.user_verifications
  add column if not exists reviewed_by_partner_code text;

alter table public.user_verifications
  add column if not exists reviewed_by_partner_name text;

create index if not exists idx_user_verifications_reviewer_tg
  on public.user_verifications(reviewed_by_telegram_id);

create index if not exists idx_user_verifications_actor_type
  on public.user_verifications(reviewed_by_actor_type);

-- Backfill existing admin approvals if legacy field exists.
update public.user_verifications
set
  reviewed_by_actor_type = coalesce(reviewed_by_actor_type, 'admin'),
  reviewed_by_telegram_id = coalesce(reviewed_by_telegram_id, reviewed_by_admin_id)
where reviewed_by_admin_id is not null;
