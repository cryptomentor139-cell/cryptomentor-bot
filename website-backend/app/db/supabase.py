import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

logger = logging.getLogger(__name__)


def _client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_unknown_column_error(exc: Exception, column: str) -> bool:
    msg = str(exc).lower()
    col = column.lower()
    return col in msg and ("schema cache" in msg or "column" in msg)


def get_user_by_tid(tg_id: int) -> Optional[Dict[str, Any]]:
    res = _client().table("users").select("*").eq("telegram_id", tg_id).limit(1).execute()
    return res.data[0] if res.data else None


def upsert_web_login(tg_id: int, username: str, first_name: str, last_name: str = None, referred_by: str = None) -> Dict[str, Any]:
    """Update profile info saat login via website. Tidak mengubah credits."""
    s = _client()
    existing = get_user_by_tid(tg_id)

    if existing:
        update = {"updated_at": _utc_now_iso()}
        if username:
            update["username"] = username.lstrip("@").lower()
        if first_name:
            update["first_name"] = first_name
        if last_name:
            update["last_name"] = last_name

        has_referral = bool(referred_by and not existing.get("referred_by_code"))
        if has_referral:
            update["referred_by_code"] = referred_by

        try:
            s.table("users").update(update).eq("telegram_id", tg_id).execute()
        except Exception as exc:
            if has_referral and _is_unknown_column_error(exc, "referred_by_code"):
                logger.warning("users.referred_by_code missing; retrying login upsert without referral column")
                update.pop("referred_by_code", None)
                s.table("users").update(update).eq("telegram_id", tg_id).execute()
            else:
                raise
        return get_user_by_tid(tg_id)

    # User belum pernah pakai bot, buat dengan 0 credits
    row = {
        "telegram_id": tg_id,
        "username": (username or "").lstrip("@").lower() or None,
        "first_name": first_name or "User",
        "last_name": last_name,
        "credits": 0,
        "updated_at": _utc_now_iso(),
    }
    if referred_by:
        row["referred_by_code"] = referred_by
    try:
        s.table("users").insert(row).execute()
    except Exception as exc:
        if referred_by and _is_unknown_column_error(exc, "referred_by_code"):
            logger.warning("users.referred_by_code missing; retrying login insert without referral column")
            row.pop("referred_by_code", None)
            s.table("users").insert(row).execute()
        else:
            raise
    return get_user_by_tid(tg_id) or row
