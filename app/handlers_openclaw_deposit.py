"""
OpenClaw Deposit Handlers
Telegram commands for deposit and credit management
"""

import os
import logging
from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from app.openclaw_payment_system import get_payment_system
from app.openclaw_db_helper import get_openclaw_db_connection

logger = logging.getLogger(__name__)


async def openclaw_deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_deposit - Start deposit process
    """
    user_id = update.effective_user.id
    
    message = (
        "💰 <b>OpenClaw Credits Deposit</b>\n\n"
        "Add credits to use OpenClaw AI Agent!\n\n"
        "<b>How it works:</b>\n"
        "1. Choose deposit amount\n"
        "2. Get unique wallet address\n"
        "3. Send crypto (USDT/USDC/BTC/ETH)\n"
        "4. Credits added automatically\n\n"
        "<b>Pricing:</b>\n"
        "• You receive: 80% in credits\n"
        "• Platform fee: 20%\n\n"
        "<b>Example:</b>\n"
        "Deposit $10 → You get $8 credits\n\n"
        "Choose amount:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("$5", callback_data="deposit_5"),
            InlineKeyboardButton("$10", callback_data="deposit_10"),
            InlineKeyboardButton("$20", callback_data="deposit_20")
        ],
        [
            InlineKeyboardButton("$50", callback_data="deposit_50"),
            InlineKeyboardButton("$100", callback_data="deposit_100"),
            InlineKeyboardButton("Custom", callback_data="deposit_custom")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="deposit_cancel")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def openclaw_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_balance - Check credit balance
    """
    user_id = update.effective_user.id
    
    try:
        payment_system = get_payment_system()
        db = get_openclaw_db_connection()
        
        balance = payment_system.get_user_balance(user_id, db)
        
        # Get transaction history
        cursor = db.cursor()
        cursor.execute("""
            SELECT COUNT(*), SUM(user_credits)
            FROM openclaw_transactions
            WHERE user_id = %s AND status = 'completed'
        """, (user_id,))
        
        tx_result = cursor.fetchone()
        tx_count = tx_result[0] if tx_result else 0
        total_deposited = tx_result[1] if tx_result and tx_result[1] else 0
        
        # Get usage stats
        cursor.execute("""
            SELECT COUNT(*), SUM(amount)
            FROM openclaw_usage_log
            WHERE user_id = %s
        """, (user_id,))
        
        usage_result = cursor.fetchone()
        usage_count = usage_result[0] if usage_result else 0
        total_spent = usage_result[1] if usage_result and usage_result[1] else 0
        
        message = (
            f"💳 <b>Your OpenClaw Balance</b>\n\n"
            f"<b>Current Balance:</b> ${balance:.2f}\n\n"
            f"<b>Statistics:</b>\n"
            f"• Total Deposited: ${total_deposited:.2f}\n"
            f"• Total Spent: ${total_spent:.2f}\n"
            f"• Deposits: {tx_count}\n"
            f"• Usage Count: {usage_count}\n\n"
        )
        
        if balance < Decimal('1.00'):
            message += "⚠️ Low balance! Consider depositing more credits."
        
        keyboard = [
            [InlineKeyboardButton("💰 Deposit", callback_data="deposit_start")],
            [InlineKeyboardButton("📊 History", callback_data="balance_history")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        await update.message.reply_text(
            "❌ Error checking balance. Please try again."
        )


async def deposit_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "deposit_cancel":
        await query.edit_message_text("❌ Deposit cancelled.")
        return
    
    if data == "deposit_start":
        # Redirect to deposit command
        await query.edit_message_text(
            "Use /openclaw_deposit to start deposit process"
        )
        return
    
    if data == "deposit_custom":
        await query.edit_message_text(
            "💰 <b>Custom Deposit Amount</b>\n\n"
            "Send the amount you want to deposit:\n"
            "Example: <code>25</code> for $25\n\n"
            "Minimum: $5\n"
            "Maximum: $1000",
            parse_mode='HTML'
        )
        # Set state for custom amount
        context.user_data['awaiting_deposit_amount'] = True
        return
    
    # Handle preset amounts
    if data.startswith("deposit_"):
        amount_str = data.replace("deposit_", "")
        try:
            amount = Decimal(amount_str)
            await process_deposit_request(query, user_id, amount)
        except Exception as e:
            logger.error(f"Error processing deposit: {e}")
            await query.edit_message_text(
                "❌ Error processing deposit. Please try again."
            )


async def process_deposit_request(query, user_id: int, amount: Decimal):
    """Process deposit request and show payment info"""
    try:
        payment_system = get_payment_system()
        
        # Validate amount
        is_valid, error = payment_system.validate_deposit(amount)
        if not is_valid:
            await query.edit_message_text(f"❌ {error}")
            return
        
        # Calculate split
        split = payment_system.calculate_split(amount)
        
        # Get admin wallet
        admin_wallet = os.getenv('ADMIN_WALLET_ADDRESS', '0xed7342ac9c22b1495af4d63f15a7c9768a028ea8')
        
        message = (
            f"💰 <b>OpenClaw Credits Deposit</b>\n\n"
            f"<b>Amount:</b> ${amount:.2f}\n\n"
            f"<b>💳 Payment Breakdown:</b>\n"
            f"• Your Credits: ${split['user_credits']:.2f} (80%)\n"
            f"• Platform Fee: ${split['platform_fee']:.2f} (20%)\n\n"
            f"<b>⛓️ Crypto Payment (BEP20)</b>\n"
            f"Network: <b>BEP20</b> (Binance Smart Chain)\n\n"
            f"<b>Wallet Address:</b>\n"
            f"<code>{admin_wallet}</code>\n\n"
            f"<b>Supported Coins:</b>\n"
            f"• USDT (BEP20)\n"
            f"• USDC (BEP20)\n"
            f"• BNB\n\n"
            f"<b>⚠️ Important:</b>\n"
            f"1. Send EXACTLY ${amount:.2f} worth\n"
            f"2. Use BEP20 network only!\n"
            f"3. Send proof to admin after payment\n\n"
            f"<b>📱 Contact Admin:</b>\n"
            f"👉 @BillFarr\n\n"
            f"<b>Include in message:</b>\n"
            f"✅ Transaction hash\n"
            f"✅ Amount: ${amount:.2f}\n"
            f"✅ Your UID: <code>{user_id}</code>\n"
            f"✅ Purpose: OpenClaw Credits\n\n"
            f"Credits will be added after admin confirmation!"
        )
        
        keyboard = [
            [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/BillFarr")],
            [InlineKeyboardButton("❌ Cancel", callback_data="deposit_cancel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Store pending deposit in database
        db = get_openclaw_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO openclaw_pending_deposits (
                user_id, deposit_wallet, amount, expires_at
            ) VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')
        """, (user_id, admin_wallet, float(amount)))
        db.commit()
        
    except Exception as e:
        logger.error(f"Error processing deposit request: {e}")
        await query.edit_message_text(
            "❌ Error processing request. Please try again."
        )


async def openclaw_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_history - View transaction history
    """
    user_id = update.effective_user.id
    
    try:
        db = get_openclaw_db_connection()
        cursor = db.cursor()
        
        # Get recent transactions
        cursor.execute("""
            SELECT transaction_hash, amount, user_credits, platform_fee, created_at
            FROM openclaw_transactions
            WHERE user_id = %s AND status = 'completed'
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        
        transactions = cursor.fetchall()
        
        if not transactions:
            await update.message.reply_text(
                "📊 No transaction history yet.\n\n"
                "Use /openclaw_deposit to add credits!"
            )
            return
        
        message = "📊 <b>Transaction History</b>\n\n"
        
        for tx in transactions:
            tx_hash, amount, credits, fee, created_at = tx
            short_hash = f"{tx_hash[:8]}...{tx_hash[-6:]}"
            date = created_at.strftime("%Y-%m-%d %H:%M")
            
            message += (
                f"<b>{date}</b>\n"
                f"• Amount: ${amount:.2f}\n"
                f"• Credits: ${credits:.2f}\n"
                f"• Fee: ${fee:.2f}\n"
                f"• TX: <code>{short_hash}</code>\n\n"
            )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        await update.message.reply_text(
            "❌ Error fetching history. Please try again."
        )


def register_openclaw_deposit_handlers(application):
    """Register deposit handlers with the bot application"""
    application.add_handler(CommandHandler("openclaw_deposit", openclaw_deposit_command))
    application.add_handler(CommandHandler("openclaw_balance", openclaw_balance_command))
    application.add_handler(CommandHandler("openclaw_history", openclaw_history_command))
    application.add_handler(CallbackQueryHandler(deposit_callback_handler, pattern=r'^deposit_'))
    application.add_handler(CallbackQueryHandler(deposit_callback_handler, pattern=r'^balance_'))
    application.add_handler(CallbackQueryHandler(deposit_callback_handler, pattern=r'^confirm_deposit_'))
    
    logger.info("OpenClaw deposit handlers registered")
