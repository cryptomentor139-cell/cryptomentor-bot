"""
OpenClaw LangChain Handlers
Telegram bot handlers using LangChain agent
"""

import logging
from decimal import Decimal
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from app.openclaw_langchain_agent_simple import get_openclaw_agent
from app.openclaw_langchain_db import get_openclaw_db
from app.admin_auth import is_admin

logger = logging.getLogger(__name__)


async def openclaw_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle OpenClaw chat messages
    User just chats normally, agent handles everything
    """
    user_id = update.effective_user.id
    message = update.message.text
    
    try:
        # Get agent and database
        agent = get_openclaw_agent()
        db = get_openclaw_db()
        
        # Check credits
        credits = db.get_user_credits(user_id)
        
        if credits <= 0:
            await update.message.reply_text(
                "❌ <b>Insufficient Credits</b>\n\n"
                "You don't have enough credits to use OpenClaw.\n\n"
                "Please contact admin to add credits:\n"
                "/admin_add_credits\n\n"
                "Pricing: Rp 100,000 = $7 USD credits",
                parse_mode='HTML'
            )
            return
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Process with agent
        result = await agent.chat(
            user_id=user_id,
            message=message,
            deduct_credits=True
        )
        
        if result['success']:
            response = result['response']
            credits_used = result['credits_used']
            
            # Get new balance
            new_balance = db.get_user_credits(user_id)
            
            # Add balance footer
            footer = f"\n\n💰 Credits used: ${credits_used:.4f} | Balance: ${new_balance:.2f}"
            
            await update.message.reply_text(
                response + footer,
                parse_mode='HTML'
            )
        else:
            error_msg = result.get('error', 'Unknown error')
            await update.message.reply_text(
                f"❌ Error: {error_msg}\n\n"
                "Please try again or contact support."
            )
    
    except Exception as e:
        logger.error(f"Error in openclaw_chat_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ An error occurred while processing your request.\n"
            "Please try again later or contact support."
        )


async def openclaw_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_balance - Check credit balance
    """
    user_id = update.effective_user.id
    
    try:
        db = get_openclaw_db()
        credits = db.get_user_credits(user_id)
        
        message = (
            "💰 <b>Your OpenClaw Credits</b>\n\n"
            f"<b>Current Balance:</b> ${credits:.2f}\n\n"
        )
        
        if credits > 0:
            message += (
                "✅ You have credits!\n"
                "Just chat normally to use OpenClaw AI.\n\n"
                "Example questions:\n"
                "• What's the Bitcoin price?\n"
                "• Analyze Ethereum market\n"
                "• Give me crypto trading signals"
            )
        else:
            message += (
                "❌ No credits available.\n\n"
                "Contact admin to add credits:\n"
                "/admin_add_credits\n\n"
                "Pricing: Rp 100,000 = $7 USD credits"
            )
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    except Exception as e:
        logger.error(f"Error in openclaw_balance_command: {e}")
        await update.message.reply_text(
            f"❌ Error checking balance: {str(e)}"
        )


