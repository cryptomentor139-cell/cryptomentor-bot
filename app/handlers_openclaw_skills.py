"""
OpenClaw Skills Handlers - Manage skill upgrades for AI Assistants
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


async def openclaw_skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available skills for upgrade"""
    user_id = update.effective_user.id
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Check if user has active session
    session = context.user_data.get('openclaw_session', {})
    if not session.get('active'):
        await update.message.reply_text(
            "❌ **No Active Session**\n\n"
            "Please start OpenClaw first: /openclaw_start",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    assistant_id = session.get('assistant_id')
    if not assistant_id:
        await update.message.reply_text(
            "❌ **No Assistant Selected**\n\n"
            "Please select an assistant first.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get available skills
    available_skills = manager.get_available_skills(assistant_id)
    installed_skills = manager.get_installed_skills(assistant_id)
    user_credits = manager.get_user_credits(user_id)
    
    if not available_skills:
        await update.message.reply_text(
            "✅ **All Skills Installed!**\n\n"
            f"Your assistant has all available skills.\n\n"
            f"💰 Credits: {user_credits:,}\n"
            f"📊 Installed Skills: {len(installed_skills)}\n\n"
            f"View installed: /openclaw_myskills",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Build message
    message = f"🛒 **Skill Marketplace**\n\n"
    message += f"💰 Your Credits: {user_credits:,}\n"
    message += f"✅ Installed: {len(installed_skills)} skills\n"
    message += f"🆕 Available: {len(available_skills)} skills\n\n"
    
    # Group by category
    categories = {}
    for skill in available_skills:
        cat = skill['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    
    # Display by category
    category_icons = {
        'crypto': '₿',
        'trading': '📈',
        'analysis': '📊',
        'automation': '🤖',
        'research': '🔍',
        'general': '💬'
    }
    
    for category, skills in sorted(categories.items()):
        icon = category_icons.get(category, '📦')
        message += f"\n{icon} **{category.upper()}**\n"
        
        for skill in skills:
            premium = "⭐ " if skill['is_premium'] else ""
            price = f"{skill['price_credits']:,} credits" if skill['price_credits'] > 0 else "FREE"
            message += f"• {premium}{skill['name']} - {price}\n"
            message += f"  _{skill['description']}_\n"
    
    message += f"\n\n💡 **How to Install:**\n"
    message += f"Use: `/openclaw_install <skill_id>`\n\n"
    message += f"📖 View details: `/openclaw_skill <skill_id>`"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def openclaw_myskills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show installed skills"""
    user_id = update.effective_user.id
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Check if user has active session
    session = context.user_data.get('openclaw_session', {})
    if not session.get('active'):
        await update.message.reply_text(
            "❌ **No Active Session**\n\n"
            "Please start OpenClaw first: /openclaw_start",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    assistant_id = session.get('assistant_id')
    if not assistant_id:
        await update.message.reply_text(
            "❌ **No Assistant Selected**",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get installed skills
    skills = manager.get_installed_skills(assistant_id)
    
    if not skills:
        await update.message.reply_text(
            "📦 **No Skills Installed**\n\n"
            "Browse available skills: /openclaw_skills",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Build message
    message = f"✅ **Your Installed Skills**\n\n"
    message += f"Total: {len(skills)} skills\n\n"
    
    # Group by category
    categories = {}
    for skill in skills:
        cat = skill['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    
    category_icons = {
        'crypto': '₿',
        'trading': '📈',
        'analysis': '📊',
        'automation': '🤖',
        'research': '🔍',
        'general': '💬'
    }
    
    for category, cat_skills in sorted(categories.items()):
        icon = category_icons.get(category, '📦')
        message += f"\n{icon} **{category.upper()}**\n"
        
        for skill in cat_skills:
            status = "✅" if skill['is_active'] else "⏸️"
            usage = skill['usage_count']
            message += f"{status} {skill['name']}\n"
            message += f"   Used: {usage} times\n"
            
            # Show capabilities
            if skill['capabilities']:
                caps = ', '.join(skill['capabilities'][:3])
                message += f"   Capabilities: {caps}\n"
    
    message += f"\n\n💡 **Commands:**\n"
    message += f"• Toggle: `/openclaw_toggle <skill_id>`\n"
    message += f"• Details: `/openclaw_skill <skill_id>`\n"
    message += f"• Browse more: `/openclaw_skills`"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def openclaw_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed skill information"""
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/openclaw_skill <skill_id>`\n\n"
            "Example: `/openclaw_skill skill_crypto_analysis`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    skill_id = context.args[0]
    user_id = update.effective_user.id
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Get skill details
    skill = manager.get_skill_details(skill_id)
    
    if not skill:
        await update.message.reply_text(
            f"❌ **Skill Not Found:** `{skill_id}`\n\n"
            f"Browse available: /openclaw_skills",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Build detailed message
    premium = "⭐ PREMIUM" if skill['is_premium'] else "FREE"
    price = f"{skill['price_credits']:,} credits" if skill['price_credits'] > 0 else "FREE"
    
    message = f"📦 **{skill['name']}** {premium}\n\n"
    message += f"**Description:**\n{skill['description']}\n\n"
    message += f"**Category:** {skill['category']}\n"
    message += f"**Price:** {price}\n"
    message += f"**Version:** {skill['version']}\n\n"
    
    if skill['capabilities']:
        message += f"**Capabilities:**\n"
        for cap in skill['capabilities']:
            message += f"• {cap.replace('_', ' ').title()}\n"
        message += "\n"
    
    # Check if user has enough credits
    user_credits = manager.get_user_credits(user_id)
    can_afford = user_credits >= skill['price_credits']
    
    if can_afford or skill['price_credits'] == 0:
        message += f"💰 Your Credits: {user_credits:,}\n"
        message += f"✅ You can install this skill!\n\n"
        message += f"**Install:** `/openclaw_install {skill_id}`"
    else:
        needed = skill['price_credits'] - user_credits
        message += f"💰 Your Credits: {user_credits:,}\n"
        message += f"❌ Need {needed:,} more credits\n\n"
        message += f"**Buy Credits:** /openclaw_buy"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def openclaw_install_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Install a skill"""
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/openclaw_install <skill_id>`\n\n"
            "Example: `/openclaw_install skill_crypto_analysis`\n\n"
            "Browse skills: /openclaw_skills",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    skill_id = context.args[0]
    user_id = update.effective_user.id
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Check if user has active session
    session = context.user_data.get('openclaw_session', {})
    if not session.get('active'):
        await update.message.reply_text(
            "❌ **No Active Session**\n\n"
            "Please start OpenClaw first: /openclaw_start",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    assistant_id = session.get('assistant_id')
    if not assistant_id:
        await update.message.reply_text(
            "❌ **No Assistant Selected**",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get skill details first
    skill = manager.get_skill_details(skill_id)
    if not skill:
        await update.message.reply_text(
            f"❌ **Skill Not Found:** `{skill_id}`\n\n"
            f"Browse available: /openclaw_skills",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Install skill
    success, message_text, credits_spent = manager.install_skill(assistant_id, skill_id, user_id)
    
    if success:
        new_balance = manager.get_user_credits(user_id)
        
        response = f"✅ **Skill Installed!**\n\n"
        response += f"📦 {skill['name']}\n"
        response += f"💰 Cost: {credits_spent:,} credits\n"
        response += f"💳 New Balance: {new_balance:,} credits\n\n"
        
        if skill['capabilities']:
            response += f"**New Capabilities:**\n"
            for cap in skill['capabilities'][:5]:
                response += f"• {cap.replace('_', ' ').title()}\n"
        
        response += f"\n✨ Your assistant is now more powerful!\n"
        response += f"View all skills: /openclaw_myskills"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            f"❌ **Installation Failed**\n\n"
            f"{message_text}\n\n"
            f"💡 Check: /openclaw_balance",
            parse_mode=ParseMode.MARKDOWN
        )


async def openclaw_toggle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle skill on/off"""
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/openclaw_toggle <skill_id>`\n\n"
            "Example: `/openclaw_toggle skill_crypto_analysis`\n\n"
            "View skills: /openclaw_myskills",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    skill_id = context.args[0]
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Check if user has active session
    session = context.user_data.get('openclaw_session', {})
    if not session.get('active'):
        await update.message.reply_text(
            "❌ **No Active Session**\n\n"
            "Please start OpenClaw first: /openclaw_start",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    assistant_id = session.get('assistant_id')
    if not assistant_id:
        await update.message.reply_text(
            "❌ **No Assistant Selected**",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get current status
    installed_skills = manager.get_installed_skills(assistant_id)
    skill = next((s for s in installed_skills if s['skill_id'] == skill_id), None)
    
    if not skill:
        await update.message.reply_text(
            f"❌ **Skill Not Installed:** `{skill_id}`\n\n"
            f"Install it first: `/openclaw_install {skill_id}`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Toggle
    new_status = not skill['is_active']
    success = manager.toggle_skill(assistant_id, skill_id, new_status)
    
    if success:
        status_text = "enabled ✅" if new_status else "disabled ⏸️"
        await update.message.reply_text(
            f"✅ **Skill {status_text.split()[0].title()}**\n\n"
            f"📦 {skill['name']} is now {status_text}\n\n"
            f"View all: /openclaw_myskills",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "❌ **Failed to toggle skill**\n\n"
            "Please try again later.",
            parse_mode=ParseMode.MARKDOWN
        )


def register_openclaw_skill_handlers(application):
    """Register OpenClaw skill command handlers"""
    from telegram.ext import CommandHandler
    
    application.add_handler(CommandHandler("openclaw_skills", openclaw_skills_command))
    application.add_handler(CommandHandler("openclaw_myskills", openclaw_myskills_command))
    application.add_handler(CommandHandler("openclaw_skill", openclaw_skill_command))
    application.add_handler(CommandHandler("openclaw_install", openclaw_install_command))
    application.add_handler(CommandHandler("openclaw_toggle", openclaw_toggle_command))
    
    logger.info("✅ OpenClaw skill handlers registered")
