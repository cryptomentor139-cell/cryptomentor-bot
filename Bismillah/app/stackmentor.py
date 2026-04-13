"""
StackMentor System - staged TP strategy with bot-side fail-safe execution.

Design goals:
1) Use staged exits (TP1/TP2/TP3) with breakeven after TP1.
2) Force-close positions at TP/SL from bot-side when exchange trigger fails.
3) Recover monitoring after process restarts by hydrating open DB trades.
"""

import asyncio
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# StackMentor Configuration
STACKMENTOR_CONFIG = {
    "enabled": True,            # Enable for all users
    "tp1_pct": 0.60,            # Close 60% at TP1
    "tp2_pct": 0.30,            # Close 30% at TP2
    "tp3_pct": 0.10,            # Close 10% at TP3
    "target_rr": 3.0,           # Average risk:reward around 1:3
    "tp1_rr": 2.0,
    "tp2_rr": 3.0,
    "tp3_rr": 5.0,
    "breakeven_after_tp1": True,
}

# Track StackMentor positions: user_id → {symbol: position_data}
_stackmentor_positions: Dict[int, Dict[str, Dict]] = {}


def calculate_stackmentor_levels(
    entry_price: float,
    sl_price: float,
    side: str
) -> Tuple[float, float, float]:
    """
    Calculate staged TP levels based on SL distance.
    Returns: (tp1, tp2, tp3)
    """
    cfg = STACKMENTOR_CONFIG
    
    # Calculate SL distance
    sl_distance = abs(entry_price - sl_price)
    
    rr1 = float(cfg.get("tp1_rr", 2.0))
    rr2 = float(cfg.get("tp2_rr", 3.0))
    rr3 = float(cfg.get("tp3_rr", 5.0))
    if side == "LONG":
        tp1 = entry_price + (sl_distance * rr1)
        tp2 = entry_price + (sl_distance * rr2)
        tp3 = entry_price + (sl_distance * rr3)
    else:  # SHORT
        tp1 = entry_price - (sl_distance * rr1)
        tp2 = entry_price - (sl_distance * rr2)
        tp3 = entry_price - (sl_distance * rr3)
    
    return (tp1, tp2, tp3)


def calculate_qty_splits(total_qty: float, min_qty: float = 0.0, precision: int = 3) -> Tuple[float, float, float]:
    """
    Split quantity for staged execution.

    Returns: (qty_tp1, qty_tp2, qty_tp3)
    """
    cfg = STACKMENTOR_CONFIG
    
    # Analyze the actual precision of total_qty
    qty_str = f"{total_qty:.8f}".rstrip('0')
    if '.' in qty_str:
        actual_prec = len(qty_str.split('.')[1])
        precision = max(precision, actual_prec)
    
    qty_tp1 = round(total_qty * cfg["tp1_pct"], precision)
    qty_tp2 = round(total_qty * cfg["tp2_pct"], precision)
    qty_tp3 = round(total_qty - qty_tp1 - qty_tp2, precision)
    
    # Collapse small fragments safely to avoid MIN_QTY Bitunix Limit exceptions
    if min_qty > 0:
        if 0 < qty_tp3 < min_qty:
            qty_tp2 += qty_tp3
            qty_tp3 = 0.0
            qty_tp2 = round(qty_tp2, precision)
            
        if 0 < qty_tp2 < min_qty:
            qty_tp1 += qty_tp2
            qty_tp2 = 0.0
            qty_tp1 = round(qty_tp1, precision)
            
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


def _remaining_qty(pos_data: Dict) -> float:
    """Get remaining quantity that should still be open."""
    qty = float(pos_data.get("total_qty") or 0)
    if pos_data.get("tp1_hit"):
        qty -= float(pos_data.get("qty_tp1") or 0)
    if pos_data.get("tp2_hit"):
        qty -= float(pos_data.get("qty_tp2") or 0)
    if pos_data.get("tp3_hit"):
        qty -= float(pos_data.get("qty_tp3") or 0)
    return max(0.0, qty)


def _normalize_side(raw_side: str) -> str:
    side = str(raw_side or "").upper()
    if side in ("BUY", "LONG"):
        return "LONG"
    if side in ("SELL", "SHORT"):
        return "SHORT"
    return "LONG"


