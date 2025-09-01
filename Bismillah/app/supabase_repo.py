import os
from typing import Optional, Dict, Any, Tuple
from supabase import create_client, Client

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_SERVICE_KEY = <REDACTED_SUPABASE_KEY>

def _client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("Set SUPABASE_URL & SUPABASE_SERVICE_KEY (Service role).")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_user_by_tid(tg_id: int) -> Optional[Dict[str, Any]]:
    s = _client()
    res = s.table("users").select("*").eq("telegram_id", int(tg_id)).limit(1).execute()
    return res.data[0] if res.data else None

def get_vuser_by_tid(tg_id: int) -> Optional[Dict[str, Any]]:
    s = _client()
    res = s.table("v_users").select("*").eq("telegram_id", int(tg_id)).limit(1).execute()
    return res.data[0] if res.data else None

def _normalize_duration(token: str) -> Tuple[str, int]:
    t = (token or "").strip().lower()
    if t == "lifetime": return ("lifetime", 0)
    if t.isdigit():     return ("days", int(t))
    if t.endswith("d") and t[:-1].isdigit(): return ("days", int(t[:-1]))
    if t.endswith(("m","mo","mon","month","months")):
        n = "".join(ch for ch in t if ch.isdigit())
        if n.isdigit(): return ("months", int(n))
    raise ValueError("Invalid duration. Use lifetime | <days>d | <days> | <months>m")

def ensure_user_exists(
    tg_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Dict[str, Any]:
    s = _client()
    # Coba RPC upsert_user_with_welcome (welcome=0 agar tidak menyentuh kredit)
    try:
        payload = {
            "p_telegram_id": int(tg_id),
            "p_username": (username or "").strip().lstrip("@").lower() or None,
            "p_first_name": first_name,
            "p_last_name": last_name,
            "p_welcome_quota": 0,
            "p_referred_by": None,
        }
        data = s.rpc("upsert_user_with_welcome", payload).execute().data
        if data:
            return data
    except Exception:
        pass
    # Fallback upsert langsung
    row = {
        "telegram_id": int(tg_id),
        "username": (username or "").strip().lstrip("@").lower() or None,
        "first_name": first_name,
        "last_name": last_name,
    }
    s.table("users").upsert(row, on_conflict="telegram_id").execute()
    r = s.table("v_users").select("*").eq("telegram_id", int(tg_id)).limit(1).execute().data
    return r.data[0] if r.data else row

def set_premium_normalized(tg_id: int, duration_token: str) -> Dict[str, Any]:
    s = _client()
    dtype, dval = _normalize_duration(duration_token)
    s.rpc("set_premium", {
        "p_telegram_id": int(tg_id),
        "p_duration_value": int(dval),
        "p_duration_type": dtype,
    }).execute()
    # verifikasi via view (punya premium_active)
    v = s.table("v_users").select("*").eq("telegram_id", int(tg_id)).limit(1).execute().data
    if not v: raise RuntimeError("Premium updated but v_users not found")
    return v[0]

def revoke_premium(tg_id: int) -> Dict[str, Any]:
    s = _client()
    s.table("users").update({
        "is_premium": False,
        "is_lifetime": False,
        "premium_until": None
    }).eq("telegram_id", int(tg_id)).execute()
    # verifikasi via view
    v = s.table("v_users").select("*").eq("telegram_id", int(tg_id)).limit(1).execute().data
    if not v: raise RuntimeError("Premium revoked but v_users not found")
    return v[0]