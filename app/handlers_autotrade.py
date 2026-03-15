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
WAITING_NEW_LEVERAGE = 5
WAITING_BITUNIX_UID  = 6

BITUNIX_REFERRAL_URL  = "https://www.bitunix.com/register?vipCode=sq45"
BITUNIX_REFERRAL_CODE = "sq45"


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
        "leverage": leverage,
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
        engine_on = engine_running(user_id)
        engine_status = "🟢 Engine berjalan" if engine_on else "🟡 Engine tidak aktif"

        # Fetch real balance dari Bitunix
        balance_line = ""
        try:
            import asyncio
            from app.bitunix_autotrade_client import BitunixAutoTradeClient
            acc = await asyncio.wait_for(
                asyncio.to_thread(BitunixAutoTradeClient(
                    api_key=keys['api_key'], api_secret=keys['api_secret']
                ).get_account_info),
                timeout=8.0
            )
            if acc.get('success'):
                balance_line = (
                    f"💳 Balance Bitunix: <b>{acc['available']:.2f} USDT</b>\n"
                    f"📈 Unrealized PnL: <b>{acc['total_unrealized_pnl']:+.2f} USDT</b>\n"
                )
        except Exception:
            balance_line = ""

        engine_btn = (
            [InlineKeyboardButton("🛑 Stop AutoTrade", callback_data="at_stop_engine")]
            if engine_on else
            [InlineKeyboardButton("🔄 Restart Engine", callback_data="at_restart_engine")]
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Status Portfolio", callback_data="at_status")],
            [InlineKeyboardButton("📈 Trade History",    callback_data="at_history")],
            engine_btn,
            [InlineKeyboardButton("⚙️ Settings",         callback_data="at_settings")],
            [InlineKeyboardButton("🔑 Ganti API Key",    callback_data="at_change_key")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {session['initial_deposit']} USDT\n"
            f"{balance_line}"
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
            [InlineKeyboardButton("🔗 Daftar Bitunix via Referral", url=BITUNIX_REFERRAL_URL)],
            [InlineKeyboardButton("✅ Sudah Daftar, Lanjut Setup",  callback_data="at_confirm_referral")],
            [InlineKeyboardButton("❓ Kenapa Harus via Referral?",  callback_data="at_why_referral")],
        ])
        await update.message.reply_text(
            "🤖 <b>Auto Trade - Bitunix</b>\n\n"
            "Untuk menggunakan fitur Auto Trade, kamu perlu akun Bitunix yang didaftarkan "
            "melalui referral kami.\n\n"
            f"🔗 <b>Link Daftar:</b>\n<code>{BITUNIX_REFERRAL_URL}</code>\n\n"
            f"🎟 <b>Referral Code:</b> <code>{BITUNIX_REFERRAL_CODE}</code>\n\n"
            "Klik tombol di bawah untuk daftar, lalu kembali ke sini setelah selesai.",
            parse_mode='HTML',
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return ConversationHandler.END


# ------------------------------------------------------------------ #
#  Referral gate & UID verification                                   #
# ------------------------------------------------------------------ #

async def callback_why_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "❓ <b>Kenapa Harus Daftar via Referral?</b>\n\n"
        "Referral memungkinkan kami terus mengembangkan bot ini secara gratis untuk kamu.\n\n"
        "✅ Kamu tetap punya full control atas akun Bitunix sendiri\n"
        "✅ Dana kamu aman — API Key hanya punya permission Trade, tidak bisa withdraw\n"
        "✅ Tidak ada biaya tambahan dari kami\n\n"
        f"🔗 Daftar sekarang: {BITUNIX_REFERRAL_URL}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Daftar Sekarang", url=BITUNIX_REFERRAL_URL)],
            [InlineKeyboardButton("✅ Sudah Daftar",    callback_data="at_confirm_referral")],
            [InlineKeyboardButton("🔙 Kembali",         callback_data="at_cancel")],
        ]),
        disable_web_page_preview=True
    )
    return ConversationHandler.END


