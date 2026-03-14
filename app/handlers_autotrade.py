"""
Auto Trade Handlers for Telegram Bot
Handles /autotrade commands with per-user API Key setup
"""

import sqlite3
import hashlib
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from typing import Optional, Dict, Any
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Conversation states
WAITING_API_KEY = 1
WAITING_API_SECRET = 2
WAITING_TRADE_AMOUNT = 3

# Database file for autotrade users
AUTOTRADE_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "autotrade_users.db")


def init_autotrade_db():
    """Initialize database for auto trade users"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autotrade_users (
            user_id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            wallet_address TEXT,
            initial_deposit REAL,
            current_balance REAL,
            total_profit REAL DEFAULT 0,
            status TEXT DEFAULT 'inactive',
            start_date TIMESTAMP,
            last_update TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_api_keys (
            telegram_id INTEGER PRIMARY KEY,
            api_key TEXT NOT NULL,
            api_secret_hash TEXT NOT NULL,
            api_secret_encrypted TEXT NOT NULL,
            exchange TEXT DEFAULT 'bitunix',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autotrade_trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            side TEXT,
            amount REAL,
            price REAL,
            profit_loss REAL,
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES autotrade_users(telegram_id)
        )
    """)

    conn.commit()
    conn.close()


init_autotrade_db()


def _simple_encrypt(text: str, key: int) -> str:
    """Simple XOR-based encryption for storing API secret"""
    key_str = str(key)
    encrypted = []
    for i, char in enumerate(text):
        encrypted.append(chr(ord(char) ^ ord(key_str[i % len(key_str)])))
    return ''.join(encrypted).encode('latin-1').hex()


def _simple_decrypt(hex_text: str, key: int) -> str:
    """Decrypt API secret"""
    key_str = str(key)
    text = bytes.fromhex(hex_text).decode('latin-1')
    decrypted = []
    for i, char in enumerate(text):
        decrypted.append(chr(ord(char) ^ ord(key_str[i % len(key_str)])))
    return ''.join(decrypted)


def save_user_api_keys(telegram_id: int, api_key: str, api_secret: str):
    """Save user's API key and secret to database"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()[:16]
    secret_encrypted = _simple_encrypt(api_secret, telegram_id)
    cursor.execute("""
        INSERT OR REPLACE INTO user_api_keys
        (telegram_id, api_key, api_secret_hash, api_secret_encrypted, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (telegram_id, api_key, secret_hash, secret_encrypted, datetime.now()))
    conn.commit()
    conn.close()


def get_user_api_keys(telegram_id: int) -> Optional[Dict]:
    """Get user's API keys from database"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT api_key, api_secret_encrypted, exchange, created_at
        FROM user_api_keys WHERE telegram_id = ?
    """, (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'api_key': row[0],
            'api_secret': _simple_decrypt(row[1], telegram_id),
            'exchange': row[2],
            'created_at': row[3]
        }
    return None


def delete_user_api_keys(telegram_id: int):
    """Delete user's API keys"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_api_keys WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def get_autotrade_user(telegram_id: int):
    """Get auto trade user from database"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM autotrade_users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def save_autotrade_user(telegram_id: int, amount: float):
    """Save auto trade user to database"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO autotrade_users
        (telegram_id, initial_deposit, current_balance, total_profit, status, start_date, last_update)
        VALUES (?, ?, ?, 0, 'active', ?, ?)
    """, (telegram_id, amount, amount, datetime.now(), datetime.now()))
    conn.commit()
    conn.close()


def update_autotrade_status(telegram_id: int, status: str):
    """Update auto trade status"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE autotrade_users SET status = ?, last_update = ? WHERE telegram_id = ?
    """, (status, datetime.now(), telegram_id))
    conn.commit()
    conn.close()


# ─── CONVERSATION FLOW: Setup API Keys ────────────────────────────────────────

