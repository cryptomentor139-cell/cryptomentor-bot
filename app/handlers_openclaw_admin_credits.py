"""
OpenClaw Admin Credit Management
Commands for admin to manage user credits and view OpenRouter balance
"""

import os
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

logger = logging.getLogger(__name__)


async def admin_openclaw_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_openclaw_balance - Check OpenRouter API balance (Admin only)
    Shows real-time balance from OpenRouter
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip().isdigit()]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Admin only command.")
        return
    
    try:
        api_key = os.getenv('OPENCLAW_API_KEY')
        
        if not api_key:
            await update.message.reply_text(
                "❌ OPENCLAW_API_KEY not configured in environment variables."
            )
            return
        
        # Fetch real-time balance from OpenRouter
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                key_data = data.get('data', {})
                
                balance = key_data.get('limit_remaining', 0)
                limit = key_data.get('limit', 0)
                usage = key_data.get('usage', 0)
                label = key_data.get('label', 'N/A')
                is_free_tier = key_data.get('is_free_tier', False)
                rate_limit = key_data.get('rate_limit', {})
                
                # Calculate percentage
                usage_percent = (usage / limit * 100) if limit > 0 else 0
                
                message = (
                    "🔑 <b>OpenRouter API Status</b>\n\n"
                    f"<b>Account:</b> {label}\n"
                    f"<b>Tier:</b> {'Free' if is_free_tier else 'Paid'}\n\n"
                    f"<b>💰 Balance:</b>\n"
                    f"• Available: <b>${balance:.2f}</b>\n"
                    f"• Total Limit: ${limit:.2f}\n"
                    f"• Used: ${usage:.2f} ({usage_percent:.1f}%)\n\n"
                    f"<b>📊 Rate Limits:</b>\n"
                    f"• Requests: {rate_limit.get('requests', 'N/A')}\n"
                    f"• Interval: {rate_limit.get('interval', 'N/A')}\n\n"
                )
                
                # Warning if low balance
                if balance < 5.00:
                    message += "⚠️ <b>LOW BALANCE!</b> Consider adding more credits.\n\n"
                elif balance < 10.00:
                    message += "⚡ Balance getting low. Monitor usage.\n\n"
                else:
                    message += "✅ Balance is healthy.\n\n"
                
                message += (
                    "<b>🔗 Quick Links:</b>\n"
                    "• <a href='https://openrouter.ai/settings/keys'>Manage Keys</a>\n"
                    "• <a href='https://openrouter.ai/settings/billing'>Add Credits</a>\n"
                    "• <a href='https://openrouter.ai/activity'>View Activity</a>"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data="admin_refresh_balance")],
                    [InlineKeyboardButton("💰 Add Credits (Web)", url="https://openrouter.ai/settings/billing")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    message,
                    parse_mode='HTML',
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            else:
                await update.message.reply_text(
                    f"❌ Failed to fetch balance from OpenRouter.\n"
                    f"Status: {response.status_code}\n"
                    f"Response: {response.text[:200]}"
                )
    
    except Exception as e:
        logger.error(f"Error fetching OpenRouter balance: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n\n"
            "Check logs for details."
        )


async def admin_notify_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_notify_credits <user_id> <amount>
    Notify user that credits have been added
    
    Example: /admin_notify_credits 123456789 10
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip().isdigit()]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Admin only command.")
        return
    
    # Parse arguments
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ <b>Usage:</b>\n"
            "<code>/admin_notify_credits &lt;user_id&gt; &lt;amount&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/admin_notify_credits 123456789 10</code>\n\n"
            "This will notify user 123456789 that $10 credits have been added.",
            parse_mode='HTML'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = float(context.args[1])
        
        # Fetch current OpenRouter balance
        api_key = os.getenv('OPENCLAW_API_KEY')
        current_balance = 0
        
        if api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://openrouter.ai/api/v1/auth/key",
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        current_balance = data.get('data', {}).get('limit_remaining', 0)
            except:
                pass
        
        # Send notification to user
        notification_message = (
            "✅ <b>Credits Added!</b>\n\n"
            f"💰 <b>Amount Added:</b> ${amount:.2f}\n"
            f"💳 <b>Current Balance:</b> ${current_balance:.2f}\n\n"
            "Your OpenClaw credits have been successfully added!\n\n"
            "You can now use OpenClaw AI Agent.\n"
            "Check your balance: /openclaw_balance\n\n"
            "Thank you for your payment! 🎉"
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=notification_message,
                parse_mode='HTML'
            )
            
            # Confirm to admin
            await update.message.reply_text(
                f"✅ <b>Notification Sent!</b>\n\n"
                f"User ID: <code>{target_user_id}</code>\n"
                f"Amount: ${amount:.2f}\n"
                f"Current Balance: ${current_balance:.2f}\n\n"
                "User has been notified.",
                parse_mode='HTML'
            )
            
        except Exception as send_error:
            await update.message.reply_text(
                f"❌ Failed to send notification to user {target_user_id}\n"
                f"Error: {str(send_error)}\n\n"
                "User may have blocked the bot or deleted their account."
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid arguments.\n"
            "User ID must be a number.\n"
            "Amount must be a number."
        )
    except Exception as e:
        logger.error(f"Error in admin_notify_credits: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def admin_openclaw_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_openclaw_help - Show admin commands for OpenClaw
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip().isdigit()]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Admin only command.")
        return
    
    message = (
        "🔧 <b>OpenClaw Admin Commands</b>\n\n"
        "<b>Balance Management:</b>\n"
        "• <code>/admin_openclaw_balance</code>\n"
        "  Check OpenRouter API balance (real-time)\n\n"
        "• <code>/admin_notify_credits &lt;user_id&gt; &lt;amount&gt;</code>\n"
        "  Notify user that credits have been added\n"
        "  Example: <code>/admin_notify_credits 123456789 10</code>\n\n"
        "<b>Workflow:</b>\n"
        "1. User sends payment proof\n"
        "2. Verify payment on BSCScan\n"
        "3. Add credits to OpenRouter (via web)\n"
        "4. Use /admin_notify_credits to notify user\n"
        "5. User checks /openclaw_balance\n\n"
        "<b>Quick Links:</b>\n"
        "• <a href='https://openrouter.ai/settings/billing'>Add Credits to OpenRouter</a>\n"
        "• <a href='https://openrouter.ai/activity'>View API Activity</a>\n"
        "• <a href='https://bscscan.com/'>Verify Payments (BSCScan)</a>"
    )
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


def register_openclaw_admin_credit_handlers(application):
    """Register admin credit management handlers"""
    application.add_handler(CommandHandler("admin_openclaw_balance", admin_openclaw_balance_command))
    application.add_handler(CommandHandler("admin_notify_credits", admin_notify_credits_command))
    application.add_handler(CommandHandler("admin_openclaw_help", admin_openclaw_help_command))
    
    logger.info("OpenClaw admin credit handlers registered")
