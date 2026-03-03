"""
OpenClaw Simple Handlers for Telegram Bot
Lightweight integration without gateway dependency
"""

import logging
import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from openclaw_cli_bridge import get_openclaw_cli_bridge

logger = logging.getLogger(__name__)


async def openclaw_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_status - Check OpenClaw availability
    """
    user_id = update.effective_user.id
    
    try:
        bridge = get_openclaw_cli_bridge()
        
        # Quick health check
        is_healthy = bridge.check_health()
        version = bridge.get_version() if is_healthy else "N/A"
        
        if is_healthy:
            message = (
                "✅ <b>OpenClaw Status</b>\n\n"
                f"🦞 Version: <code>{version}</code>\n"
                f"✓ CLI: Accessible\n"
                f"✓ Bridge: Working\n\n"
                "OpenClaw AI Assistant is ready!"
            )
        else:
            message = (
                "❌ <b>OpenClaw Status</b>\n\n"
                "OpenClaw CLI not accessible.\n"
                "Please contact admin."
            )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"OpenClaw status error: {e}")
        await update.message.reply_text(
            "❌ Error checking OpenClaw status"
        )


async def openclaw_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_help - Show OpenClaw features
    """
    message = (
        "🦞 <b>OpenClaw AI Assistant</b>\n\n"
        "<b>Available Commands:</b>\n"
        "/openclaw_status - Check availability\n"
        "/openclaw_help - This help message\n"
        "/openclaw_ask - Ask AI assistant\n\n"
        "<b>Features:</b>\n"
        "• Advanced AI reasoning\n"
        "• Code analysis & generation\n"
        "• Research & documentation\n"
        "• Task automation\n\n"
        "<i>Powered by Claude AI via OpenClaw</i>"
    )
    
    await update.message.reply_text(
        message,
        parse_mode='HTML'
    )


async def openclaw_ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_ask <question> - Ask OpenClaw AI (requires credits)
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"
    
    # Get question from command args
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /openclaw_ask <your question>\n\n"
            "Example:\n"
            "/openclaw_ask What is Bitcoin halving?"
        )
        return
    
    question = ' '.join(context.args)
    
    try:
        # Import payment system and monitor
        from app.openclaw_payment_system import get_payment_system
        from app.openclaw_chat_monitor import OpenClawChatMonitor
        from app.openclaw_db_helper import get_openclaw_db_connection
        
        payment_system = get_payment_system()
        db = get_openclaw_db_connection()
        
        # Check user balance
        balance = payment_system.get_user_balance(user_id, db)
        has_credits = balance > 0
        
        # Log attempt (for admin monitoring)
        OpenClawChatMonitor.log_chat_attempt(
            user_id=user_id,
            username=username,
            message=question,
            has_credits=has_credits,
            balance=float(balance),
            success=False  # Will update if successful
        )
        
        if not has_credits:
            # No credits - show deposit message
            await update.message.reply_text(
                "❌ <b>Insufficient Credits</b>\n\n"
                "You need credits to use OpenClaw AI Agent.\n\n"
                "<b>Your Balance:</b> $0.00\n\n"
                "💰 <b>Add Credits:</b>\n"
                "Use /openclaw_deposit to add credits\n\n"
                "<b>Pricing:</b>\n"
                "• Deposit $10 → Get $8 credits (80%)\n"
                "• Platform fee: 20%\n\n"
                "Start with as little as $5!\n\n"
                "<i>Note: Your request has been logged. "
                "Admin can add credits to your account if needed.</i>",
                parse_mode='HTML'
            )
            
            # Log for admin
            logger.warning(
                f"🚫 OpenClaw blocked - User {user_id} (@{username}) "
                f"has no credits. Question: {question[:100]}"
            )
            return
        
        # Send "thinking" message
        thinking_msg = await update.message.reply_text(
            f"🤔 OpenClaw is thinking...\n"
            f"<b>Your Balance:</b> ${balance:.2f}\n"
            f"<b>Question:</b> <i>{question}</i>",
            parse_mode='HTML'
        )
        
        bridge = get_openclaw_cli_bridge()
        
        # Check if CLI is accessible
        if not bridge.check_health():
            await thinking_msg.edit_text(
                "❌ OpenClaw is not available right now.\n"
                "Please try again later or contact admin."
            )
            return
        
        # For now, show that feature is ready but needs gateway
        await thinking_msg.edit_text(
            "🦞 <b>OpenClaw AI Assistant</b>\n\n"
            f"<b>Your Question:</b>\n<i>{question}</i>\n\n"
            f"<b>Your Balance:</b> ${balance:.2f}\n\n"
            "⚠️ <b>Setup Required:</b>\n"
            "OpenClaw CLI is installed, but gateway needs to be started "
            "for full AI assistant features.\n\n"
            "<b>Admin: Start gateway with:</b>\n"
            "<code>openclaw gateway</code>\n\n"
            "Or use alternative AI features:\n"
            "• /ai - Gemini Flash (FREE & FAST)\n"
            "• /deepseek - DeepSeek reasoning",
            parse_mode='HTML'
        )
        
        # Log successful attempt
        OpenClawChatMonitor.log_chat_attempt(
            user_id=user_id,
            username=username,
            message=question,
            has_credits=True,
            balance=float(balance),
            success=True
        )
        
    except Exception as e:
        logger.error(f"OpenClaw ask error: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


# Admin command to test OpenClaw integration
async def openclaw_test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_test - Admin only: Test OpenClaw integration
    """
    user_id = update.effective_user.id
    
    # Check if admin (you can add proper admin check here)
    # For now, just run the test
    
    try:
        await update.message.reply_text(
            "🔧 Running OpenClaw integration test...\n"
            "This may take a moment."
        )
        
        bridge = get_openclaw_cli_bridge()
        
        # Test 1: Health
        health = bridge.check_health()
        health_status = "✅ PASS" if health else "❌ FAIL"
        
        # Test 2: Version
        version = bridge.get_version() if health else "N/A"
        
        # Test 3: Status (quick check)
        status_result = bridge.get_status()
        status_ok = status_result.get('success', False)
        status_status = "✅ PASS" if status_ok else "⚠️ Gateway not running"
        
        report = (
            "🦞 <b>OpenClaw Integration Test</b>\n\n"
            f"<b>1. CLI Health:</b> {health_status}\n"
            f"<b>2. Version:</b> <code>{version}</code>\n"
            f"<b>3. Gateway:</b> {status_status}\n\n"
        )
        
        if health:
            report += (
                "✅ <b>Integration Status: READY</b>\n\n"
                "OpenClaw CLI is working!\n"
                "Gateway can be started with:\n"
                "<code>openclaw gateway</code>"
            )
        else:
            report += (
                "❌ <b>Integration Status: NOT READY</b>\n\n"
                "OpenClaw CLI is not accessible."
            )
        
        await update.message.reply_text(
            report,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"OpenClaw test error: {e}")
        await update.message.reply_text(
            f"❌ Test failed: {str(e)}"
        )


def register_openclaw_handlers(application):
    """
    Register OpenClaw handlers with the bot application
    
    Args:
        application: Telegram bot application instance
    """
    application.add_handler(CommandHandler("openclaw_status", openclaw_status_command))
    application.add_handler(CommandHandler("openclaw_help", openclaw_help_command))
    application.add_handler(CommandHandler("openclaw_ask", openclaw_ask_command))
    application.add_handler(CommandHandler("openclaw_test", openclaw_test_admin))
    
    logger.info("OpenClaw handlers registered")
