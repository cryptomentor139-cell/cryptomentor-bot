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
    /openclaw_deposit or /deposit - Add credits to OpenClaw
    """
    user_id = update.effective_user.id
    
    message = (
        "💰 <b>OpenClaw Credits Top-Up</b>\n\n"
        "Add credits to use OpenClaw AI Agent!\n\n"
        "<b>How it works:</b>\n"
        "1. Choose deposit amount below\n"
        "2. Get wallet address for payment\n"
        "3. Send crypto (USDT/USDC/BNB on BEP20)\n"
        "4. Send proof to admin @BillFarr\n"
        "5. Credits added after verification\n\n"
        "<b>💡 Important:</b>\n"
        "• Your credits = Your OpenRouter API balance\n"
        "• Real-time sync with OpenRouter\n"
        "• No internal credit system\n"
        "• Admin manually adds to your OpenRouter account\n\n"
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
    /openclaw_balance - Check your personal OpenClaw credit balance
    """
    user_id = update.effective_user.id
    
    try:
        # Check if user is admin (gets free access)
        from app.admin_auth import is_admin
        from services import get_database
        db = get_database()
        
        # Check admin status
        if is_admin(user_id):
            message = (
                "💳 <b>Your OpenClaw Balance</b>\n\n"
                "👑 <b>Admin Account</b>\n"
                "You have unlimited free access!\n\n"
                "No credits needed for your account.\n\n"
                "📊 Check system status: /admin_system_status"
            )
            
            await update.message.reply_text(
                message,
                parse_mode='HTML'
            )
            return
        
        # Get user's personal credit balance
        from app.openclaw_user_credits import get_user_credits
        from decimal import Decimal
        
        user_credits = get_user_credits(db, user_id)
        
        # Get usage stats
        cursor = db.cursor  # Property, not method
        cursor.execute("""
            SELECT 
                COALESCE(SUM(credits_used), 0) as total_used,
                COUNT(*) as message_count
            FROM openclaw_credit_usage
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        total_used = Decimal(str(result[0])) if result else Decimal('0')
        message_count = result[1] if result else 0
        
        cursor.close()
        
        # Calculate average cost per message
        avg_cost = total_used / message_count if message_count > 0 else Decimal('0')
        
        message = (
            f"💳 <b>Your OpenClaw Balance</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"💰 <b>Available Credits:</b> ${float(user_credits):.2f}\n\n"
            f"<b>📊 Usage Stats:</b>\n"
            f"• Total Used: ${float(total_used):.2f}\n"
            f"• Messages Sent: {message_count}\n"
            f"• Avg Cost/Message: ${float(avg_cost):.4f}\n\n"
        )
        
        if user_credits < Decimal('1.00'):
            message += (
                "⚠️ <b>Low balance!</b>\n"
                "Consider topping up to continue using OpenClaw.\n\n"
            )
        elif user_credits < Decimal('5.00'):
            message += "⚡ Balance getting low. Consider topping up soon.\n\n"
        else:
            message += "✅ Balance is healthy.\n\n"
        
        message += (
            "<b>💰 Top-Up Credits:</b>\n"
            "Use /subscribe to see payment options\n\n"
            "<b>📞 Need Help?</b>\n"
            "Contact admin: @BillFarr"
        )
        
        keyboard = [
            [InlineKeyboardButton("💰 Top-Up Credits", callback_data="deposit_start")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            "❌ Error checking balance. Please try again or contact admin: @BillFarr"
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
            "Use /deposit or /openclaw_deposit to start deposit process"
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
    
    # Handle balance check from /subscribe
    if data == "balance_check":
        # Redirect to balance command
        from app.handlers_openclaw_deposit import openclaw_balance_command
        # Create fake update for command
        await openclaw_balance_command(update, context)
        return
    
    # Handle preset amounts - SIMPLIFIED
    if data.startswith("deposit_"):
        amount_str = data.replace("deposit_", "")
        try:
            amount = Decimal(amount_str)
            
            # Get wallet address (same as /subscribe)
            admin_wallet = os.getenv('ADMIN_WALLET_ADDRESS', '0xed7342ac9c22b1495af4d63f15a7c9768a028ea8')
            
            # Simple payment instructions (like /subscribe)
            message = (
                f"💰 <b>OpenClaw Credits Top-Up</b>\n\n"
                f"<b>Amount:</b> ${amount:.2f}\n\n"
                f"<b>⛓️ Payment via Crypto (BEP20)</b>\n"
                f"Network: <b>BEP20</b> (Binance Smart Chain)\n\n"
                f"<b>Wallet Address:</b>\n"
                f"<code>{admin_wallet}</code>\n\n"
                f"<b>Supported Coins:</b>\n"
                f"• USDT (BEP20)\n"
                f"• USDC (BEP20)\n"
                f"• BNB\n\n"
                f"<b>⚠️ Important:</b>\n"
                f"1. Send EXACTLY ${amount:.2f} worth of crypto\n"
                f"2. Use BEP20 network ONLY!\n"
                f"3. Send payment proof to admin\n\n"
                f"<b>📱 Contact Admin:</b>\n"
                f"👉 @BillFarr\n\n"
                f"<b>Include in your message:</b>\n"
                f"✅ Transaction hash/screenshot\n"
                f"✅ Amount: ${amount:.2f}\n"
                f"✅ Your User ID: <code>{user_id}</code>\n"
                f"✅ Purpose: OpenClaw Credits\n\n"
                f"💡 <b>Note:</b> Credits will be added to your account after admin verification.\n\n"
                f"Your credits balance reflects your OpenRouter API balance in real-time!"
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
            
        except Exception as e:
            logger.error(f"Error processing deposit: {e}")
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                "❌ <b>Error Processing Request</b>\n\n"
                "Please try again or contact admin: @BillFarr",
                parse_mode='HTML'
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
        
        # Get admin wallet with fallback
        admin_wallet = os.getenv('ADMIN_WALLET_ADDRESS')
        
        if not admin_wallet:
            # Fallback wallet address if env var not set
            admin_wallet = '0xed7342ac9c22b1495af4d63f15a7c9768a028ea8'
            logger.warning("ADMIN_WALLET_ADDRESS not set in environment, using fallback")
        
        # Validate wallet address format
        if not admin_wallet or len(admin_wallet) < 20:
            await query.edit_message_text(
                "❌ <b>Configuration Error</b>\n\n"
                "Deposit wallet address not configured.\n"
                "Please contact admin: @BillFarr",
                parse_mode='HTML'
            )
            return
        
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
        try:
            db = get_openclaw_db_connection()
            cursor = db.cursor  # Property, not method
            cursor.execute("""
                INSERT INTO openclaw_pending_deposits (
                    user_id, deposit_wallet, amount, expires_at
                ) VALUES (?, ?, ?, NOW() + INTERVAL '24 hours')
            """, (user_id, admin_wallet, float(amount)))
            db.commit()
            cursor.close()
        except Exception as db_error:
            logger.error(f"Error storing pending deposit: {db_error}")
            # Continue anyway - user can still contact admin
        
    except Exception as e:
        logger.error(f"Error processing deposit request: {e}")
        import traceback
        traceback.print_exc()
        await query.edit_message_text(
            "❌ <b>Error Processing Request</b>\n\n"
            "Please try again or contact admin: @BillFarr",
            parse_mode='HTML'
        )


async def openclaw_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_history - View transaction history
    """
    user_id = update.effective_user.id
    
    try:
        db = get_openclaw_db_connection()
        cursor = db.cursor  # Property, not method
        
        # Get recent transactions
        cursor.execute("""
            SELECT transaction_hash, amount, user_credits, platform_fee, created_at
            FROM openclaw_transactions
            WHERE user_id = ? AND status = 'completed'
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
    application.add_handler(CommandHandler("deposit", openclaw_deposit_command))  # Alias for easier access
    application.add_handler(CommandHandler("openclaw_balance", openclaw_balance_command))
    application.add_handler(CommandHandler("openclaw_history", openclaw_history_command))
    application.add_handler(CallbackQueryHandler(deposit_callback_handler, pattern=r'^deposit_'))
    application.add_handler(CallbackQueryHandler(deposit_callback_handler, pattern=r'^balance_'))
    application.add_handler(CallbackQueryHandler(deposit_callback_handler, pattern=r'^confirm_deposit_'))
    
    logger.info("OpenClaw deposit handlers registered (including /deposit alias)")