async def callback_confirm_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User konfirmasi sudah daftar via referral — minta UID Bitunix."""
    query = update.callback_query
    await query.answer()

    # Kalau sudah punya UID tersimpan, skip langsung ke setup key
    user_id = query.from_user.id
    existing_keys = get_user_api_keys(user_id)
    if existing_keys:
        # Sudah pernah setup sebelumnya
        await query.edit_message_text(
            f"✅ <b>Akun sudah terdaftar</b>\n\n"
            f"🔑 API Key: <code>...{existing_keys['key_hint']}</code>\n\n"
            "Lanjutkan ke setup trading:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Mulai Trading", callback_data="at_start_trade")],
                [InlineKeyboardButton("🔑 Ganti API Key", callback_data="at_change_key")],
            ])
        )
        return ConversationHandler.END

    # Cek apakah UID sudah tersimpan di session
    uid_saved = _get_saved_uid(user_id)
    if uid_saved:
        session = get_autotrade_session(user_id)
        uid_status = session.get("status", "") if session else ""

        if uid_status == "uid_verified":
            # UID sudah diverifikasi, langsung ke setup API key
            await query.edit_message_text(
                f"✅ <b>UID Bitunix terverifikasi:</b> <code>{uid_saved}</code>\n\n"
                "Sekarang masukkan API Key kamu:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔑 Setup API Key", callback_data="at_setup_key")],
                ])
            )
            return ConversationHandler.END
        elif uid_status == "pending_verification":
            await query.edit_message_text(
                f"⏳ <b>UID kamu sedang diverifikasi admin</b>\n\n"
                f"🔢 UID: <code>{uid_saved}</code>\n\n"
                "Mohon tunggu, kamu akan dapat notifikasi setelah diverifikasi.",
                parse_mode='HTML'
            )
            return ConversationHandler.END
        elif uid_status == "uid_rejected":
            await query.edit_message_text(
                f"❌ <b>UID sebelumnya ditolak</b>\n\n"
                f"UID <code>{uid_saved}</code> tidak terverifikasi.\n\n"
                "Masukkan UID baru jika kamu sudah daftar ulang via referral:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Daftar via Referral", url=BITUNIX_REFERRAL_URL)],
                    [InlineKeyboardButton("🔄 Masukkan UID Baru",   callback_data="at_confirm_referral")],
                ])
            )
            # Reset UID agar bisa input ulang
            _save_uid(user_id, "", status="pending")
            return ConversationHandler.END

    await query.edit_message_text(
        "✅ <b>Langkah 1/3 — Verifikasi UID</b>\n\n"
        "Masukkan <b>UID Bitunix</b> kamu.\n\n"
        "📍 Cara cek UID:\n"
        "Login Bitunix → klik foto profil → UID tertera di bawah nama kamu\n\n"
        "Contoh: <code>123456789</code>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Batal", callback_data="at_cancel")]
        ])
    )
    return WAITING_BITUNIX_UID


async def receive_bitunix_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terima UID Bitunix dari user, kirim ke admin untuk verifikasi."""
    uid = update.message.text.strip()
    user_id = update.effective_user.id
    user = update.effective_user

    try:
        await update.message.delete()
    except Exception:
        pass

    # Validasi: UID Bitunix biasanya angka 6–12 digit
    if not uid.isdigit() or len(uid) < 5:
        await update.message.reply_text(
            "❌ UID tidak valid. UID Bitunix berupa angka (contoh: <code>123456789</code>).\n\nCoba lagi:",
            parse_mode='HTML'
        )
        return WAITING_BITUNIX_UID

    # Simpan UID ke Supabase dengan status pending_verification
    _save_uid(user_id, uid, status="pending_verification")

    # Kirim notifikasi ke semua admin
    admin_ids = _get_admin_ids()
    username_display = f"@{user.username}" if user.username else f"#{user_id}"
    full_name = user.full_name or "Unknown"

    admin_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ACC",   callback_data=f"uid_acc_{user_id}"),
            InlineKeyboardButton("❌ TOLAK", callback_data=f"uid_reject_{user_id}"),
        ]
    ])

    admin_text = (
        f"🔔 <b>Verifikasi UID AutoTrade</b>\n\n"
        f"👤 User: <b>{full_name}</b> ({username_display})\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"🔢 Bitunix UID: <code>{uid}</code>\n\n"
        f"Pastikan UID ini terdaftar under referral <b>sq45</b> di Bitunix.\n\n"
        f"Acc atau tolak pendaftaran user ini:"
    )

    notified = 0
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                parse_mode='HTML',
                reply_markup=admin_keyboard
            )
            notified += 1
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Gagal kirim notif ke admin {admin_id}: {e}")

    # Konfirmasi ke user bahwa UID sedang diverifikasi
    await update.message.reply_text(
        f"⏳ <b>UID kamu sedang diverifikasi</b>\n\n"
        f"🔢 UID: <code>{uid}</code>\n\n"
        "Admin kami akan memverifikasi bahwa akun Bitunix kamu terdaftar under referral kami.\n\n"
        "Kamu akan mendapat notifikasi setelah verifikasi selesai (biasanya dalam beberapa menit).",
        parse_mode='HTML'
    )
    return ConversationHandler.END