async def admin_add_credits_langchain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_add_credits <user_id> <amount> [reason]
    Admin command to add credits to user
    """
    user_id = update.effective_user.id
    
    # Check admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command")
        return
    
    # Parse arguments
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ <b>Usage:</b>\n"
            "<code>/admin_add_credits &lt;user_id&gt; &lt;amount&gt; [reason]</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/admin_add_credits 123456789 7 Payment Rp 100k</code>",
            parse_mode='HTML'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = Decimal(context.args[1])
        reason = ' '.join(context.args[2:]) if len(context.args) > 2 else 'Manual allocation'
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be positive")
            return
        
        # Add credits
        db = get_openclaw_db()
        result = db.add_credits(
            user_id=target_user_id,
            amount=amount,
            admin_id=user_id,
            reason=reason
        )
        
        if result['success']:
            # Send notification to user
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=(
                        "✅ <b>Credits Added!</b>\n\n"
                        f"💰 <b>Amount Added:</b> ${amount:.2f}\n"
                        f"💳 <b>Your Balance:</b> ${result['balance_after']:.2f}\n\n"
                        "Your OpenClaw credits have been successfully added!\n\n"
                        "You can now use OpenClaw AI Agent.\n"
                        "Just chat normally - no commands needed!\n\n"
                        "Check balance: /openclaw_balance\n\n"
                        "Thank you for your payment! 🎉"
                    ),
                    parse_mode='HTML'
                )
                notification_status = "✅ Notification sent"
            except Exception as send_error:
                notification_status = f"⚠️ Notification failed: {str(send_error)}"
            
            # Confirm to admin
            await update.message.reply_text(
                f"✅ <b>Credits Allocated Successfully!</b>\n\n"
                f"<b>User:</b> <code>{target_user_id}</code>\n"
                f"<b>Amount:</b> ${amount:.2f}\n"
                f"<b>Reason:</b> {reason}\n\n"
                f"<b>User Balance:</b>\n"
                f"• Before: ${result['balance_before']:.2f}\n"
                f"• After: ${result['balance_after']:.2f}\n\n"
                f"{notification_status}",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to add credits: {result.get('error', 'Unknown error')}"
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid arguments.\n"
            "User ID must be a number.\n"
            "Amount must be a number."
        )
    except Exception as e:
        logger.error(f"Error in admin_add_credits_langchain: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def admin_system_stats_langchain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_system_stats - View system statistics
    """
    user_id = update.effective_user.id
    
    # Check admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command")
        return
    
    try:
        db = get_openclaw_db()
        stats = db.get_system_stats()
        
        message = (
            "📊 <b>OpenClaw System Statistics</b>\n\n"
            f"<b>Total Users:</b> {stats['user_count']}\n"
            f"<b>Total Credits:</b> ${stats['total_credits']:.2f}\n"
            f"<b>Total Allocated:</b> ${stats['total_allocated']:.2f}\n"
            f"<b>Total Used:</b> ${stats['total_used']:.2f}\n\n"
            f"<b>Average per User:</b> ${stats['total_credits'] / max(stats['user_count'], 1):.2f}\n\n"
            "<b>🔗 Quick Actions:</b>\n"
            "• /admin_add_credits - Allocate to user\n"
            "• /openclaw_balance - Check user balance"
        )
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    except Exception as e:
        logger.error(f"Error in admin_system_stats_langchain: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def openclaw_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /openclaw_help - Show help message
    """
    message = (
        "🤖 <b>OpenClaw AI Agent</b>\n\n"
        "<b>What is OpenClaw?</b>\n"
        "Advanced AI crypto analyst powered by GPT-4.1\n\n"
        "<b>Features:</b>\n"
        "• Real-time crypto price data\n"
        "• Market analysis & insights\n"
        "• Trading signals\n"
        "• Technical analysis\n"
        "• 24/7 AI assistant\n\n"
        "<b>How to Use:</b>\n"
        "Just chat normally! No special commands needed.\n\n"
        "<b>Example Questions:</b>\n"
        "• What's the Bitcoin price?\n"
        "• Analyze Ethereum market trend\n"
        "• Give me crypto trading signals\n"
        "• What's my balance?\n\n"
        "<b>Commands:</b>\n"
        "• /openclaw_balance - Check your credits\n"
        "• /openclaw_help - Show this help\n\n"
        "<b>Pricing:</b>\n"
        "~$0.01-0.05 per message\n"
        "Rp 100,000 = $7 USD credits\n\n"
        "<b>Need Credits?</b>\n"
        "Contact admin to add credits"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')


def register_openclaw_langchain_handlers(application):
    """Register OpenClaw LangChain handlers"""
    
    # User commands
    application.add_handler(CommandHandler("openclaw_balance", openclaw_balance_command))
    application.add_handler(CommandHandler("openclaw_help", openclaw_help_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin_add_credits", admin_add_credits_langchain))
    application.add_handler(CommandHandler("admin_system_stats", admin_system_stats_langchain))
    
    # Chat handler (must be last - catches all text messages)
    # Only for users with credits
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            openclaw_chat_handler
        )
    )
    
    logger.info("OpenClaw LangChain handlers registered successfully")
