"""
OpenClaw Admin Credit Management
Commands for admin to manage user credits and view OpenRouter balance
"""

import os
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from app.admin_auth import is_admin

logger = logging.getLogger(__name__)


async def admin_openclaw_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_openclaw_balance - Check OpenRouter API balance (Admin only)
    Shows real-time balance from OpenRouter
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
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


async def admin_add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_add_credits <user_id> <amount> [reason]
    Allocate credits to specific user from OpenRouter balance
    
    Example: /admin_add_credits 123456789 7 "Payment Rp 100k"
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command.")
        return
    
    # Parse arguments
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ <b>Usage:</b>\n"
            "<code>/admin_add_credits &lt;user_id&gt; &lt;amount&gt; [reason]</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/admin_add_credits 123456789 7 Payment Rp 100k</code>\n\n"
            "This will allocate $7 credits to user 123456789.\n\n"
            "<b>⚠️ IMPORTANT:</b>\n"
            "• Credits are allocated from OpenRouter balance\n"
            "• Total allocated cannot exceed OpenRouter balance\n"
            "• System will check before allocation",
            parse_mode='HTML'
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = float(context.args[1])
        reason = ' '.join(context.args[2:]) if len(context.args) > 2 else 'Manual allocation'
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be positive.")
            return
        
        # Fetch current OpenRouter balance
        api_key = os.getenv('OPENCLAW_API_KEY')
        
        if not api_key:
            await update.message.reply_text(
                "❌ OPENCLAW_API_KEY not configured in environment variables."
            )
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                await update.message.reply_text(
                    f"❌ Failed to fetch OpenRouter balance.\n"
                    f"Status: {response.status_code}"
                )
                return
            
            data = response.json()
            openrouter_balance = data.get('data', {}).get('limit_remaining', 0)
        
        # Get database connection
        from services import get_database
        db = get_database()
        cursor = db.cursor  # cursor is a property, not a method
        
        # Calculate total currently allocated to all users
        cursor.execute("""
            SELECT COALESCE(SUM(credits), 0) as total_allocated
            FROM openclaw_user_credits
        """)
        result = cursor.fetchone()
        total_allocated = float(result[0]) if result else 0
        
        # Check if allocation would exceed OpenRouter balance
        new_total_allocated = total_allocated + amount
        
        if new_total_allocated > openrouter_balance:
            available = openrouter_balance - total_allocated
            await update.message.reply_text(
                f"❌ <b>Insufficient OpenRouter Balance!</b>\n\n"
                f"💰 OpenRouter Balance: ${openrouter_balance:.2f}\n"
                f"📊 Total Allocated: ${total_allocated:.2f}\n"
                f"✅ Available to Allocate: ${available:.2f}\n\n"
                f"❌ Requested: ${amount:.2f}\n"
                f"⚠️ Would exceed balance by: ${new_total_allocated - openrouter_balance:.2f}\n\n"
                f"<b>Solution:</b>\n"
                f"1. Top-up OpenRouter first: https://openrouter.ai/settings/billing\n"
                f"2. Or allocate max ${available:.2f} to this user",
                parse_mode='HTML'
            )
            cursor.close()
            return
        
        # Create user credit record if doesn't exist
        cursor.execute("""
            INSERT INTO openclaw_user_credits (user_id, credits, total_allocated, total_used)
            VALUES (?, 0, 0, 0)
            ON CONFLICT (user_id) DO NOTHING
        """, (target_user_id,))
        
        # Get user's current balance
        cursor.execute("""
            SELECT credits FROM openclaw_user_credits WHERE user_id = ?
        """, (target_user_id,))
        result = cursor.fetchone()
        balance_before = float(result[0]) if result else 0
        
        # Add credits to user
        cursor.execute("""
            UPDATE openclaw_user_credits
            SET credits = credits + ?,
                total_allocated = total_allocated + ?
            WHERE user_id = ?
        """, (amount, amount, target_user_id))
        
        # Log allocation
        cursor.execute("""
            INSERT INTO openclaw_credit_allocations (
                user_id, admin_id, amount, reason,
                openrouter_balance_before, openrouter_balance_after,
                total_allocated_before, total_allocated_after
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_user_id, user_id, amount, reason,
            openrouter_balance, openrouter_balance,  # Same before/after (admin tops up separately)
            total_allocated, new_total_allocated
        ))
        
        # Create balance snapshot
        cursor.execute("""
            INSERT INTO openclaw_balance_snapshots (
                openrouter_balance, total_allocated, total_used,
                available_to_allocate, user_count
            )
            SELECT 
                ?,
                COALESCE(SUM(total_allocated), 0),
                COALESCE(SUM(total_used), 0),
                ? - COALESCE(SUM(total_allocated), 0),
                COUNT(*)
            FROM openclaw_user_credits
        """, (openrouter_balance, openrouter_balance))
        
        db.commit()
        cursor.close()
        
        balance_after = balance_before + amount
        available_after = openrouter_balance - new_total_allocated
        
        # Send notification to user
        notification_message = (
            "✅ <b>Credits Added!</b>\n\n"
            f"💰 <b>Amount Added:</b> ${amount:.2f}\n"
            f"💳 <b>Your Balance:</b> ${balance_after:.2f}\n\n"
            "Your OpenClaw credits have been successfully added!\n\n"
            "You can now use OpenClaw AI Agent.\n"
            "Just chat normally - no commands needed!\n\n"
            "Check balance: /openclaw_balance\n\n"
            "Thank you for your payment! 🎉"
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=notification_message,
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
            f"• Before: ${balance_before:.2f}\n"
            f"• After: ${balance_after:.2f}\n\n"
            f"<b>System Status:</b>\n"
            f"💰 OpenRouter Balance: ${openrouter_balance:.2f}\n"
            f"📊 Total Allocated: ${new_total_allocated:.2f}\n"
            f"✅ Available: ${available_after:.2f}\n\n"
            f"{notification_status}",
            parse_mode='HTML'
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid arguments.\n"
            "User ID must be a number.\n"
            "Amount must be a number."
        )
    except Exception as e:
        logger.error(f"Error in admin_add_credits: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def admin_notify_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    DEPRECATED: Use /admin_add_credits instead
    This command is kept for backward compatibility
    """
    await update.message.reply_text(
        "⚠️ <b>Command Deprecated</b>\n\n"
        "Please use <code>/admin_add_credits</code> instead.\n\n"
        "New command allocates credits directly to user's balance.\n\n"
        "<b>Usage:</b>\n"
        "<code>/admin_add_credits &lt;user_id&gt; &lt;amount&gt; [reason]</code>\n\n"
        "<b>Example:</b>\n"
        "<code>/admin_add_credits 123456789 7 Payment Rp 100k</code>",
        parse_mode='HTML'
    )


async def admin_system_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_system_status - View OpenRouter vs Allocated balance
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command.")
        return
    
    try:
        # Fetch OpenRouter balance
        api_key = os.getenv('OPENCLAW_API_KEY')
        
        if not api_key:
            await update.message.reply_text(
                "❌ OPENCLAW_API_KEY not configured in environment variables."
            )
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                await update.message.reply_text(
                    f"❌ Failed to fetch OpenRouter balance.\n"
                    f"Status: {response.status_code}"
                )
                return
            
            data = response.json()
            openrouter_balance = data.get('data', {}).get('limit_remaining', 0)
        
        # Get database stats
        from services import get_database
        db = get_database()
        cursor = db.cursor  # Property, not method
        
        # Total allocated to all users
        cursor.execute("""
            SELECT 
                COALESCE(SUM(credits), 0) as total_credits,
                COALESCE(SUM(total_allocated), 0) as total_allocated,
                COALESCE(SUM(total_used), 0) as total_used,
                COUNT(*) as user_count
            FROM openclaw_user_credits
        """)
        result = cursor.fetchone()
        
        if result:
            total_credits, total_allocated, total_used, user_count = result
            total_credits = float(total_credits)
            total_allocated = float(total_allocated)
            total_used = float(total_used)
        else:
            total_credits = 0
            total_allocated = 0
            total_used = 0
            user_count = 0
        
        # Top users by balance
        cursor.execute("""
            SELECT user_id, credits, total_used
            FROM openclaw_user_credits
            WHERE credits > 0
            ORDER BY credits DESC
            LIMIT 5
        """)
        top_users = cursor.fetchall()
        
        cursor.close()
        
        # Calculate metrics
        available_to_allocate = openrouter_balance - total_credits
        allocation_percentage = (total_credits / openrouter_balance * 100) if openrouter_balance > 0 else 0
        
        # Build message
        message = (
            "📊 <b>OpenClaw System Status</b>\n\n"
            f"<b>💰 OpenRouter Balance:</b> ${openrouter_balance:.2f}\n"
            f"<b>📊 Total Allocated:</b> ${total_credits:.2f} ({allocation_percentage:.1f}%)\n"
            f"<b>✅ Available to Allocate:</b> ${available_to_allocate:.2f}\n\n"
            f"<b>📈 Usage Stats:</b>\n"
            f"• Total Ever Allocated: ${total_allocated:.2f}\n"
            f"• Total Used: ${total_used:.2f}\n"
            f"• Active Users: {user_count}\n\n"
        )
        
        if available_to_allocate < 0:
            message += (
                "⚠️ <b>WARNING: Over-allocated!</b>\n"
                f"You've allocated ${abs(available_to_allocate):.2f} more than available.\n"
                "Top-up OpenRouter immediately!\n\n"
            )
        elif available_to_allocate < 5:
            message += (
                "⚡ <b>Low Balance Warning</b>\n"
                "Consider topping up OpenRouter soon.\n\n"
            )
        
        if top_users:
            message += "<b>👥 Top Users by Balance:</b>\n"
            for user_id, credits, used in top_users:
                message += f"• <code>{user_id}</code>: ${float(credits):.2f} (used: ${float(used):.2f})\n"
        
        message += (
            "\n<b>🔗 Quick Actions:</b>\n"
            "• /admin_add_credits - Allocate to user\n"
            "• /admin_openclaw_balance - Check OpenRouter\n"
            "• <a href='https://openrouter.ai/settings/billing'>Top-up OpenRouter</a>"
        )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in admin_system_status: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def admin_openclaw_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_openclaw_help - Show admin commands for OpenClaw
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await update.message.reply_text("❌ Admin only command.")
        return
    
    message = (
        "🔧 <b>OpenClaw Admin Commands</b>\n\n"
        "<b>💰 Credit Management:</b>\n"
        "• <code>/admin_add_credits &lt;user_id&gt; &lt;amount&gt; [reason]</code>\n"
        "  Allocate credits to user from OpenRouter balance\n"
        "  Example: <code>/admin_add_credits 123456789 7 Payment Rp 100k</code>\n\n"
        "• <code>/admin_openclaw_balance</code>\n"
        "  Check OpenRouter API balance (real-time)\n\n"
        "• <code>/admin_system_status</code>\n"
        "  View OpenRouter vs Allocated balance\n\n"
        "<b>📋 New Workflow:</b>\n"
        "1. User sends payment proof (Rp 100k = ~$7)\n"
        "2. Verify payment (bank/e-money/crypto)\n"
        "3. Top-up OpenRouter if needed (via web)\n"
        "4. Use <code>/admin_add_credits</code> to allocate\n"
        "5. System auto-notifies user\n"
        "6. User's credits updated instantly\n\n"
        "<b>⚠️ IMPORTANT:</b>\n"
        "• Each user has their own credit balance\n"
        "• Credits deducted per message automatically\n"
        "• Total allocated cannot exceed OpenRouter balance\n"
        "• System checks before each allocation\n\n"
        "<b>🔗 Quick Links:</b>\n"
        "• <a href='https://openrouter.ai/settings/billing'>Top-up OpenRouter</a>\n"
        "• <a href='https://openrouter.ai/activity'>View API Activity</a>\n"
        "• <a href='https://bscscan.com/'>Verify Crypto Payments</a>"
    )
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


def register_openclaw_admin_credit_handlers(application):
    """Register admin credit management handlers"""
    application.add_handler(CommandHandler("admin_openclaw_balance", admin_openclaw_balance_command))
    application.add_handler(CommandHandler("admin_add_credits", admin_add_credits_command))
    application.add_handler(CommandHandler("admin_notify_credits", admin_notify_credits_command))  # Deprecated
    application.add_handler(CommandHandler("admin_system_status", admin_system_status_command))
    application.add_handler(CommandHandler("admin_openclaw_help", admin_openclaw_help_command))
    
    logger.info("OpenClaw admin credit handlers registered (per-user credit system)")
