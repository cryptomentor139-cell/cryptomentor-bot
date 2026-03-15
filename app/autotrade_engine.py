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


def _compute_signal_simple(base_symbol: str, client) -> Optional[Dict]:
    """
    Simple but reliable signal using EMA crossover + RSI + momentum.
    Fallback ke compute_signal_fast kalau available.
    """
    import requests

    symbol = base_symbol.upper() + "USDT"

    try:
        # Ambil klines dari Binance (public, no auth needed)
        r = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": "15m", "limit": 50},
            timeout=8
        )
        klines = r.json()
        if not isinstance(klines, list) or len(klines) < 20:
            return None

        closes = [float(k[4]) for k in klines]
        highs  = [float(k[2]) for k in klines]
        lows   = [float(k[3]) for k in klines]
        price  = closes[-1]

        # EMA calculation
        def ema(data, period):
            k = 2 / (period + 1)
            e = data[0]
            for v in data[1:]:
                e = v * k + e * (1 - k)
            return e

        ema9  = ema(closes, 9)
        ema21 = ema(closes, 21)
        ema9_prev  = ema(closes[:-1], 9)
        ema21_prev = ema(closes[:-1], 21)

        # RSI
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            (gains if diff > 0 else losses).append(abs(diff))
        avg_gain = sum(gains) / 14 if gains else 0.001
        avg_loss = sum(losses) / 14 if losses else 0.001
        rsi = 100 - (100 / (1 + avg_gain / avg_loss))

        # 24h change
        change_24h = (price - closes[0]) / closes[0] * 100

        # Recent high/low (last 20 candles)
        recent_high = max(highs[-20:])
        recent_low  = min(lows[-20:])
        range_pct   = (recent_high - recent_low) / recent_low * 100

        side = None
        confidence = 50
        reasons = []

        # EMA crossover bullish
        if ema9 > ema21 and ema9_prev <= ema21_prev:
            side = "LONG"
            confidence = 72
            reasons.append("EMA9 cross above EMA21")
        # EMA crossover bearish
        elif ema9 < ema21 and ema9_prev >= ema21_prev:
            side = "SHORT"
            confidence = 72
            reasons.append("EMA9 cross below EMA21")
        # EMA trend + RSI
        elif ema9 > ema21 and rsi < 45:
            side = "LONG"
            confidence = 68
            reasons.append(f"Uptrend + RSI oversold ({rsi:.0f})")
        elif ema9 < ema21 and rsi > 55:
            side = "SHORT"
            confidence = 68
            reasons.append(f"Downtrend + RSI overbought ({rsi:.0f})")
        # Breakout
        elif price > recent_high * 0.999 and change_24h > 1.5:
            side = "LONG"
            confidence = 70
            reasons.append(f"Breakout high + momentum {change_24h:+.1f}%")
        elif price < recent_low * 1.001 and change_24h < -1.5:
            side = "SHORT"
            confidence = 70
            reasons.append(f"Breakdown low + momentum {change_24h:.1f}%")

        if side is None:
            return None

        # RSI confirmation bonus
        if side == "LONG" and rsi < 50:
            confidence += 5
            reasons.append(f"RSI {rsi:.0f}")
        elif side == "SHORT" and rsi > 50:
            confidence += 5
            reasons.append(f"RSI {rsi:.0f}")

        # TP/SL based on recent range
        atr = range_pct / 100 * price * 0.3  # simplified ATR
        if side == "LONG":
            tp1 = price + atr * 2
            sl  = price - atr
        else:
            tp1 = price - atr * 2
            sl  = price + atr

        return {
            "symbol": symbol,
            "side": side,
            "confidence": int(min(confidence, 90)),
            "entry_price": price,
            "tp1": round(tp1, 6),
            "tp2": round(tp1 * (1.01 if side == "LONG" else 0.99), 6),
            "sl": round(sl, 6),
            "reasons": reasons,
        }

    except Exception as e:
        logger.warning(f"_compute_signal_simple error {base_symbol}: {e}")
        return None


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

    def _task_done_callback(task: asyncio.Task):
        if task.cancelled():
            logger.info(f"AutoTrade task cancelled for user {user_id}")
        elif task.exception():
            logger.error(f"AutoTrade task CRASHED for user {user_id}: {task.exception()}", exc_info=task.exception())
        else:
            logger.info(f"AutoTrade task completed normally for user {user_id}")

    task = asyncio.create_task(
        _trade_loop(bot, user_id, api_key, api_secret, amount, leverage, notify_chat_id)
    )
    task.add_done_callback(_task_done_callback)
    _running_tasks[user_id] = task
    logger.info(f"AutoTrade started for user {user_id}, amount={amount}, leverage={leverage}x")


