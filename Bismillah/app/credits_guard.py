from typing import Tuple
from app.users_repo import is_premium_active
from app.supabase_repo import ensure_user_exists_no_credit, get_credits, debit_credits_rpc

def require_credits(tg_id: int, cost: int, username: str = None, first: str = None, last: str = None) -> Tuple[bool, int, str]:
    """
    Check and deduct credits for non-premium users.
    - Premium users: bypass debit, unlimited access
    - Non-premium: debit via RPC (atomic)
    Returns: (allowed, remaining, message)
    """
    # Pastikan user exists TANPA mengubah credits
    ensure_user_exists_no_credit(tg_id, username, first, last)

    # Check premium status - jika premium, tidak debit credits
    if is_premium_active(tg_id):
        remaining = get_credits(tg_id)  # hanya untuk display
        return True, remaining, "✅ **Premium aktif** - Akses unlimited, kredit tidak terpakai"

    # Non-premium: check credits dan debit atomically
    current = get_credits(tg_id)
    if current < cost:
        return False, current, f"❌ **Kredit tidak cukup**\n💳 Sisa: **{current}** | Biaya: **{cost}**\n\n💡 Gunakan `/credits` atau upgrade premium"

    # Debit credits via RPC (atomic operation)
    remaining = debit_credits_rpc(tg_id, cost)
    return True, remaining, f"💳 **Credit terpakai**: {cost} | **Sisa**: {remaining}"

def check_credits_balance(tg_id: int) -> Tuple[bool, int]:
    """
    Check user's credit balance without deducting
    Returns: (is_premium, credits)
    """
    if is_premium_active(tg_id):
        credits = get_credits(tg_id)
        return True, credits

    credits = get_credits(tg_id)
    return False, credits
