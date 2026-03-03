"""
OpenClaw Admin Handlers
Admin commands for credit management and monitoring
"""

import os
import logging
from decimal import Decimal
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.openclaw_payment_system import get_payment_system
from app.openclaw_db_helper import get_openclaw_db_connection

logger = logging.getLogger(__name__)

# Admin IDs from environment
ADMIN_IDS = set()
for key in ['ADMIN1', 'ADMIN2', 'ADMIN3']:
    admin_id = os.getenv(key)
    if admin_id and admin_id.isdigit():
        ADMIN_IDS.add(int(admin_id))


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


async def openclaw_add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_add_credits <user_id> <amount> - Admin: Add credits to user
    
    Example:
    /openclaw_add_credits 123456789 10.00
    """
    user_id = update.effective_user.id
    
    # Check admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command")
        return
    
    # Parse arguments
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Usage: /openclaw_add_credits <user_id> <amount>\n\n"
            "Example:\n"
            "/openclaw_add_credits 123456789 10.00"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = Decimal(context.args[1])
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be positive")
            return
        
        # Add credits
        payment_system = get_payment_system()
        db = get_openclaw_db_connection()
        
        result = payment_system._add_user_credits(
            user_id=target_user_id,
            amount=amount,
            db_connection=db
        )
        
        if result['success']:
            await update.message.reply_text(
                f"✅ <b>Credits Added</b>\n\n"
                f"<b>User ID:</b> <code>{target_user_id}</code>\n"
                f"<b>Amount:</b> ${amount:.2f}\n"
                f"<b>New Balance:</b> ${result['new_balance']:.2f}\n\n"
                f"User can now use OpenClaw!",
                parse_mode='HTML'
            )
            
            logger.info(f"Admin {user_id} added ${amount} credits to user {target_user_id}")
        else:
            await update.message.reply_text(
                f"❌ Error: {result.get('error', 'Unknown error')}"
            )
            
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format. Use:\n"
            "/openclaw_add_credits <user_id> <amount>"
        )
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def openclaw_check_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_check_user <user_id> - Admin: Check user balance and stats
    
    Example:
    /openclaw_check_user 123456789
    """
    user_id = update.effective_user.id
    
    # Check admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command")
        return
    
    # Parse arguments
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Usage: /openclaw_check_user <user_id>\n\n"
            "Example:\n"
            "/openclaw_check_user 123456789"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        
        payment_system = get_payment_system()
        db = get_openclaw_db_connection()
        
        # Get balance
        balance = payment_system.get_user_balance(target_user_id, db)
        
        # Get transaction stats
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as tx_count,
                COALESCE(SUM(user_credits), 0) as total_deposited
            FROM openclaw_transactions
            WHERE user_id = %s AND status = 'completed'
        """, (target_user_id,))
        
        tx_result = cursor.fetchone()
        tx_count = tx_result[0] if tx_result else 0
        total_deposited = tx_result[1] if tx_result else 0
        
        # Get usage stats
        cursor.execute("""
            SELECT 
                COUNT(*) as usage_count,
                COALESCE(SUM(amount), 0) as total_spent
            FROM openclaw_usage_log
            WHERE user_id = %s
        """, (target_user_id,))
        
        usage_result = cursor.fetchone()
        usage_count = usage_result[0] if usage_result else 0
        total_spent = usage_result[1] if usage_result else 0
        
        # Get recent activity
        cursor.execute("""
            SELECT reason, amount, created_at
            FROM openclaw_usage_log
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (target_user_id,))
        
        recent_usage = cursor.fetchall()
        
        message = (
            f"👤 <b>User OpenClaw Stats</b>\n\n"
            f"<b>User ID:</b> <code>{target_user_id}</code>\n\n"
            f"<b>💰 Balance:</b> ${balance:.2f}\n\n"
            f"<b>📊 Statistics:</b>\n"
            f"• Total Deposited: ${total_deposited:.2f}\n"
            f"• Total Spent: ${total_spent:.2f}\n"
            f"• Deposits: {tx_count}\n"
            f"• Usage Count: {usage_count}\n\n"
        )
        
        if recent_usage:
            message += "<b>📝 Recent Activity:</b>\n"
            for reason, amount, created_at in recent_usage:
                date = created_at.strftime("%Y-%m-%d %H:%M")
                message += f"• {date}: ${amount:.2f} - {reason}\n"
        else:
            message += "<i>No usage history</i>"
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        logger.error(f"Error checking user: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def openclaw_list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_list_users - Admin: List all users with credits
    """
    user_id = update.effective_user.id
    
    # Check admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command")
        return
    
    try:
        db = get_openclaw_db_connection()
        cursor = db.cursor()
        
        # Get all users with credits
        cursor.execute("""
            SELECT 
                user_id,
                credits,
                total_deposited,
                total_spent,
                updated_at
            FROM openclaw_credits
            ORDER BY credits DESC
            LIMIT 20
        """)
        
        users = cursor.fetchall()
        
        if not users:
            await update.message.reply_text(
                "📊 No users with OpenClaw credits yet"
            )
            return
        
        message = "📊 <b>OpenClaw Users (Top 20)</b>\n\n"
        
        for user_id, credits, deposited, spent, updated_at in users:
            date = updated_at.strftime("%Y-%m-%d")
            message += (
                f"<b>UID:</b> <code>{user_id}</code>\n"
                f"• Balance: ${credits:.2f}\n"
                f"• Deposited: ${deposited:.2f}\n"
                f"• Spent: ${spent:.2f}\n"
                f"• Updated: {date}\n\n"
            )
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def openclaw_monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_monitor - Admin: Show monitoring dashboard
    """
    user_id = update.effective_user.id
    
    # Check admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command")
        return
    
    try:
        db = get_openclaw_db_connection()
        cursor = db.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM openclaw_credits")
        total_users = cursor.fetchone()[0]
        
        # Total credits in system
        cursor.execute("SELECT COALESCE(SUM(credits), 0) FROM openclaw_credits")
        total_credits = cursor.fetchone()[0]
        
        # Total deposited
        cursor.execute("""
            SELECT COALESCE(SUM(user_credits), 0)
            FROM openclaw_transactions
            WHERE status = 'completed'
        """)
        total_deposited = cursor.fetchone()[0]
        
        # Total platform fees
        cursor.execute("""
            SELECT COALESCE(SUM(platform_fee), 0)
            FROM openclaw_transactions
            WHERE status = 'completed'
        """)
        total_fees = cursor.fetchone()[0]
        
        # Total spent
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM openclaw_usage_log")
        total_spent = cursor.fetchone()[0]
        
        # Pending deposits
        cursor.execute("""
            SELECT COUNT(*)
            FROM openclaw_pending_deposits
            WHERE status = 'pending' AND expires_at > NOW()
        """)
        pending_count = cursor.fetchone()[0]
        
        # Recent activity (last 24h)
        cursor.execute("""
            SELECT COUNT(*)
            FROM openclaw_usage_log
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        recent_activity = cursor.fetchone()[0]
        
        message = (
            "📊 <b>OpenClaw Monitoring Dashboard</b>\n\n"
            f"<b>👥 Users:</b> {total_users}\n"
            f"<b>💰 Total Credits:</b> ${total_credits:.2f}\n\n"
            f"<b>📈 Revenue:</b>\n"
            f"• Total Deposited: ${total_deposited:.2f}\n"
            f"• Platform Fees (20%): ${total_fees:.2f}\n"
            f"• Total Spent: ${total_spent:.2f}\n\n"
            f"<b>⏳ Pending:</b> {pending_count} deposits\n"
            f"<b>🔥 Activity (24h):</b> {recent_activity} uses\n\n"
            f"<b>Admin Commands:</b>\n"
            f"/openclaw_add_credits - Add credits\n"
            f"/openclaw_check_user - Check user\n"
            f"/openclaw_list_users - List users\n"
            f"/openclaw_monitor - This dashboard"
        )
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error showing monitor: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


def register_openclaw_admin_handlers(application):
    """Register admin handlers with the bot application"""
    application.add_handler(CommandHandler("openclaw_add_credits", openclaw_add_credits_command))
    application.add_handler(CommandHandler("openclaw_check_user", openclaw_check_user_command))
    application.add_handler(CommandHandler("openclaw_list_users", openclaw_list_users_command))
    application.add_handler(CommandHandler("openclaw_monitor", openclaw_monitor_command))
    
    logger.info("OpenClaw admin handlers registered")