def _hydrate_stackmentor_positions(user_id: int):
    """
    Reload in-memory StackMentor map from open DB trades.
    This protects monitoring continuity after service restarts.
    """
    try:
        from app.supabase_repo import _client
        s = _client()
        rows = s.table("autotrade_trades").select(
            "symbol, side, entry_price, sl_price, tp1_price, tp2_price, tp3_price, "
            "qty, quantity, leverage, qty_tp1, qty_tp2, qty_tp3, strategy, status, "
            "tp1_hit, tp2_hit, tp3_hit, tp1_hit_at, tp2_hit_at, tp3_hit_at, breakeven_mode, opened_at"
        ).eq("telegram_id", int(user_id)).eq("status", "open").execute().data or []
    except Exception as e:
        logger.warning(f"[StackMentor:{user_id}] Hydration query failed: {e}")
        return

    if user_id not in _stackmentor_positions:
        _stackmentor_positions[user_id] = {}

    hydrated = 0
    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol or symbol in _stackmentor_positions[user_id]:
            continue

        strategy = str(row.get("strategy") or "").lower()
        if strategy == "legacy":
            continue

        total_qty = float(row.get("qty") or row.get("quantity") or 0)
        if total_qty <= 0:
            continue

        side = _normalize_side(row.get("side"))
        entry = float(row.get("entry_price") or 0)
        sl = float(row.get("sl_price") or 0)
        if entry <= 0 or sl <= 0:
            continue

        tp1 = float(row.get("tp1_price") or 0)
        tp2 = float(row.get("tp2_price") or 0)
        tp3 = float(row.get("tp3_price") or 0)
        if tp1 <= 0 or tp2 <= 0 or tp3 <= 0:
            tp1, tp2, tp3 = calculate_stackmentor_levels(entry, sl, side)

        qty_tp1 = float(row.get("qty_tp1") or 0)
        qty_tp2 = float(row.get("qty_tp2") or 0)
        qty_tp3 = float(row.get("qty_tp3") or 0)
        if qty_tp1 <= 0 and qty_tp2 <= 0 and qty_tp3 <= 0:
            qty_tp1, qty_tp2, qty_tp3 = calculate_qty_splits(total_qty, precision=3)

        _stackmentor_positions[user_id][symbol] = {
            "entry_price": entry,
            "sl_price": sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "total_qty": total_qty,
            "qty_tp1": qty_tp1,
            "qty_tp2": qty_tp2,
            "qty_tp3": qty_tp3,
            "side": side,
            "leverage": int(row.get("leverage") or 1),
            "tp1_hit": bool(row.get("tp1_hit")),
            "tp2_hit": bool(row.get("tp2_hit")),
            "tp3_hit": bool(row.get("tp3_hit")),
            "tp1_hit_at": row.get("tp1_hit_at"),
            "tp2_hit_at": row.get("tp2_hit_at"),
            "tp3_hit_at": row.get("tp3_hit_at"),
            "breakeven_mode": bool(row.get("breakeven_mode")),
            "opened_at": datetime.utcnow(),
        }
        hydrated += 1

    if hydrated > 0:
        logger.info(f"[StackMentor:{user_id}] Hydrated {hydrated} open position(s) from DB")


