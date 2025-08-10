
<file_path>Bismillah/scripts/migrate_backup_to_supabase.py</file_path>
<line_number>1</line_number>
import json
import os
import sys
import math
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BACKUP_PATH = os.getenv("BACKUP_FILE", "premium_users_backup_20250802_130229.json")
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
SUPABASE_SERVICE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or "").strip()
REST = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=representation"
}

def load_backup() -> List[Dict[str, Any]]:
    """Load backup file with flexible format detection"""
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # data can be array or dict containing list; normalize to list of users
    if isinstance(data, dict):
        # try detecting common keys
        for k in ("users", "premium_users", "data"):
            if k in data and isinstance(data[k], list):
                return data[k]
        # fallback: wrap single dict as list
        return [data]
    return data

def map_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flexible mapping from backup → Supabase users schema:
      - telegram_id (required)
      - is_premium
      - premium_until (ISO) or None → lifetime
      - banned (default false)
      - credits (default 0)
    Accept various field variations: 'user_id', 'telegramId', 'tg_id', 'premiumUntil', 'plan', 'lifetime', etc.
    """
    tid = rec.get("telegram_id") or rec.get("user_id") or rec.get("telegramId") or rec.get("tg_id")
    if tid is None:
        raise ValueError("Record without telegram_id")
    try:
        tid = int(str(tid).strip())
    except Exception:
        raise ValueError(f"Invalid telegram_id: {tid}")

    # is_premium from backup
    is_p = bool(rec.get("is_premium") or rec.get("premium") or rec.get("isPremium", False))

    # Lifetime & premium_until
    pu = rec.get("premium_until") or rec.get("premiumUntil") or rec.get("until") or None
    plan = (rec.get("plan") or rec.get("subscription") or "").lower()
    lifetime_flag = bool(rec.get("lifetime") or ("lifetime" in plan))

    # Normalize premium_until → ISO / None
    if lifetime_flag:
        premium_until = None
        is_p = True
    else:
        if pu in (None, "", "null"):
            premium_until = None
        else:
            # try parsing; if failed, treat as lifetime
            try:
                # allow common formats
                dt = datetime.fromisoformat(str(pu).replace("Z", "+00:00"))
                premium_until = dt.astimezone(timezone.utc).isoformat()
            except Exception:
                premium_until = None

    credits = rec.get("credits") or rec.get("balance") or 100  # Default 100 credits
    try:
        credits = int(credits)
    except Exception:
        credits = 100

    banned = bool(rec.get("banned") or rec.get("is_banned") or rec.get("blocked") or False)

    # If premium_until in future or None (lifetime) → is_premium True
    if not is_p:
        if premium_until is None:
            # don't auto-premium if not lifetime
            pass
        else:
            try:
                if datetime.fromisoformat(premium_until) >= datetime.now(timezone.utc):
                    is_p = True
            except Exception:
                pass

    # Add required fields with defaults
    return {
        "telegram_id": tid,
        "first_name": rec.get("first_name", "Unknown"),
        "username": rec.get("username", "no_username"),
        "is_premium": is_p,
        "premium_until": premium_until,
        "credits": credits,
        "banned": banned,
        "created_at": rec.get("created_at") or datetime.now(timezone.utc).isoformat(),
        "restart_required": False
    }

def batch_upsert(rows: List[Dict[str, Any]], table: str = "users"):
    """Batch upsert to Supabase"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("Supabase env missing")
    
    params = {"on_conflict": "telegram_id"}
    r = requests.post(f"{REST}/{table}", headers=HEADERS, params=params, json=rows, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"UPSERT batch failed: {r.status_code} {r.text}")

def run():
    """Main migration function"""
    print("[migrate] Starting backup migration to Supabase...")
    
    # Check if backup file exists
    if not os.path.exists(BACKUP_PATH):
        print(f"[migrate] ❌ Backup file not found: {BACKUP_PATH}")
        return False
    
    data = load_backup()
    print(f"[migrate] Loaded {len(data)} records from backup")
    
    mapped = []
    errors = 0
    
    for i, rec in enumerate(data):
        try:
            mapped.append(map_record(rec))
        except Exception as e:
            errors += 1
            print(f"[migrate] Skip record {i+1}: {e}")
    
    print(f"[migrate] Mapped {len(mapped)} records ({errors} errors)")

    # Dedup by telegram_id (last write wins)
    dedup = {}
    for r in mapped:
        dedup[r["telegram_id"]] = r
    rows = list(dedup.values())
    print(f"[migrate] Dedup → {len(rows)} unique users")

    # Batching
    BATCH = 100  # Smaller batches for reliability
    success_count = 0
    
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i+BATCH]
        try:
            batch_upsert(chunk)
            success_count += len(chunk)
            print(f"[migrate] Upserted {success_count}/{len(rows)} users")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"[migrate] ❌ Batch {i//BATCH + 1} failed: {e}")

    print(f"[migrate] ✅ Done! Successfully migrated {success_count}/{len(rows)} users")
    return success_count > 0

if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
