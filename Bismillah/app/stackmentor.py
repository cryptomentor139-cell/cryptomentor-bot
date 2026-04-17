"""
StackMentor System - Unified Target Strategy

Default mode uses a fixed risk:reward target of 1:3 with full close at TP.
Optional runner mode (feature-flagged) uses:
- TP1 at 3R with partial close (default 80%)
- Remaining runner to TP3 at 5R with breakeven protection
"""

import asyncio
import logging
import os
import time
from typing import Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return float(default)
    try:
        return float(raw)
    except Exception:
        return float(default)


_RUNNER_ENABLED = _env_bool("STACKMENTOR_RUNNER_ENABLED", False)
_TP1_CLOSE_PCT = min(1.0, max(0.0, _env_float("STACKMENTOR_TP1_CLOSE_PCT", 0.80)))
_TP3_RR = max(3.0, _env_float("STACKMENTOR_TP3_RR", 5.0))

# StackMentor Configuration
STACKMENTOR_CONFIG = {
    "enabled": True,            # Enable for all users
    "runner_enabled": _RUNNER_ENABLED,
    "tp1_pct": _TP1_CLOSE_PCT if _RUNNER_ENABLED else 1.00,
    "tp2_pct": 0.00,
    "tp3_pct": (1.0 - _TP1_CLOSE_PCT) if _RUNNER_ENABLED else 0.00,
    "target_rr": 3.0,           # Fixed R:R 1:3 for all trades
    "tp1_rr": 3.0,              # Keep compatibility with existing callers / TP1 gate
    "tp2_rr": 3.0,
    "tp3_rr": _TP3_RR if _RUNNER_ENABLED else 3.0,
    "breakeven_after_tp1": _RUNNER_ENABLED,
}

# Track StackMentor positions: user_id → {symbol: position_data}
_stackmentor_positions: Dict[int, Dict[str, Dict]] = {}


def stackmentor_runner_enabled() -> bool:
    cfg = STACKMENTOR_CONFIG
    return bool(cfg.get("runner_enabled", False)) and float(cfg.get("tp1_pct", 1.0)) < 1.0


def get_exchange_tp_price(tp1: float, tp3: float) -> float:
    """
    Determine which TP should be attached on exchange at entry.
    - Runner OFF: exchange TP is TP1 (3R).
    - Runner ON : exchange TP is TP3 (runner target, e.g. 5R).
    """
    if stackmentor_runner_enabled():
        return float(tp3)
    return float(tp1)


def calculate_stackmentor_levels(
    entry_price: float,
    sl_price: float,
    side: str
) -> Tuple[float, float, float]:
    """
    Calculate TP levels based on SL distance.
    In unified mode all TP levels are the same 1:3 target.

    Returns: (tp1, tp2, tp3) for backward compatibility.
    """
    cfg = STACKMENTOR_CONFIG
    side = str(side or "").upper()
    
    # Calculate SL distance
    sl_distance = abs(entry_price - sl_price)
    
    rr_tp1 = float(cfg.get("target_rr", 3.0))
    rr_tp3 = float(cfg.get("tp3_rr", rr_tp1)) if stackmentor_runner_enabled() else rr_tp1
    if side == "LONG":
        tp1 = entry_price + (sl_distance * rr_tp1)
        tp3 = entry_price + (sl_distance * rr_tp3)
    else:  # SHORT
        tp1 = entry_price - (sl_distance * rr_tp1)
        tp3 = entry_price - (sl_distance * rr_tp3)
    tp2 = tp1
    if not stackmentor_runner_enabled():
        tp3 = tp1
    
    return (tp1, tp2, tp3)


