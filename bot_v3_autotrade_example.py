"""
Contoh Integrasi Auto Trade ke Bot V3
Untuk python-telegram-bot atau telebot
"""

from automaton_autotrade_client import AutomatonAutoTradeClient
import sqlite3
from datetime import datetime

# Initialize Automaton client
automaton = AutomatonAutoTradeClient()

# Database untuk tracking user auto trade
AUTOTRADE_DB = "autotrade_users.db"

def init_autotrade_db():
    """Initialize database untuk auto trade users"""
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

# Initialize database
init_autotrade_db()

# ============================================
# HELPER FUNCTIONS
# ============================================

def is_premium_user(telegram_id: int) -> bool:
    """Check if user is premium member"""
    # TODO: Implement your premium check logic
    # Contoh: query database premium users
    return True  # Placeholder

def get_user_wallet(telegram_id: int) -> str:
    """Get user's wallet address"""
    # TODO: Implement wallet retrieval
    # Contoh: query dari database user
    return "0x1234567890abcdef1234567890abcdef12345678"  # Placeholder

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

# ============================================
# BOT HANDLERS - python-telegram-bot
# ============================================

async def autotrade_start_handler(update, context):
    """Handler untuk /autotrade_start <amount>"""
    user_id = update.effective_user.id
    
    # Check premium status
    if not is_premium_user(user_id):
        await update.message.reply_text(
            "⚠️ Auto Trade hanya untuk Premium Members!\n\n"
            "Upgrade ke Premium untuk akses fitur ini."
        )
        return
    
    # Check if already has active auto trade
    existing = get_autotrade_user(user_id)
    if existing and existing[6] == 'active':  # status column
        await update.message.reply_text(
            "⚠️ Anda sudah memiliki Auto Trade aktif!\n\n"
            "Gunakan /autotrade_status untuk cek status\n"
            "atau /autotrade_withdraw untuk withdraw."
        )
        return
    
    # Get amount
    if not context.args:
        await update.message.reply_text(
            "📊 Auto Trade - AI Trading Bot\n\n"
            "Usage: /autotrade_start <amount_usdc>\n"
            "Contoh: /autotrade_start 50\n\n"
            "Minimum: 10 USDC\n"
            "Target: 5-10% per bulan\n"
            "Fee: 25% dari profit\n"
            "Risk: Medium"
        )
        return
    
    try:
        amount = float(context.args[0])
        if amount < 10:
            await update.message.reply_text("❌ Minimum deposit: 10 USDC")
            return
        if amount > 1000:
            await update.message.reply_text("❌ Maximum deposit: 1000 USDC untuk safety")
            return
    except ValueError:
        await update.message.reply_text("❌ Amount harus berupa angka")
        return
    
    # Get user wallet
    wallet = get_user_wallet(user_id)
    
    # Send loading message
    loading_msg = await update.message.reply_text(
        "🤖 Memulai Auto Trade...\n"
        "AI sedang menganalisis market dan menyiapkan strategy...\n\n"
        "⏳ Mohon tunggu 30-60 detik..."
    )
    
    # Check Automaton status first
    status = automaton.check_automaton_status()
    if not status.get('online'):
        await loading_msg.edit_text(
            "❌ Automaton AI sedang offline!\n\n"
            "Silakan coba lagi nanti atau hubungi admin."
        )
        return
    
    # Start auto trade
    result = automaton.start_autotrade(
        user_id=user_id,
        amount=amount,
        wallet_address=wallet
    )
    
    if result['success']:
        # Save to database
        save_autotrade_user(user_id, amount, wallet)
        
        await loading_msg.edit_text(
            f"✅ Auto Trade Aktif!\n\n"
            f"💰 Deposit: {amount} USDC\n"
            f"🤖 AI Trader: Automaton\n"
            f"📊 Target: 5-10% per bulan\n"
            f"⚠️ Risk: Medium\n"
            f"💼 Wallet: {wallet[:10]}...{wallet[-8:]}\n\n"
            f"🎯 Strategy:\n{result['response'][:300]}...\n\n"
            f"Automaton akan mulai trading dalam beberapa menit.\n"
            f"Gunakan /autotrade_status untuk cek progress."
        )
    else:
        await loading_msg.edit_text(
            f"❌ Error memulai Auto Trade:\n{result['error']}\n\n"
            f"Silakan coba lagi atau hubungi admin."
        )

