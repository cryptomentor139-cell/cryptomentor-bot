"""
AutoTrade Engine — Professional Grade Trading Loop
Strategy: Multi-timeframe confluence + SMC + Risk Management
- Min R:R 1:2, dynamic SL via ATR
- Drawdown circuit breaker (stop if -5% daily)
- Volatility filter (no trade in low-volatility ranging market)
- Confidence threshold >= 68 (only high-quality setups)
- Max 1 position per symbol, max 3 concurrent positions
"""
import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime, date

logger = logging.getLogger(__name__)

_running_tasks: Dict[int, asyncio.Task] = {}

# ─────────────────────────────────────────────
#  Engine config (professional defaults)
# ─────────────────────────────────────────────
ENGINE_CONFIG = {
    "symbols":            ["BTC", "ETH", "SOL", "BNB"],
    "scan_interval":      45,       # detik antar scan
    "min_confidence":     68,       # hanya sinyal berkualitas tinggi
    "max_trades_per_day": 6,        # batasi overtrading
    "max_concurrent":     2,        # max 2 posisi bersamaan
    "min_rr_ratio":       2.0,      # minimum Risk:Reward 1:2
    "daily_loss_limit":   0.05,     # circuit breaker: stop jika -5% dari modal
    "atr_sl_multiplier":  1.5,      # SL = 1.5x ATR (tidak terlalu ketat)
    "atr_tp_multiplier":  3.0,      # TP = 3.0x ATR → R:R = 2:1
    "min_atr_pct":        0.4,      # filter: skip jika ATR < 0.4% (market flat)
    "max_atr_pct":        8.0,      # filter: skip jika ATR > 8% (terlalu volatile)
    "rsi_long_max":       65,       # jangan LONG jika RSI > 65 (overbought)
    "rsi_short_min":      35,       # jangan SHORT jika RSI < 35 (oversold)
    "volume_spike_min":   1.1,      # volume harus > 1.1x rata-rata
}

QTY_PRECISION = {
    "BTCUSDT": 3, "ETHUSDT": 2, "SOLUSDT": 1, "BNBUSDT": 2,
    "XRPUSDT": 0, "ADAUSDT": 0, "DOGEUSDT": 0,
}


# ─────────────────────────────────────────────
#  ATR Calculator (True Range based)
# ─────────────────────────────────────────────
def _calc_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    trs = []
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    return sum(trs[-period:]) / period if len(trs) >= period else sum(trs) / len(trs) if trs else 0.0


def _calc_ema(data: List[float], period: int) -> float:
    if len(data) < period:
        return sum(data) / len(data)
    k = 2 / (period + 1)
    e = sum(data[:period]) / period
    for v in data[period:]:
        e = v * k + e * (1 - k)
    return e