def calculate_qty_splits(total_qty: float, min_qty: float = 0.0, precision: int = 3) -> Tuple[float, float, float]:
    """
    Split quantity for execution.
    Unified mode closes 100% at TP1 and keeps TP2/TP3 at 0 for compatibility.

    Returns: (qty_tp1, qty_tp2, qty_tp3)
    """
    cfg = STACKMENTOR_CONFIG
    
    # Analyze the actual precision of total_qty
    qty_str = f"{total_qty:.8f}".rstrip('0')
    if '.' in qty_str:
        actual_prec = len(qty_str.split('.')[1])
        precision = max(precision, actual_prec)

    if stackmentor_runner_enabled():
        tp1_pct = min(1.0, max(0.0, float(cfg.get("tp1_pct", 0.80))))
        qty_tp1 = round(total_qty * tp1_pct, precision)
        qty_tp2 = 0.0
        qty_tp3 = round(total_qty - qty_tp1, precision)
    else:
        qty_tp1 = round(total_qty, precision)
        qty_tp2 = 0.0
        qty_tp3 = 0.0
    
    # Collapse small fragments safely to avoid MIN_QTY Bitunix Limit exceptions
    if min_qty > 0:
        if 0 < qty_tp1 < min_qty:
            qty_tp1 = round(total_qty, precision)
            qty_tp2 = 0.0
            qty_tp3 = 0.0

        if 0 < qty_tp3 < min_qty:
            qty_tp1 = round(qty_tp1 + qty_tp3, precision)
            qty_tp3 = 0.0
             
        if 0 < qty_tp1 < min_qty:
            qty_tp1 = round(total_qty, precision)
            qty_tp2 = 0.0
            qty_tp3 = 0.0
            
    return (qty_tp1, qty_tp2, qty_tp3)


def register_stackmentor_position(
    user_id: int,
    symbol: str,
    entry_price: float,
    sl_price: float,
    tp1: float,
    tp2: float,
    tp3: float,
    total_qty: float,
    qty_tp1: float,
    qty_tp2: float,
    qty_tp3: float,
    side: str,
    leverage: int
):
    """Register a new StackMentor position for monitoring"""
    if user_id not in _stackmentor_positions:
        _stackmentor_positions[user_id] = {}
    
    _stackmentor_positions[user_id][symbol] = {
        "entry_price": entry_price,
        "sl_price": sl_price,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "total_qty": total_qty,
        "qty_tp1": qty_tp1,
        "qty_tp2": qty_tp2,
        "qty_tp3": qty_tp3,
        "side": side,
        "leverage": leverage,
        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,
        "breakeven_mode": False,
        "opened_at": datetime.utcnow(),
    }
    
    logger.info(
        f"[StackMentor:{user_id}] Registered {symbol} {side} — "
        f"TP1={tp1:.4f} TP2={tp2:.4f} TP3={tp3:.4f}"
    )


def get_stackmentor_position(user_id: int, symbol: str) -> Optional[Dict]:
    """Get StackMentor position data"""
    if user_id not in _stackmentor_positions:
        return None
    return _stackmentor_positions[user_id].get(symbol)


def remove_stackmentor_position(user_id: int, symbol: str):
    """Remove StackMentor position (fully closed)"""
    if user_id in _stackmentor_positions:
        _stackmentor_positions[user_id].pop(symbol, None)
        logger.info(f"[StackMentor:{user_id}] Removed {symbol} from monitoring")