async def autotrade_status_handler(update, context):
    """Handler untuk /autotrade_status"""
    user_id = update.effective_user.id
    
    # Check if user has auto trade
    user_data = get_autotrade_user(user_id)
    if not user_data:
        await update.message.reply_text(
            "⚠️ Anda belum memiliki Auto Trade aktif.\n\n"
            "Gunakan /autotrade_start untuk memulai."
        )
        return
    
    loading_msg = await update.message.reply_text(
        "📊 Mengambil data portfolio...\n"
        "⏳ Mohon tunggu..."
    )
    
    # Get status from Automaton
    result = automaton.get_autotrade_status(user_id)
    
    if result['success']:
        # Parse response and format nicely
        await loading_msg.edit_text(
            f"📊 Auto Trade Status\n\n"
            f"{result['response']}\n\n"
            f"💸 Gunakan /autotrade_withdraw untuk withdraw profit\n"
            f"📈 Gunakan /autotrade_history untuk lihat trade history"
        )
    else:
        await loading_msg.edit_text(
            f"❌ Error mengambil status:\n{result['error']}\n\n"
            f"Silakan coba lagi nanti."
        )

async def autotrade_withdraw_handler(update, context):
    """Handler untuk /autotrade_withdraw"""
    user_id = update.effective_user.id
    
    # Check if user has auto trade
    user_data = get_autotrade_user(user_id)
    if not user_data or user_data[6] != 'active':  # status column
        await update.message.reply_text(
            "⚠️ Anda tidak memiliki Auto Trade aktif.\n\n"
            "Gunakan /autotrade_start untuk memulai."
        )
        return
    
    loading_msg = await update.message.reply_text(
        "💸 Memproses withdrawal...\n"
        "Closing positions dan calculating profit...\n\n"
        "⏳ Mohon tunggu 30-60 detik..."
    )
    
    # Process withdrawal
    result = automaton.withdraw_autotrade(user_id)
    
    if result['success']:
        # Update status to closed
        update_autotrade_status(user_id, 'closed')
        
        await loading_msg.edit_text(
            f"✅ Withdrawal Berhasil!\n\n"
            f"{result['response']}\n\n"
            f"Terima kasih telah menggunakan Auto Trade!\n"
            f"Gunakan /autotrade_start untuk memulai lagi."
        )
    else:
        await loading_msg.edit_text(
            f"❌ Error processing withdrawal:\n{result['error']}\n\n"
            f"Silakan coba lagi atau hubungi admin."
        )

async def autotrade_history_handler(update, context):
    """Handler untuk /autotrade_history"""
    user_id = update.effective_user.id
    
    # Check if user has auto trade
    user_data = get_autotrade_user(user_id)
    if not user_data:
        await update.message.reply_text(
            "⚠️ Anda belum memiliki Auto Trade.\n\n"
            "Gunakan /autotrade_start untuk memulai."
        )
        return
    
    loading_msg = await update.message.reply_text(
        "📜 Mengambil trade history...\n"
        "⏳ Mohon tunggu..."
    )
    
    # Get trade history
    result = automaton.get_trade_history(user_id, limit=10)
    
    if result['success']:
        await loading_msg.edit_text(
            f"📜 Trade History (Last 10)\n\n"
            f"{result['response']}"
        )
    else:
        await loading_msg.edit_text(
            f"❌ Error mengambil history:\n{result['error']}"
        )

# ============================================
# BOT HANDLERS - telebot (alternative)
# ============================================

def register_autotrade_handlers_telebot(bot):
    """Register handlers untuk telebot"""
    
    @bot.message_handler(commands=['autotrade_start'])
    def handle_autotrade_start(message):
        user_id = message.from_user.id
        
        # Similar logic as above but using telebot syntax
        if not is_premium_user(user_id):
            bot.reply_to(message, "⚠️ Auto Trade hanya untuk Premium Members!")
            return
        
        # ... rest of the logic
        
    @bot.message_handler(commands=['autotrade_status'])
    def handle_autotrade_status(message):
        # Similar logic as above
        pass
    
    @bot.message_handler(commands=['autotrade_withdraw'])
    def handle_autotrade_withdraw(message):
        # Similar logic as above
        pass

# ============================================
# MAIN - untuk testing
# ============================================

if __name__ == "__main__":
    print("Auto Trade Integration Example")
    print("=" * 50)
    print("\nFungsi yang tersedia:")
    print("1. autotrade_start_handler - Mulai auto trade")
    print("2. autotrade_status_handler - Cek status portfolio")
    print("3. autotrade_withdraw_handler - Withdraw profit")
    print("4. autotrade_history_handler - Lihat trade history")
    print("\nIntegrasikan handler ini ke bot V3 Anda.")