async def cmd_autotrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: /autotrade — cek API keys dulu"""
    user_id = update.effective_user.id
    keys = get_user_api_keys(user_id)
    user_data = get_autotrade_user(user_id)
    has_active = user_data and user_data[6] == 'active'

    if keys and has_active:
        # Sudah setup dan aktif — tampilkan dashboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Status Portfolio", callback_data="at_status")],
            [InlineKeyboardButton("📈 Trade History", callback_data="at_history")],
            [InlineKeyboardButton("💸 Withdraw", callback_data="at_withdraw")],
            [InlineKeyboardButton("🔑 Ganti API Key", callback_data="at_change_key")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {user_data[3]} USDT\n"
            f"📊 Balance: {user_data[4]} USDT\n"
            f"📈 Profit: {user_data[5]:.2f} USDT\n\n"
            f"🔑 API Key: <code>{keys['api_key'][:8]}...{keys['api_key'][-4:]}</code>\n"
            f"🏦 Exchange: {keys['exchange'].upper()}",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        return ConversationHandler.END

    elif keys and not has_active:
        # Punya key tapi belum mulai trading
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Mulai Trading", callback_data="at_start_trade")],
            [InlineKeyboardButton("🔑 Ganti API Key", callback_data="at_change_key")],
            [InlineKeyboardButton("❌ Hapus API Key", callback_data="at_delete_key")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade - Bitunix</b>\n\n"
            f"✅ API Key sudah tersimpan\n"
            f"🔑 Key: <code>{keys['api_key'][:8]}...{keys['api_key'][-4:]}</code>\n"
            f"🏦 Exchange: {keys['exchange'].upper()}\n\n"
            "Pilih aksi:",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        return ConversationHandler.END

    else:
        # Belum ada API key — mulai setup flow
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Setup API Key Sekarang", callback_data="at_setup_key")],
            [InlineKeyboardButton("❓ Cara Dapat API Key", callback_data="at_howto")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade - Bitunix</b>\n\n"
            "Untuk memulai auto trading, kamu perlu menghubungkan akun Bitunix kamu.\n\n"
            "📋 <b>Yang dibutuhkan:</b>\n"
            "• API Key dari akun Bitunix kamu\n"
            "• API Secret dari akun Bitunix kamu\n\n"
            "🔒 API key disimpan terenkripsi dan hanya digunakan untuk trading atas nama kamu.\n\n"
            "Klik tombol di bawah untuk mulai setup:",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        return ConversationHandler.END


async def callback_setup_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: mulai input API Key"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]
    ])
    await query.edit_message_text(
        "🔑 <b>Setup API Key - Langkah 1/2</b>\n\n"
        "Masukkan <b>API Key</b> Bitunix kamu:\n\n"
        "💡 Cara mendapatkan API Key:\n"
        "1. Login ke bitunix.com\n"
        "2. Buka Settings → API Management\n"
        "3. Buat API Key baru dengan permission: <i>Trade, Read</i>\n"
        "4. Copy API Key dan paste di sini\n\n"
        "⚠️ Jangan share API Key ke siapapun selain bot ini.",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    return WAITING_API_KEY


async def callback_change_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: ganti API Key"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]
    ])
    await query.edit_message_text(
        "🔑 <b>Ganti API Key - Langkah 1/2</b>\n\n"
        "Masukkan <b>API Key</b> Bitunix baru kamu:",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    return WAITING_API_KEY


async def receive_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima input API Key dari user"""
    api_key = update.message.text.strip()

    # Hapus pesan user untuk keamanan
    try:
        await update.message.delete()
    except Exception:
        pass

    if len(api_key) < 10:
        await update.message.reply_text(
            "❌ API Key tidak valid. Minimal 10 karakter.\n\nCoba lagi atau /cancel untuk batal."
        )
        return WAITING_API_KEY

    context.user_data['temp_api_key'] = api_key

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]
    ])
    await update.message.reply_text(
        "✅ API Key diterima.\n\n"
        "🔐 <b>Setup API Key - Langkah 2/2</b>\n\n"
        "Sekarang masukkan <b>API Secret</b> Bitunix kamu:\n\n"
        "⚠️ Pesan ini akan otomatis terhapus setelah diproses.",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    return WAITING_API_SECRET


async def receive_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima input API Secret, simpan, lalu test koneksi"""
    api_secret = update.message.text.strip()
    user_id = update.effective_user.id

    # Hapus pesan user untuk keamanan
    try:
        await update.message.delete()
    except Exception:
        pass

    if len(api_secret) < 10:
        await update.message.reply_text(
            "❌ API Secret tidak valid. Minimal 10 karakter.\n\nCoba lagi atau /cancel untuk batal."
        )
        return WAITING_API_SECRET

    api_key = context.user_data.get('temp_api_key')
    if not api_key:
        await update.message.reply_text("❌ Session expired. Silakan mulai ulang dengan /autotrade")
        return ConversationHandler.END

    # Simpan ke database
    save_user_api_keys(user_id, api_key, api_secret)
    context.user_data.pop('temp_api_key', None)

    # Test koneksi dengan key user
    loading_msg = await update.message.reply_text(
        "⏳ <b>Menyimpan dan memverifikasi API Key...</b>",
        parse_mode='HTML'
    )

    try:
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        client = BitunixAutoTradeClient(api_key=api_key, api_secret=api_secret)
        result = client.check_connection()
    except Exception as e:
        result = {'online': False, 'error': str(e)}

    if result.get('online'):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Mulai Trading Sekarang", callback_data="at_start_trade")],
            [InlineKeyboardButton("📋 Lihat Dashboard", callback_data="at_dashboard")],
        ])
        await loading_msg.edit_text(
            "✅ <b>API Key berhasil disimpan dan terverifikasi!</b>\n\n"
            f"🔑 Key: <code>{api_key[:8]}...{api_key[-4:]}</code>\n"
            "🏦 Exchange: BITUNIX\n"
            "🔗 Status: Terhubung\n\n"
            "Sekarang kamu bisa mulai auto trading:",
            parse_mode='HTML',
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Coba Lagi", callback_data="at_setup_key")],
            [InlineKeyboardButton("✅ Simpan Tetap", callback_data="at_dashboard")],
        ])
        await loading_msg.edit_text(
            "⚠️ <b>API Key disimpan, tapi koneksi gagal diverifikasi.</b>\n\n"
            f"Error: {result.get('error', 'Unknown')}\n\n"
            "Kemungkinan penyebab:\n"
            "• API Key/Secret salah\n"
            "• Permission API tidak cukup (butuh: Trade, Read)\n"
            "• Server Bitunix sedang down\n\n"
            "Kamu bisa coba lagi atau simpan tetap dan coba trading nanti.",
            parse_mode='HTML',
            reply_markup=keyboard
        )

    return ConversationHandler.END


async def callback_start_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: mulai input amount untuk trading"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    keys = get_user_api_keys(user_id)
    if not keys:
        await query.edit_message_text(
            "❌ API Key tidak ditemukan. Gunakan /autotrade untuk setup."
        )
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]
    ])
    await query.edit_message_text(
        "💰 <b>Mulai Auto Trade</b>\n\n"
        "Masukkan jumlah USDT yang ingin kamu tradingkan:\n\n"
        "📌 Minimum: 10 USDT\n"
        "📌 Maximum: 1000 USDT\n\n"
        "Contoh: ketik <code>50</code> untuk 50 USDT",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    context.user_data['at_flow'] = 'start_trade'
    return WAITING_TRADE_AMOUNT


async def receive_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima jumlah USDT dan mulai trading"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    try:
        amount = float(text)
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka yang valid. Contoh: <code>50</code>", parse_mode='HTML')
        return WAITING_TRADE_AMOUNT

    if amount < 10:
        await update.message.reply_text("❌ Minimum 10 USDT.")
        return WAITING_TRADE_AMOUNT
    if amount > 1000:
        await update.message.reply_text("❌ Maximum 1000 USDT.")
        return WAITING_TRADE_AMOUNT

    keys = get_user_api_keys(user_id)
    if not keys:
        await update.message.reply_text("❌ API Key tidak ditemukan. Gunakan /autotrade untuk setup.")
        return ConversationHandler.END

    loading_msg = await update.message.reply_text(
        "🤖 <b>Memulai Auto Trade...</b>\n⏳ Mohon tunggu...",
        parse_mode='HTML'
    )

    try:
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
        client = BitunixAutoTradeClient(api_key=keys['api_key'], api_secret=keys['api_secret'])
        result = client.start_autotrade(user_id=user_id, amount=amount, wallet_address=f"user_{user_id}")
    except Exception as e:
        result = {'success': False, 'error': str(e)}

    if result.get('success'):
        save_autotrade_user(user_id, amount)
        await loading_msg.edit_text(
            f"✅ <b>Auto Trade Aktif!</b>\n\n"
            f"💰 Deposit: {amount} USDT\n"
            f"🏦 Exchange: BITUNIX\n"
            f"📊 Target: 5-10% per bulan\n\n"
            f"Gunakan /autotrade untuk cek status.",
            parse_mode='HTML'
        )
    else:
        await loading_msg.edit_text(
            f"❌ <b>Gagal memulai Auto Trade:</b>\n{result.get('error', 'Unknown error')}\n\n"
            f"Cek API Key kamu atau hubungi admin.",
            parse_mode='HTML'
        )

    return ConversationHandler.END


async def callback_howto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: cara mendapatkan API Key"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Setup API Key", callback_data="at_setup_key")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="at_back")],
    ])
    await query.edit_message_text(
        "📖 <b>Cara Mendapatkan API Key Bitunix</b>\n\n"
        "1. Buka <a href='https://www.bitunix.com'>bitunix.com</a> dan login\n"
        "2. Klik foto profil → <b>API Management</b>\n"
        "3. Klik <b>Create API Key</b>\n"
        "4. Beri nama (contoh: CryptoMentorBot)\n"
        "5. Centang permission: ✅ <b>Trade</b>, ✅ <b>Read</b>\n"
        "6. Masukkan IP Whitelist jika diminta (opsional)\n"
        "7. Copy <b>API Key</b> dan <b>Secret Key</b>\n\n"
        "⚠️ Secret Key hanya ditampilkan sekali — simpan baik-baik!",
        parse_mode='HTML',
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    return ConversationHandler.END


async def callback_delete_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: hapus API Key"""
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Ya, Hapus", callback_data="at_confirm_delete")],
        [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")],
    ])
    await query.edit_message_text(
        "⚠️ <b>Hapus API Key?</b>\n\nIni akan menghapus API Key yang tersimpan dan menghentikan auto trading.",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    return ConversationHandler.END


async def callback_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: konfirmasi hapus API Key"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    delete_user_api_keys(user_id)
    update_autotrade_status(user_id, 'inactive')

    await query.edit_message_text(
        "✅ API Key berhasil dihapus.\n\nGunakan /autotrade untuk setup ulang."
    )
    return ConversationHandler.END


async def callback_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: batal"""
    query = update.callback_query
    await query.answer()
    context.user_data.pop('temp_api_key', None)
    context.user_data.pop('at_flow', None)
    await query.edit_message_text("❌ Dibatalkan. Gunakan /autotrade untuk memulai lagi.")
    return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /cancel untuk keluar dari conversation"""
    context.user_data.pop('temp_api_key', None)
    context.user_data.pop('at_flow', None)
    await update.message.reply_text("❌ Dibatalkan.")
    return ConversationHandler.END


async def callback_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: tampilkan dashboard"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    keys = get_user_api_keys(user_id)
    user_data = get_autotrade_user(user_id)
    has_active = user_data and user_data[6] == 'active'

    if has_active:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Status Portfolio", callback_data="at_status")],
            [InlineKeyboardButton("💸 Withdraw", callback_data="at_withdraw")],
            [InlineKeyboardButton("🔑 Ganti API Key", callback_data="at_change_key")],
        ])
        await query.edit_message_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {user_data[3]} USDT\n"
            f"🔑 API Key: <code>{keys['api_key'][:8]}...{keys['api_key'][-4:]}</code>",
            parse_mode='HTML',
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Mulai Trading", callback_data="at_start_trade")],
            [InlineKeyboardButton("🔑 Ganti API Key", callback_data="at_change_key")],
        ])
        await query.edit_message_text(
            "🤖 <b>Auto Trade</b>\n\n"
            f"✅ API Key tersimpan\n"
            f"🔑 Key: <code>{keys['api_key'][:8]}...{keys['api_key'][-4:]}</code>\n"
            "⏸ Status: Belum aktif\n\n"
            "Klik Mulai Trading untuk memulai:",
            parse_mode='HTML',
            reply_markup=keyboard
        )
    return ConversationHandler.END


def register_autotrade_handlers(application):
    """Register all autotrade handlers with the application"""

    # ConversationHandler untuk setup API Key dan mulai trade
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("autotrade", cmd_autotrade),
            CallbackQueryHandler(callback_setup_key, pattern="^at_setup_key$"),
            CallbackQueryHandler(callback_change_key, pattern="^at_change_key$"),
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
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )

    application.add_handler(conv_handler)

    # Standalone callback handlers (di luar conversation)
    application.add_handler(CallbackQueryHandler(callback_howto, pattern="^at_howto$"))
    application.add_handler(CallbackQueryHandler(callback_delete_key, pattern="^at_delete_key$"))
    application.add_handler(CallbackQueryHandler(callback_confirm_delete, pattern="^at_confirm_delete$"))
    application.add_handler(CallbackQueryHandler(callback_dashboard, pattern="^at_dashboard$"))

    print("✅ AutoTrade handlers registered (with API Key setup flow)")