async def monitor_stackmentor_positions(bot, user_id: int, client, notify_chat_id: int):
    """
    Monitor StackMentor positions for TP hits
    Called from main trade loop every scan interval
    """
    if user_id not in _stackmentor_positions:
        return
    
    positions = _stackmentor_positions[user_id].copy()
    
    for symbol, pos_data in positions.items():
        try:
            # Get current mark price
            ticker_result = await asyncio.to_thread(client.get_ticker, symbol)
            if not ticker_result.get('success'):
                continue
            
            mark_price = float(ticker_result.get('mark_price', 0))
            if mark_price == 0:
                continue
            
            side = pos_data['side']
            
            # Check TP1 hit (trigger breakeven)
            if not pos_data['tp1_hit']:
                tp1_hit = (side == "LONG" and mark_price >= pos_data['tp1']) or \
                          (side == "SHORT" and mark_price <= pos_data['tp1'])
                
                if tp1_hit:
                    await handle_tp1_hit(bot, user_id, client, notify_chat_id, symbol, pos_data, mark_price)
            
            # Check TP2 hit
            elif not pos_data['tp2_hit']:
                tp2_hit = (side == "LONG" and mark_price >= pos_data['tp2']) or \
                          (side == "SHORT" and mark_price <= pos_data['tp2'])
                
                if tp2_hit:
                    await handle_tp2_hit(bot, user_id, client, notify_chat_id, symbol, pos_data, mark_price)
            
            # Check TP3 hit
            elif not pos_data['tp3_hit']:
                tp3_hit = (side == "LONG" and mark_price >= pos_data['tp3']) or \
                          (side == "SHORT" and mark_price <= pos_data['tp3'])
                
                if tp3_hit:
                    await handle_tp3_hit(bot, user_id, client, notify_chat_id, symbol, pos_data, mark_price)
        
        except Exception as e:
            logger.error(f"[StackMentor:{user_id}] Monitor error {symbol}: {e}")


