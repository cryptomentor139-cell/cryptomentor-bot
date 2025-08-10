# app/supabase_conn.py
import os
import requests
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

# Alias for SUPABASE_URL and SUPABASE_SERVICE_KEY for easier use in functions
SB_URL = SUPABASE_URL
SB_KEY = SUPABASE_SERVICE_KEY
SB_REST = f"{SB_URL}/rest/v1"  # Base URL for REST API

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

def health() -> Tuple[bool, str]:
    """Check Supabase connection health"""
    try:
        if not SB_URL or not SB_KEY:
            return False, "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY"

        # Test connection dengan timeout singkat
        response = requests.get(f"{SB_REST}/users?limit=1", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return True, f"Connected to {SB_URL[:30]}..."
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def get_user_by_tid(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by telegram ID from Supabase"""
    try:
        url = f"{SB_REST}/users?telegram_id=eq.{telegram_id}&select=*"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        return None
    except Exception as e:
        print(f"Error getting user from Supabase: {e}")
        return None

def upsert_user_tid(telegram_id: int, table_name: str = "users", **fields) -> Dict[str, Any]:
    """UPSERT user berdasarkan telegram_id dengan on_conflict"""
    if not SB_URL or not SB_KEY:
        raise RuntimeError("Supabase env missing")

    payload = [{"telegram_id": telegram_id, **fields}]
    hdrs = {**HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"}
    params = {"on_conflict": "telegram_id"}  # PENTING: UPSERT berdasarkan telegram_id

    response = requests.post(f"{SB_REST}/{table_name}", headers=hdrs, params=params, json=payload, timeout=20)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"UPSERT {table_name} failed: {response.status_code} {response.text}")

    try:
        data = response.json()
    except Exception:
        data = None

    if isinstance(data, list) and data:
        return data[0]
    return data or {"telegram_id": telegram_id, **fields}

def update_user_tid(telegram_id: int, table_name: str = "users", **fields) -> Dict[str, Any]:
    """UPDATE user berdasarkan telegram_id"""
    if not SB_URL or not SB_KEY:
        raise RuntimeError("Supabase env missing")

    hdrs = {**HEADERS, "Prefer": "return=representation"}
    params = {"telegram_id": f"eq.{telegram_id}"}

    response = requests.patch(f"{SB_REST}/{table_name}", headers=hdrs, params=params, json=fields, timeout=20)

    if response.status_code not in (200, 204):
        raise RuntimeError(f"UPDATE {table_name} failed: {response.status_code} {response.text}")

    return response.json()[0] if response.status_code == 200 and response.text else {"telegram_id": telegram_id, **fields}

def _env() -> Tuple[str, str, str]:
    """Helper to get Supabase env variables and construct REST URL."""
    return SUPABASE_URL, SUPABASE_SERVICE_KEY, SB_REST

def _headers(key: str, *, count: bool = False):
    """Enhanced headers with optional count preference"""
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if count:
        h["Prefer"] = "count=exact"
    return h

def sb_list_users(params: dict, columns: str = "telegram_id,is_premium,premium_until,banned,credits,updated_at", table: str = "users", limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
    """List users from Supabase with flexible filtering"""
    url, key, rest = _env()
    if not url or not key:
        raise RuntimeError("Supabase env missing")

    q = {"select": columns, "limit": str(limit), "offset": str(offset)}
    q.update(params or {})

    r = requests.get(f"{rest}/{table}", headers=_headers(key), params=q, timeout=20)
    if r.status_code not in (200, 206):
        raise RuntimeError(f"LIST {table} failed: {r.status_code} {r.text}")
    return r.json()

def sb_count_users(premium_active: bool = False, lifetime: bool = False, table: str = "users") -> int:
    """
    Count users with flexible filters:
    premium_active: is_premium=true AND (premium_until is null OR >= now)
    lifetime: is_premium=true AND premium_until is null
    """
    url, key, rest = _env()
    if not url or not key:
        raise RuntimeError("Supabase env missing")

    nowiso = datetime.now(timezone.utc).isoformat()
    params = {}

    if lifetime:
        params = {
            "is_premium": "eq.true",
            "premium_until": "is.null",
        }
    elif premium_active:
        # or=(premium_until.is.null,premium_until.gte.<iso>)
        params = {
            "is_premium": "eq.true",
            "or": f"(premium_until.is.null,premium_until.gte.{nowiso})",
        }

    headers = _headers(key, count=True)
    # Use HEAD + Range: 0-0, Content-Range contains total
    headers["Range"] = "0-0"

    r = requests.get(f"{rest}/{table}", headers=headers, params={**params, "select": "telegram_id"}, timeout=20)
    if r.status_code not in (200, 206):
        # 206 for partial range
        raise RuntimeError(f"COUNT {table} failed: {r.status_code} {r.text}")

    cr = r.headers.get("Content-Range", "")
    # format: "0-0/123"
    total = 0
    if "/" in cr:
        try:
            total = int(cr.split("/")[-1])
        except Exception:
            total = 0
    return total