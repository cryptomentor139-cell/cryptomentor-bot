"""
Auto Trade Handlers for Telegram Bot
API Key user disimpan di Supabase, terenkripsi AES-256-GCM.
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from typing import Optional, Dict
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lib.crypto import encrypt, decrypt
from app.supabase_repo import _client

# Conversation states
WAITING_API_KEY      = 1
WAITING_API_SECRET   = 2
WAITING_TRADE_AMOUNT = 3
WAITING_LEVERAGE     = 4


# ------------------------------------------------------------------ #
#  Supabase helpers — user_api_keys                                   #
# ------------------------------------------------------------------ #

def save_user_api_keys(telegram_id: int, api_key: str, api_secret: str):
    """Simpan API key + secret terenkripsi ke Supabase."""
    s = _client()
    row = {
        "telegram_id": int(telegram_id),
        "exchange": "bitunix",
        "api_key": api_key,
        "api_secret_enc": encrypt(api_secret),
        "key_hint": api_key[-4:],
        "updated_at": datetime.utcnow().isoformat(),
    }
    s.table("user_api_keys").upsert(row, on_conflict="telegram_id").execute()


def get_user_api_keys(telegram_id: int) -> Optional[Dict]:
    """Ambil dan dekripsi API keys dari Supabase."""
    s = _client()
    res = s.table("user_api_keys").select("*").eq("telegram_id", int(telegram_id)).limit(1).execute()
    if not res.data:
        return None
    row = res.data[0]
    try:
        secret = decrypt(row["api_secret_enc"])
    except Exception:
        return None
    return {
        "api_key": row["api_key"],
        "api_secret": secret,
        "exchange": row.get("exchange", "bitunix"),
        "created_at": row.get("created_at"),
        "key_hint": row.get("key_hint", row["api_key"][-4:]),
    }


def delete_user_api_keys(telegram_id: int):
    """Hapus API keys dari Supabase."""
    _client().table("user_api_keys").delete().eq("telegram_id", int(telegram_id)).execute()


# ------------------------------------------------------------------ #
#  Supabase helpers — autotrade_sessions                              #
# ------------------------------------------------------------------ #

def _ensure_autotrade_table():
    """Pastikan tabel autotrade_sessions ada (idempotent via upsert)."""
    pass  # dibuat via SQL migration


def get_autotrade_session(telegram_id: int) -> Optional[Dict]:
    s = _client()
    res = s.table("autotrade_sessions").select("*").eq("telegram_id", int(telegram_id)).limit(1).execute()
    return res.data[0] if res.data else None


def save_autotrade_session(telegram_id: int, amount: float, leverage: int = 10):
    s = _client()
    row = {
        "telegram_id": int(telegram_id),
        "initial_deposit": amount,
        "current_balance": amount,
        "total_profit": 0,
        "status": "active",
        "started_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    s.table("autotrade_sessions").upsert(row, on_conflict="telegram_id").execute()


def update_autotrade_status(telegram_id: int, status: str):
    s = _client()
    s.table("autotrade_sessions").upsert(
        {"telegram_id": int(telegram_id), "status": status,
         "updated_at": datetime.utcnow().isoformat()},
        on_conflict="telegram_id"
    ).execute()


# ------------------------------------------------------------------ #
#  Conversation: /autotrade entry                                     #
# ------------------------------------------------------------------ #

async def cmd_autotrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keys = get_user_api_keys(user_id)
    session = get_autotrade_session(user_id)
    is_active = session and session.get("status") == "active"

    if keys and is_active:
        from app.autotrade_engine import is_running as engine_running
        engine_status = "🟢 Engine berjalan" if engine_running(user_id) else "🟡 Engine tidak aktif (restart bot?)"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Status Portfolio", callback_data="at_status")],
            [InlineKeyboardButton("📈 Trade History",    callback_data="at_history")],
            [InlineKeyboardButton("💸 Withdraw",         callback_data="at_withdraw")],
            [InlineKeyboardButton("🛑 Stop AutoTrade",   callback_data="at_stop_engine")],
            [InlineKeyboardButton("🔑 Ganti API Key",    callback_data="at_change_key")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {session['initial_deposit']} USDT\n"
            f"📊 Balance: {session['current_balance']} USDT\n"
            f"📈 Profit: {session['total_profit']:.2f} USDT\n\n"
            f"🔑 API Key: <code>...{keys['key_hint']}</code>\n"
            f"🏦 Exchange: {keys['exchange'].upper()}\n"
            f"⚙️ {engine_status}",
            parse_mode='HTML', reply_markup=keyboard
        )
        return ConversationHandler.END

    elif keys:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Mulai Trading",  callback_data="at_start_trade")],
            [InlineKeyboardButton("🔑 Ganti API Key",  callback_data="at_change_key")],
            [InlineKeyboardButton("❌ Hapus API Key",  callback_data="at_delete_key")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade - Bitunix</b>\n\n"
            f"✅ API Key tersimpan: <code>...{keys['key_hint']}</code>\n"
            "⏸ Status: Belum aktif\n\nPilih aksi:",
            parse_mode='HTML', reply_markup=keyboard
        )
        return ConversationHandler.END

    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Setup API Key",      callback_data="at_setup_key")],
            [InlineKeyboardButton("❓ Cara Dapat API Key", callback_data="at_howto")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade - Bitunix</b>\n\n"
            "Hubungkan akun Bitunix kamu untuk mulai auto trading.\n\n"
            "🔒 API Secret disimpan terenkripsi (AES-256-GCM) di server kami.\n"
            "Tidak ada yang bisa membacanya selain sistem trading.",
            parse_mode='HTML', reply_markup=keyboard
        )
        return ConversationHandler.END


# ------------------------------------------------------------------ #
#  Conversation: input API Key                                        #
# ------------------------------------------------------------------ #

async def callback_setup_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Kalau sudah punya key, jangan minta input lagi — langsung ke dashboard
    existing = get_user_api_keys(user_id)
    if existing:
        await query.edit_message_text(
            f"✅ <b>API Key sudah tersimpan</b>\n\n"
            f"🔑 Key: <code>...{existing['key_hint']}</code>\n"
            f"🏦 Exchange: {existing['exchange'].upper()}\n\n"
            "Gunakan <b>Ganti API Key</b> jika ingin menggantinya.",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Mulai Trading", callback_data="at_start_trade")],
                [InlineKeyboardButton("🔑 Ganti API Key", callback_data="at_change_key")],
                [InlineKeyboardButton("❌ Hapus API Key", callback_data="at_delete_key")],
            ])
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "🔑 <b>Setup API Key — Langkah 1/2</b>\n\n"
        "Masukkan <b>API Key</b> Bitunix kamu:\n\n"
        "💡 Settings → API Management → Create API Key\n"
        "Permission yang dibutuhkan: ✅ Trade, ✅ Read",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]])
    )
    return WAITING_API_KEY


async def callback_change_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔑 <b>Ganti API Key — Langkah 1/2</b>\n\nMasukkan <b>API Key</b> Bitunix baru:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]])
    )
    return WAITING_API_KEY


async def receive_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = update.message.text.strip()
    try:
        await update.message.delete()
    except Exception:
        pass

    if len(api_key) < 10:
        await update.message.reply_text("❌ API Key tidak valid (min 10 karakter). Coba lagi:")
        return WAITING_API_KEY

    context.user_data['temp_api_key'] = api_key
    await update.message.reply_text(
        "✅ API Key diterima.\n\n"
        "🔐 <b>Langkah 2/2</b> — Masukkan <b>API Secret</b>:\n\n"
        "⚠️ Pesan ini akan dihapus setelah diproses.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]])
    )
    return WAITING_API_SECRET


async def receive_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_secret = update.message.text.strip()
    user_id = update.effective_user.id
    try:
        await update.message.delete()
    except Exception:
        pass

    if len(api_secret) < 10:
        await update.message.reply_text("❌ API Secret tidak valid. Coba lagi:")
        return WAITING_API_SECRET

    api_key = context.user_data.pop('temp_api_key', None)
    if not api_key:
        await update.message.reply_text("❌ Session expired. Mulai ulang dengan /autotrade")
        return ConversationHandler.END

    # Simpan terenkripsi ke Supabase
    try:
        save_user_api_keys(user_id, api_key, api_secret)
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menyimpan API Key: {e}")
        return ConversationHandler.END

    loading = await update.message.reply_text("⏳ <b>Memverifikasi koneksi...</b>", parse_mode='HTML')

    try:
        import asyncio
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        client = BitunixAutoTradeClient(api_key=api_key, api_secret=api_secret)
        result = await asyncio.wait_for(
            asyncio.to_thread(client.check_connection),
            timeout=15.0
        )
    except asyncio.TimeoutError:
        result = {'online': False, 'error': 'Timeout: server tidak merespons dalam 15 detik'}
    except Exception as e:
        result = {'online': False, 'error': str(e)}

    if result.get('online'):
        await loading.edit_text(
            "✅ <b>API Key tersimpan dan terverifikasi!</b>\n\n"
            f"🔑 Key: <code>...{api_key[-4:]}</code>\n"
            "🏦 Exchange: BITUNIX\n"
            "🔒 Secret: terenkripsi AES-256-GCM\n\n"
            "Siap mulai trading:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Mulai Trading", callback_data="at_start_trade")],
            ])
        )
    else:
        err = result.get('error', '')
        if '403' in str(err) or 'TOKEN_INVALID' in str(err):
            msg = (
                "⚠️ <b>API Key tersimpan, tapi akses ditolak</b>\n\n"
                "API Key kamu punya <b>IP Restriction</b> yang memblokir server bot.\n\n"
                "<b>Cara fix (wajib):</b>\n"
                "1. Login Bitunix → API Management\n"
                "2. Hapus API Key yang ada\n"
                "3. Buat API Key baru\n"
                "4. Di bagian <b>Bind IP Address</b> → <b>KOSONGKAN</b> (jangan isi apapun)\n"
                "5. Centang permission: ✅ Trade\n"
                "6. Setup ulang di bot ini\n\n"
                "⚠️ <b>Kenapa harus kosong?</b>\n"
                "Server bot menggunakan IP dinamis. Jika diisi IP tertentu, Bitunix akan blokir semua request dari IP lain."
            )
        else:
            msg = (
                f"⚠️ <b>Tersimpan, tapi verifikasi gagal:</b>\n{err}\n\n"
                "Pastikan API Key dan Secret sudah benar, lalu coba lagi."
            )
        await loading.edit_text(
            msg,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Tutorial", callback_data="at_howto")],
                [InlineKeyboardButton("🔄 Coba Lagi", callback_data="at_setup_key")],
                [InlineKeyboardButton("✅ Simpan Tetap", callback_data="at_dashboard")],
            ])
        )
    return ConversationHandler.END


# ------------------------------------------------------------------ #
#  Conversation: mulai trading                                        #
# ------------------------------------------------------------------ #

async def callback_start_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not get_user_api_keys(user_id):
        await query.edit_message_text("❌ API Key tidak ditemukan. Gunakan /autotrade untuk setup.")
        return ConversationHandler.END

    # Cek balance real dari Bitunix
    keys = get_user_api_keys(user_id)
    try:
        import asyncio
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        acc = await asyncio.wait_for(
            asyncio.to_thread(BitunixAutoTradeClient(
                api_key=keys['api_key'], api_secret=keys['api_secret']
            ).get_account_info),
            timeout=10.0
        )
        balance_line = f"\n💳 Balance tersedia: <b>{acc.get('available', 0):.2f} USDT</b>" if acc.get('success') else ""
    except Exception:
        balance_line = ""

    await query.edit_message_text(
        f"💰 <b>Mulai Auto Trade</b>{balance_line}\n\n"
        "Masukkan jumlah USDT yang ingin ditradingkan:\n\n"
        "📌 Min: 10 USDT | Max: 1000 USDT\n"
        "Contoh: ketik <code>50</code>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]])
    )
    context.user_data['at_flow'] = 'start_trade'
    return WAITING_TRADE_AMOUNT


async def receive_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        amount = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka. Contoh: <code>50</code>", parse_mode='HTML')
        return WAITING_TRADE_AMOUNT

    if amount < 10:
        await update.message.reply_text("❌ Minimum 10 USDT.")
        return WAITING_TRADE_AMOUNT
    if amount > 1000:
        await update.message.reply_text("❌ Maximum 1000 USDT.")
        return WAITING_TRADE_AMOUNT

    keys = get_user_api_keys(user_id)
    if not keys:
        await update.message.reply_text("❌ API Key tidak ditemukan. Gunakan /autotrade.")
        return ConversationHandler.END

    context.user_data['trade_amount'] = amount

    # Tanya leverage
    await update.message.reply_text(
        f"⚙️ <b>Pilih Leverage</b>\n\n"
        f"Modal: <b>{amount} USDT</b>\n\n"
        "Pilih leverage atau ketik angka (1-125):",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5x",  callback_data="at_lev_5"),
                InlineKeyboardButton("10x", callback_data="at_lev_10"),
                InlineKeyboardButton("20x", callback_data="at_lev_20"),
            ],
            [
                InlineKeyboardButton("50x",  callback_data="at_lev_50"),
                InlineKeyboardButton("75x",  callback_data="at_lev_75"),
                InlineKeyboardButton("100x", callback_data="at_lev_100"),
            ],
            [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")],
        ])
    )
    return WAITING_LEVERAGE


# ------------------------------------------------------------------ #
#  Misc callbacks                                                     #
# ------------------------------------------------------------------ #

async def _show_leverage_preview(update_or_query, context, leverage: int, from_callback: bool):
    """Tampilkan risk/reward preview berdasarkan amount + leverage, minta konfirmasi."""
    amount = context.user_data.get('trade_amount', 0)

    # Contoh kalkulasi dengan asumsi trade 2% move
    notional = amount * leverage
    potential_profit_2pct = notional * 0.02   # TP ~2%
    potential_loss_2pct   = notional * 0.02   # SL ~2%
    liquidation_pct       = round(100 / leverage, 1)

    # Risk level label
    if leverage <= 10:
        risk_label = "🟢 RENDAH"
        risk_note  = "Cocok untuk pemula. Risiko likuidasi kecil."
    elif leverage <= 25:
        risk_label = "🟡 SEDANG"
        risk_note  = "Perlu manajemen risiko yang baik."
    elif leverage <= 50:
        risk_label = "🟠 TINGGI"
        risk_note  = "Hanya untuk trader berpengalaman."
    else:
        risk_label = "🔴 SANGAT TINGGI"
        risk_note  = "Risiko likuidasi sangat besar. Hati-hati!"

    text = (
        f"📊 <b>Preview Risk/Reward — {leverage}x Leverage</b>\n\n"
        f"💵 Modal: <b>{amount} USDT</b>\n"
        f"📈 Notional value: <b>{notional:.0f} USDT</b>\n\n"
        f"✅ Potensi profit (TP ~2%): <b>+{potential_profit_2pct:.2f} USDT</b>\n"
        f"❌ Potensi loss (SL ~2%): <b>-{potential_loss_2pct:.2f} USDT</b>\n"
        f"💥 Likuidasi jika harga turun: <b>{liquidation_pct}%</b>\n\n"
        f"⚠️ Risk Level: {risk_label}\n"
        f"📝 {risk_note}\n\n"
        f"Bot akan otomatis:\n"
        f"• Scan signal SMC + Order Block setiap menit\n"
        f"• Eksekusi order dengan TP & SL otomatis\n"
        f"• Notifikasi setiap trade masuk\n\n"
        f"Lanjutkan dengan <b>{leverage}x</b>?"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ Mulai dengan {leverage}x", callback_data=f"at_confirm_trade")],
        [InlineKeyboardButton("🔄 Ganti Leverage", callback_data="at_start_trade")],
        [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")],
    ])

    context.user_data['trade_leverage'] = leverage

    if from_callback:
        await update_or_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update_or_query.reply_text(text, parse_mode='HTML', reply_markup=keyboard)


async def callback_leverage_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tombol leverage 5x/10x/20x/50x/75x/100x."""
    query = update.callback_query
    await query.answer()
    leverage = int(query.data.split("_")[-1])
    await _show_leverage_preview(query, context, leverage, from_callback=True)
    return ConversationHandler.END


