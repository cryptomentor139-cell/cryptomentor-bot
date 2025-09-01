from typing import Tuple
from app.users_repo import is_premium_active, get_vuser_by_telegram_id

def require_credits(tg_id: int, cost: int) -> Tuple[bool, int, str]:
    """
    Check and deduct credits for non-premium users
    Returns: (success, remaining_credits, message)
    """
    # Premium aktif: tidak didebit
    if is_premium_active(tg_id):
        row = get_vuser_by_telegram_id(tg_id) or {}
        remain = int(row.get("credits") or 0)
        return True, remain, "✅ Premium aktif — kredit tidak terpakai."

    # Non-premium: ambil saldo & debit sesuai implementasi
    from app.supabase_conn import get_supabase_client
    s = get_supabase_client()
    user = s.table("users").select("credits").eq("telegram_id", int(tg_id)).limit(1).execute().data
    cur = int((user[0] if user else {}).get("credits") or 0)

    if cur < cost:
        return False, cur, f"❌ Kredit tidak cukup. Sisa: {cur}, biaya: {cost}. Upgrade ke premium untuk unlimited access."

    newv = cur - cost
    s.table("users").update({"credits": newv}).eq("telegram_id", int(tg_id)).execute()
    return True, newv, f"✅ {cost} kredit terpakai. Sisa: {newv}."

def check_credits_balance(tg_id: int) -> Tuple[bool, int]:
    """
    Check user's credit balance without deducting
    Returns: (is_premium, credits)
    """
    if is_premium_active(tg_id):
        row = get_vuser_by_telegram_id(tg_id) or {}
        credits = int(row.get("credits") or 0)
        return True, credits

    from app.supabase_conn import get_supabase_client
    s = get_supabase_client()
    user = s.table("users").select("credits").eq("telegram_id", int(tg_id)).limit(1).execute().data
    credits = int((user[0] if user else {}).get("credits") or 0)
    return False, credits