def _save_uid(telegram_id: int, uid: str, status: str = "pending_verification"):
    """Simpan Bitunix UID ke Supabase autotrade_sessions."""
    try:
        _client().table("autotrade_sessions").upsert({
            "telegram_id": int(telegram_id),
            "bitunix_uid": uid,
            "status": status,
            "initial_deposit": 0,
            "current_balance": 0,
            "total_profit": 0,
            "updated_at": datetime.utcnow().isoformat(),
        }, on_conflict="telegram_id").execute()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"_save_uid error: {e}")


def _get_admin_ids() -> list:
    """Ambil semua admin ID dari env vars."""
    import os
    admin_ids = []
    for key in ['ADMIN1', 'ADMIN2', 'ADMIN3', 'ADMIN_IDS']:
        val = os.getenv(key, '')
        if not val:
            continue
        for part in val.split(','):
            part = part.strip()
            if part.isdigit():
                admin_ids.append(int(part))
    return list(set(admin_ids))


def _get_saved_uid(telegram_id: int) -> Optional[str]:
    """Ambil UID yang sudah tersimpan."""
    try:
        res = _client().table("autotrade_sessions").select("bitunix_uid").eq(
            "telegram_id", int(telegram_id)
        ).limit(1).execute()
        if res.data:
            return res.data[0].get("bitunix_uid")
    except Exception:
        pass
    return None


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


async def callback_restart_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart autotrade engine untuk user ini tanpa perlu restart bot."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    keys = get_user_api_keys(user_id)
    session = get_autotrade_session(user_id)

    if not keys or not session or session.get("status") != "active":
        await query.edit_message_text(
            "❌ Tidak ada sesi aktif. Gunakan /autotrade untuk mulai.",
            parse_mode='HTML'
        )
        return ConversationHandler.END

    from app.autotrade_engine import start_engine, is_running
    if is_running(user_id):
        await query.answer("✅ Engine sudah berjalan!", show_alert=True)
        return ConversationHandler.END

    amount = float(session.get("initial_deposit", 10))
    leverage = int(session.get("leverage", 10))

    start_engine(
        bot=query.get_bot(),
        user_id=user_id,
        api_key=keys["api_key"],
        api_secret=keys["api_secret"],
        amount=amount,
        leverage=leverage,
        notify_chat_id=user_id,
    )

    await query.edit_message_text(
        "✅ <b>Engine berhasil direstart!</b>\n\n"
        f"💵 Modal: {amount} USDT | ⚙️ Leverage: {leverage}x\n\n"
        "Bot sedang memantau pasar. Gunakan /autotrade untuk cek status.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Dashboard", callback_data="at_dashboard")],
            [InlineKeyboardButton("🛑 Stop AutoTrade", callback_data="at_stop_engine")],
        ])
    )
    return ConversationHandler.END


# ------------------------------------------------------------------ #
#  Admin: verifikasi UID user                                         #
# ------------------------------------------------------------------ #

