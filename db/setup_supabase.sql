
-- 1) Schema tabel & index
create table if not exists public.users (
  id bigserial primary key,
  telegram_id bigint unique not null,
  username text,
  first_name text,
  last_name text,
  is_premium boolean not null default false,
  is_lifetime boolean not null default false,
  premium_until timestamptz,
  credits integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_users_tg on public.users(telegram_id);

create table if not exists public.user_events (
  id bigserial primary key,
  telegram_id bigint not null,
  event_type text not null,   -- 'REGISTER','SET_PREMIUM','DEBIT_CREDIT', dst.
  meta jsonb not null default '{}',
  created_at timestamptz not null default now()
);

create index if not exists idx_user_events_tg on public.user_events(telegram_id);

-- 2) Trigger updated_at
create or replace function public.tg_touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end$$;

drop trigger if exists tg_users_updated on public.users;
create trigger tg_users_updated
before update on public.users
for each row execute procedure public.tg_touch_updated_at();

-- 3) Helper function & view
create or replace function public.is_currently_premium(p_is_premium boolean, p_is_lifetime boolean, p_until timestamptz)
returns boolean language sql immutable as $$
  select coalesce(p_is_lifetime, false)
         or (coalesce(p_is_premium, false) and (p_until is not null and p_until > now()));
$$;

create or replace view public.v_users as
select
  id, telegram_id, username, first_name, last_name,
  is_premium, is_lifetime, premium_until, credits,
  public.is_currently_premium(is_premium, is_lifetime, premium_until) as premium_active,
  created_at, updated_at
from public.users;

-- 4) RPC / Function untuk premium & credit
create or replace function public.set_premium(
  p_telegram_id bigint,
  p_duration_value integer,
  p_duration_type text  -- 'days' | 'months' | 'lifetime'
) returns void language plpgsql security definer as $$
declare
  v_now timestamptz := now();
  v_until timestamptz;
begin
  if p_duration_type = 'lifetime' then
    update public.users
    set is_premium = true,
        is_lifetime = true,
        premium_until = null
    where telegram_id = p_telegram_id;
  elsif p_duration_type in ('days','months') then
    if p_duration_type = 'days' then
      v_until := greatest(coalesce((select premium_until from public.users where telegram_id=p_telegram_id), v_now), v_now) + (p_duration_value || ' days')::interval;
    else
      v_until := greatest(coalesce((select premium_until from public.users where telegram_id=p_telegram_id), v_now), v_now) + (p_duration_value || ' months')::interval;
    end if;

    update public.users
    set is_premium = true,
        is_lifetime = false,
        premium_until = v_until
    where telegram_id = p_telegram_id;
  else
    raise exception 'Invalid duration_type. Use "days", "months", or "lifetime".';
  end if;

  insert into public.user_events (telegram_id, event_type, meta)
  values (p_telegram_id, 'SET_PREMIUM', jsonb_build_object('duration_value', p_duration_value, 'duration_type', p_duration_type));
end$$;

create or replace function public.debit_credits(
  p_telegram_id bigint,
  p_amount integer
) returns integer language plpgsql security definer as $$
declare
  v_remaining integer;
begin
  update public.users
  set credits = greatest(0, credits - p_amount)
  where telegram_id = p_telegram_id
  returning credits into v_remaining;

  insert into public.user_events (telegram_id, event_type, meta)
  values (p_telegram_id, 'DEBIT_CREDIT', jsonb_build_object('amount', p_amount, 'remaining', v_remaining));

  return v_remaining;
end$$;

-- 5) (Opsional) RLS kebijakan dasar
-- Jika akses hanya lewat Service Key dari backend, kamu boleh aktifkan RLS minimal seperti ini.

alter table public.users enable row level security;
alter table public.user_events enable row level security;

create policy users_service_only on public.users
  for all
  using (true)
  with check (true);

create policy user_events_service_only on public.user_events
  for all
  using (true)
  with check (true);
