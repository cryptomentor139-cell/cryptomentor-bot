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
WAITING_API_KEY    = 1
WAITING_API_SECRET = 2
WAITING_TRADE_AMOUNT = 3


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


def save_autotrade_session(telegram_id: int, amount: float):
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
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Status Portfolio", callback_data="at_status")],
            [InlineKeyboardButton("📈 Trade History",    callback_data="at_history")],
            [InlineKeyboardButton("💸 Withdraw",         callback_data="at_withdraw")],
            [InlineKeyboardButton("🔑 Ganti API Key",    callback_data="at_change_key")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {session['initial_deposit']} USDT\n"
            f"📊 Balance: {session['current_balance']} USDT\n"
            f"📈 Profit: {session['total_profit']:.2f} USDT\n\n"
            f"🔑 API Key: <code>...{keys['key_hint']}</code>\n"
            f"🏦 Exchange: {keys['exchange'].upper()}",
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
        await loading.edit_text(
            f"⚠️ <b>Tersimpan, tapi verifikasi gagal:</b>\n{result.get('error')}\n\n"
            "Cek API Key/Secret atau coba lagi nanti.",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
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

    await query.edit_message_text(
        "💰 <b>Mulai Auto Trade</b>\n\n"
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

    loading = await update.message.reply_text("🤖 <b>Memulai Auto Trade...</b>", parse_mode='HTML')

    try:
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        result = BitunixAutoTradeClient(
            api_key=keys['api_key'], api_secret=keys['api_secret']
        ).start_autotrade(user_id=user_id, amount=amount, wallet_address=f"user_{user_id}")
    except Exception as e:
        result = {'success': False, 'error': str(e)}

    if result.get('success'):
        save_autotrade_session(user_id, amount)
        await loading.edit_text(
            f"✅ <b>Auto Trade Aktif!</b>\n\n"
            f"💰 Deposit: {amount} USDT | 🏦 BITUNIX\n\n"
            "Gunakan /autotrade untuk cek status.",
            parse_mode='HTML'
        )
    else:
        await loading.edit_text(
            f"❌ <b>Gagal:</b> {result.get('error', 'Unknown')}\n\nCek API Key atau hubungi admin.",
            parse_mode='HTML'
        )
    return ConversationHandler.END


# ------------------------------------------------------------------ #
#  Misc callbacks                                                     #
# ------------------------------------------------------------------ #

async def callback_howto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 <b>Cara Mendapatkan API Key Bitunix</b>\n\n"
        "1. Login ke <a href='https://www.bitunix.com'>bitunix.com</a>\n"
        "2. Profil → <b>API Management</b>\n"
        "3. <b>Create API Key</b>\n"
        "4. Permission: ✅ Trade, ✅ Read\n"
        "5. Copy API Key & Secret Key\n\n"
        "⚠️ Secret Key hanya tampil sekali — simpan baik-baik!",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Setup API Key", callback_data="at_setup_key")]
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

    print("✅ AutoTrade handlers registered (Supabase + AES-256-GCM)")