async def callback_uid_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin acc UID user — update status dan notifikasi user."""
    query = update.callback_query
    await query.answer("✅ User di-ACC")
    admin_id = query.from_user.id

    # Parse target user_id dari callback data: uid_acc_{user_id}
    target_user_id = int(query.data.split("_")[-1])

    # Update status di Supabase
    try:
        _client().table("autotrade_sessions").update({
            "status": "uid_verified",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("telegram_id", target_user_id).execute()
    except Exception:
        pass

    # Edit pesan admin
    await query.edit_message_text(
        query.message.text + f"\n\n✅ <b>Di-ACC oleh admin</b>",
        parse_mode='HTML'
    )

    # Notifikasi ke user
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "✅ <b>UID Kamu Telah Diverifikasi!</b>\n\n"
                "Akun Bitunix kamu sudah terkonfirmasi under referral kami.\n\n"
                "Sekarang setup API Key untuk mulai Auto Trade:"
            ),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Setup API Key", callback_data="at_setup_key")]
            ])
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Gagal notif user {target_user_id}: {e}")


async def callback_uid_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin tolak UID user — update status dan notifikasi user."""
    query = update.callback_query
    await query.answer("❌ User ditolak")

    target_user_id = int(query.data.split("_")[-1])

    # Update status di Supabase
    try:
        _client().table("autotrade_sessions").update({
            "status": "uid_rejected",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("telegram_id", target_user_id).execute()
    except Exception:
        pass

    # Edit pesan admin
    await query.edit_message_text(
        query.message.text + f"\n\n❌ <b>Ditolak oleh admin</b>",
        parse_mode='HTML'
    )

    # Notifikasi ke user
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "❌ <b>Verifikasi UID Ditolak</b>\n\n"
                "UID Bitunix kamu tidak terdeteksi terdaftar under referral kami.\n\n"
                "Pastikan kamu mendaftar Bitunix menggunakan link berikut:\n"
                f"🔗 <code>{BITUNIX_REFERRAL_URL}</code>\n\n"
                "Setelah daftar ulang dengan referral yang benar, kirim UID baru kamu dengan /autotrade."
            ),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Daftar Ulang via Referral", url=BITUNIX_REFERRAL_URL)],
                [InlineKeyboardButton("🔄 Coba Lagi", callback_data="at_confirm_referral")],
            ]),
            disable_web_page_preview=True
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Gagal notif user {target_user_id}: {e}")


# ------------------------------------------------------------------ #
#  Settings: leverage & margin mode                                   #
# ------------------------------------------------------------------ #

async def callback_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan menu settings leverage & margin mode."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    session = get_autotrade_session(user_id)
    current_leverage = int(session.get("leverage", 10)) if session else 10
    current_margin   = session.get("margin_mode", "cross") if session else "cross"
    margin_label     = "Cross ♾️" if current_margin == "cross" else "Isolated 🔒"

    await query.edit_message_text(
        f"⚙️ <b>Settings AutoTrade</b>\n\n"
        f"📊 Leverage saat ini: <b>{current_leverage}x</b>\n"
        f"💼 Margin mode: <b>{margin_label}</b>\n\n"
        "Pilih yang ingin diubah:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Ganti Leverage",    callback_data="at_set_leverage")],
            [InlineKeyboardButton("💼 Ganti Margin Mode", callback_data="at_set_margin")],
            [InlineKeyboardButton("🔙 Kembali",           callback_data="at_dashboard")],
        ])
    )
    return ConversationHandler.END


async def callback_set_leverage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan pilihan leverage baru."""
    query = update.callback_query
    await query.answer()

    session = get_autotrade_session(query.from_user.id)
    current = int(session.get("leverage", 10)) if session else 10

    await query.edit_message_text(
        f"📊 <b>Ganti Leverage</b>\n\n"
        f"Leverage saat ini: <b>{current}x</b>\n\n"
        "Pilih leverage baru atau ketik angka (1–125):",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5x",  callback_data="at_newlev_5"),
                InlineKeyboardButton("10x", callback_data="at_newlev_10"),
                InlineKeyboardButton("20x", callback_data="at_newlev_20"),
            ],
            [
                InlineKeyboardButton("50x",  callback_data="at_newlev_50"),
                InlineKeyboardButton("75x",  callback_data="at_newlev_75"),
                InlineKeyboardButton("100x", callback_data="at_newlev_100"),
            ],
            [InlineKeyboardButton("🔙 Kembali", callback_data="at_settings")],
        ])
    )
    return WAITING_NEW_LEVERAGE


async def receive_new_leverage_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input leverage manual dari teks."""
    try:
        leverage = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka. Contoh: <code>25</code>", parse_mode='HTML')
        return WAITING_NEW_LEVERAGE

    if leverage < 1 or leverage > 125:
        await update.message.reply_text("❌ Leverage harus antara 1–125.")
        return WAITING_NEW_LEVERAGE

    await _apply_new_leverage(update.message, update.effective_user.id, leverage, context, from_callback=False)
    return ConversationHandler.END


