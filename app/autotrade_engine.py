"""
AutoTrade Engine — per-user trading loop.
Flow: generate signal → set leverage → place order with TP/SL → monitor → repeat.
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# user_id → asyncio.Task
_running_tasks: Dict[int, asyncio.Task] = {}


def is_running(user_id: int) -> bool:
    t = _running_tasks.get(user_id)
    return t is not None and not t.done()


def stop_engine(user_id: int):
    t = _running_tasks.get(user_id)
    if t and not t.done():
        t.cancel()
        logger.info(f"AutoTrade stopped for user {user_id}")


def start_engine(bot, user_id: int, api_key: str, api_secret: str,
                 amount: float, leverage: int, notify_chat_id: int):
    """Start per-user autotrade loop as background asyncio task."""
    stop_engine(user_id)  # cancel existing if any
    task = asyncio.create_task(
        _trade_loop(bot, user_id, api_key, api_secret, amount, leverage, notify_chat_id)
    )
    _running_tasks[user_id] = task
    logger.info(f"AutoTrade started for user {user_id}, amount={amount}, leverage={leverage}x")


async def _trade_loop(bot, user_id: int, api_key: str, api_secret: str,
                      amount: float, leverage: int, notify_chat_id: int):
    """Main trading loop — runs until cancelled."""
    from app.bitunix_autotrade_client import BitunixAutoTradeClient
    from app.autosignal_fast import compute_signal_fast
    from app.supabase_repo import _client

    client = BitunixAutoTradeClient(api_key=api_key, api_secret=api_secret)

    # Symbols to scan (top liquid futures)
    SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    SCAN_INTERVAL = 60   # seconds between scans
    MIN_CONFIDENCE = 75  # only trade high-confidence signals

    await bot.send_message(
        chat_id=notify_chat_id,
        text="🤖 <b>AutoTrade Engine aktif!</b>\n\nBot sedang memantau pasar dan akan eksekusi trade otomatis.",
        parse_mode='HTML'
    )

    while True:
        try:
            # 1. Cek apakah ada posisi terbuka — skip scan kalau masih ada
            pos_result = await asyncio.to_thread(client.get_positions)
            open_positions = pos_result.get('positions', []) if pos_result.get('success') else []

            if open_positions:
                pos_text = "\n".join([
                    f"• {p['symbol']} {p['side']} | PnL: {p['pnl']:+.2f} USDT"
                    for p in open_positions
                ])
                logger.info(f"User {user_id} has {len(open_positions)} open positions, skipping scan")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            # 2. Scan symbols untuk signal
            best_signal: Optional[Dict] = None
            for sym in SYMBOLS:
                try:
                    sig = await asyncio.to_thread(compute_signal_fast, sym)
                    if sig and sig.get('confidence', 0) >= MIN_CONFIDENCE:
                        if best_signal is None or sig['confidence'] > best_signal['confidence']:
                            best_signal = sig
                except Exception as e:
                    logger.warning(f"Signal scan error for {sym}: {e}")

            if not best_signal:
                logger.info(f"User {user_id}: no signal found, waiting {SCAN_INTERVAL}s")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            sig = best_signal
            symbol = sig['symbol']       # e.g. BTCUSDT
            side = sig['side']           # LONG / SHORT
            entry = sig['entry_price']
            tp1 = sig['tp1']
            sl = sig['sl']
            confidence = sig['confidence']

            # 3. Hitung qty berdasarkan amount + leverage
            # qty = (amount * leverage) / entry_price
            notional = amount * leverage
            qty = round(notional / entry, 4)
            if qty <= 0:
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            # 4. Set leverage
            order_side = "BUY" if side == "LONG" else "SELL"
            await asyncio.to_thread(client.set_leverage, symbol, leverage)

            # 5. Place order dengan TP/SL
            order_result = await asyncio.to_thread(
                client.place_order_with_tpsl,
                symbol, order_side, qty, tp1, sl
            )

            if not order_result.get('success'):
                err = order_result.get('error', 'Unknown error')
                logger.error(f"User {user_id} order failed: {err}")
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=f"⚠️ <b>Order gagal:</b> {err}\n\nBot tetap berjalan dan akan coba signal berikutnya.",
                    parse_mode='HTML'
                )
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            order_id = order_result.get('order_id', '-')

            # 6. Notifikasi user
            risk_pct = abs(entry - sl) / entry * 100 * leverage
            reward_pct = abs(tp1 - entry) / entry * 100 * leverage
            potential_profit = amount * (reward_pct / 100)
            potential_loss = amount * (risk_pct / 100)

            await bot.send_message(
                chat_id=notify_chat_id,
                text=(
                    f"✅ <b>ORDER TEREKSEKUSI</b>\n\n"
                    f"📊 {symbol} | {side} | {leverage}x\n"
                    f"💵 Entry: <code>{entry:.4f}</code>\n"
                    f"🎯 TP: <code>{tp1:.4f}</code>\n"
                    f"🛑 SL: <code>{sl:.4f}</code>\n"
                    f"📦 Qty: {qty}\n\n"
                    f"💰 Potensi profit: +{potential_profit:.2f} USDT ({reward_pct:.1f}%)\n"
                    f"⚠️ Potensi loss: -{potential_loss:.2f} USDT ({risk_pct:.1f}%)\n"
                    f"🧠 Confidence: {confidence}%\n"
                    f"🔖 Order ID: <code>{order_id}</code>"
                ),
                parse_mode='HTML'
            )

            # 7. Update session di Supabase
            try:
                _client().table("autotrade_sessions").update({
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_id", user_id).execute()
            except Exception:
                pass

            # 8. Tunggu sebelum scan berikutnya
            await asyncio.sleep(SCAN_INTERVAL * 2)

        except asyncio.CancelledError:
            logger.info(f"AutoTrade loop cancelled for user {user_id}")
            try:
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text="🛑 <b>AutoTrade dihentikan.</b>",
                    parse_mode='HTML'
                )
            except Exception:
                pass
            return

        except Exception as e:
            logger.error(f"AutoTrade loop error for user {user_id}: {e}", exc_info=True)
            await asyncio.sleep(30)  # brief pause before retry