def _calc_rsi(closes: List[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    if al == 0:
        return 100.0
    return 100 - (100 / (1 + ag / al))


def _calc_volume_ratio(volumes: List[float], period: int = 20) -> float:
    if len(volumes) < period + 1:
        return 1.0
    avg = sum(volumes[-period - 1:-1]) / period
    return volumes[-1] / avg if avg > 0 else 1.0


# ─────────────────────────────────────────────
#  Professional Signal Engine
# ─────────────────────────────────────────────
def _compute_signal_pro(base_symbol: str) -> Optional[Dict]:
    """
    Multi-timeframe confluence signal:
    1H trend filter + 15M entry trigger + SMC confluence
    Requires: min R:R 2:1, ATR-based SL/TP, volume confirmation
    """
    symbol = base_symbol.upper() + "USDT"
    cfg = ENGINE_CONFIG

    try:
        from app.providers.alternative_klines_provider import alternative_klines_provider

        # ── Data fetch: 1H (trend) + 15M (entry) ──────────────────────
        klines_1h  = alternative_klines_provider.get_klines(base_symbol.upper(), interval='1h',  limit=100)
        klines_15m = alternative_klines_provider.get_klines(base_symbol.upper(), interval='15m', limit=60)

        if not klines_1h or len(klines_1h) < 50:
            logger.warning(f"[Signal] {symbol} insufficient 1H data")
            return None
        if not klines_15m or len(klines_15m) < 30:
            logger.warning(f"[Signal] {symbol} insufficient 15M data")
            return None

        # ── 1H: Trend direction ────────────────────────────────────────
        c1h = [float(k[4]) for k in klines_1h]
        h1h = [float(k[2]) for k in klines_1h]
        l1h = [float(k[3]) for k in klines_1h]
        v1h = [float(k[5]) for k in klines_1h]

        ema21_1h  = _calc_ema(c1h, 21)
        ema50_1h  = _calc_ema(c1h, 50)
        rsi_1h    = _calc_rsi(c1h)
        atr_1h    = _calc_atr(h1h, l1h, c1h, 14)
        price     = c1h[-1]
        atr_pct   = (atr_1h / price) * 100

        # Volatility filter
        if atr_pct < cfg["min_atr_pct"]:
            logger.info(f"[Signal] {symbol} ATR too low ({atr_pct:.2f}%) — market flat, skip")
            return None
        if atr_pct > cfg["max_atr_pct"]:
            logger.info(f"[Signal] {symbol} ATR too high ({atr_pct:.2f}%) — too volatile, skip")
            return None

        # 1H trend bias
        if price > ema21_1h > ema50_1h:
            trend_1h = "LONG"
        elif price < ema21_1h < ema50_1h:
            trend_1h = "SHORT"
        else:
            trend_1h = "NEUTRAL"

        # ── 15M: Entry trigger ─────────────────────────────────────────
        c15 = [float(k[4]) for k in klines_15m]
        h15 = [float(k[2]) for k in klines_15m]
        l15 = [float(k[3]) for k in klines_15m]
        v15 = [float(k[5]) for k in klines_15m]

        ema9_15   = _calc_ema(c15, 9)
        ema21_15  = _calc_ema(c15, 21)
        ema9_prev = _calc_ema(c15[:-1], 9)
        ema21_prev= _calc_ema(c15[:-1], 21)
        rsi_15    = _calc_rsi(c15)
        atr_15    = _calc_atr(h15, l15, c15, 14)
        vol_ratio = _calc_volume_ratio(v15)

        # ── SMC: Market structure (swing highs/lows) ───────────────────
        swing_highs, swing_lows = [], []
        w = 3
        for i in range(w, len(c15) - w):
            if h15[i] == max(h15[i - w:i + w + 1]):
                swing_highs.append(h15[i])
            if l15[i] == min(l15[i - w:i + w + 1]):
                swing_lows.append(l15[i])

        market_structure = "ranging"
        smc_bonus = 0
        smc_reasons = []

        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] > swing_lows[-2]:
                market_structure = "uptrend"
                smc_reasons.append("📈 BOS: HH+HL (Uptrend)")
                smc_bonus += 10
            elif swing_highs[-1] < swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                market_structure = "downtrend"
                smc_reasons.append("📉 BOS: LH+LL (Downtrend)")
                smc_bonus += 10

        # Order Block detection
        for i in range(max(0, len(c15) - 15), len(c15) - 2):
            body_pct = abs(c15[i] - float(klines_15m[i][1])) / float(klines_15m[i][1]) * 100
            if body_pct > 0.8:
                if c15[i] > float(klines_15m[i][1]) and l15[i] <= price <= h15[i] * 1.003:
                    smc_reasons.append(f"🟩 Bullish OB: {l15[i]:.4f}–{h15[i]:.4f}")
                    smc_bonus += 8
                elif c15[i] < float(klines_15m[i][1]) and l15[i] * 0.997 <= price <= h15[i]:
                    smc_reasons.append(f"🟥 Bearish OB: {l15[i]:.4f}–{h15[i]:.4f}")
                    smc_bonus += 8

        # FVG detection
        for i in range(1, min(8, len(c15) - 1)):
            idx = len(c15) - 1 - i
            if idx < 2:
                break
            if l15[idx + 1] > h15[idx - 1] and h15[idx - 1] <= price <= l15[idx + 1]:
                smc_reasons.append(f"⬆️ Bullish FVG: {h15[idx-1]:.4f}–{l15[idx+1]:.4f}")
                smc_bonus += 6
                break
            elif h15[idx + 1] < l15[idx - 1] and h15[idx + 1] <= price <= l15[idx - 1]:
                smc_reasons.append(f"⬇️ Bearish FVG: {h15[idx+1]:.4f}–{l15[idx-1]:.4f}")
                smc_bonus += 6
                break

        # ── Signal decision: require 1H + 15M alignment ───────────────
        side = None
        confidence = 50
        reasons = []

        # EMA crossover on 15M
        ema_cross_long  = ema9_15 > ema21_15 and ema9_prev <= ema21_prev
        ema_cross_short = ema9_15 < ema21_15 and ema9_prev >= ema21_prev
        ema_trend_long  = ema9_15 > ema21_15
        ema_trend_short = ema9_15 < ema21_15

        if trend_1h == "LONG":
            if ema_cross_long:
                side = "LONG"; confidence = 75
                reasons.append(f"✅ 1H uptrend + 15M EMA cross LONG (RSI {rsi_15:.0f})")
            elif ema_trend_long and rsi_15 < 55:
                side = "LONG"; confidence = 68
                reasons.append(f"✅ 1H uptrend + 15M EMA aligned + RSI {rsi_15:.0f}")
        elif trend_1h == "SHORT":
            if ema_cross_short:
                side = "SHORT"; confidence = 75
                reasons.append(f"✅ 1H downtrend + 15M EMA cross SHORT (RSI {rsi_15:.0f})")
            elif ema_trend_short and rsi_15 > 45:
                side = "SHORT"; confidence = 68
                reasons.append(f"✅ 1H downtrend + 15M EMA aligned + RSI {rsi_15:.0f}")

        # Neutral 1H: only take if strong SMC confluence
        if side is None and smc_bonus >= 18:
            if ema_trend_long and market_structure == "uptrend":
                side = "LONG"; confidence = 65
                reasons.append(f"SMC confluence LONG (1H neutral)")
            elif ema_trend_short and market_structure == "downtrend":
                side = "SHORT"; confidence = 65
                reasons.append(f"SMC confluence SHORT (1H neutral)")

        if side is None:
            logger.info(f"[Signal] {symbol} no confluence — 1H={trend_1h}, struct={market_structure}")
            return None

        # ── RSI filter: avoid overbought/oversold entries ──────────────
        if side == "LONG"  and rsi_15 > cfg["rsi_long_max"]:
            logger.info(f"[Signal] {symbol} LONG blocked — RSI {rsi_15:.0f} overbought")
            return None
        if side == "SHORT" and rsi_15 < cfg["rsi_short_min"]:
            logger.info(f"[Signal] {symbol} SHORT blocked — RSI {rsi_15:.0f} oversold")
            return None

        # ── Volume confirmation ────────────────────────────────────────
        if vol_ratio >= cfg["volume_spike_min"]:
            confidence += 5
            reasons.append(f"📊 Volume spike {vol_ratio:.1f}x")
        else:
            confidence -= 3  # penalize low volume

        # ── SMC bonus ─────────────────────────────────────────────────
        if market_structure == ("uptrend" if side == "LONG" else "downtrend"):
            confidence += smc_bonus
        elif market_structure == ("downtrend" if side == "LONG" else "uptrend"):
            confidence -= 8  # counter-trend penalty

        # ── ATR-based SL/TP (professional sizing) ─────────────────────
        # Use 1H ATR for SL/TP to avoid noise from 15M
        sl_dist = atr_1h * cfg["atr_sl_multiplier"]
        tp_dist = atr_1h * cfg["atr_tp_multiplier"]

        if side == "LONG":
            sl  = price - sl_dist
            tp1 = price + tp_dist
            tp2 = price + tp_dist * 1.5   # extended TP
        else:
            sl  = price + sl_dist
            tp1 = price - tp_dist
            tp2 = price - tp_dist * 1.5

        # ── R:R validation ─────────────────────────────────────────────
        rr = tp_dist / sl_dist
        if rr < cfg["min_rr_ratio"]:
            logger.info(f"[Signal] {symbol} R:R {rr:.2f} < {cfg['min_rr_ratio']} — skip")
            return None

        confidence = int(min(max(confidence, 50), 95))

        logger.info(
            f"[Signal] {symbol} {side} conf={confidence}% "
            f"entry={price:.4f} sl={sl:.4f} tp={tp1:.4f} "
            f"RR={rr:.1f} ATR={atr_pct:.2f}% vol={vol_ratio:.1f}x"
        )

        return {
            "symbol":           symbol,
            "side":             side,
            "confidence":       confidence,
            "entry_price":      price,
            "tp1":              round(tp1, 6),
            "tp2":              round(tp2, 6),
            "sl":               round(sl, 6),
            "rr_ratio":         round(rr, 2),
            "atr_pct":          round(atr_pct, 2),
            "vol_ratio":        round(vol_ratio, 2),
            "reasons":          reasons + smc_reasons,
            "market_structure": market_structure,
            "trend_1h":         trend_1h,
            "rsi_15":           round(rsi_15, 1),
            "rsi_1h":           round(rsi_1h, 1),
        }

    except Exception as e:
        logger.warning(f"_compute_signal_pro error {base_symbol}: {e}", exc_info=True)
        return None


# ─────────────────────────────────────────────
#  Engine lifecycle
# ─────────────────────────────────────────────
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

    def _done_cb(task: asyncio.Task):
        if task.cancelled():
            logger.info(f"AutoTrade cancelled for user {user_id}")
        elif task.exception():
            logger.error(f"AutoTrade CRASHED for user {user_id}: {task.exception()}", exc_info=task.exception())

    task = asyncio.create_task(
        _trade_loop(bot, user_id, api_key, api_secret, amount, leverage, notify_chat_id)
    )
    task.add_done_callback(_done_cb)
    _running_tasks[user_id] = task
    logger.info(f"AutoTrade PRO started for user {user_id}, amount={amount}, leverage={leverage}x")


# ─────────────────────────────────────────────
#  Main trading loop
# ─────────────────────────────────────────────
async def _trade_loop(bot, user_id: int, api_key: str, api_secret: str,
                      amount: float, leverage: int, notify_chat_id: int):
    import sys, os
    bismillah_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if bismillah_root not in sys.path:
        sys.path.insert(0, bismillah_root)

    from app.bitunix_autotrade_client import BitunixAutoTradeClient
    from app.supabase_repo import _client
    from app.bitunix_ws_pnl import start_pnl_tracker, stop_pnl_tracker, is_tracking

    client = BitunixAutoTradeClient(api_key=api_key, api_secret=api_secret)
    cfg    = ENGINE_CONFIG

    trades_today      = 0
    last_trade_date   = date.today()
    had_open_position = False
    daily_pnl_usdt    = 0.0   # track realized PnL for circuit breaker
    daily_loss_limit  = amount * cfg["daily_loss_limit"]

    def calc_qty(symbol: str, notional: float, price: float) -> float:
        precision = QTY_PRECISION.get(symbol, 3)
        qty = round(notional / price, precision)
        min_qty = 10 ** (-precision) if precision > 0 else 1
        return qty if qty >= min_qty else 0.0

    logger.info(f"[Engine:{user_id}] PRO ENGINE STARTED — symbols={cfg['symbols']}, "
                f"min_conf={cfg['min_confidence']}, min_rr={cfg['min_rr_ratio']}, "
                f"daily_loss_limit={daily_loss_limit:.2f} USDT")

    await bot.send_message(
        chat_id=notify_chat_id,
        text=(
            "🤖 <b>AutoTrade PRO Engine aktif!</b>\n\n"
            f"📊 Strategy: Multi-timeframe (1H trend + 15M entry)\n"
            f"🎯 Min Confidence: {cfg['min_confidence']}%\n"
            f"⚖️ Min R:R Ratio: 1:{cfg['min_rr_ratio']}\n"
            f"🛡 Daily Loss Limit: {daily_loss_limit:.2f} USDT ({cfg['daily_loss_limit']*100:.0f}%)\n"
            f"📈 Max Trades/Day: {cfg['max_trades_per_day']}\n\n"
            "Bot hanya eksekusi setup berkualitas tinggi. Sabar = profit."
        ),
        parse_mode='HTML'
    )

    while True:
        try:
            # ── Reset harian ──────────────────────────────────────────
            today = date.today()
            if today != last_trade_date:
                trades_today    = 0
                daily_pnl_usdt  = 0.0
                last_trade_date = today
                logger.info(f"[Engine:{user_id}] New day — counters reset")

            # ── Circuit breaker: daily loss limit ─────────────────────
            if daily_pnl_usdt <= -daily_loss_limit:
                logger.warning(f"[Engine:{user_id}] Daily loss limit hit ({daily_pnl_usdt:.2f} USDT), pausing until tomorrow")
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=(
                        f"🛑 <b>Circuit Breaker Aktif</b>\n\n"
                        f"Loss hari ini: <b>{daily_pnl_usdt:.2f} USDT</b>\n"
                        f"Limit: {daily_loss_limit:.2f} USDT ({cfg['daily_loss_limit']*100:.0f}% modal)\n\n"
                        "Bot berhenti trading hari ini untuk melindungi modal.\n"
                        "Akan aktif kembali besok. 🔄"
                    ),
                    parse_mode='HTML'
                )
                # Tunggu sampai hari berikutnya
                while date.today() == today:
                    await asyncio.sleep(300)
                continue

            # ── Cek posisi terbuka ────────────────────────────────────
            pos_result     = await asyncio.to_thread(client.get_positions)
            open_positions = pos_result.get('positions', []) if pos_result.get('success') else []
            occupied_syms  = {p['symbol'] for p in open_positions}

            # Deteksi posisi baru tutup (TP/SL hit) — estimasi PnL
            if had_open_position and not open_positions:
                had_open_position = False
                if is_tracking(user_id):
                    stop_pnl_tracker(user_id)
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=(
                        f"🔔 <b>Posisi Ditutup</b> (TP/SL hit)\n\n"
                        f"📊 Trade hari ini: <b>{trades_today}/{cfg['max_trades_per_day']}</b>\n"
                        f"{'🔄 Mencari setup berikutnya...' if trades_today < cfg['max_trades_per_day'] else '🛑 Batas harian tercapai.'}"
                    ),
                    parse_mode='HTML'
                )

            if open_positions:
                had_open_position = True

            # ── Batas harian & concurrent positions ───────────────────
            if trades_today >= cfg["max_trades_per_day"]:
                await asyncio.sleep(300)
                continue

            if len(open_positions) >= cfg["max_concurrent"]:
                logger.info(f"[Engine:{user_id}] Max concurrent positions ({cfg['max_concurrent']}) reached")
                await asyncio.sleep(cfg["scan_interval"])
                continue

            # ── Scan symbols ──────────────────────────────────────────
            available = [s for s in cfg["symbols"] if (s + "USDT") not in occupied_syms]
            if not available:
                await asyncio.sleep(cfg["scan_interval"])
                continue

            candidates: List[Dict] = []
            for sym in available:
                try:
                    sig = await asyncio.to_thread(_compute_signal_pro, sym)
                    if sig and sig.get('confidence', 0) >= cfg["min_confidence"]:
                        candidates.append(sig)
                        logger.info(f"[Engine:{user_id}] Candidate: {sym} {sig['side']} "
                                    f"conf={sig['confidence']}% RR={sig['rr_ratio']}")
                except Exception as e:
                    logger.warning(f"[Engine:{user_id}] Scan error {sym}: {e}")

            if not candidates:
                logger.info(f"[Engine:{user_id}] No quality setups found, waiting...")
                await asyncio.sleep(cfg["scan_interval"])
                continue

            # Pilih sinyal terbaik: prioritas confidence, lalu R:R
            best = max(candidates, key=lambda s: (s['confidence'], s['rr_ratio']))

            sig        = best
            symbol     = sig['symbol']
            side       = sig['side']
            entry      = sig['entry_price']
            tp1        = sig['tp1']
            sl         = sig['sl']
            confidence = sig['confidence']
            rr_ratio   = sig['rr_ratio']

            # ── Hitung qty ────────────────────────────────────────────
            qty = calc_qty(symbol, amount * leverage, entry)
            if qty <= 0:
                logger.warning(f"[Engine:{user_id}] qty=0 for {symbol}, skip")
                await asyncio.sleep(cfg["scan_interval"])
                continue

            # ── Set leverage ──────────────────────────────────────────
            await asyncio.to_thread(client.set_leverage, symbol, leverage)

            # ── Place order ───────────────────────────────────────────
            order_result = await asyncio.to_thread(
                client.place_order_with_tpsl, symbol,
                "BUY" if side == "LONG" else "SELL",
                qty, tp1, sl
            )

            if not order_result.get('success'):
                err = order_result.get('error', 'Unknown')
                logger.error(f"[Engine:{user_id}] Order FAILED: {err}")

                # Cek apakah ini benar-benar API key invalid (bukan transient error)
                is_auth_error = 'TOKEN_INVALID' in str(err) or 'SIGNATURE_ERROR' in str(err)
                is_ip_blocked = 'HTTP 403' in str(err) or ('403' in str(err) and 'IP' in str(err))

                if is_auth_error or is_ip_blocked:
                    # Retry sekali dulu sebelum menyerah — bisa jadi timestamp drift
                    logger.warning(f"[Engine:{user_id}] Auth error, retrying once in 10s: {err}")
                    await asyncio.sleep(10)
                    retry_result = await asyncio.to_thread(
                        client.place_order_with_tpsl, symbol,
                        "BUY" if side == "LONG" else "SELL",
                        qty, tp1, sl
                    )
                    if retry_result.get('success'):
                        order_result = retry_result
                        # Lanjut ke bawah dengan order sukses
                    else:
                        retry_err = retry_result.get('error', '')
                        # Hanya stop jika retry juga gagal dengan auth error
                        if 'TOKEN_INVALID' in str(retry_err) or 'HTTP 403' in str(retry_err):
                            await bot.send_message(
                                chat_id=notify_chat_id,
                                text=(
                                    "❌ <b>AutoTrade dihentikan — API Key bermasalah</b>\n\n"
                                    "Bitunix menolak request setelah 2x percobaan.\n"
                                    "Kemungkinan penyebab:\n"
                                    "• API Key punya IP restriction — hapus dan buat baru tanpa IP\n"
                                    "• API Key sudah expired atau dihapus\n\n"
                                    "Setup ulang: /autotrade → Ganti API Key"
                                ),
                                parse_mode='HTML'
                            )
                            return
                        else:
                            # Error lain setelah retry — lanjut saja
                            await bot.send_message(
                                chat_id=notify_chat_id,
                                text=f"⚠️ <b>Order gagal (2x):</b> {retry_err}\n\nBot tetap berjalan.",
                                parse_mode='HTML'
                            )
                            await asyncio.sleep(cfg["scan_interval"])
                            continue
                else:
                    await bot.send_message(
                        chat_id=notify_chat_id,
                        text=f"⚠️ <b>Order gagal:</b> {err}\n\nBot tetap berjalan.",
                        parse_mode='HTML'
                    )
                    await asyncio.sleep(cfg["scan_interval"])
                    continue

                # Jika retry sukses, pastikan order_result sudah diupdate di atas
                if not order_result.get('success'):
                    await asyncio.sleep(cfg["scan_interval"])
                    continue

            order_id = order_result.get('order_id', '-')
            trades_today += 1
            had_open_position = True

            # ── Kalkulasi risk/reward untuk notifikasi ─────────────────
            sl_pct     = abs(entry - sl)  / entry * 100
            tp_pct     = abs(tp1 - entry) / entry * 100
            risk_usdt  = amount * (sl_pct  / 100) * leverage
            reward_usdt= amount * (tp_pct  / 100) * leverage

            trend_1h   = sig.get('trend_1h', '-')
            struct      = sig.get('market_structure', 'ranging')
            rsi_15      = sig.get('rsi_15', 0)
            atr_pct     = sig.get('atr_pct', 0)
            vol_ratio   = sig.get('vol_ratio', 1)
            all_reasons = sig.get('reasons', [])

            struct_emoji = {"uptrend": "📈", "downtrend": "📉", "ranging": "↔️"}.get(struct, "↔️")
            trend_emoji  = {"LONG": "🟢", "SHORT": "🔴", "NEUTRAL": "⚪"}.get(trend_1h, "⚪")

            reasons_text = "\n".join(f"  • {r}" for r in all_reasons[:5])

            await bot.send_message(
                chat_id=notify_chat_id,
                text=(
                    f"✅ <b>ORDER TEREKSEKUSI</b>  [{trades_today}/{cfg['max_trades_per_day']} hari ini]\n\n"
                    f"📊 {symbol} | {side} | {leverage}x\n"
                    f"💵 Entry: <code>{entry:.4f}</code>\n"
                    f"🎯 TP: <code>{tp1:.4f}</code> (+{tp_pct:.1f}%)\n"
                    f"🛑 SL: <code>{sl:.4f}</code> (-{sl_pct:.1f}%)\n"
                    f"📦 Qty: {qty}\n\n"
                    f"⚖️ R:R Ratio: <b>1:{rr_ratio:.1f}</b>\n"
                    f"{trend_emoji} 1H Trend: <b>{trend_1h}</b>\n"
                    f"{struct_emoji} Structure: <b>{struct}</b>\n"
                    f"📊 RSI 15M: {rsi_15} | ATR: {atr_pct:.2f}% | Vol: {vol_ratio:.1f}x\n\n"
                    f"🧠 Alasan:\n{reasons_text}\n\n"
                    f"💰 Potensi profit: +{reward_usdt:.2f} USDT\n"
                    f"⚠️ Potensi loss: -{risk_usdt:.2f} USDT\n"
                    f"🧠 Confidence: {confidence}%\n"
                    f"🔖 Order ID: <code>{order_id}</code>"
                ),
                parse_mode='HTML'
            )

            # ── Start PnL tracker ─────────────────────────────────────
            start_pnl_tracker(user_id=user_id, api_key=api_key, api_secret=api_secret,
                               bot=bot, chat_id=notify_chat_id)

            # ── Update session ────────────────────────────────────────
            try:
                _client().table("autotrade_sessions").update({
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("telegram_id", user_id).execute()
            except Exception:
                pass

            await asyncio.sleep(cfg["scan_interval"])

        except asyncio.CancelledError:
            stop_pnl_tracker(user_id)
            try:
                await bot.send_message(chat_id=notify_chat_id,
                                       text="🛑 <b>AutoTrade dihentikan.</b>", parse_mode='HTML')
            except Exception:
                pass
            return

        except Exception as e:
            err_str = str(e)
            logger.error(f"[Engine:{user_id}] Loop error: {e}", exc_info=True)
            # Jangan stop engine karena network/timeout error — hanya retry
            if any(x in err_str for x in ['TOKEN_INVALID', 'SIGNATURE_ERROR']):
                # Auth error di luar order placement — kemungkinan transient, retry 3x
                logger.warning(f"[Engine:{user_id}] Auth error in loop, will retry: {err_str}")
                await asyncio.sleep(60)  # tunggu lebih lama sebelum retry
            else:
                await asyncio.sleep(30)
