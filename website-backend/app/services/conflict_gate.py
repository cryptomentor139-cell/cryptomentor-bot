from __future__ import annotations

import os
import sys
import time
from typing import Any, Dict

from app.db.supabase import _client
from app.services import bitunix as bsvc


_BISMILLAH_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Bismillah")
)
_BISMILLAH_APP_PATH = os.path.join(_BISMILLAH_PATH, "app")
if _BISMILLAH_APP_PATH not in sys.path:
    sys.path.insert(0, _BISMILLAH_APP_PATH)

try:
    from symbol_coordinator import get_coordinator, StrategyOwner, PositionSide  # type: ignore
    _COORDINATOR_AVAILABLE = True
except Exception:
    get_coordinator = None  # type: ignore
    StrategyOwner = None  # type: ignore
    PositionSide = None  # type: ignore
    _COORDINATOR_AVAILABLE = False


def _normalize_symbol(symbol: str) -> str:
    return str(symbol or "").upper().replace("/", "")


def _normalize_side(side: str) -> str:
    v = str(side or "").upper()
    if v in ("BUY", "LONG"):
        return "LONG"
    if v in ("SELL", "SHORT"):
        return "SHORT"
    return v


def _strategy_owner(strategy: str):
    if not _COORDINATOR_AVAILABLE:
        return None
    m = {
        "one_click": StrategyOwner.ONE_CLICK,
        "scalp": StrategyOwner.SCALP,
        "swing": StrategyOwner.SWING,
        "manual": StrategyOwner.MANUAL,
    }
    return m.get(str(strategy or "").lower(), StrategyOwner.ONE_CLICK)


def _position_side(side: str):
    if not _COORDINATOR_AVAILABLE:
        return None
    s = _normalize_side(side)
    if s == "LONG":
        return PositionSide.LONG
    if s == "SHORT":
        return PositionSide.SHORT
    return PositionSide.NONE


async def check_entry_conflicts(
    tg_id: int,
    symbol: str,
    requested_side: str,
    strategy: str = "one_click",
) -> Dict[str, Any]:
    """
    Canonical backend conflict gate for order-entry paths.
    Returns a structured decision with reason_code and details.
    """
    sym = _normalize_symbol(symbol)
    req_side = _normalize_side(requested_side)
    now_ts = time.time()

    # 1) In-memory coordinator ownership/pending/cooldown checks.
    if _COORDINATOR_AVAILABLE:
        try:
            coordinator = get_coordinator()
            owner = _strategy_owner(strategy)
            allowed, reason = await coordinator.can_enter(tg_id, sym, owner, now_ts)
            if not allowed:
                return {
                    "allowed": False,
                    "reason_code": "coordinator_block",
                    "reason": reason,
                    "symbol": sym,
                }
        except Exception as exc:
            return {
                "allowed": False,
                "reason_code": "coordinator_error",
                "reason": f"coordinator_check_failed: {exc}",
                "symbol": sym,
            }

    s = _client()

    # 2) DB open trade snapshot.
    try:
        trade_res = (
            s.table("autotrade_trades")
            .select("id, side, status, symbol")
            .eq("telegram_id", int(tg_id))
            .eq("symbol", sym)
            .eq("status", "open")
            .limit(1)
            .execute()
        )
        row = (trade_res.data or [None])[0]
        if row:
            side = _normalize_side(row.get("side"))
            if side and req_side and side != req_side:
                return {
                    "allowed": False,
                    "reason_code": "existing_position_opposite_side",
                    "reason": f"existing {sym} open trade is {side}, requested {req_side}",
                    "symbol": sym,
                }
            return {
                "allowed": False,
                "reason_code": "existing_position",
                "reason": f"existing {sym} open trade already managed",
                "symbol": sym,
            }
    except Exception:
        # Non-fatal: continue with exchange-state check.
        pass

    # 3) Pending order queue snapshot (best-effort, table may be absent).
    try:
        pending_res = (
            s.table("signal_queue")
            .select("id, symbol, status")
            .eq("telegram_id", int(tg_id))
            .eq("symbol", sym)
            .in_("status", ["queued", "executing", "pending"])
            .limit(1)
            .execute()
        )
        if pending_res.data:
            return {
                "allowed": False,
                "reason_code": "pending_order",
                "reason": f"pending order exists for {sym}",
                "symbol": sym,
            }
    except Exception:
        pass

    # 4) Live exchange state mismatch safety.
    try:
        positions = await bsvc.fetch_positions(tg_id)
        for p in (positions.get("positions") or []):
            psym = _normalize_symbol(p.get("symbol"))
            if psym != sym:
                continue
            qty = abs(float(p.get("amount", p.get("size", 0)) or 0))
            if qty <= 0:
                continue
            live_side = _normalize_side(p.get("side", p.get("positionSide", "")))
            if live_side and req_side and live_side != req_side:
                return {
                    "allowed": False,
                    "reason_code": "exchange_position_opposite_side",
                    "reason": f"live exchange {sym} side={live_side}, requested={req_side}",
                    "symbol": sym,
                }
            return {
                "allowed": False,
                "reason_code": "exchange_position_exists",
                "reason": f"live exchange position exists for {sym}",
                "symbol": sym,
            }
    except Exception:
        # Keep fail-open here because caller has other safety checks.
        pass

    return {"allowed": True, "reason_code": "ok", "reason": "allowed", "symbol": sym}


async def mark_pending(tg_id: int, symbol: str, strategy: str = "one_click") -> None:
    if not _COORDINATOR_AVAILABLE:
        return
    coordinator = get_coordinator()
    await coordinator.set_pending(int(tg_id), _normalize_symbol(symbol), _strategy_owner(strategy))


async def clear_pending(tg_id: int, symbol: str) -> None:
    if not _COORDINATOR_AVAILABLE:
        return
    coordinator = get_coordinator()
    await coordinator.clear_pending(int(tg_id), _normalize_symbol(symbol))


async def confirm_open(
    tg_id: int,
    symbol: str,
    strategy: str,
    side: str,
    qty: float,
    entry_price: float,
    exchange_position_id: str | None = None,
) -> None:
    if not _COORDINATOR_AVAILABLE:
        return
    coordinator = get_coordinator()
    await coordinator.confirm_open(
        int(tg_id),
        _normalize_symbol(symbol),
        _strategy_owner(strategy),
        _position_side(side),
        float(qty),
        float(entry_price),
        exchange_position_id=exchange_position_id,
    )

