"""
Auto Trade Handlers for Telegram Bot
Handles /autotrade commands with Automaton AI integration
"""

import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from typing import Optional, Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    try:
        from app.bitunix_autotrade_client import BitunixAutoTradeClient
    except ImportError:
        from bitunix_autotrade_client import BitunixAutoTradeClient
    print("[OK] BitunixAutoTradeClient imported successfully")
except ImportError:
    print("[WARN] BitunixAutoTradeClient not found, creating mock client")
    class BitunixAutoTradeClient:
        def check_connection(self):
            return {'online': False, 'error': 'Bitunix client not available'}
        def start_autotrade(self, user_id, amount, wallet_address):
            return {'success': False, 'error': 'Bitunix client not available'}
        def get_autotrade_status(self, user_id):
            return {'success': False, 'error': 'Bitunix client not available'}
        def withdraw_autotrade(self, user_id):
            return {'success': False, 'error': 'Bitunix client not available'}
        def get_trade_history(self, user_id, limit=10):
            return {'success': False, 'error': 'Bitunix client not available'}

# Initialize Bitunix client
bitunix = BitunixAutoTradeClient()

# Database file for autotrade users
AUTOTRADE_DB = "autotrade_users.db"

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
            total_profit REAL,
            status TEXT,
            start_date TIMESTAMP,
            last_update TIMESTAMP
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
            FOREIGN KEY (user_id) REFERENCES autotrade_users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on import
init_autotrade_db()

def is_premium_user(telegram_id: int) -> bool:
    """Check if user is premium member"""
    try:
        from services import get_database
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT premium_until FROM users 
            WHERE telegram_id = ? AND premium_until > datetime('now')
        """, (telegram_id,))
        
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Exception as e:
        print(f"Error checking premium status: {e}")
        # For admin users, allow access
        admin_ids = [1187119989, 7079544380]  # From .env
        return telegram_id in admin_ids

def get_user_wallet(telegram_id: int) -> str:
    """Get user's wallet address"""
    try:
        from services import get_database
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT wallet_address FROM users WHERE telegram_id = ?
        """, (telegram_id,))
        
        result = cursor.fetchone()
        if result and result[0]:
            return result[0]
        else:
            # Generate placeholder wallet for demo
            return f"0x{telegram_id:016x}{'0' * 24}"
    except Exception as e:
        print(f"Error getting wallet: {e}")
        return f"0x{telegram_id:016x}{'0' * 24}"

def save_autotrade_user(telegram_id: int, amount: float, wallet: str):
    """Save auto trade user to database"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO autotrade_users 
        (telegram_id, wallet_address, initial_deposit, current_balance, total_profit, status, start_date, last_update)
        VALUES (?, ?, ?, ?, 0, 'active', ?, ?)
    """, (telegram_id, wallet, amount, amount, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()

def get_autotrade_user(telegram_id: int):
    """Get auto trade user from database"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM autotrade_users WHERE telegram_id = ?
    """, (telegram_id,))
    
    result = cursor.fetchone()
    conn.close()
    return result

def update_autotrade_status(telegram_id: int, status: str):
    """Update auto trade status"""
    conn = sqlite3.connect(AUTOTRADE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE autotrade_users 
        SET status = ?, last_update = ?
        WHERE telegram_id = ?
    """, (status, datetime.now(), telegram_id))
    
    conn.commit()
    conn.close()

