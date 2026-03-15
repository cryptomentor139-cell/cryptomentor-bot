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
    Signal using EMA crossover + RSI + SMC analysis (Order Blocks, FVG, Market Structure).
    """
    symbol = base_symbol.upper() + "USDT"
    logger.info(f"[Signal] Computing for {symbol}...")

    try:
        from app.providers.alternative_klines_provider import alternative_klines_provider

        klines = alternative_klines_provider.get_klines(base_symbol.upper(), interval='15m', limit=50)

        if not klines or len(klines) < 20:
            logger.warning(f"[Signal] {symbol} klines empty from alternative provider")
            return None

        closes = [float(k[4]) for k in klines]
        highs  = [float(k[2]) for k in klines]
        lows   = [float(k[3]) for k in klines]
        opens  = [float(k[1]) for k in klines]
        price  = closes[-1]
        logger.info(f"[Signal] {symbol} price={price:.4f} candles={len(klines)}")

        def ema(data, period):
            k = 2 / (period + 1)
            e = data[0]
            for v in data[1:]:
                e = v * k + e * (1 - k)
            return e

        ema9       = ema(closes, 9)
        ema21      = ema(closes, 21)
        ema9_prev  = ema(closes[:-1], 9)
        ema21_prev = ema(closes[:-1], 21)

        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            (gains if diff > 0 else losses).append(abs(diff))
        avg_gain = sum(gains) / 14 if gains else 0.001
        avg_loss = sum(losses) / 14 if losses else 0.001
        rsi = 100 - (100 / (1 + avg_gain / avg_loss))

        change_24h  = (price - closes[0]) / closes[0] * 100
        recent_high = max(highs[-20:])
        recent_low  = min(lows[-20:])
        range_pct   = (recent_high - recent_low) / recent_low * 100

        # ── SMC Analysis ──────────────────────────────────────────────
        smc_reasons = []
        smc_confidence_bonus = 0

        swing_highs, swing_lows = [], []
        window = 3
        for i in range(window, len(closes) - window):
            if highs[i] == max(highs[i-window:i+window+1]):
                swing_highs.append(highs[i])
            if lows[i] == min(lows[i-window:i+window+1]):
                swing_lows.append(lows[i])

        market_structure = "ranging"
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] > swing_lows[-2]:
                market_structure = "uptrend"
                smc_reasons.append("📈 BOS: Higher High + Higher Low (Uptrend)")
                smc_confidence_bonus += 8
            elif swing_highs[-1] < swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                market_structure = "downtrend"
                smc_reasons.append("� BOS: Lower High + Lower Low (Downtrend)")
                smc_confidence_bonus += 8

        ob_bullish_zone = None
        ob_bearish_zone = None
        for i in range(max(0, len(closes)-15), len(closes)-2):
            body_pct = abs(closes[i] - opens[i]) / opens[i] * 100
            if body_pct > 1.0:
                if closes[i] > opens[i]:
                    zone_high = highs[i]
                    zone_low  = lows[i]
                    if zone_low <= price <= zone_high * 1.005:
                        ob_bullish_zone = (zone_low, zone_high)
                        smc_reasons.append(f"🟩 Bullish OB: {zone_low:.4f}–{zone_high:.4f}")
                        smc_confidence_bonus += 10
                elif closes[i] < opens[i]:
                    zone_high = highs[i]
                    zone_low  = lows[i]
                    if zone_low * 0.995 <= price <= zone_high:
                        ob_bearish_zone = (zone_low, zone_high)
                        smc_reasons.append(f"� Bearish OB: {zone_low:.4f}–{zone_high:.4f}")
                        smc_confidence_bonus += 10

        for i in range(1, min(10, len(closes)-1)):
            idx = len(closes) - 1 - i
            if idx < 2:
                break
            if lows[idx+1] > highs[idx-1]:
                fvg_low  = highs[idx-1]
                fvg_high = lows[idx+1]
                if fvg_low <= price <= fvg_high:
                    smc_reasons.append(f"⬆️ Bullish FVG: {fvg_low:.4f}–{fvg_high:.4f}")
                    smc_confidence_bonus += 7
                    break
            elif highs[idx+1] < lows[idx-1]:
                fvg_high = lows[idx-1]
                fvg_low  = highs[idx+1]
                if fvg_low <= price <= fvg_high:
                    smc_reasons.append(f"⬇️ Bearish FVG: {fvg_low:.4f}–{fvg_high:.4f}")
                    smc_confidence_bonus += 7
                    break

        prev_high_20 = max(highs[-21:-1])
        prev_low_20  = min(lows[-21:-1])
        if price > prev_high_20 * 0.998 and closes[-1] < opens[-1]:
            smc_reasons.append(f"🎯 Liquidity Sweep High: {prev_high_20:.4f} (bearish rejection)")
            smc_confidence_bonus += 6
        elif price < prev_low_20 * 1.002 and closes[-1] > opens[-1]:
            smc_reasons.append(f"🎯 Liquidity Sweep Low: {prev_low_20:.4f} (bullish reversal)")
            smc_confidence_bonus += 6

        eq_mid = (recent_high + recent_low) / 2
        if price < eq_mid:
            smc_reasons.append(f"💎 Discount Zone ({((eq_mid-price)/eq_mid*100):.1f}% below EQ)")
            smc_confidence_bonus += 4
        else:
            smc_reasons.append(f"⚡ Premium Zone ({((price-eq_mid)/eq_mid*100):.1f}% above EQ)")
            smc_confidence_bonus += 2

        side = None
        confidence = 50
        reasons = []

        if ema9 > ema21 and ema9_prev <= ema21_prev:
            side = "LONG";  confidence = 72; reasons.append(f"EMA9 cross above EMA21 (RSI {rsi:.0f})")
        elif ema9 < ema21 and ema9_prev >= ema21_prev:
            side = "SHORT"; confidence = 72; reasons.append(f"EMA9 cross below EMA21 (RSI {rsi:.0f})")
        elif ema9 > ema21 and rsi < 45:
            side = "LONG";  confidence = 68; reasons.append(f"Uptrend + RSI oversold ({rsi:.0f})")
        elif ema9 < ema21 and rsi > 55:
            side = "SHORT"; confidence = 68; reasons.append(f"Downtrend + RSI overbought ({rsi:.0f})")
        elif price > recent_high * 0.999 and change_24h > 1.5:
            side = "LONG";  confidence = 70; reasons.append(f"Breakout high + momentum {change_24h:+.1f}%")
        elif price < recent_low * 1.001 and change_24h < -1.5:
            side = "SHORT"; confidence = 70; reasons.append(f"Breakdown low + momentum {change_24h:.1f}%")

        if side is None:
            if ema9 >= ema21:
                side = "LONG";  confidence = 55; reasons.append(f"EMA trend LONG (RSI {rsi:.0f})")
            else:
                side = "SHORT"; confidence = 55; reasons.append(f"EMA trend SHORT (RSI {rsi:.0f})")

        if side == "LONG":
            confidence += smc_confidence_bonus if market_structure == "uptrend" else (-5 if market_structure == "downtrend" else 0)
            if ob_bullish_zone: confidence += 5
        elif side == "SHORT":
            confidence += smc_confidence_bonus if market_structure == "downtrend" else (-5 if market_structure == "uptrend" else 0)
            if ob_bearish_zone: confidence += 5

        atr = range_pct / 100 * price * 0.3
        if side == "LONG":
            tp1 = price + atr * 2
            sl  = price - atr
        else:
            tp1 = price - atr * 2
            sl  = price + atr

        return {
            "symbol":           symbol,
            "side":             side,
            "confidence":       int(min(max(confidence, 50), 95)),
            "entry_price":      price,
            "tp1":              round(tp1, 6),
            "tp2":              round(tp1 * (1.01 if side == "LONG" else 0.99), 6),
            "sl":               round(sl, 6),
            "reasons":          reasons + smc_reasons,
            "market_structure": market_structure,
            "rsi":              round(rsi, 1),
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
    stop_engine(user_id)

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
    from app.bitunix_ws_pnl import start_pnl_tracker, stop_pnl_tracker, is_tracking

    client = BitunixAutoTradeClient(api_key=api_key, api_secret=api_secret)

    SYMBOLS            = ["BTC", "ETH", "BNB", "SOL"]  # 4 coin fokus
    SCAN_INTERVAL      = 30                              # detik antar scan
    MIN_CONFIDENCE     = 0
    MAX_TRADES_PER_DAY = 8

    QTY_PRECISION = {"BTCUSDT": 3, "ETHUSDT": 2, "SOLUSDT": 1, "BNBUSDT": 2}

    def calc_qty(symbol: str, notional: float, price: float) -> float:
        precision = QTY_PRECISION.get(symbol, 3)
        qty = round(notional / price, precision)
        min_qty = 10 ** (-precision) if precision > 0 else 1
        return qty if qty >= min_qty else 0.0

    from datetime import date
    trades_today      = 0
    last_trade_date   = date.today()
    had_open_position = False

    logger.info(f"[Engine:{user_id}] ENGINE v3 STARTED — {SYMBOLS}, max {MAX_TRADES_PER_DAY}x/day")

    await bot.send_message(
        chat_id=notify_chat_id,
        text="🤖 <b>AutoTrade Engine aktif!</b>\n\nBot sedang memantau pasar dan akan eksekusi trade otomatis.",
        parse_mode='HTML'
    )

    while True:
        try:
            # Reset counter harian
            today = date.today()
            if today != last_trade_date:
                trades_today    = 0
                last_trade_date = today
                logger.info(f"[Engine:{user_id}] New day — trade counter reset")

            # 1. Cek posisi terbuka
            pos_result     = await asyncio.to_thread(client.get_positions)
            open_positions = pos_result.get('positions', []) if pos_result.get('success') else []
            occupied_syms  = {p['symbol'] for p in open_positions}

            # Deteksi posisi baru saja tutup (TP/SL hit)
            if had_open_position and not open_positions:
                had_open_position = False
                if is_tracking(user_id):
                    stop_pnl_tracker(user_id)
                    logger.info(f"[Engine:{user_id}] Position closed, PnL tracker stopped")
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=(
                        f"🔔 <b>Posisi Ditutup</b> (TP/SL hit)\n\n"
                        f"📊 Trade hari ini: <b>{trades_today}/{MAX_TRADES_PER_DAY}</b>\n"
                        f"{'🔄 Mencari sinyal berikutnya...' if trades_today < MAX_TRADES_PER_DAY else '🛑 Batas harian tercapai, lanjut besok.'}"
                    ),
                    parse_mode='HTML'
                )

            if open_positions:
                had_open_position = True
                logger.info(f"[Engine:{user_id}] Open: {list(occupied_syms)}, scanning others...")

            # 2. Cek batas harian
            if trades_today >= MAX_TRADES_PER_DAY:
                logger.info(f"[Engine:{user_id}] Daily limit reached ({trades_today}), sleeping 5min")
                await asyncio.sleep(300)
                continue

            # 3. Scan symbols yang belum ada posisi terbuka
            available = [s for s in SYMBOLS if (s + "USDT") not in occupied_syms]
            if not available:
                logger.info(f"[Engine:{user_id}] All 4 symbols occupied, waiting...")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            best_signal: Optional[Dict] = None
            scan_results = []
            for sym in available:
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

            logger.info(f"[Engine:{user_id}] Scan {available}: {', '.join(scan_results)}")

            if not best_signal:
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            sig        = best_signal
            symbol     = sig['symbol']
            side       = sig['side']
            entry      = sig['entry_price']
            tp1        = sig['tp1']
            sl         = sig['sl']
            confidence = sig['confidence']

            # 4. Hitung qty
            qty = calc_qty(symbol, amount * leverage, entry)
            if qty <= 0:
                logger.warning(f"[Engine:{user_id}] qty=0 for {symbol}, skip")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            logger.info(f"[Engine:{user_id}] Signal: {symbol} {side} conf={confidence}% entry={entry} tp={tp1} sl={sl} qty={qty}")

            # 5. Set leverage
            order_side = "BUY" if side == "LONG" else "SELL"
            await asyncio.to_thread(client.set_leverage, symbol, leverage)

            # 6. Place order dengan TP/SL
            order_result = await asyncio.to_thread(
                client.place_order_with_tpsl, symbol, order_side, qty, tp1, sl
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
            trades_today += 1
            had_open_position = True

            # 7. Notifikasi user
            risk_pct         = abs(entry - sl)  / entry * 100 * leverage
            reward_pct       = abs(tp1 - entry) / entry * 100 * leverage
            potential_profit = amount * (reward_pct / 100)
            potential_loss   = amount * (risk_pct  / 100)
            all_reasons      = sig.get('reasons', [])
            market_structure = sig.get('market_structure', 'ranging')

            smc_kw = ['OB:', 'FVG:', 'BOS:', 'Liquidity', 'Zone', 'Higher', 'Lower']
            tech_reasons = [r for r in all_reasons if not any(x in r for x in smc_kw)]
            smc_reasons  = [r for r in all_reasons if     any(x in r for x in smc_kw)]

            struct_emoji = {"uptrend": "📈", "downtrend": "📉", "ranging": "↔️"}.get(market_structure, "↔️")
            struct_label = {"uptrend": "Uptrend (HH/HL)", "downtrend": "Downtrend (LH/LL)", "ranging": "Ranging"}.get(market_structure, market_structure)
            smc_block    = ("\n🔬 <b>SMC Analysis:</b>\n" + "\n".join(f"  • {r}" for r in smc_reasons[:4]))  if smc_reasons  else ""
            tech_block   = ("\n📐 <b>Technical:</b>\n"    + "\n".join(f"  • {r}" for r in tech_reasons[:3])) if tech_reasons else ""

            await bot.send_message(
                chat_id=notify_chat_id,
                text=(
                    f"✅ <b>ORDER TEREKSEKUSI</b>  [{trades_today}/{MAX_TRADES_PER_DAY} hari ini]\n\n"
                    f"📊 {symbol} | {side} | {leverage}x\n"
                    f"💵 Entry: <code>{entry:.4f}</code>\n"
                    f"🎯 TP: <code>{tp1:.4f}</code>\n"
                    f"🛑 SL: <code>{sl:.4f}</code>\n"
                    f"📦 Qty: {qty}\n\n"
                    f"{struct_emoji} <b>Market Structure:</b> {struct_label}\n"
                    f"{smc_block}"
                    f"{tech_block}\n\n"
                    f"💰 Potensi profit: +{potential_profit:.2f} USDT ({reward_pct:.1f}%)\n"
                    f"⚠️ Potensi loss: -{potential_loss:.2f} USDT ({risk_pct:.1f}%)\n"
                    f"🧠 Confidence: {confidence}%\n"
                    f"🔖 Order ID: <code>{order_id}</code>"
                ),
                parse_mode='HTML'
            )

            # 8. Start live PnL tracker
            start_pnl_tracker(user_id=user_id, api_key=api_key, api_secret=api_secret,
                               bot=bot, chat_id=notify_chat_id)

            # 9. Update session timestamp
            try:
                _client().table("autotrade_sessions").update({
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_id", user_id).execute()
            except Exception:
                pass

            await asyncio.sleep(SCAN_INTERVAL)

        except asyncio.CancelledError:
            logger.info(f"[Engine:{user_id}] Cancelled")
            stop_pnl_tracker(user_id)
            try:
                await bot.send_message(chat_id=notify_chat_id, text="🛑 <b>AutoTrade dihentikan.</b>", parse_mode='HTML')
            except Exception:
                pass
            return

        except Exception as e:
            logger.error(f"[Engine:{user_id}] Loop error: {e}", exc_info=True)
            await asyncio.sleep(30)
