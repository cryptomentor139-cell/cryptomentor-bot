
from typing import Tuple
from .users_repo import is_premium_active, debit_credits, get_credits

def require_credits(tg_id: int, cost: int) -> Tuple[bool, int, str]:
    """
    Return (allowed, remaining, message)
    - Premium active: always allowed, remaining = current credits (not debited).
    - Non-premium: debit 'cost' atomically; if insufficient, rejected.
    """
    if is_premium_active(tg_id):
        return True, get_credits(tg_id), "✅ Premium: kredit tidak terpakai."
    
    current = get_credits(tg_id)
    if current < cost:
        return False, current, f"❌ Kredit tidak cukup. Sisa: {current}, biaya: {cost}."
    
    remaining = debit_credits(tg_id, cost)
    return True, remaining, f"✅ {cost} kredit terpakai. Sisa: {remaining}."