async def handle_tp1_hit(bot, user_id: int, client, notify_chat_id: int, 
                        symbol: str, pos_data: Dict, mark_price: float):
    """
    TP1 hit handling.
    - Runner OFF: close full position at TP1 (3R).
    - Runner ON : close TP1 partial, move SL to breakeven, keep runner open.
    """
    logger.warning(f"[StackMentor:{user_id}] TP1 HIT {symbol} @ {mark_price:.4f}")
    
    entry = pos_data['entry_price']
    side = pos_data['side']
    qty_tp1 = float(pos_data.get('qty_tp1', 0) or 0)
    total_qty = float(pos_data.get("total_qty", qty_tp1) or qty_tp1)
    qty_tp3 = float(pos_data.get("qty_tp3", 0) or 0)
    runner_on = stackmentor_runner_enabled() and qty_tp3 > 0

    # 1) Close TP1 allocation via reduce-only close_partial
    # Pass position_side for hedge mode compatibility
    qty_to_close = qty_tp1 if qty_tp1 > 0 else total_qty
    if qty_to_close <= 0:
        logger.error(f"[StackMentor:{user_id}] TP1 close skipped {symbol}: qty_to_close <= 0")
        return

    close_side = "SELL" if side == "LONG" else "BUY"
    close_result = await asyncio.to_thread(
        client.close_partial,
        symbol,
        close_side,
        qty_to_close,
        side,  # position_side: LONG or SHORT (required for hedge mode)
    )
    
    if not close_result.get('success'):
        logger.error(f"[StackMentor:{user_id}] TP1 close failed: {close_result.get('error')}")
        return

    profit_tp1 = abs(mark_price - entry) * qty_to_close
    remaining_qty = max(0.0, float(total_qty - qty_to_close))

    # 2) Update position data
    pos_data['tp1_hit'] = True
    pos_data['tp1_hit_at'] = datetime.utcnow()
    pos_data['profit_tp1'] = float(profit_tp1)
    pos_data['remaining_qty'] = float(remaining_qty)

    if runner_on:
        logger.info(
            f"[StackMentor:{user_id}] TP1 partial close @ {mark_price:.4f} "
            f"qty_closed={qty_to_close:.8f} remaining={remaining_qty:.8f}"
        )
        # TP2 is skipped in runner mode; jump directly to TP3 checks.
        pos_data['tp2_hit'] = True
        pos_data['tp2_hit_at'] = datetime.utcnow()

        # 3) Move SL to breakeven for runner protection.
        sl_move_ok = False
        try:
            sl_result = await asyncio.to_thread(client.set_position_sl, symbol, float(entry))
            sl_move_ok = bool(sl_result.get("success"))
            if sl_move_ok:
                pos_data["sl_price"] = float(entry)
            else:
                logger.warning(
                    f"[StackMentor:{user_id}] Breakeven SL move failed for {symbol}: "
                    f"{sl_result.get('error')}"
                )
        except Exception as sl_err:
            logger.warning(f"[StackMentor:{user_id}] Breakeven SL exception for {symbol}: {sl_err}")

        pos_data['breakeven_mode'] = sl_move_ok

        # 4) Persist partial realization while keeping trade OPEN.
        try:
            from app.supabase_repo import _client
            db_update = {
                "tp1_hit": True,
                "tp1_hit_at": datetime.utcnow().isoformat(),
                "tp2_hit": True,
                "tp2_hit_at": datetime.utcnow().isoformat(),
                "breakeven_mode": bool(sl_move_ok),
                "sl_moved_to_bep": bool(sl_move_ok),
                "profit_tp1": float(profit_tp1),
                "pnl_usdt": float(profit_tp1),
                "qty": float(remaining_qty),
                "quantity": float(remaining_qty),
                "remaining_quantity": float(remaining_qty),
                "updated_at": datetime.utcnow().isoformat(),
            }
            if sl_move_ok:
                db_update["sl_price"] = float(entry)
                db_update["sl_bep_at"] = datetime.utcnow().isoformat()

            _client().table("autotrade_trades").update(db_update).eq(
                "telegram_id", user_id
            ).eq("symbol", symbol).eq("status", "open").execute()
        except Exception as e:
            logger.error(f"[StackMentor:{user_id}] TP1 partial DB update failed: {e}")

        profit_pct = abs(mark_price - entry) / entry * 100 * pos_data['leverage']
        runner_pct = max(0.0, min(100.0, (remaining_qty / total_qty * 100.0) if total_qty > 0 else 0.0))
        await bot.send_message(
            chat_id=notify_chat_id,
            text=(
                f"🎯 <b>TP1 Hit! — {symbol}</b>\n\n"
                f"✅ Closed <b>{100.0 - runner_pct:.0f}%</b> @ <code>{mark_price:.4f}</code> (1:3)\n"
                f"🔒 Breakeven protection: <b>{'ON' if sl_move_ok else 'FAILED'}</b>\n"
                f"⏳ Runner still open: <b>{runner_pct:.0f}%</b> toward TP3 (1:{float(STACKMENTOR_CONFIG.get('tp3_rr', 5.0)):.0f})\n"
                f"💰 Realized so far: <b>+${profit_tp1:.2f} USDT</b> (+{profit_pct:.1f}%)"
            ),
            parse_mode='HTML'
        )
        return

    logger.info(f"[StackMentor:{user_id}] TP hit, full close @ {mark_price:.4f}")

    # Runner OFF: full close at TP1.
    pos_data['tp2_hit'] = True
    pos_data['tp2_hit_at'] = datetime.utcnow()
    pos_data['tp3_hit'] = True
    pos_data['tp3_hit_at'] = datetime.utcnow()
    pos_data['breakeven_mode'] = False

    # 4) Update database
    try:
        from app.supabase_repo import _client
        from app.trade_history import build_win_reasoning
        from app.win_playbook import compute_playbook_match_from_reasons
        open_row_res = _client().table("autotrade_trades").select("*").eq(
            "telegram_id", user_id
        ).eq("symbol", symbol).eq("status", "open").order("opened_at", desc=True).limit(1).execute()
        open_row = open_row_res.data[0] if open_row_res.data else {}
        match_meta = compute_playbook_match_from_reasons(open_row.get("entry_reasons", []))
        trade_ctx = dict(open_row)
        trade_ctx.update({
            "exit_price": mark_price,
            "pnl_usdt": profit_tp1,
            "close_reason": "closed_tp",
        })
        win_reasoning = build_win_reasoning(
            trade_ctx,
            playbook_tags=match_meta.get("matched_tags", []),
            playbook_score=match_meta.get("playbook_match_score"),
        )
        
        _client().table("autotrade_trades").update({
            "tp1_hit": True,
            "tp1_hit_at": datetime.utcnow().isoformat(),
            "tp2_hit": True,
            "tp2_hit_at": datetime.utcnow().isoformat(),
            "tp3_hit": True,
            "tp3_hit_at": datetime.utcnow().isoformat(),
            "breakeven_mode": False,
            "profit_tp1": float(profit_tp1),
            "pnl_usdt": float(profit_tp1),
            "close_reason": "closed_tp",
            "status": "closed_tp",
            "win_reasoning": win_reasoning,
            "win_reason_tags": match_meta.get("matched_tags", []),
            "playbook_match_score": float(match_meta.get("playbook_match_score", open_row.get("playbook_match_score", 0.0) or 0.0)),
            "effective_risk_pct": open_row.get("effective_risk_pct"),
            "risk_overlay_pct": open_row.get("risk_overlay_pct"),
            "closed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("telegram_id", user_id).eq("symbol", symbol).eq("status", "open").execute()
    except Exception as e:
        logger.error(f"[StackMentor:{user_id}] DB update failed: {e}")

    # 5) Notify user
    profit_pct = abs(mark_price - entry) / entry * 100 * pos_data['leverage']

    remove_stackmentor_position(user_id, symbol)

    # Confirm position closed with coordinator
    try:
        from app.symbol_coordinator import get_coordinator
        coordinator = get_coordinator()
        await coordinator.confirm_closed(user_id, symbol, time.time())
    except Exception as e:
        logger.warning(f"[StackMentor:{user_id}] Coordinator confirm_closed failed: {e}")

    await bot.send_message(
        chat_id=notify_chat_id,
        text=(
            f"🎯 <b>Take Profit Hit! — {symbol}</b>\n\n"
            f"✅ Closed 100% position @ <code>{mark_price:.4f}</code>\n"
            f"⚖️ Fixed R:R: <b>1:3</b>\n"
            f"💰 Profit: <b>+${profit_tp1:.2f} USDT</b> (+{profit_pct:.1f}%)\n\n"
            f"✅ Trade completed with unified StackMentor target."
        ),
        parse_mode='HTML'
    )


async def handle_tp2_hit(bot, user_id: int, client, notify_chat_id: int,
                        symbol: str, pos_data: Dict, mark_price: float):
    """
    TP2 Hit: Close 30% of original position
    """
    logger.warning(f"[StackMentor:{user_id}] TP2 HIT {symbol} @ {mark_price:.4f}")

    entry = pos_data['entry_price']
    side = pos_data['side']
    qty_tp2 = pos_data['qty_tp2']

    if qty_tp2 <= 0:
        logger.error(
            f"[StackMentor:{user_id}] TP2 qty=0 for {symbol} — qty_splits were miscalculated. "
            f"Marking hit anyway to unblock TP3."
        )
        # Still mark hit so monitoring advances to TP3
        pos_data['tp2_hit'] = True
        pos_data['tp2_hit_at'] = datetime.utcnow()
        return

    # Close 30% via reduce-only close_partial
    close_side = "SELL" if side == "LONG" else "BUY"
    close_result = await asyncio.to_thread(
        client.close_partial,
        symbol,
        close_side,
        qty_tp2,
        side,
    )

    if not close_result.get('success'):
        logger.error(f"[StackMentor:{user_id}] TP2 close failed: {close_result.get('error')}")
        return
    
    logger.info(f"[StackMentor:{user_id}] TP2 closed 30% @ {mark_price:.4f}")
    
    # Update position data
    pos_data['tp2_hit'] = True
    pos_data['tp2_hit_at'] = datetime.utcnow()
    
    # Update database
    try:
        from app.supabase_repo import _client
        profit_tp2 = abs(mark_price - entry) * qty_tp2
        
        _client().table("autotrade_trades").update({
            "tp2_hit": True,
            "tp2_hit_at": datetime.utcnow().isoformat(),
            "profit_tp2": profit_tp2,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("telegram_id", user_id).eq("symbol", symbol).eq("status", "open").execute()
    except Exception as e:
        logger.error(f"[StackMentor:{user_id}] DB update failed: {e}")
    
    # Notify user
    profit_pct = abs(mark_price - entry) / entry * 100 * pos_data['leverage']
    
    await bot.send_message(
        chat_id=notify_chat_id,
        text=(
            f"🎯🎯 <b>Take Profit 2 Hit! — {symbol}</b>\n\n"
            f"✅ Closed 30% position @ <code>{mark_price:.4f}</code>\n"
            f"💰 Additional profit: <b>+${profit_tp2:.2f} USDT</b> (+{profit_pct:.1f}%)\n\n"
            f"🔒 SL remains at breakeven (entry price)\n"
            f"⏳ Final 10% still running to TP3 (target 1:5)...\n\n"
            f"💡 <b>Status:</b>\n"
            f"✅ 90% of position closed with profit\n"
            f"✅ Last 10% = bonus if market continues\n"
            f"✅ Zero loss risk (SL at breakeven)\n\n"
            f"🎯 StackMentor: Profit secured, bonus trade still running!"
        ),
        parse_mode='HTML'
    )


async def handle_tp3_hit(bot, user_id: int, client, notify_chat_id: int,
                        symbol: str, pos_data: Dict, mark_price: float):
    """
    TP3 Hit: Close final runner allocation and finalize trade.
    """
    logger.warning(f"[StackMentor:{user_id}] TP3 HIT {symbol} @ {mark_price:.4f}")

    entry = pos_data['entry_price']
    side = pos_data['side']
    qty_tp3 = float(pos_data.get('qty_tp3', 0) or 0)
    qty_tp1 = float(pos_data.get("qty_tp1", 0) or 0)
    qty_tp2 = float(pos_data.get("qty_tp2", 0) or 0)
    total_qty = float(pos_data.get("total_qty", max(0.0, qty_tp1 + qty_tp2 + qty_tp3)) or 0.0)

    if qty_tp3 <= 0:
        logger.error(
            f"[StackMentor:{user_id}] TP3 qty=0 for {symbol} — qty_splits were miscalculated. "
            f"Position already fully closed by TP1/TP2. Cleaning up."
        )
        remove_stackmentor_position(user_id, symbol)
        return

    # Close final 10% via reduce-only close_partial
    close_side = "SELL" if side == "LONG" else "BUY"
    close_result = await asyncio.to_thread(
        client.close_partial,
        symbol,
        close_side,
        qty_tp3,
        side,
    )

    if not close_result.get('success'):
        logger.error(f"[StackMentor:{user_id}] TP3 close failed: {close_result.get('error')}")
        return
    
    logger.info(f"[StackMentor:{user_id}] TP3 closed 10% @ {mark_price:.4f}")
    
    # Calculate total profit
    profit_tp1 = float(pos_data.get("profit_tp1") or abs(pos_data['tp1'] - entry) * qty_tp1)
    profit_tp2 = float(pos_data.get("profit_tp2") or abs(pos_data['tp2'] - entry) * qty_tp2)
    profit_tp3 = abs(mark_price - entry) * qty_tp3
    total_profit = profit_tp1 + profit_tp2 + profit_tp3
    
    # Update position data
    pos_data['tp3_hit'] = True
    pos_data['tp3_hit_at'] = datetime.utcnow()
    
    # Update database - position fully closed
    try:
        from app.supabase_repo import _client
        from app.trade_history import build_win_reasoning
        from app.win_playbook import compute_playbook_match_from_reasons
        open_row_res = _client().table("autotrade_trades").select("*").eq(
            "telegram_id", user_id
        ).eq("symbol", symbol).eq("status", "open").order("opened_at", desc=True).limit(1).execute()
        open_row = open_row_res.data[0] if open_row_res.data else {}
        match_meta = compute_playbook_match_from_reasons(open_row.get("entry_reasons", []))
        trade_ctx = dict(open_row)
        trade_ctx.update({
            "exit_price": mark_price,
            "pnl_usdt": total_profit,
            "close_reason": "closed_tp3",
        })
        win_reasoning = build_win_reasoning(
            trade_ctx,
            playbook_tags=match_meta.get("matched_tags", []),
            playbook_score=match_meta.get("playbook_match_score"),
        )
        
        _client().table("autotrade_trades").update({
            "tp3_hit": True,
            "tp3_hit_at": datetime.utcnow().isoformat(),
            "profit_tp1": float(profit_tp1),
            "profit_tp2": float(profit_tp2),
            "profit_tp3": float(profit_tp3),
            "pnl_usdt": float(total_profit),
            "close_reason": "closed_tp3",
            "status": "closed_tp3",
            "qty": 0.0,
            "quantity": 0.0,
            "remaining_quantity": 0.0,
            "win_reasoning": win_reasoning,
            "win_reason_tags": match_meta.get("matched_tags", []),
            "playbook_match_score": float(match_meta.get("playbook_match_score", open_row.get("playbook_match_score", 0.0) or 0.0)),
            "effective_risk_pct": open_row.get("effective_risk_pct"),
            "risk_overlay_pct": open_row.get("risk_overlay_pct"),
            "closed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("telegram_id", user_id).eq("symbol", symbol).eq("status", "open").execute()
    except Exception as e:
        logger.error(f"[StackMentor:{user_id}] DB update failed: {e}")
    
    # Remove from monitoring
    remove_stackmentor_position(user_id, symbol)

    # Confirm position closed with coordinator
    try:
        from app.symbol_coordinator import get_coordinator
        coordinator = get_coordinator()
        await coordinator.confirm_closed(user_id, symbol, time.time())
    except Exception as e:
        logger.warning(f"[StackMentor:{user_id}] Coordinator confirm_closed failed: {e}")
    
    # Notify user - CELEBRATION!
    profit_pct = abs(mark_price - entry) / entry * 100 * pos_data['leverage']
    tp1_pct = (qty_tp1 / total_qty * 100.0) if total_qty > 0 else 0.0
    tp2_pct = (qty_tp2 / total_qty * 100.0) if total_qty > 0 else 0.0
    tp3_pct = (qty_tp3 / total_qty * 100.0) if total_qty > 0 else 0.0
    
    await bot.send_message(
        chat_id=notify_chat_id,
        text=(
            f"🎉🎉🎉 <b>Runner Target Hit! — {symbol}</b>\n\n"
            f"✅ Closed final runner @ <code>{mark_price:.4f}</code>\n"
            f"💰 TP3 profit: <b>+${profit_tp3:.2f} USDT</b> (+{profit_pct:.1f}%)\n\n"
            f"🏆 <b>TOTAL PROFIT THIS TRADE:</b>\n"
            f"💵 <b>+${total_profit:.2f} USDT</b>\n\n"
            f"📊 <b>Staged Profit Breakdown:</b>\n"
            f"• TP1 ({tp1_pct:.0f}%): +${profit_tp1:.2f} ✅\n"
            f"• TP2 ({tp2_pct:.0f}%): +${profit_tp2:.2f} ✅\n"
            f"• TP3 ({tp3_pct:.0f}%): +${profit_tp3:.2f} ✅\n\n"
            f"💡 <b>Why this strategy works:</b>\n"
            f"✅ Profit taken in stages (not greedy)\n"
            f"✅ Risk minimized (SL moved to breakeven)\n"
            f"✅ Still captured bonus if market kept running\n\n"
            f"🎯 StackMentor: Perfect execution! All targets hit! 🔥"
        ),
        parse_mode='HTML'
    )
    
    # Broadcast big wins (≥$10)
    if total_profit >= 10.0:
        try:
            from app.social_proof import broadcast_profit
            from app.supabase_repo import get_user_by_tid
            
            user_data = get_user_by_tid(user_id)
            fname = user_data.get("first_name", "User") if user_data else "User"
            
            asyncio.create_task(broadcast_profit(
                bot=bot,
                user_id=user_id,
                first_name=fname,
                symbol=symbol,
                side=side,
                pnl_usdt=total_profit,
                leverage=pos_data['leverage'],
            ))
        except Exception as e:
            logger.warning(f"[StackMentor:{user_id}] Broadcast failed: {e}")
