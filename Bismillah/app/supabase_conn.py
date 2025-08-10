
# app/supabase_conn.py
import os
import requests
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

def _headers():
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

def health() -> Tuple[bool, str]:
    """Check Supabase connection health"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return False, "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY"
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?select=count&limit=1"
        response = requests.get(url, headers=_headers(), timeout=10)
        if response.status_code == 200:
            return True, "Connected"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def get_user_by_tid(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by telegram ID from Supabase"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}&select=*"
        response = requests.get(url, headers=_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        return None
    except Exception as e:
        print(f"Error getting user from Supabase: {e}")
        return None

def upsert_user_tid(telegram_id: int, **fields) -> Dict[str, Any]:
    """Upsert user in Supabase"""
    try:
        # Prepare data
        data = {
            "telegram_id": telegram_id,
            "updated_at": datetime.now().isoformat(),
            **fields
        }
        
        url = f"{SUPABASE_URL}/rest/v1/users"
        headers = {**_headers(), "Prefer": "resolution=merge-duplicates"}
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_user_tid(telegram_id: int, **fields) -> Dict[str, Any]:
    """Update user in Supabase"""
    try:
        data = {
            "updated_at": datetime.now().isoformat(),
            **fields
        }
        
        url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}"
        response = requests.patch(url, json=data, headers=_headers(), timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sb_is_premium_user(telegram_id: int) -> bool:
    """
    Check if user is premium (lifetime or timed) in Supabase.
    Returns True if user has is_premium=true, banned=false, and valid premium_until
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}&is_premium=eq.true&banned=eq.false&limit=1"
        response = requests.get(url, headers=_headers(), timeout=10)
        
        if response.status_code == 200:
            rows = response.json()
            if not rows:
                return False
            
            user = rows[0]
            # Lifetime premium (premium_until is NULL)
            if user.get("premium_until") is None:
                return True
            
            # Timed premium - check if still valid
            try:
                from datetime import timezone
                until = datetime.fromisoformat(user["premium_until"].replace("Z", "+00:00"))
                return until >= datetime.now(timezone.utc)
            except Exception:
                return False
        
        return False
    except Exception as e:
        print(f"Error checking premium status for {telegram_id}: {e}")
        return False

def sb_list_users(filters: Dict[str, str]) -> list:
    """
    List users from Supabase with filters
    """
    try:
        params = "&".join([f"{k}={v}" for k, v in filters.items()])
        url = f"{SUPABASE_URL}/rest/v1/users?{params}"
        response = requests.get(url, headers=_headers(), timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error listing users: {e}")
        return []

def sb_get_premium_count() -> Dict[str, int]:
    """
    Get premium user counts from Supabase
    """
    try:
        # Count lifetime premium users
        lifetime_url = f"{SUPABASE_URL}/rest/v1/users?is_premium=eq.true&banned=eq.false&premium_until=is.null&select=count"
        lifetime_response = requests.get(lifetime_url, headers={**_headers(), "Prefer": "count=exact"}, timeout=10)
        
        # Count timed premium users (with valid premium_until)
        from datetime import timezone
        now = datetime.now(timezone.utc).isoformat()
        timed_url = f"{SUPABASE_URL}/rest/v1/users?is_premium=eq.true&banned=eq.false&premium_until=gte.{now}&select=count"
        timed_response = requests.get(timed_url, headers={**_headers(), "Prefer": "count=exact"}, timeout=10)
        
        lifetime_count = 0
        timed_count = 0
        
        if lifetime_response.status_code == 200:
            lifetime_count = int(lifetime_response.headers.get('Content-Range', '0').split('/')[-1])
        
        if timed_response.status_code == 200:
            timed_count = int(timed_response.headers.get('Content-Range', '0').split('/')[-1])
        
        return {
            "lifetime": lifetime_count,
            "timed": timed_count,
            "total": lifetime_count + timed_count
        }
    except Exception as e:
        print(f"Error getting premium counts: {e}")
        return {"lifetime": 0, "timed": 0, "total": 0}