async def receive_leverage_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input leverage manual (angka)."""
    try:
        leverage = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka leverage. Contoh: <code>20</code>", parse_mode='HTML')
        return WAITING_LEVERAGE

    if leverage < 1 or leverage > 125:
        await update.message.reply_text("❌ Leverage harus antara 1–125.")
        return WAITING_LEVERAGE

    await _show_leverage_preview(update.message, context, leverage, from_callback=False)
    return ConversationHandler.END


async def callback_confirm_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User konfirmasi — start engine."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    amount   = context.user_data.get('trade_amount')
    leverage = context.user_data.get('trade_leverage', 10)

    if not amount:
        await query.edit_message_text("❌ Session expired. Mulai ulang dengan /autotrade.")
        return ConversationHandler.END

    keys = get_user_api_keys(user_id)
    if not keys:
        await query.edit_message_text("❌ API Key tidak ditemukan.")
        return ConversationHandler.END

    # Cek balance sebelum mulai
    loading = await query.edit_message_text("⏳ <b>Memverifikasi balance...</b>", parse_mode='HTML')

    try:
        import asyncio
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        acc = await asyncio.wait_for(
            asyncio.to_thread(BitunixAutoTradeClient(
                api_key=keys['api_key'], api_secret=keys['api_secret']
            ).get_account_info),
            timeout=15.0
        )
    except asyncio.TimeoutError:
        await loading.edit_text("❌ Timeout saat cek balance. Coba lagi.")
        return ConversationHandler.END
    except Exception as e:
        await loading.edit_text(f"❌ Error: {e}")
        return ConversationHandler.END

    if not acc.get('success'):
        err = acc.get('error', '')
        if '403' in str(err) or 'TOKEN_INVALID' in str(err):
            await loading.edit_text(
                "❌ <b>Akses ditolak Bitunix</b>\n\n"
                "API Key kamu punya <b>IP Restriction</b> yang memblokir server bot.\n\n"
                "<b>Cara fix:</b>\n"
                "1. Login Bitunix → API Management\n"
                "2. Hapus API Key yang ada\n"
                "3. Buat API Key baru\n"
                "4. Di bagian <b>Bind IP Address</b> → <b>KOSONGKAN</b>\n"
                "5. Centang permission: ✅ Trade\n"
                "6. Setup ulang di bot: /autotrade → Ganti API Key",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❓ Tutorial Lengkap", callback_data="at_howto")],
                    [InlineKeyboardButton("🔑 Setup Ulang API Key", callback_data="at_change_key")],
                ])
            )
        else:
            await loading.edit_text(f"❌ Gagal cek balance: {err}", parse_mode='HTML')
        return ConversationHandler.END

    available = acc.get('available', 0)
    if available < amount:
        await loading.edit_text(
            f"❌ <b>Balance tidak cukup</b>\n\n"
            f"Tersedia: {available:.2f} USDT\n"
            f"Dibutuhkan: {amount} USDT",
            parse_mode='HTML'
        )
        return ConversationHandler.END

    # Simpan session dan start engine
    save_autotrade_session(user_id, amount, leverage)

    from app.autotrade_engine import start_engine
    start_engine(
        bot=query.get_bot(),
        user_id=user_id,
        api_key=keys['api_key'],
        api_secret=keys['api_secret'],
        amount=amount,
        leverage=leverage,
        notify_chat_id=user_id,
    )

    await loading.edit_text(
        f"✅ <b>AutoTrade Aktif!</b>\n\n"
        f"💵 Modal: {amount} USDT\n"
        f"⚙️ Leverage: {leverage}x\n"
        f"🏦 Exchange: BITUNIX\n\n"
        f"Bot sedang memantau pasar. Kamu akan dapat notifikasi setiap kali ada trade masuk.\n\n"
        f"Gunakan /autotrade untuk cek status atau stop.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛑 Stop AutoTrade", callback_data="at_stop_engine")],
            [InlineKeyboardButton("📊 Dashboard", callback_data="at_dashboard")],
        ])
    )
    return ConversationHandler.END


async def callback_stop_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop autotrade engine untuk user ini."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    from app.autotrade_engine import stop_engine, is_running
    if is_running(user_id):
        stop_engine(user_id)
        # Update status di Supabase
        try:
            _client().table("autotrade_sessions").update({
                "status": "stopped",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("telegram_id", user_id).execute()
        except Exception:
            pass
        await query.edit_message_text(
            "🛑 <b>AutoTrade dihentikan.</b>\n\nGunakan /autotrade untuk mulai lagi.",
            parse_mode='HTML'
        )
    else:
        await query.edit_message_text(
            "ℹ️ AutoTrade tidak sedang berjalan.\n\nGunakan /autotrade untuk mulai.",
            parse_mode='HTML'
        )
    return ConversationHandler.END


def _get_server_ip() -> str:
    """Ambil IP publik server ini (Railway/VPS)."""
    try:
        import requests as _req
        r = _req.get("https://api.ipify.org?format=json", timeout=5)
        return r.json().get("ip", "tidak diketahui")
    except Exception:
        return "tidak diketahui"


async def callback_howto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📖 <b>Cara Setup API Key Bitunix</b>\n\n"
        "<b>Langkah-langkah:</b>\n"
        "1. Login ke <a href='https://www.bitunix.com'>bitunix.com</a>\n"
        "2. Klik foto profil → <b>API Management</b>\n"
        "3. Klik <b>Create API Key</b>\n"
        "4. Isi <b>Note</b>: bebas (contoh: AutoTrade)\n"
        "5. <b>Purpose</b>: pilih <b>Trading API</b>\n"
        "6. <b>Bind IP address</b>: ⚠️ <b>WAJIB KOSONG</b> — jangan isi apapun\n"
        "7. <b>Permission</b>: centang ✅ <b>Trade</b>\n"
        "8. Klik <b>Confirm</b> → verifikasi email\n"
        "9. Copy <b>API Key</b> dan <b>Secret Key</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🚫 <b>JANGAN isi Bind IP Address</b>\n\n"
        "Server bot menggunakan IP dinamis yang bisa berubah sewaktu-waktu. "
        "Jika IP diisi, Bitunix akan blokir semua request dari IP lain dan autotrade tidak bisa jalan.\n\n"
        "✅ <b>Aman tanpa IP restriction?</b>\n"
        "Ya — API key ini hanya punya permission <b>Trade</b>, "
        "tidak bisa withdraw dana. Dana kamu tetap aman.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Secret Key hanya tampil <b>sekali</b> — simpan baik-baik sebelum klik Got it!",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Setup API Key", callback_data="at_setup_key")],
            [InlineKeyboardButton("🌐 Buka Bitunix API Management",
                                  url="https://www.bitunix.com/user/api-management")],
        ]),
        disable_web_page_preview=True
    )
    return ConversationHandler.END



async def callback_delete_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⚠️ <b>Hapus API Key?</b>\n\nIni akan menghentikan auto trading dan menghapus API Key.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Ya, Hapus", callback_data="at_confirm_delete")],
            [InlineKeyboardButton("❌ Batal",     callback_data="at_cancel")],
        ])
    )
    return ConversationHandler.END


async def callback_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    delete_user_api_keys(user_id)
    update_autotrade_status(user_id, 'inactive')
    await query.edit_message_text("✅ API Key dihapus. Gunakan /autotrade untuk setup ulang.")
    return ConversationHandler.END


async def callback_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop('temp_api_key', None)
    context.user_data.pop('at_flow', None)
    await query.edit_message_text("❌ Dibatalkan. Gunakan /autotrade untuk memulai lagi.")
    return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('temp_api_key', None)
    context.user_data.pop('at_flow', None)
    await update.message.reply_text("❌ Dibatalkan.")
    return ConversationHandler.END


async def callback_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    keys = get_user_api_keys(user_id)
    session = get_autotrade_session(user_id)
    is_active = session and session.get("status") == "active"

    if is_active and keys:
        await query.edit_message_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {session['initial_deposit']} USDT\n"
            f"🔑 Key: <code>...{keys['key_hint']}</code>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Status", callback_data="at_status")],
                [InlineKeyboardButton("💸 Withdraw", callback_data="at_withdraw")],
            ])
        )
    else:
        await query.edit_message_text(
            "🤖 <b>Auto Trade</b>\n\n"
            f"✅ API Key: <code>...{keys['key_hint'] if keys else '????'}</code>\n"
            "⏸ Status: Belum aktif",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Mulai Trading", callback_data="at_start_trade")]
            ])
        )
    return ConversationHandler.END


# ------------------------------------------------------------------ #
#  Register handlers                                                  #
# ------------------------------------------------------------------ #

def register_autotrade_handlers(application):
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("autotrade", cmd_autotrade),
            CallbackQueryHandler(callback_setup_key,   pattern="^at_setup_key$"),
            CallbackQueryHandler(callback_change_key,  pattern="^at_change_key$"),
            CallbackQueryHandler(callback_start_trade, pattern="^at_start_trade$"),
        ],
        states={
            WAITING_API_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_key),
                CallbackQueryHandler(callback_cancel, pattern="^at_cancel$"),
            ],
            WAITING_API_SECRET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_secret),
                CallbackQueryHandler(callback_cancel, pattern="^at_cancel$"),
            ],
            WAITING_TRADE_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_trade_amount),
                CallbackQueryHandler(callback_cancel, pattern="^at_cancel$"),
            ],
            WAITING_LEVERAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_leverage_text),
                CallbackQueryHandler(callback_leverage_select, pattern="^at_lev_\\d+$"),
                CallbackQueryHandler(callback_cancel, pattern="^at_cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cmd_cancel),
            CallbackQueryHandler(callback_cancel, pattern="^at_cancel$"),
        ],
        per_user=True, per_chat=True, allow_reentry=True,
    )

    application.add_handler(conv)
    application.add_handler(CallbackQueryHandler(callback_howto,          pattern="^at_howto$"))
    application.add_handler(CallbackQueryHandler(callback_delete_key,     pattern="^at_delete_key$"))
    application.add_handler(CallbackQueryHandler(callback_confirm_delete, pattern="^at_confirm_delete$"))
    application.add_handler(CallbackQueryHandler(callback_dashboard,      pattern="^at_dashboard$"))
    application.add_handler(CallbackQueryHandler(callback_confirm_trade,  pattern="^at_confirm_trade$"))
    application.add_handler(CallbackQueryHandler(callback_stop_engine,    pattern="^at_stop_engine$"))

    print("✅ AutoTrade handlers registered (Supabase + AES-256-GCM + Engine)")