async def _trade_loop(bot, user_id: int, api_key: str, api_secret: str,
                      amount: float, leverage: int, notify_chat_id: int):
    """Main trading loop — runs until cancelled."""
    import sys, os
    bismillah_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if bismillah_root not in sys.path:
        sys.path.insert(0, bismillah_root)

    from app.bitunix_autotrade_client import BitunixAutoTradeClient
    from app.supabase_repo import _client

    client = BitunixAutoTradeClient(api_key=api_key, api_secret=api_secret)

    SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    SCAN_INTERVAL = 60
    MIN_CONFIDENCE = 65

    # Qty precision per symbol (Bitunix minimum & decimal places)
    QTY_PRECISION = {
        "BTCUSDT": 3,   # min 0.001
        "ETHUSDT": 2,   # min 0.01
        "SOLUSDT": 1,   # min 0.1
        "BNBUSDT": 2,
        "XRPUSDT": 0,   # min 1
    }

    def calc_qty(symbol: str, notional: float, price: float) -> float:
        raw = notional / price
        precision = QTY_PRECISION.get(symbol, 3)
        qty = round(raw, precision)
        # Ensure minimum qty
        min_qty = 10 ** (-precision) if precision > 0 else 1
        return qty if qty >= min_qty else 0.0

    await bot.send_message(
        chat_id=notify_chat_id,
        text="🤖 <b>AutoTrade Engine aktif!</b>\n\nBot sedang memantau pasar dan akan eksekusi trade otomatis.",
        parse_mode='HTML'
    )

    while True:
        try:
            # 1. Cek posisi terbuka
            pos_result = await asyncio.to_thread(client.get_positions)
            open_positions = pos_result.get('positions', []) if pos_result.get('success') else []

            if open_positions:
                logger.info(f"[Engine:{user_id}] {len(open_positions)} open positions, skip scan")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            # 2. Scan symbols untuk signal
            best_signal: Optional[Dict] = None
            scan_results = []
            for sym in SYMBOLS:
                try:
                    sig = await asyncio.to_thread(_compute_signal_simple, sym, client)
                    if sig:
                        scan_results.append(f"{sym}:{sig.get('confidence',0)}%")
                        if sig.get('confidence', 0) >= MIN_CONFIDENCE:
                            if best_signal is None or sig['confidence'] > best_signal['confidence']:
                                best_signal = sig
                    else:
                        scan_results.append(f"{sym}:no_signal")
                except Exception as e:
                    scan_results.append(f"{sym}:err")
                    logger.warning(f"[Engine:{user_id}] Signal scan error {sym}: {e}")

            logger.info(f"[Engine:{user_id}] Scan: {', '.join(scan_results)}")

            if not best_signal:
                logger.info(f"[Engine:{user_id}] No signal >= {MIN_CONFIDENCE}%, waiting {SCAN_INTERVAL}s")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            sig = best_signal
            symbol = sig['symbol']
            side = sig['side']
            entry = sig['entry_price']
            tp1 = sig['tp1']
            sl = sig['sl']
            confidence = sig['confidence']

            # 3. Hitung qty dengan precision yang betul
            notional = amount * leverage
            qty = calc_qty(symbol, notional, entry)
            if qty <= 0:
                logger.warning(f"[Engine:{user_id}] qty=0 for {symbol}, skip")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            logger.info(f"[Engine:{user_id}] Signal: {symbol} {side} conf={confidence}% entry={entry} tp={tp1} sl={sl} qty={qty}")

            # 4. Set leverage
            order_side = "BUY" if side == "LONG" else "SELL"
            lev_result = await asyncio.to_thread(client.set_leverage, symbol, leverage)
            logger.info(f"[Engine:{user_id}] Set leverage {leverage}x: {lev_result}")

            # 5. Place order dengan TP/SL
            order_result = await asyncio.to_thread(
                client.place_order_with_tpsl,
                symbol, order_side, qty, tp1, sl
            )

            logger.info(f"[Engine:{user_id}] Order result: {order_result}")

            if not order_result.get('success'):
                err = order_result.get('error', 'Unknown error')
                logger.error(f"[Engine:{user_id}] Order FAILED: {err}")

                if 'TOKEN_INVALID' in str(err) or '403' in str(err):
                    await bot.send_message(
                        chat_id=notify_chat_id,
                        text=(
                            "❌ <b>AutoTrade dihentikan — API Key bermasalah</b>\n\n"
                            "Bitunix menolak request.\n\n"
                            "<b>Cara fix:</b>\n"
                            "1. Login Bitunix → API Management\n"
                            "2. Hapus API Key lama, buat baru\n"
                            "3. <b>Jangan isi IP Whitelist</b> (kosongkan)\n"
                            "4. Setup ulang: /autotrade → Ganti API Key"
                        ),
                        parse_mode='HTML'
                    )
                    return

                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=f"⚠️ <b>Order gagal:</b> {err}\n\nBot tetap berjalan.",
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

            # 7. Update session
            try:
                _client().table("autotrade_sessions").update({
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_id", user_id).execute()
            except Exception:
                pass

            await asyncio.sleep(SCAN_INTERVAL * 2)

        except asyncio.CancelledError:
            logger.info(f"[Engine:{user_id}] Cancelled")
            try:
                await bot.send_message(chat_id=notify_chat_id, text="🛑 <b>AutoTrade dihentikan.</b>", parse_mode='HTML')
            except Exception:
                pass
            return

        except Exception as e:
            logger.error(f"[Engine:{user_id}] Loop error: {e}", exc_info=True)
            await asyncio.sleep(30)