async def cmd_autotrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main autotrade command - shows menu"""
    user_id = update.effective_user.id
    
    # Check if user has active autotrade
    user_data = get_autotrade_user(user_id)
    has_active = user_data and user_data[6] == 'active'  # status column
    
    if has_active:
        await update.message.reply_text(
            "🤖 <b>Auto Trade Dashboard</b>\n\n"
            "✅ Status: <b>AKTIF</b>\n"
            f"💰 Deposit: {user_data[3]} USDT\n"
            f"📊 Balance: {user_data[4]} USDT\n"
            f"📈 Profit: {user_data[5]:.2f} USDT\n\n"
            "<b>Commands:</b>\n"
            "/autotrade_status - Cek portfolio detail\n"
            "/autotrade_history - Lihat trade history\n"
            "/autotrade_withdraw - Withdraw profit\n\n"
            "🤖 AI sedang trading untuk Anda 24/7!",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "🤖 <b>Auto Trade - AI Trading Bot</b>\n\n"
            "🎯 <b>Features:</b>\n"
            "• AI trading 24/7 dengan Bitunix\n"
            "• Target: 5-10% profit per bulan\n"
            "• Risk management otomatis\n"
            "• Fee: 25% dari profit saja\n\n"
            "💰 <b>Minimum:</b> 10 USDT\n"
            "🔒 <b>Premium Only</b>\n\n"
            "<b>Commands:</b>\n"
            "/autotrade_start <amount> - Mulai auto trade\n"
            "/autotrade_status - Cek status\n"
            "/autotrade_history - Trade history\n\n"
            "Contoh: `/autotrade_start 50`",
            parse_mode='HTML'
        )

async def cmd_autotrade_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /autotrade_start <amount>"""
    user_id = update.effective_user.id
    
    # Check premium status
    if not is_premium_user(user_id):
        await update.message.reply_text(
            "⚠️ <b>Auto Trade hanya untuk Premium Members!</b>\n\n"
            "Upgrade ke Premium untuk akses fitur ini.\n"
            "Gunakan /subscribe untuk upgrade.",
            parse_mode='HTML'
        )
        return
    
    # Check if already has active auto trade
    existing = get_autotrade_user(user_id)
    if existing and existing[6] == 'active':  # status column
        await update.message.reply_text(
            "⚠️ <b>Anda sudah memiliki Auto Trade aktif!</b>\n\n"
            "Gunakan /autotrade_status untuk cek status\n"
            "atau /autotrade_withdraw untuk withdraw.",
            parse_mode='HTML'
        )
        return
    
    # Get amount
    if not context.args:
        await update.message.reply_text(
            "📊 <b>Auto Trade - AI Trading Bot</b>\n\n"
            "<b>Usage:</b> `/autotrade_start <amount_usdt>`\n"
            "<b>Contoh:</b> `/autotrade_start 50`\n\n"
            "💰 <b>Minimum:</b> 10 USDT\n"
            "🎯 <b>Target:</b> 5-10% per bulan\n"
            "💸 <b>Fee:</b> 25% dari profit\n"
            "⚠️ <b>Risk:</b> Medium",
            parse_mode='HTML'
        )
        return
    
    try:
        amount = float(context.args[0])
        if amount < 10:
            await update.message.reply_text("❌ <b>Minimum deposit: 10 USDT</b>", parse_mode='HTML')
            return
        if amount > 1000:
            await update.message.reply_text("❌ <b>Maximum deposit: 1000 USDT untuk safety</b>", parse_mode='HTML')
            return
    except ValueError:
        await update.message.reply_text("❌ <b>Amount harus berupa angka</b>", parse_mode='HTML')
        return
    
    # Get user wallet
    wallet = get_user_wallet(user_id)
    
    # Send loading message
    loading_msg = await update.message.reply_text(
        "🤖 <b>Memulai Auto Trade...</b>\n"
        "AI sedang menganalisis market dan menyiapkan strategy...\n\n"
        "⏳ Mohon tunggu 30-60 detik..."
    )
    
    # Check Bitunix connection first
    connection = bitunix.check_connection()
    if not connection.get('online'):
        await loading_msg.edit_text(
            "❌ <b>AutoTrade system temporarily unavailable. Please try again later.</b>\n\n"
            "If this issue persists, please contact support.\n\n"
            f"Error: {connection.get('error', 'Bitunix API offline')}"
        )
        return
    
    # Start auto trade
    result = bitunix.start_autotrade(
        user_id=user_id,
        amount=amount,
        wallet_address=wallet
    )
    
    if result['success']:
        # Save to database
        save_autotrade_user(user_id, amount, wallet)
        
        await loading_msg.edit_text(
            f"✅ <b>Auto Trade Aktif!</b>\n\n"
            f"💰 <b>Deposit:</b> {amount} USDT\n"
            f"🤖 <b>Exchange:</b> Bitunix\n"
            f"📊 <b>Target:</b> 5-10% per bulan\n"
            f"⚠️ <b>Risk:</b> Medium\n"
            f"💼 <b>Wallet:</b> `{wallet[:10]}...{wallet[-8:]}`\n\n"
            f"🎯 <b>Strategy:</b>\n{result['response'][:300]}...\n\n"
            f"Bitunix akan mulai trading dalam beberapa menit.\n"
            f"Gunakan /autotrade_status untuk cek progress.",
            parse_mode='HTML'
        )
    else:
        await loading_msg.edit_text(
            f"❌ <b>Error memulai Auto Trade:</b>\n{result['error']}\n\n"
            f"Silakan coba lagi atau hubungi admin."
        )

