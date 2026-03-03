"""
OpenClaw Callback Handlers - Handle inline keyboard callbacks
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


async def handle_openclaw_select_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle assistant selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    assistant_id = query.data.replace('openclaw_select_', '')
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Get assistant info
    assistant = manager.get_assistant_info(assistant_id)
    
    if not assistant:
        await query.edit_message_text(
            "❌ **Assistant not found**",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Activate session
    context.user_data['openclaw_session'] = {
        'active': True,
        'assistant_id': assistant_id,
        'conversation_id': None
    }
    
    # Check credits
    credits = manager.get_user_credits(user_id)
    
    await query.edit_message_text(
        f"✅ **OpenClaw Mode Activated**\n\n"
        f"🤖 Assistant: {assistant['name']}\n"
        f"💰 Credits: {credits}\n\n"
        f"💬 **You can now chat freely!**\n"
        f"Just type your message - no commands needed.\n\n"
        f"🔙 Exit mode: /openclaw_exit\n"
        f"💰 Buy credits: /openclaw_buy\n"
        f"📊 View history: /openclaw_history",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_openclaw_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle credit purchase callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Extract amount from callback data
    amount_str = query.data.replace('openclaw_buy_', '')
    
    if amount_str == 'custom':
        # Custom amount - ask user
        context.user_data['awaiting_openclaw_amount'] = True
        await query.edit_message_text(
            "💰 **Custom Amount**\n\n"
            "Enter amount in USDC (minimum 5 USDC):\n\n"
            "Example: `100`\n\n"
            "🔙 Cancel: /openclaw_buy",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        amount_usdc = float(amount_str)
    except ValueError:
        await query.edit_message_text(
            "❌ **Invalid amount**",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Calculate platform fee and net credits
    platform_fee = amount_usdc * 0.20
    net_amount = amount_usdc - platform_fee
    net_credits = int(net_amount * 100)
    
    # Get wallet address (you need to implement this)
    wallet_address = "0x63116672bef9f26fd906cd2a57550f7a13925822"  # Example
    
    await query.edit_message_text(
        f"💰 **Purchase Summary**\n\n"
        f"**Amount:** {amount_usdc} USDC\n"
        f"**Platform Fee (20%):** {platform_fee:.2f} USDC\n"
        f"**Net Amount:** {net_amount:.2f} USDC\n"
        f"**Credits:** {net_credits:,} credits\n\n"
        f"📍 **Deposit Address:**\n"
        f"`{wallet_address}`\n\n"
        f"**Network:** Base (USDC)\n\n"
        f"⚠️ **Important:**\n"
        f"• Send exactly {amount_usdc} USDC\n"
        f"• Use Base network only\n"
        f"• Credits added automatically after confirmation\n\n"
        f"💡 After deposit, check balance: /openclaw_balance",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_openclaw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel callback"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ **Cancelled**\n\n"
        "Use /openclaw_help for more information.",
        parse_mode=ParseMode.MARKDOWN
    )


def register_openclaw_callbacks(application):
    """Register OpenClaw callback handlers"""
    from telegram.ext import CallbackQueryHandler
    
    application.add_handler(CallbackQueryHandler(
        handle_openclaw_select_assistant,
        pattern=r'^openclaw_select_'
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_openclaw_buy,
        pattern=r'^openclaw_buy_'
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_openclaw_cancel,
        pattern=r'^openclaw_cancel$'
    ))
    
    logger.info("✅ OpenClaw callback handlers registered")
