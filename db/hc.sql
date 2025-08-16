
create or replace function public.hc()
returns text
language sql stable as $$
  select 'Supabase connection healthy at ' || now()::text;
$$;

NOTIFY pgrst, 'reload schema';