async def cmd_autotrade_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /autotrade_status"""
    user_id = update.effective_user.id
    
    # Check if user has auto trade
    user_data = get_autotrade_user(user_id)
    if not user_data:
        await update.message.reply_text(
            "⚠️ <b>Anda belum memiliki Auto Trade aktif.</b>\n\n"
            "Gunakan /autotrade_start untuk memulai.",
            parse_mode='HTML'
        )
        return
    
    loading_msg = await update.message.reply_text(
        "📊 <b>Mengambil data portfolio...</b>\n"
        "⏳ Mohon tunggu..."
    )
    
    # Get status from Bitunix
    result = bitunix.get_autotrade_status(user_id)
    
    if result['success']:
        # Parse response and format nicely
        await loading_msg.edit_text(
            f"📊 <b>Auto Trade Status</b>\n\n"
            f"{result['response']}\n\n"
            f"💸 Gunakan /autotrade_withdraw untuk withdraw profit\n"
            f"📈 Gunakan /autotrade_history untuk lihat trade history",
            parse_mode='HTML'
        )
    else:
        await loading_msg.edit_text(
            f"❌ <b>Error mengambil status:</b>\n{result['error']}\n\n"
            f"Silakan coba lagi nanti."
        )

async def cmd_autotrade_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /autotrade_withdraw"""
    user_id = update.effective_user.id
    
    # Check if user has auto trade
    user_data = get_autotrade_user(user_id)
    if not user_data or user_data[6] != 'active':  # status column
        await update.message.reply_text(
            "⚠️ <b>Anda tidak memiliki Auto Trade aktif.</b>\n\n"
            "Gunakan /autotrade_start untuk memulai.",
            parse_mode='HTML'
        )
        return
    
    loading_msg = await update.message.reply_text(
        "💸 <b>Memproses withdrawal...</b>\n"
        "Closing positions dan calculating profit...\n\n"
        "⏳ Mohon tunggu 30-60 detik..."
    )
    
    # Process withdrawal
    result = bitunix.withdraw_autotrade(user_id)
    
    if result['success']:
        # Update status to closed
        update_autotrade_status(user_id, 'closed')
        
        await loading_msg.edit_text(
            f"✅ <b>Withdrawal Berhasil!</b>\n\n"
            f"{result['response']}\n\n"
            f"Terima kasih telah menggunakan Auto Trade!\n"
            f"Gunakan /autotrade_start untuk memulai lagi.",
            parse_mode='HTML'
        )
    else:
        await loading_msg.edit_text(
            f"❌ <b>Error processing withdrawal:</b>\n{result['error']}\n\n"
            f"Silakan coba lagi atau hubungi admin."
        )

async def cmd_autotrade_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /autotrade_history"""
    user_id = update.effective_user.id
    
    # Check if user has auto trade
    user_data = get_autotrade_user(user_id)
    if not user_data:
        await update.message.reply_text(
            "⚠️ <b>Anda belum memiliki Auto Trade aktif.</b>\n\n"
            "Gunakan /autotrade_start untuk memulai.",
            parse_mode='HTML'
        )
        return
    
    loading_msg = await update.message.reply_text(
        "📈 <b>Mengambil trade history...</b>\n"
        "⏳ Mohon tunggu..."
    )
    
    # Get trade history from Bitunix
    result = bitunix.get_trade_history(user_id, limit=10)
    
    if result['success']:
        await loading_msg.edit_text(
            f"📈 <b>Trade History (Last 10)</b>\n\n"
            f"{result['response']}\n\n"
            f"💡 Gunakan /autotrade_status untuk portfolio summary",
            parse_mode='HTML'
        )
    else:
        await loading_msg.edit_text(
            f"❌ <b>Error mengambil history:</b>\n{result['error']}\n\n"
            f"Silakan coba lagi nanti."
        )

def register_autotrade_handlers(application):
    """Register all autotrade handlers with the application"""
    from telegram.ext import CommandHandler
    
    # Register autotrade command handlers
    application.add_handler(CommandHandler("autotrade", cmd_autotrade))
    application.add_handler(CommandHandler("autotrade_start", cmd_autotrade_start))
    application.add_handler(CommandHandler("autotrade_status", cmd_autotrade_status))
    application.add_handler(CommandHandler("autotrade_withdraw", cmd_autotrade_withdraw))
    application.add_handler(CommandHandler("autotrade_history", cmd_autotrade_history))
    
    print("✅ AutoTrade handlers registered:")
    print("   • /autotrade - Main autotrade menu")
    print("   • /autotrade_start <amount> - Start auto trading")
    print("   • /autotrade_status - Check portfolio status")
    print("   • /autotrade_withdraw - Withdraw profits")
    print("   • /autotrade_history - View trade history")