async def callback_new_leverage_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tombol leverage baru (at_newlev_XX)."""
    query = update.callback_query
    await query.answer()
    leverage = int(query.data.split("_")[-1])
    await _apply_new_leverage(query, query.from_user.id, leverage, context, from_callback=True)
    return ConversationHandler.END


async def _apply_new_leverage(msg_or_query, user_id: int, leverage: int,
                               context, from_callback: bool):
    """Simpan leverage baru ke Supabase + apply ke Bitunix jika engine aktif."""
    from app.bitunix_autotrade_client import BitunixAutoTradeClient
    import asyncio

    keys    = get_user_api_keys(user_id)
    session = get_autotrade_session(user_id)

    # Update di Supabase
    try:
        _client().table("autotrade_sessions").update({
            "leverage": leverage,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("telegram_id", user_id).execute()
    except Exception as e:
        pass

    # Apply ke Bitunix untuk semua symbol aktif
    apply_status = ""
    if keys:
        try:
            client = BitunixAutoTradeClient(api_key=keys['api_key'], api_secret=keys['api_secret'])
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
            margin_mode = session.get("margin_mode", "cross") if session else "cross"
            results = []
            for sym in symbols:
                r = await asyncio.to_thread(client.set_leverage, sym, leverage, margin_mode)
                results.append("✅" if r.get("success") else "⚠️")
            apply_status = f"\n\nApply ke Bitunix: {' '.join(results)}"
        except Exception as e:
            apply_status = f"\n\n⚠️ Gagal apply ke Bitunix: {e}"

    # Restart engine dengan leverage baru jika sedang berjalan
    from app.autotrade_engine import is_running, start_engine, stop_engine
    engine_restarted = ""
    if is_running(user_id) and keys and session:
        stop_engine(user_id)
        import asyncio
        await asyncio.sleep(0.5)
        bot = msg_or_query.get_bot() if from_callback else context.bot
        start_engine(
            bot=bot,
            user_id=user_id,
            api_key=keys['api_key'],
            api_secret=keys['api_secret'],
            amount=float(session.get("initial_deposit", 10)),
            leverage=leverage,
            notify_chat_id=user_id,
        )
        engine_restarted = "\n🔄 Engine direstart dengan leverage baru."

    text = (
        f"✅ <b>Leverage diubah ke {leverage}x</b>"
        f"{apply_status}"
        f"{engine_restarted}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Settings", callback_data="at_settings")],
        [InlineKeyboardButton("🏠 Dashboard", callback_data="at_dashboard")],
    ])

    if from_callback:
        await msg_or_query.edit_message_text(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await msg_or_query.reply_text(text, parse_mode='HTML', reply_markup=keyboard)


async def callback_set_margin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan pilihan margin mode."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    session = get_autotrade_session(user_id)
    current = session.get("margin_mode", "cross") if session else "cross"

    cross_check    = "✅ " if current == "cross"    else ""
    isolated_check = "✅ " if current == "isolated" else ""

    await query.edit_message_text(
        f"💼 <b>Ganti Margin Mode</b>\n\n"
        f"Mode saat ini: <b>{'Cross ♾️' if current == 'cross' else 'Isolated 🔒'}</b>\n\n"
        "<b>Cross Margin</b> — semua balance dipakai sebagai margin, risiko likuidasi lebih kecil.\n"
        "<b>Isolated Margin</b> — margin terbatas per posisi, loss maksimal = margin yang dialokasikan.\n\n"
        "Pilih mode:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{cross_check}♾️ Cross Margin",    callback_data="at_margin_cross")],
            [InlineKeyboardButton(f"{isolated_check}🔒 Isolated Margin", callback_data="at_margin_isolated")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="at_settings")],
        ])
    )
    return ConversationHandler.END


async def callback_margin_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Apply margin mode yang dipilih."""
    query = update.callback_query
    await query.answer()
    user_id  = query.from_user.id
    mode     = query.data.split("_")[-1]   # "cross" or "isolated"
    mode_label = "Cross ♾️" if mode == "cross" else "Isolated 🔒"

    keys    = get_user_api_keys(user_id)
    session = get_autotrade_session(user_id)
    leverage = int(session.get("leverage", 10)) if session else 10

    # Simpan ke Supabase
    try:
        _client().table("autotrade_sessions").update({
            "margin_mode": mode,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("telegram_id", user_id).execute()
    except Exception:
        pass

    # Apply ke Bitunix
    apply_status = ""
    if keys:
        try:
            import asyncio
            from app.bitunix_autotrade_client import BitunixAutoTradeClient
            client  = BitunixAutoTradeClient(api_key=keys['api_key'], api_secret=keys['api_secret'])
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
            results = []
            for sym in symbols:
                r = await asyncio.to_thread(client.set_leverage, sym, leverage, mode)
                results.append("✅" if r.get("success") else "⚠️")
            apply_status = f"\n\nApply ke Bitunix: {' '.join(results)}"
        except Exception as e:
            apply_status = f"\n\n⚠️ Gagal apply: {e}"

    await query.edit_message_text(
        f"✅ <b>Margin mode diubah ke {mode_label}</b>"
        f"{apply_status}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Settings",  callback_data="at_settings")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="at_dashboard")],
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
            CallbackQueryHandler(callback_setup_key,        pattern="^at_setup_key$"),
            CallbackQueryHandler(callback_change_key,       pattern="^at_change_key$"),
            CallbackQueryHandler(callback_start_trade,      pattern="^at_start_trade$"),
            CallbackQueryHandler(callback_set_leverage,     pattern="^at_set_leverage$"),
            CallbackQueryHandler(callback_confirm_referral, pattern="^at_confirm_referral$"),
        ],
        states={
            WAITING_BITUNIX_UID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_bitunix_uid),
                CallbackQueryHandler(callback_cancel, pattern="^at_cancel$"),
            ],
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
            WAITING_NEW_LEVERAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_leverage_text),
                CallbackQueryHandler(callback_new_leverage_select, pattern="^at_newlev_\\d+$"),
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
    application.add_handler(CallbackQueryHandler(callback_howto,              pattern="^at_howto$"))
    application.add_handler(CallbackQueryHandler(callback_delete_key,         pattern="^at_delete_key$"))
    application.add_handler(CallbackQueryHandler(callback_confirm_delete,     pattern="^at_confirm_delete$"))
    application.add_handler(CallbackQueryHandler(callback_dashboard,          pattern="^at_dashboard$"))
    application.add_handler(CallbackQueryHandler(callback_confirm_trade,      pattern="^at_confirm_trade$"))
    application.add_handler(CallbackQueryHandler(callback_stop_engine,        pattern="^at_stop_engine$"))
    application.add_handler(CallbackQueryHandler(callback_restart_engine,     pattern="^at_restart_engine$"))
    application.add_handler(CallbackQueryHandler(callback_settings,           pattern="^at_settings$"))
    application.add_handler(CallbackQueryHandler(callback_set_margin,         pattern="^at_set_margin$"))
    application.add_handler(CallbackQueryHandler(callback_margin_select,      pattern="^at_margin_(cross|isolated)$"))
    application.add_handler(CallbackQueryHandler(callback_why_referral,       pattern="^at_why_referral$"))
    application.add_handler(CallbackQueryHandler(callback_uid_acc,            pattern="^uid_acc_\\d+$"))
    application.add_handler(CallbackQueryHandler(callback_uid_reject,         pattern="^uid_reject_\\d+$"))

    print("✅ AutoTrade handlers registered (Supabase + AES-256-GCM + Engine)")
