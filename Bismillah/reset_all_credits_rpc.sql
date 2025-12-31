-- Function 1: Reset ALL users credits (existing behavior)
create or replace function public.reset_all_user_credits(
  p_amount integer default 100
) returns integer language plpgsql security definer as $$
declare 
  v_updated_count integer;
begin
  update public.users
  set credits = p_amount
  where is_premium = false
  and telegram_id is not null;
  
  get diagnostics v_updated_count = row_count;
  
  insert into public.user_events (telegram_id, event_type, meta)
  values (0, 'MASS_CREDIT_RESET', jsonb_build_object('amount', p_amount, 'updated_count', v_updated_count));
  
  return v_updated_count;
end$$;

-- Function 2: Reset ONLY users with credits below threshold
create or replace function public.reset_credits_below_threshold(
  p_threshold integer default 100,
  p_new_amount integer default 100
) returns integer language plpgsql security definer as $$
declare 
  v_updated_count integer;
begin
  update public.users
  set credits = p_new_amount
  where credits < p_threshold
  and is_premium = false
  and telegram_id is not null;
  
  get diagnostics v_updated_count = row_count;
  
  insert into public.user_events (telegram_id, event_type, meta)
  values (0, 'RESET_CREDITS_BELOW_THRESHOLD', jsonb_build_object(
    'threshold', p_threshold, 
    'new_amount', p_new_amount, 
    'updated_count', v_updated_count
  ));
  
  return v_updated_count;
end$$;