async def monitor_stackmentor_positions(bot, user_id: int, client, notify_chat_id: int):
    """
    Monitor StackMentor positions for TP hits
    Called from main trade loop every scan interval
    """
    if user_id not in _stackmentor_positions or not _stackmentor_positions.get(user_id):
        _hydrate_stackmentor_positions(user_id)
    if user_id not in _stackmentor_positions or not _stackmentor_positions.get(user_id):
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

            # Bot-side SL watchdog (fail-safe if exchange SL did not trigger).
            sl_hit = (side == "LONG" and mark_price <= pos_data['sl_price']) or \
                     (side == "SHORT" and mark_price >= pos_data['sl_price'])
            if sl_hit:
                await handle_sl_hit(bot, user_id, client, notify_chat_id, symbol, pos_data, mark_price)
                continue
            
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
    TP1 Hit: close partial and move SL to breakeven for remaining size.
    """
    logger.warning(f"[StackMentor:{user_id}] TP1 HIT {symbol} @ {mark_price:.4f}")
    
    entry = pos_data['entry_price']
    side = pos_data['side']
    qty_tp1 = pos_data['qty_tp1']
    
    if qty_tp1 <= 0:
        logger.error(f"[StackMentor:{user_id}] TP1 qty=0 for {symbol} — skipping")
        return

    # 1) Close TP1 tranche via reduce-only.
    close_side = "SELL" if side == "LONG" else "BUY"
    close_result = await asyncio.to_thread(
        client.close_partial,
        symbol,
        close_side,
        qty_tp1,
        side,  # position_side: LONG or SHORT (required for hedge mode)
    )
    
    if not close_result.get('success'):
        logger.error(f"[StackMentor:{user_id}] TP1 close failed: {close_result.get('error')}")
        return
    
    logger.info(f"[StackMentor:{user_id}] TP1 closed tranche @ {mark_price:.4f}")

    # 2) Update in-memory state.
    pos_data['tp1_hit'] = True
    pos_data['tp1_hit_at'] = datetime.utcnow()
    profit_tp1 = abs(mark_price - entry) * qty_tp1

    remaining_qty = _remaining_qty(pos_data)
    moved_to_be = False
    if STACKMENTOR_CONFIG.get("breakeven_after_tp1", True) and remaining_qty > 0:
        # 3) Move SL to breakeven for remaining qty.
        try:
            be_result = await asyncio.to_thread(client.set_position_sl, symbol, entry)
            moved_to_be = bool(be_result.get("success"))
        except Exception as e:
            logger.warning(f"[StackMentor:{user_id}] Breakeven SL update failed: {e}")
            moved_to_be = False
        if moved_to_be:
            pos_data["sl_price"] = entry
            pos_data["breakeven_mode"] = True

    # 4) Persist DB state.
    try:
        from app.supabase_repo import _client
        update_payload = {
            "tp1_hit": True,
            "tp1_hit_at": datetime.utcnow().isoformat(),
            "breakeven_mode": moved_to_be,
            "profit_tp1": profit_tp1,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if moved_to_be:
            update_payload["sl_price"] = entry

        # If no remainder, close as TP immediately.
        if remaining_qty <= 0:
            now_iso = datetime.utcnow().isoformat()
            update_payload.update({
                "tp2_hit": True,
                "tp2_hit_at": now_iso,
                "tp3_hit": True,
                "tp3_hit_at": now_iso,
                "pnl_usdt": profit_tp1,
                "status": "closed_tp",
                "closed_at": now_iso,
            })
        _client().table("autotrade_trades").update(update_payload).eq("telegram_id", user_id).eq("symbol", symbol).eq("status", "open").execute()
    except Exception as e:
        logger.error(f"[StackMentor:{user_id}] DB update failed: {e}")
    
    # 5) Notify user.
    profit_pct = abs(mark_price - entry) / entry * 100 * pos_data['leverage']
    if remaining_qty <= 0:
        remove_stackmentor_position(user_id, symbol)
        await bot.send_message(
            chat_id=notify_chat_id,
            text=(
                f"🎯 <b>Take Profit Hit! — {symbol}</b>\n\n"
                f"✅ Closed 100% position @ <code>{mark_price:.4f}</code>\n"
                f"⚖️ Fixed R:R: <b>1:3</b>\n"
                f"💰 Profit: <b>+${profit_tp1:.2f} USDT</b> (+{profit_pct:.1f}%)\n\n"
                f"✅ Trade completed."
            ),
            parse_mode='HTML'
        )
    else:
        await bot.send_message(
            chat_id=notify_chat_id,
            text=(
                f"🎯 <b>TP1 Hit — {symbol}</b>\n\n"
                f"✅ Closed TP1 tranche @ <code>{mark_price:.4f}</code>\n"
                f"💰 Locked: <b>+${profit_tp1:.2f} USDT</b> (+{profit_pct:.1f}%)\n"
                + (f"🔒 SL moved to breakeven: <code>{entry:.4f}</code>\n" if moved_to_be else "⚠️ Breakeven SL update failed — will retry via monitor\n")
                + f"\n⏳ Remaining position continues to TP2/TP3."
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


async def handle_sl_hit(bot, user_id: int, client, notify_chat_id: int,
                        symbol: str, pos_data: Dict, mark_price: float):
    """
    Force-close remaining quantity when mark crosses SL.
    This acts as bot-side fail-safe if exchange SL trigger misses.
    """
    logger.error(f"[StackMentor:{user_id}] SL HIT watchdog for {symbol} @ {mark_price:.4f} — forcing close")

    entry = float(pos_data.get("entry_price") or 0)
    side = pos_data.get("side", "LONG")
    remaining_qty = _remaining_qty(pos_data)
    if remaining_qty <= 0:
        remove_stackmentor_position(user_id, symbol)
        return

    close_side = "SELL" if side == "LONG" else "BUY"
    close_result = await asyncio.to_thread(
        client.close_partial,
        symbol,
        close_side,
        remaining_qty,
        side,
    )
    if not close_result.get("success"):
        logger.error(f"[StackMentor:{user_id}] SL force-close failed: {close_result.get('error')}")
        return

    pnl_force = abs(mark_price - entry) * remaining_qty
    if side == "LONG":
        pnl_force = (mark_price - entry) * remaining_qty
    else:
        pnl_force = (entry - mark_price) * remaining_qty

    try:
        from app.supabase_repo import _client
        _client().table("autotrade_trades").update({
            "pnl_usdt": pnl_force,
            "close_reason": "stackmentor_force_sl",
            "status": "closed_sl",
            "closed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("telegram_id", user_id).eq("symbol", symbol).eq("status", "open").execute()
    except Exception as e:
        logger.error(f"[StackMentor:{user_id}] SL DB update failed: {e}")

    remove_stackmentor_position(user_id, symbol)
    await bot.send_message(
        chat_id=notify_chat_id,
        text=(
            f"🛑 <b>Stop Loss Triggered — {symbol}</b>\n\n"
            f"⚠️ Exchange SL was not confirmed in time, bot executed force close.\n"
            f"📍 Exit: <code>{mark_price:.4f}</code>\n"
            f"💵 PnL: <b>{pnl_force:+.2f} USDT</b>"
        ),
        parse_mode='HTML'
    )


async def handle_tp3_hit(bot, user_id: int, client, notify_chat_id: int,
                        symbol: str, pos_data: Dict, mark_price: float):
    """
    TP3 Hit: Close final 10% - JACKPOT!
    """
    logger.warning(f"[StackMentor:{user_id}] TP3 HIT {symbol} @ {mark_price:.4f} — JACKPOT!")

    entry = pos_data['entry_price']
    side = pos_data['side']
    qty_tp3 = pos_data['qty_tp3']

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
    total_qty = pos_data['total_qty']
    profit_tp1 = abs(pos_data['tp1'] - entry) * pos_data['qty_tp1']
    profit_tp2 = abs(pos_data['tp2'] - entry) * pos_data['qty_tp2']
    profit_tp3 = abs(mark_price - entry) * qty_tp3
    total_profit = profit_tp1 + profit_tp2 + profit_tp3
    
    # Update position data
    pos_data['tp3_hit'] = True
    pos_data['tp3_hit_at'] = datetime.utcnow()
    
    # Update database - position fully closed
    try:
        from app.supabase_repo import _client
        
        _client().table("autotrade_trades").update({
            "tp3_hit": True,
            "tp3_hit_at": datetime.utcnow().isoformat(),
            "profit_tp3": profit_tp3,
            "pnl_usdt": total_profit,
            "status": "closed_tp3",
            "closed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("telegram_id", user_id).eq("symbol", symbol).eq("status", "open").execute()
    except Exception as e:
        logger.error(f"[StackMentor:{user_id}] DB update failed: {e}")
    
    # Remove from monitoring
    remove_stackmentor_position(user_id, symbol)
    
    # Notify user - CELEBRATION!
    profit_pct = abs(mark_price - entry) / entry * 100 * pos_data['leverage']
    
    await bot.send_message(
        chat_id=notify_chat_id,
        text=(
            f"🎉🎉🎉 <b>JACKPOT! Take Profit 3 Hit! — {symbol}</b>\n\n"
            f"✅ Closed final 10% @ <code>{mark_price:.4f}</code>\n"
            f"💰 TP3 profit: <b>+${profit_tp3:.2f} USDT</b> (+{profit_pct:.1f}%)\n\n"
            f"🏆 <b>TOTAL PROFIT THIS TRADE:</b>\n"
            f"💵 <b>+${total_profit:.2f} USDT</b>\n\n"
            f"📊 <b>Staged Profit Breakdown:</b>\n"
            f"• TP1 (60% position): +${profit_tp1:.2f} ✅\n"
            f"• TP2 (30% position): +${profit_tp2:.2f} ✅\n"
            f"• TP3 (10% position): +${profit_tp3:.2f} ✅\n\n"
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
