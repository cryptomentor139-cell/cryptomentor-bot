
import os
import requests
import logging
from datetime import datetime, timezone

REQ_TIMEOUT = 15

def _env():
    url = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
    key = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()
    rest = f"{url}/rest/v1" if url else ""
    return url, key, rest

def _headers(key: str, *, prefer: str | None = None):
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if prefer: 
        h["Prefer"] = prefer
    return h

def sb_health():
    """Test Supabase connection health"""
    url, key, rest = _env()
    if not url or not key:
        return False, "ENV missing (SUPABASE_URL / SUPABASE_SERVICE_KEY)"
    try:
        r0 = requests.get(rest, headers=_headers(key), timeout=REQ_TIMEOUT)
        r1 = requests.get(f"{rest}/users", headers=_headers(key),
                          params={"select": "telegram_id", "limit": "1"},
                          timeout=REQ_TIMEOUT)
        ok = (r0.status_code in (200,401,404)) and (r1.status_code in (200,206))
        detail = f"root={r0.status_code} users={r1.status_code}"
        return ok, detail
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def _count(table: str, params: dict) -> int:
    """Count rows in table with filters"""
    url, key, rest = _env()
    hdr = _headers(key, prefer="count=exact")
    hdr["Range"] = "0-0"
    r = requests.get(f"{rest}/{table}", headers=hdr, 
                     params={"select":"id","limit":"1", **params}, 
                     timeout=REQ_TIMEOUT)
    if r.status_code not in (200,206):
        raise RuntimeError(f"COUNT {table} {r.status_code} {r.text}")
    cr = r.headers.get("Content-Range","")
    return int(cr.split("/")[-1]) if "/" in cr else 0

def sb_counts_safe():
    """Get user counts and detect missing columns"""
    missing = set()
    nowiso = datetime.now(timezone.utc).isoformat()
    out = {}
    
    # registered: fallback ke total baris users
    try:
        out["registered"] = _count("users", {})
    except Exception as e:
        raise

    # premium_active
    try:
        out["premium_active"] = _count("users", {
            "is_premium": "eq.true",
            "banned": "eq.false",
            "or": f"(premium_until.is.null,premium_until.gte.{nowiso})",
        })
    except Exception as e:
        text = str(e)
        if "is_premium" in text: 
            missing.add("is_premium")
        if "premium_until" in text: 
            missing.add("premium_until")
        if "banned" in text: 
            missing.add("banned")
        out["premium_active"] = 0

    # lifetime
    try:
        out["lifetime"] = _count("users", {
            "is_premium": "eq.true",
            "banned": "eq.false",
            "premium_until": "is.null",
        })
    except Exception as e:
        text = str(e)
        if "is_premium" in text: 
            missing.add("is_premium")
        if "premium_until" in text: 
            missing.add("premium_until")
        if "banned" in text: 
            missing.add("banned")
        out["lifetime"] = 0

    # banned
    try:
        out["banned"] = _count("users", {"banned": "eq.true"})
    except Exception as e:
        if "banned" in str(e): 
            missing.add("banned")
        out["banned"] = 0

    # referred
    try:
        out["referred"] = _count("users", {"referred_by": "not.is.null"})
    except Exception as e:
        if "referred_by" in str(e): 
            missing.add("referred_by")
        out["referred"] = 0

    # registered_by_start
    try:
        out["registered_by_start"] = _count("users", {"is_registered":"eq.true"})
    except Exception as e:
        if "is_registered" in str(e): 
            missing.add("is_registered")
        out["registered_by_start"] = 0

    return out, sorted(missing)

SQL_FIX_TEMPLATE = """-- Jalankan di Supabase SQL Editor:
create extension if not exists pgcrypto;

alter table public.users
{add_is_registered}
{add_referred_by};

-- index dasar
create unique index if not exists users_telegram_id_idx on public.users(telegram_id);
create index if not exists users_is_registered_idx on public.users(is_registered);
create index if not exists users_premium_active_idx on public.users(is_premium, premium_until, banned);

-- aktifkan RLS untuk backend via service_role
alter table public.users enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where tablename='users' and policyname='allow_service_role_all') then
    create policy allow_service_role_all on public.users
      for all to service_role using (true) with check (true);
  end if;
end$$;
"""

def build_sql_fix(missing_cols: list[str]) -> str:
    """Build SQL fix for missing columns"""
    add_is_registered = "-- kolom is_registered sudah ada"
    add_referred_by = "-- kolom referred_by sudah ada"
    
    if "is_registered" in missing_cols:
        add_is_registered = "add column if not exists is_registered boolean not null default false,"
    if "referred_by" in missing_cols:
        add_referred_by = "add column if not exists referred_by bigint"
    
    # Fix comma handling
    if add_is_registered.endswith(",") and "referred_by" not in missing_cols:
        add_is_registered = add_is_registered[:-1]
        
    return SQL_FIX_TEMPLATE.format(
        add_is_registered=add_is_registered,
        add_referred_by=add_referred_by
    )

def log_console_panel():
    """Log DB status to console on startup"""
    ok, detail = sb_health()
    logging.info("🔌 Supabase Health: %s (%s)", "OK" if ok else "FAIL", detail)
    
    try:
        counts, missing = sb_counts_safe()
        logging.info("📊 Users | registered=%s premium_active=%s lifetime=%s banned=%s referred=%s",
                     counts.get("registered"), counts.get("premium_active"),
                     counts.get("lifetime"), counts.get("banned"), counts.get("referred"))
        
        if missing:
            logging.warning("⚠️ Missing columns: %s", ", ".join(missing))
            sql = build_sql_fix(missing)
            logging.warning("🛠️ SQL Fix (copy ke Supabase SQL Editor):\n%s", sql)
        else:
            logging.info("✅ Schema OK (no missing columns)")
            
    except Exception as e:
        logging.error("❌ DB counts error: %s", e)
