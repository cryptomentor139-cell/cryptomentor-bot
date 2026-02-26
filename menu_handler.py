#!/usr/bin/env python3
"""
Button-Based Menu System for CryptoMentor AI Bot
InlineKeyboard UI for all commands with fallback to slash commands
Uses python-telegram-bot framework
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

# =============================================================================
# STATE MANAGEMENT HELPER
# =============================================================================

def set_user_state(context: ContextTypes.DEFAULT_TYPE, state_key: str, state_value: any):
    """
    Set user state with timestamp to track when it was created
    This helps detect stale states after bot restart
    """
    context.user_data[state_key] = state_value
    context.user_data['state_timestamp'] = time.time()
    context.user_data['state_created_at'] = datetime.now().isoformat()

def clear_user_state(context: ContextTypes.DEFAULT_TYPE):
    """Clear all user state data"""
    context.user_data.clear()

# =============================================================================
# ESTIMATED TIME HELPER
# =============================================================================

def get_estimated_time_message(seconds: int, user_timezone: str = 'WIB') -> str:
    """
    Generate estimated time message with completion time
    Format: ⏱️ Estimated: ~Xs (selesai 14:30:25 WIB)
    """
    try:
        from pytz import timezone as tz_module
        
        # Map timezone codes to pytz
        tz_map = {
            'WIB': 'Asia/Jakarta',
            'WITA': 'Asia/Makassar', 
            'WIT': 'Asia/Jayapura',
            'UTC': 'UTC',
            'EST': 'America/New_York',
            'PST': 'America/Los_Angeles',
            'GMT': 'Europe/London',
            'JST': 'Asia/Tokyo',
            'KST': 'Asia/Seoul',
            'SGT': 'Asia/Singapore',
        }
        
        tz_name = tz_map.get(user_timezone, 'Asia/Jakarta')
        user_tz = tz_module(tz_name)
        
        # Calculate completion time
        now = datetime.now(user_tz)
        completion_time = now + timedelta(seconds=seconds)
        completion_str = completion_time.strftime('%H:%M:%S')
        
        return f"⏱️ Estimated: ~{seconds}s (selesai {completion_str} {user_timezone})"
    except Exception as e:
        logger.error(f"Error in get_estimated_time_message: {e}")
        return f"⏱️ Estimated: ~{seconds}s"


def get_user_timezone_from_context(context, user_id: int = None) -> str:
    """Get user timezone from context, database, or default to WIB"""
    try:
        # First check context cache
        cached_tz = context.user_data.get('timezone')
        if cached_tz:
            return cached_tz
        
        # Try to get from database if user_id available
        if user_id:
            try:
                from services import get_database
                db = get_database()
                user_tz = db.get_user_timezone(user_id)
                if user_tz:
                    context.user_data['timezone'] = user_tz
                    return user_tz
            except Exception as e:
                logger.debug(f"Could not get timezone from db: {e}")
        
        return 'WIB'
    except:
        return 'WIB'

# =============================================================================
# CALLBACK DATA CONSTANTS (for routing)
# =============================================================================

# Main menu
MAIN_MENU = "main_menu"

# Categories
PRICE_MARKET = "price_market"
TRADING_ANALYSIS = "trading_analysis"
FUTURES_SIGNALS = "futures_signals"
PORTFOLIO_CREDITS = "portfolio_credits"
PREMIUM_REFERRAL = "premium_referral"
ASK_AI = "ask_ai"
SETTINGS = "settings"

# Price & Market submenu
CHECK_PRICE = "check_price"
MARKET_OVERVIEW = "market_overview"

# Trading Analysis submenu
SPOT_ANALYSIS = "spot_analysis"
FUTURES_ANALYSIS = "futures_analysis"

# Futures Signals submenu
MULTI_COIN_SIGNALS = "multi_coin_signals"
AUTO_SIGNAL_INFO = "auto_signal_info"

# Portfolio & Credits submenu
MY_PORTFOLIO = "my_portfolio"
ADD_COIN = "add_coin"
CHECK_CREDITS = "check_credits"
UPGRADE_PREMIUM = "upgrade_premium"

# Premium & Referral submenu
REFERRAL_PROGRAM = "referral_program"
PREMIUM_EARNINGS = "premium_earnings"

# Ask AI submenu
ASK_CRYPTOMENTOR = "ask_cryptomentor"

# Settings submenu
CHANGE_LANGUAGE = "change_language"

# Input states for ConversationHandler
INPUT_SYMBOL = 1
INPUT_AMOUNT = 2
INPUT_QUESTION = 3

# =============================================================================
# MENU BUILDERS
# =============================================================================

def build_main_menu() -> InlineKeyboardMarkup:
    """Build main menu with 6 categories (AI disabled)"""
    keyboard = [
        [
            InlineKeyboardButton("📈 Price & Market", callback_data=PRICE_MARKET),
            InlineKeyboardButton("🧠 Trading Analysis", callback_data=TRADING_ANALYSIS),
        ],
        [
            InlineKeyboardButton("🚀 Futures Signals", callback_data=FUTURES_SIGNALS),
            InlineKeyboardButton("💼 Portfolio", callback_data=PORTFOLIO_CREDITS),
        ],
        [
            InlineKeyboardButton("👑 Premium & Referral", callback_data=PREMIUM_REFERRAL),
            InlineKeyboardButton("🤖 Ask AI", callback_data=ASK_AI),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data=SETTINGS),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_price_market_menu() -> InlineKeyboardMarkup:
    """Build Price & Market submenu"""
    keyboard = [
        [InlineKeyboardButton("🔹 Check Price", callback_data=CHECK_PRICE)],
        [InlineKeyboardButton("🌍 Market Overview", callback_data=MARKET_OVERVIEW)],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_trading_analysis_menu() -> InlineKeyboardMarkup:
    """Build Trading Analysis submenu"""
    keyboard = [
        [InlineKeyboardButton("📊 Spot Analysis (SnD)", callback_data=SPOT_ANALYSIS)],
        [InlineKeyboardButton("📉 Futures Analysis (SnD)", callback_data=FUTURES_ANALYSIS)],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_futures_signals_menu() -> InlineKeyboardMarkup:
    """Build Futures Signals submenu"""
    keyboard = [
        [InlineKeyboardButton("🔥 Multi-Coin Signals", callback_data=MULTI_COIN_SIGNALS)],
        [InlineKeyboardButton("👑 Auto Signals (Lifetime)", callback_data=AUTO_SIGNAL_INFO)],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_portfolio_menu() -> InlineKeyboardMarkup:
    """Build Portfolio & Credits submenu"""
    keyboard = [
        [InlineKeyboardButton("📂 My Portfolio", callback_data=MY_PORTFOLIO)],
        [InlineKeyboardButton("➕ Add Coin", callback_data=ADD_COIN)],
        [InlineKeyboardButton("💳 Check Credits", callback_data=CHECK_CREDITS)],
        [InlineKeyboardButton("⭐ Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_premium_referral_menu() -> InlineKeyboardMarkup:
    """Build Premium & Referral submenu"""
    keyboard = [
        [InlineKeyboardButton("🎁 Referral Program", callback_data=REFERRAL_PROGRAM)],
        [InlineKeyboardButton("💰 Premium Earnings", callback_data=PREMIUM_EARNINGS)],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_ask_ai_menu() -> InlineKeyboardMarkup:
    """Build Ask AI submenu with Cerebras AI options"""
    keyboard = [
        [InlineKeyboardButton("💬 Chat dengan AI", callback_data="ai_chat_prompt")],
        [InlineKeyboardButton("📊 Analisis Market AI", callback_data="ai_analyze_prompt")],
        [InlineKeyboardButton("🌍 Market Summary AI", callback_data="ai_market_summary")],
        [InlineKeyboardButton("❓ Panduan AI", callback_data="ai_guide")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_settings_menu() -> InlineKeyboardMarkup:
    """Build Settings submenu"""
    keyboard = [
        [InlineKeyboardButton("🌐 Change Language", callback_data=CHANGE_LANGUAGE)],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_symbol_input_keyboard() -> InlineKeyboardMarkup:
    """Quick symbol input keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("₿ BTC", callback_data="symbol_BTC"),
            InlineKeyboardButton("Ξ ETH", callback_data="symbol_ETH"),
            InlineKeyboardButton("BNB", callback_data="symbol_BNB"),
        ],
        [
            InlineKeyboardButton("SOL", callback_data="symbol_SOL"),
            InlineKeyboardButton("XRP", callback_data="symbol_XRP"),
            InlineKeyboardButton("ADA", callback_data="symbol_ADA"),
        ],
        [InlineKeyboardButton("⌨️ Type Custom", callback_data="symbol_custom")],
        [InlineKeyboardButton("❌ Cancel", callback_data=MAIN_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


# =============================================================================
# CALLBACK HANDLERS (Map to existing command functions)
# =============================================================================

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="🎯 **CryptoMentor AI - Main Menu**\n\nChoose a category:",
        reply_markup=build_main_menu(),
        parse_mode='Markdown'
    )


async def price_market_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Price & Market submenu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="📈 **Price & Market**\n\nSelect an option:",
        reply_markup=build_price_market_menu(),
        parse_mode='Markdown'
    )


async def check_price_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for symbol to check price"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="🔹 **Check Price**\n\nSelect a symbol or type a custom one:\n(e.g., BTC, ETH, BTCUSDT)",
        reply_markup=build_symbol_input_keyboard(),
        parse_mode='Markdown'
    )
    
    context.user_data['action'] = 'price'


async def market_overview_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display market overview for top 5 pairs (BTC, ETH, BNB, SOL, XRP)"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Send loading message with estimated time
        user_id = update.effective_user.id
        user_tz = get_user_timezone_from_context(context, user_id)
        est_time = get_estimated_time_message(5, user_tz)
        
        await query.edit_message_text(
            text=f"📊 Fetching market data...\n{est_time}",
            reply_markup=None,
            parse_mode='HTML'
        )
        
        # Get crypto API instance
        from crypto_api import crypto_api
        
        # Fetch market data in parallel (5 pairs, <3 second target)
        market_data = crypto_api.get_market_overview_fast()
        
        if not market_data.get('success', False):
            error_msg = market_data.get('error', 'Unknown error')
            await query.edit_message_text(
                text=f"❌ <b>Market Data Error</b>\n\nFailed to fetch market data:\n<code>{error_msg}</code>",
                parse_mode='HTML'
            )
            return
        
        # Format market overview message
        pairs = market_data.get('pairs', [])
        sentiment = market_data.get('sentiment', 'UNKNOWN')
        
        # Sentiment emoji and color
        sentiment_emoji = '🟢' if sentiment == 'BULLISH' else ('🟡' if sentiment == 'NEUTRAL' else '🔴')
        sentiment_text = f"{sentiment_emoji} <b>{sentiment}</b>"
        
        # Build pairs summary
        pairs_lines = []
        for pair in pairs:
            emoji = pair.get('emoji', '○')
            symbol = pair.get('symbol', 'N/A')
            price = pair.get('price', 0)
            change = pair.get('change_24h', 0)
            volume = pair.get('volume_24h', 0)
            
            # Format price
            if price >= 1:
                price_str = f"${price:,.0f}" if price > 1000 else f"${price:.2f}"
            else:
                price_str = f"${price:.6f}"
            
            # Format change with color
            change_str = f"{'+' if change > 0 else ''}{change:.2f}%"
            change_emoji = '🟢' if change > 0 else ('🔴' if change < 0 else '⚪')
            
            # Format volume
            if volume > 1_000_000_000:
                volume_str = f"${volume/1_000_000_000:.1f}B"
            elif volume > 1_000_000:
                volume_str = f"${volume/1_000_000:.1f}M"
            else:
                volume_str = f"${volume/1_000:,.0f}K"
            
            pair_line = f"{emoji} <b>{symbol}</b>: {price_str} | {change_emoji} {change_str} | 📈 {volume_str}"
            pairs_lines.append(pair_line)
        
        pairs_text = "\n".join(pairs_lines)
        
        # Build final message
        from datetime import datetime
        from pytz import timezone as tz_module
        current_time = datetime.now(tz_module('Asia/Jakarta')).strftime('%H:%M:%S')
        
        message_text = f"""<b>🌍 GLOBAL MARKET OVERVIEW</b>

<b>⏰ {current_time}</b> WIB

<b>📊 Market Sentiment:</b> {sentiment_text}

────────────────

{pairs_text}

────────────────

<i>💡 Data from Binance Spot Market</i>"""
        
        # Send formatted message
        await query.edit_message_text(
            text=message_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=PRICE_MARKET)]])
        )
        
        logger.info(f"Market overview sent successfully. Sentiment: {sentiment}")
    
    except Exception as e:
        logger.error(f"Market overview error: {e}", exc_info=True)
        await query.edit_message_text(
            text=f"❌ <b>Error</b>\n\n{str(e)[:100]}",
            parse_mode='HTML'
        )
        context.user_data['action'] = None


async def trading_analysis_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Trading Analysis submenu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="🧠 **Trading Analysis (Supply & Demand)**\n\nSelect an option:",
        reply_markup=build_trading_analysis_menu(),
        parse_mode='Markdown'
    )


async def spot_analysis_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for symbol to analyze (spot)"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="📊 **Spot Analysis (Supply & Demand)**\n\nSelect a symbol:\n(20 credits required)",
        reply_markup=build_symbol_input_keyboard(),
        parse_mode='Markdown'
    )
    
    context.user_data['action'] = 'analyze'


async def futures_analysis_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for symbol to analyze (futures)"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="📉 **Futures Analysis (Supply & Demand)**\n\nSelect a symbol:\n(20 credits required)",
        reply_markup=build_symbol_input_keyboard(),
        parse_mode='Markdown'
    )
    
    context.user_data['action'] = 'futures'


async def futures_signals_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Futures Signals submenu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="🚀 **Futures Signals**\n\nSelect an option:",
        reply_markup=build_futures_signals_menu(),
        parse_mode='Markdown'
    )


async def multi_coin_signals_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate multi-coin futures signals with async processing"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = update.effective_user.id
    user_tz = get_user_timezone_from_context(context, user_id)
    est_time = get_estimated_time_message(10, user_tz)
    
    # Check and deduct credits (60 for Multi-Coin Signals)
    try:
        from app.credits_guard import require_credits
        ok, remain, msg = require_credits(user_id, 60)
        if not ok:
            keyboard = [[InlineKeyboardButton("⭐ Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                        [InlineKeyboardButton("🔙 Back", callback_data=FUTURES_SIGNALS)]]
            await query.edit_message_text(
                text=f"❌ {msg}\n\n⭐ Upgrade ke Premium untuk akses unlimited!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        print(f"✅ Credit deducted for user {user_id}: 60 credits (multi-coin), remaining: {remain}")
    except Exception as e:
        print(f"❌ Credit check error for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        await query.edit_message_text(
            text="❌ Sistem kredit sedang bermasalah. Silakan coba lagi nanti.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=FUTURES_SIGNALS)]])
        )
        return
    
    await query.edit_message_text(
        text=f"🔥 **Multi-Coin Futures Signals**\n\n⏳ Generating signals...\n{est_time}",
        reply_markup=None,
        parse_mode='Markdown'
    )
    
    async def generate_and_send():
        """Generate signals with comprehensive error handling and timeout"""
        try:
            from futures_signal_generator import FuturesSignalGenerator
            generator = FuturesSignalGenerator()
            
            # Add 30 second timeout to prevent infinite hanging
            signals = await asyncio.wait_for(
                generator.generate_multi_signals(),
                timeout=30.0
            )
            
            if len(signals) > 4000:
                signals = signals[:3900] + "\n\n... (truncated)"
            
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=signals,
                parse_mode=None
            )
            logger.info(f"✅ Multi-coin signals sent successfully to user {user_id}")
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Multi-coin signals TIMEOUT (30s) for user {user_id}")
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=FUTURES_SIGNALS)]]
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ Signal generation timeout (30s)\n\n"
                     "API sedang lambat. Silakan coba lagi dalam beberapa menit.\n\n"
                     "💡 Tip: Gunakan saat traffic rendah untuk hasil lebih cepat.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"❌ Multi-coin signals error for user {user_id}: {e}", exc_info=True)
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=FUTURES_SIGNALS)]]
            error_msg = str(e)[:100] if str(e) else "Unknown error"
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"❌ Error generating signals\n\n{error_msg}\n\nSilakan coba lagi.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    # Create task with proper error handling
    asyncio.create_task(generate_and_send())


async def auto_signal_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show auto signal info"""
    query = update.callback_query
    await query.answer()
    
    info_text = """👑 **Auto Signal Scanner (Lifetime Premium)**

🔄 **How It Works:**
• Automatic scanning every 30 minutes
• Supply & Demand zone detection
• Multi-timeframe analysis (1H + 4H)
• Curated top 3 signals per cycle

📊 **Entry Signals:**
• BUY: Price revisits demand zone
• SELL: Price revisits supply zone

✅ **Available For:**
• Admin users
• Lifetime premium members

📱 **Notifications:**
You'll receive instant signals in DM

💡 **Tip:** Upgrade to Lifetime Premium for automatic signal notifications!"""
    
    keyboard = [[InlineKeyboardButton("⭐ Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                [InlineKeyboardButton("🔙 Back", callback_data=FUTURES_SIGNALS)]]
    
    await query.edit_message_text(
        text=info_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def portfolio_credits_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Portfolio & Credits submenu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="💼 **Portfolio & Credits**\n\nSelect an option:",
        reply_markup=build_portfolio_menu(),
        parse_mode='Markdown'
    )


async def my_portfolio_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger /portfolio command"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_tz = get_user_timezone_from_context(context, user_id)
    est_time = get_estimated_time_message(3, user_tz)
    
    await query.edit_message_text(
        text=f"📂 **My Portfolio**\n\nLoading your portfolio...\n{est_time}",
        reply_markup=None,
        parse_mode='Markdown'
    )
    
    context.user_data['action'] = 'portfolio'


async def add_coin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start Add Coin flow (step 1: symbol)"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="➕ **Add Coin to Portfolio**\n\n**Step 1:** Select a symbol:",
        reply_markup=build_symbol_input_keyboard(),
        parse_mode='Markdown'
    )
    
    context.user_data['action'] = 'add_coin'
    context.user_data['step'] = 'symbol'


async def check_credits_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user credits - fetch from Supabase with different response for premium users"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Get user language
    from services import get_database
    db = get_database()
    user_lang = db.get_user_language(user_id)
    
    # Check premium status
    from app.users_repo import is_premium_active
    is_premium = is_premium_active(user_id)
    
    # Fetch credits and user data from Supabase
    credits = 0
    is_lifetime = False
    premium_until = None
    try:
        from supabase_client import get_user as supabase_get_user
        user_data = supabase_get_user(user_id)
        if user_data:
            credits = user_data.get('credits', 0) or 0
            is_lifetime = user_data.get('is_lifetime', False)
            premium_until = user_data.get('premium_until')
            if user_data.get('first_name'):
                user_name = user_data.get('first_name')
        else:
            credits = db.get_user_credits(user_id)
    except Exception as e:
        print(f"Error fetching credits from Supabase: {e}")
        credits = db.get_user_credits(user_id)
    
    if is_premium:
        # Premium user response
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data=PORTFOLIO_CREDITS)]
        ]
        
        if is_lifetime:
            premium_status = "♾️ LIFETIME"
        elif premium_until:
            premium_status = f"⏳ Until: {str(premium_until)[:10]}"
        else:
            premium_status = "✅ Active"
        
        if user_lang == 'id':
            await query.edit_message_text(
                text=f"👑 <b>Status Premium Aktif</b>\n\n"
                     f"👤 Pengguna: {user_name}\n"
                     f"🆔 UID Telegram: <code>{user_id}</code>\n"
                     f"🏆 Status: {premium_status}\n\n"
                     f"✨ <b>Keuntungan Premium:</b>\n"
                     f"✔ Akses UNLIMITED ke semua fitur\n"
                     f"✔ Tidak membutuhkan kredit\n"
                     f"✔ Spot & Futures Analysis tanpa batas\n"
                     f"✔ Multi-Coin Signals tanpa batas\n"
                     f"✔ Auto Signal (Lifetime only)\n\n"
                     f"🎉 Nikmati semua fitur tanpa batasan!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                text=f"👑 <b>Premium Status Active</b>\n\n"
                     f"👤 User: {user_name}\n"
                     f"🆔 Telegram UID: <code>{user_id}</code>\n"
                     f"🏆 Status: {premium_status}\n\n"
                     f"✨ <b>Premium Benefits:</b>\n"
                     f"✔ UNLIMITED access to all features\n"
                     f"✔ No credits required\n"
                     f"✔ Unlimited Spot & Futures Analysis\n"
                     f"✔ Unlimited Multi-Coin Signals\n"
                     f"✔ Auto Signal (Lifetime only)\n\n"
                     f"🎉 Enjoy all features without limits!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    else:
        # Free user response
        keyboard = [
            [InlineKeyboardButton("⭐ Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
            [InlineKeyboardButton("🔙 Back", callback_data=PORTFOLIO_CREDITS)]
        ]
        
        if user_lang == 'id':
            await query.edit_message_text(
                text=f"💳 <b>Saldo Kredit</b>\n\n"
                     f"👤 Pengguna: {user_name}\n"
                     f"🆔 UID Telegram: <code>{user_id}</code>\n"
                     f"💰 Kredit: {credits}\n\n"
                     f"📊 <b>Biaya Kredit:</b>\n"
                     f"• Analisis Spot: 20 kredit\n"
                     f"• Analisis Futures: 20 kredit\n"
                     f"• Sinyal Multi-Coin: 60 kredit\n\n"
                     f"⭐ Upgrade ke Premium untuk akses unlimited!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                text=f"💳 <b>Credit Balance</b>\n\n"
                     f"👤 User: {user_name}\n"
                     f"🆔 Telegram UID: <code>{user_id}</code>\n"
                     f"💰 Credits: {credits}\n\n"
                     f"📊 <b>Credit Costs:</b>\n"
                     f"• Spot Analysis: 20 credits\n"
                     f"• Futures Analysis: 20 credits\n"
                     f"• Multi-Coin Signals: 60 credits\n\n"
                     f"⭐ Upgrade to Premium for unlimited access!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )


async def upgrade_premium_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium subscription packages with user's Telegram ID - identical to /subscribe"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Exact same text as /subscribe command in bot.py
    subscription_text = f"""🚀 <b>CryptoMentor AI 3.0 – Paket Berlangganan</b>

Trading lebih terarah dengan AI berbasis Supply & Demand (SnD), data real-time Binance, dan sistem signal profesional tanpa hambatan credits (Unlimited access).

💎 <b>PILIH PAKET PREMIUM</b>

🔹 <b>Monthly</b>
💰 Rp320.000 / bulan
✔ Futures & Spot SnD Signals
✔ Analisis on-demand
✔ Semua fitur premium

🔹 <b>2 Bulan</b>
💰 Rp600.000 / 2 bulan
✔ Lebih hemat dari bulanan
✔ Semua fitur premium
✔ Cocok untuk swing trader

🔹 ⭐ <b>1 Tahun (Most Popular)</b>
💰 Rp3.500.000 / tahun
✔ Semua fitur premium
✔ Lebih hemat & tanpa perpanjang bulanan

🔥 <b>LIFETIME (LIMITED SLOT)</b>
💰 Rp6.500.000 – Sekali Bayar

🚀 Akses Seumur Hidup + Auto Signal

<b>Benefit LIFETIME:</b>
✔ Semua fitur premium (selamanya)
✔ Auto Futures & Spot Signal (SnD Based)
✔ Priority Signal (zona terbaik lebih dulu)
✔ Akses SETIAP pembaruan fitur CryptoMentor AI ke depan
✔ Tidak ada biaya bulanan / tahunan lagi

💳 <b>METODE PEMBAYARAN</b>

🏦 <b>Transfer Bank</b>
Nama: NABIL FARREL AL FARI
Bank: Mandiri
No Rek: 1560018407074

📱 <b>E-Money</b>
ShopeePay / GoPay / DANA
📞 0877-7927-4400

⛓️ <b>On-Chain Crypto</b>
Network: BEP20
Address:
<code>0xed7342ac9c22b1495af4d63f15a7c9768a028ea8</code>

✅ <b>CARA AKTIVASI (WAJIB)</b>

1️⃣ Lakukan pembayaran sesuai paket yang dipilih
2️⃣ Kirim bukti pembayaran ke admin: 👉 @BillFarr
3️⃣ Sertakan informasi berikut:

✅ Paket yang dipilih (Monthly / 2 Bulan / 1 Tahun / Lifetime)
✅ UID Telegram kamu: <code>{user_id}</code>

4️⃣ Akun akan diaktifkan setelah dikonfirmasi admin

📌 <b>CATATAN</b>
📊 Signal berbasis Supply & Demand, bukan tebak-tebakan
🤖 Data 100% dari Binance
🧠 Cocok untuk pemula hingga advanced
❌ Tidak menjanjikan profit, fokus probability & risk management"""
    
    keyboard = [
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/BillFarr")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data=MAIN_MENU)],
    ]
    
    await query.edit_message_text(
        text=subscription_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def premium_referral_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Premium & Referral submenu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="👑 **Premium & Referral**\n\nSelect an option:",
        reply_markup=build_premium_referral_menu(),
        parse_mode='Markdown'
    )


async def referral_program_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral program details with referral link"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Generate referral link using bot username (assuming bot is @CryptoMentorAI_bot)
    bot_username = context.bot.username or "CryptoMentorAI_bot"
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    referral_text = f"""🎁 **REFERRAL PROGRAM - Ajak Teman Dapatkan Bonus!**

👋 Halo **{user_name}**!

Dapatkan **PREMIUM GRATIS** dengan mengajak teman menggunakan link referral Anda!

📋 **Cara Kerja:**
• Setiap teman yang join menggunakan link Anda = +5 Credits
• Teman mendapatkan 10 bonus signals gratis
• Anda mendapatkan komisi 10% dari premium mereka

🔗 **Your Referral Link:**
```
{referral_link}
```

📊 **Your Referral Stats:**
• Total Referrals: 0
• Total Earnings: $0
• Lifetime Commissions: $0

🎯 **Tier System:**
• Bronze: 1-5 referrals (5% bonus)
• Silver: 6-15 referrals (8% bonus + Badge)
• Gold: 16-50 referrals (12% bonus + Badge)
• Platinum: 50+ referrals (15% bonus + Exclusive)

💡 **Pro Tip:** 
Share your link dengan crypto community untuk earning maksimal!

✅ Premium aktif - Akses unlimited, kredit tidak terpakai"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data="referral_copy_link")],
        [InlineKeyboardButton("📊 My Earnings", callback_data=PREMIUM_EARNINGS)],
        [InlineKeyboardButton("🔙 Back", callback_data=PREMIUM_REFERRAL)],
    ]
    
    await query.edit_message_text(
        text=referral_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def premium_earnings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium earnings and referral statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    earnings_text = f"""💰 **PREMIUM EARNINGS REPORT**

👤 **{user_name}** (ID: {user_id})

📈 **Revenue Summary:**
• This Month: $0.00
• Last Month: $0.00
• Total Lifetime: $0.00
• Pending Balance: $0.00

📊 **Referral Performance:**
• Active Referrals: 0
• Inactive (30+ days): 0
• Conversion Rate: 0%
• Avg. Value per Referral: $0

💳 **Payment History:**
• Last Withdrawal: Never
• Withdrawal Method: Bank Transfer
• Minimum Threshold: $50

🎯 **Performance Metrics:**
• Click-through Rate (CTR): 0%
• Signup Conversion: 0%
• Premium Upgrade Rate: 0%

📅 **Recent Transactions:**
(No transactions yet)

💡 **Tips to Increase Earnings:**
1. Share di Telegram crypto groups
2. Buat content di Twitter/YouTube dengan link
3. Ajak network Anda untuk join
4. Maksimalkan dengan tier system

⚠️ **Withdrawal Policy:**
• Minimum: $50 USD
• Proses: 3-5 business days
• Fee: 2% untuk bank transfer

✅ Ready to earn? Share your referral link!"""
    
    keyboard = [
        [InlineKeyboardButton("🎁 Back to Referral", callback_data=REFERRAL_PROGRAM)],
        [InlineKeyboardButton("🔙 Main Menu", callback_data=PREMIUM_REFERRAL)],
    ]
    
    await query.edit_message_text(
        text=earnings_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def referral_copy_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral link copy notification"""
    query = update.callback_query
    user_id = update.effective_user.id
    bot_username = context.bot.username or "CryptoMentorAI_bot"
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    await query.answer(f"✅ Link copied! {referral_link}", show_alert=True)


async def ask_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Ask AI submenu with CryptoMentor AI options"""
    query = update.callback_query
    await query.answer()
    
    ai_menu_text = """🤖 **CryptoMentor AI Assistant**

⚡ **Powered by Cerebras AI** (Ultra Fast!)
Response time: ~0.4 detik (70x lebih cepat!)

Pilih fitur AI yang ingin Anda gunakan:

💬 **Chat dengan AI**
   Tanya apa saja tentang crypto & trading

📊 **Analisis Market AI**
   Analisis mendalam untuk coin tertentu

🌍 **Market Summary AI**
   Ringkasan kondisi market global

❓ **Panduan AI**
   Cara menggunakan fitur AI

🆓 GRATIS untuk semua user!
Pilih opsi di bawah:"""
    
    await query.edit_message_text(
        text=ai_menu_text,
        reply_markup=build_ask_ai_menu(),
        parse_mode='Markdown'
    )


async def ask_cryptomentor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for AI question"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="💬 **Ask CryptoMentor AI**\n\nType your question below:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=ASK_AI)]])
    )
    
    context.user_data['action'] = 'ask_ai'
    context.user_data['awaiting_input'] = True


async def ai_chat_prompt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for AI chat question"""
    query = update.callback_query
    await query.answer()
    
    chat_text = """💬 **Chat dengan CryptoMentor AI**

Ketik pertanyaan Anda tentang crypto & trading.

**Contoh:**
• Bagaimana kondisi market Bitcoin hari ini?
• Apa itu support dan resistance?
• Jelaskan strategi DCA untuk pemula
• Kapan waktu terbaik untuk buy the dip?

Ketik pertanyaan Anda di bawah:"""
    
    await query.edit_message_text(
        text=chat_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=ASK_AI)]]),
        parse_mode='Markdown'
    )
    
    set_user_state(context, 'action', 'ai_chat')
    set_user_state(context, 'awaiting_input', True)


async def ai_analyze_prompt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for symbol to analyze"""
    query = update.callback_query
    await query.answer()
    
    analyze_text = """📊 **Analisis Market dengan AI**

Ketik symbol coin yang ingin dianalisis.

**Contoh:**
• BTC
• ETH
• SOL
• BNB

Ketik symbol di bawah:"""
    
    await query.edit_message_text(
        text=analyze_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=ASK_AI)]]),
        parse_mode='Markdown'
    )
    
    set_user_state(context, 'action', 'ai_analyze')
    set_user_state(context, 'awaiting_input', True)


async def ai_market_summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI market summary directly"""
    query = update.callback_query
    await query.answer("⏳ Generating market summary...")
    
    try:
        # Import handler
        from app.handlers_deepseek import handle_ai_market_summary
        
        # Call the handler directly
        await handle_ai_market_summary(update, context)
        
    except Exception as e:
        await query.edit_message_text(
            text=f"❌ Error: {str(e)}\n\nSilakan coba lagi.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=ASK_AI)]]),
            parse_mode='Markdown'
        )


async def ai_guide_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI guide"""
    query = update.callback_query
    await query.answer()
    
    guide_text = """❓ **Panduan CryptoMentor AI**

**Powered by Cerebras AI** ⚡
Ultra-fast response (~0.4 detik!)

**3 Fitur Utama:**

1️⃣ **Chat dengan AI** 💬
   Command: `/chat <pertanyaan>`
   Contoh: `/chat Apa itu bull market?`
   
2️⃣ **Analisis Market** 📊
   Command: `/ai <symbol>`
   Contoh: `/ai BTC`
   
3️⃣ **Market Summary** 🌍
   Command: `/aimarket`
   Ringkasan kondisi market global

**Tips:**
✅ Tanya hal spesifik untuk jawaban lebih baik
✅ Gunakan bahasa Indonesia atau English
✅ AI memberikan analisis, bukan jaminan profit
✅ Response time: ~0.4s (70x lebih cepat!)

**Biaya:**
🆓 GRATIS untuk semua user!
(Cerebras AI free tier)"""
    
    await query.edit_message_text(
        text=guide_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=ASK_AI)]]),
        parse_mode='Markdown'
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Settings submenu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="⚙️ **Settings**\n\nSelect an option:",
        reply_markup=build_settings_menu(),
        parse_mode='Markdown'
    )


async def change_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language options"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
            InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="lang_id"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data=SETTINGS)],
    ]
    
    await query.edit_message_text(
        text="🌐 **Choose Language / Pilih Bahasa:**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def lang_en_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set language to English"""
    query = update.callback_query
    await query.answer("✅ Language set to English")
    
    user_id = update.effective_user.id
    context.user_data['language'] = 'en'
    
    # Save to database
    try:
        from app.users_repo import update_user_language
        update_user_language(user_id, 'en')
    except:
        pass
    
    await query.edit_message_text(
        text="🌐 **Language Changed**\n\n✅ Your language is now set to **English**\n\nAll messages will be in English.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data=SETTINGS)]]),
        parse_mode='Markdown'
    )


async def lang_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set language to Bahasa Indonesia"""
    query = update.callback_query
    await query.answer("✅ Bahasa diubah ke Bahasa Indonesia")
    
    user_id = update.effective_user.id
    context.user_data['language'] = 'id'
    
    # Save to database
    try:
        from app.users_repo import update_user_language
        update_user_language(user_id, 'id')
    except:
        pass
    
    await query.edit_message_text(
        text="🌐 **Bahasa Diubah**\n\n✅ Bahasa Anda sekarang diatur ke **Bahasa Indonesia**\n\nSemua pesan akan dalam Bahasa Indonesia.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali ke Pengaturan", callback_data=SETTINGS)]]),
        parse_mode='Markdown'
    )


# =============================================================================
# SYMBOL SELECTION CALLBACK
# =============================================================================

async def symbol_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle symbol selection from buttons"""
    query = update.callback_query
    symbol = query.data.replace("symbol_", "").upper()
    
    if symbol == "CUSTOM":
        await query.answer("Type the symbol (e.g., BTCUSDT):")
        context.user_data['awaiting_manual_symbol'] = True
        context.user_data['current_action'] = context.user_data.get('action', 'analyze')
        return
    
    await query.answer(f"Selected: {symbol}")
    
    action = context.user_data.get('action')
    step = context.user_data.get('step')
    user_id = update.effective_user.id
    
    # Add USDT if not present
    if not any(symbol.endswith(pair) for pair in ['USDT', 'BUSD', 'USDC']):
        symbol += 'USDT'
    
    # Different flows based on action
    if action == 'price':
        await query.edit_message_text(text=f"📈 Fetching price for {symbol}...", reply_markup=None)
        context.user_data['symbol'] = symbol
        
    elif action == 'analyze':
        # Check and deduct credits (20 for Spot Analysis)
        try:
            from app.credits_guard import require_credits
            ok, remain, msg = require_credits(user_id, 20)
            if not ok:
                keyboard = [[InlineKeyboardButton("⭐ Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                            [InlineKeyboardButton("🔙 Back", callback_data=TRADING_ANALYSIS)]]
                await query.edit_message_text(
                    text=f"❌ {msg}\n\n⭐ Upgrade ke Premium untuk akses unlimited!",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            print(f"✅ Credit deducted for user {user_id}: 20 credits, remaining: {remain}")
        except Exception as e:
            print(f"❌ Credit check error for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                text="❌ Sistem kredit sedang bermasalah. Silakan coba lagi nanti.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=TRADING_ANALYSIS)]])
            )
            return
        
        user_tz = get_user_timezone_from_context(context, user_id)
        est_time = get_estimated_time_message(5, user_tz)
        
        await query.edit_message_text(
            text=f"📊 <b>Analyzing {symbol}...</b>\n\n🔍 Detecting S&D zones...\n{est_time}",
            reply_markup=None,
            parse_mode='HTML'
        )
        
        # Run actual spot analysis
        try:
            from snd_zone_detector import detect_snd_zones
            snd_result = detect_snd_zones(symbol, "1h", limit=100)
            
            if 'error' in snd_result:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=f"❌ <b>Error:</b> {snd_result['error']}",
                    parse_mode='HTML'
                )
                return
            
            current_price = snd_result.get('current_price', 0)
            demand_zones = snd_result.get('demand_zones', [])
            supply_zones = snd_result.get('supply_zones', [])
            
            def fmt_price(p):
                if p >= 1000: return f"${p:,.2f}"
                elif p >= 1: return f"${p:,.4f}"
                elif p >= 0.0001: return f"${p:.6f}"
                else: return f"${p:.8f}"
            
            display_symbol = symbol.replace('USDT', '')
            response = f"📊 <b>Spot Signal – {display_symbol} (1H)</b>\n\n💰 <b>Price:</b> {fmt_price(current_price)}\n\n🟢 <b>BUY ZONES</b>\n"
            
            zone_labels = [("A", "Strong", "40%"), ("B", "Discount", "35%"), ("C", "Deep", "25%")]
            sorted_demands = sorted(demand_zones, key=lambda z: abs(current_price - z.midpoint))
            
            for i, zone in enumerate(sorted_demands[:3]):
                label, desc, alloc = zone_labels[i] if i < len(zone_labels) else ("", "", "")
                response += f"\n<b>Zone {label}</b> ({desc}) — {alloc}\n"
                response += f"  📍 Entry: {fmt_price(zone.low)} - {fmt_price(zone.high)}\n"
                sl = zone.low * 0.97
                response += f"  🛑 SL: {fmt_price(sl)}\n"
            
            if not demand_zones:
                response += "No active demand zones\n"
            
            response += "\n🔴 <b>TAKE PROFIT</b>\n"
            if supply_zones:
                closest_supply = min(supply_zones, key=lambda z: abs(current_price - z.midpoint))
                response += f"  🎯 TP: {fmt_price(closest_supply.low)} - {fmt_price(closest_supply.high)}\n"
            else:
                response += "No active supply zone\n"
            
            response += f"\n💳 <i>Credit terpakai: 20 | Sisa: {remain}</i>"
            response += "\n\n<i>⚠️ Spot only • LIMIT order at zone</i>"
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=TRADING_ANALYSIS)]]
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=response,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Spot analysis error: {e}")
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"❌ Error: {str(e)[:100]}",
                parse_mode='HTML'
            )
        
    elif action == 'futures':
        # Check and deduct credits (20 for Futures Analysis)
        try:
            from app.credits_guard import require_credits
            ok, remain, msg = require_credits(user_id, 20)
            if not ok:
                keyboard = [[InlineKeyboardButton("⭐ Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                            [InlineKeyboardButton("🔙 Back", callback_data=TRADING_ANALYSIS)]]
                await query.edit_message_text(
                    text=f"❌ {msg}\n\n⭐ Upgrade ke Premium untuk akses unlimited!",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            print(f"✅ Credit deducted for user {user_id}: 20 credits (futures), remaining: {remain}")
        except Exception as e:
            print(f"❌ Credit check error for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                text="❌ Sistem kredit sedang bermasalah. Silakan coba lagi nanti.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=TRADING_ANALYSIS)]])
            )
            return
        
        user_tz = get_user_timezone_from_context(context, user_id)
        est_time = get_estimated_time_message(5, user_tz)
        
        await query.edit_message_text(
            text=f"📉 <b>Analyzing Futures {symbol}...</b>\n\n🔍 Detecting S&D zones...\n{est_time}",
            reply_markup=None,
            parse_mode='HTML'
        )
        
        # Run actual futures analysis
        try:
            from snd_zone_detector import detect_snd_zones
            snd_result = detect_snd_zones(symbol, "1h", limit=100)
            
            if 'error' in snd_result:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=f"❌ <b>Error:</b> {snd_result['error']}",
                    parse_mode='HTML'
                )
                return
            
            current_price = snd_result.get('current_price', 0)
            demand_zones = snd_result.get('demand_zones', [])
            supply_zones = snd_result.get('supply_zones', [])
            signal_type = snd_result.get('entry_signal')
            
            def fmt_price(p):
                if p >= 1000: return f"${p:,.2f}"
                elif p >= 1: return f"${p:,.4f}"
                elif p >= 0.0001: return f"${p:.6f}"
                else: return f"${p:.8f}"
            
            display_symbol = symbol.replace('USDT', '')
            response = f"📉 <b>Futures Signal – {display_symbol} (1H)</b>\n\n💰 <b>Price:</b> {fmt_price(current_price)}\n"
            
            # Demand zones (LONG setup)
            if demand_zones:
                response += f"\n🟢 <b>LONG SETUP</b> ({len(demand_zones)} zone)\n"
                for i, zone in enumerate(demand_zones[:2], 1):
                    zone_width = zone.high - zone.low
                    sl = zone.low - (zone_width * 0.5)
                    tp1 = current_price + (zone_width * 1.5)
                    tp2 = current_price + (zone_width * 2.5)
                    response += f"\n<b>Zone {i}:</b>\n"
                    response += f"  📍 Entry: {fmt_price(zone.low)} - {fmt_price(zone.high)}\n"
                    response += f"  🛑 SL: {fmt_price(sl)}\n"
                    response += f"  🎯 TP1: {fmt_price(tp1)} | TP2: {fmt_price(tp2)}\n"
            
            # Supply zones (SHORT setup)
            if supply_zones:
                response += f"\n🔴 <b>SHORT SETUP</b> ({len(supply_zones)} zone)\n"
                for i, zone in enumerate(supply_zones[:2], 1):
                    zone_width = zone.high - zone.low
                    sl = zone.high + (zone_width * 0.5)
                    tp1 = current_price - (zone_width * 1.5)
                    tp2 = current_price - (zone_width * 2.5)
                    response += f"\n<b>Zone {i}:</b>\n"
                    response += f"  📍 Entry: {fmt_price(zone.low)} - {fmt_price(zone.high)}\n"
                    response += f"  🛑 SL: {fmt_price(sl)}\n"
                    response += f"  🎯 TP1: {fmt_price(tp1)} | TP2: {fmt_price(tp2)}\n"
            
            if signal_type:
                response += f"\n⚡ <b>Signal:</b> {signal_type}\n"
            
            response += f"\n💳 <i>Credit terpakai: 20 | Sisa: {remain}</i>"
            response += "\n\n<i>⚠️ Futures • LIMIT order at zone</i>"
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=TRADING_ANALYSIS)]]
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=response,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Futures analysis error: {e}")
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"❌ Error: {str(e)[:100]}",
                parse_mode='HTML'
            )
        
    elif action == 'add_coin' and step == 'symbol':
        await query.edit_message_text(
            text=f"➕ **Add {symbol}**\n\n**Step 2:** How much {symbol} do you have?\n\nEnter amount (e.g., 1.5)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=MAIN_MENU)]])
        )
        context.user_data['symbol'] = symbol
        context.user_data['step'] = 'amount'
        context.user_data['awaiting_amount'] = True


# =============================================================================
# HANDLER REGISTRATION (Add to bot.py)
# =============================================================================

def register_menu_handlers(application):
    """
    Register all menu callbacks with the Telegram application
    
    Call this function in your bot.py main setup:
    
    Example:
        from menu_handler import register_menu_handlers
        
        application = Application.builder().token(TOKEN).build()
        register_menu_handlers(application)
    """
    
    # Main callbacks
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern=f"^{MAIN_MENU}$"))
    
    # Category callbacks
    application.add_handler(CallbackQueryHandler(price_market_callback, pattern=f"^{PRICE_MARKET}$"))
    application.add_handler(CallbackQueryHandler(trading_analysis_callback, pattern=f"^{TRADING_ANALYSIS}$"))
    application.add_handler(CallbackQueryHandler(futures_signals_callback, pattern=f"^{FUTURES_SIGNALS}$"))
    application.add_handler(CallbackQueryHandler(portfolio_credits_callback, pattern=f"^{PORTFOLIO_CREDITS}$"))
    application.add_handler(CallbackQueryHandler(premium_referral_callback, pattern=f"^{PREMIUM_REFERRAL}$"))
    application.add_handler(CallbackQueryHandler(ask_ai_callback, pattern=f"^{ASK_AI}$"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern=f"^{SETTINGS}$"))
    
    # Price & Market
    application.add_handler(CallbackQueryHandler(check_price_callback, pattern=f"^{CHECK_PRICE}$"))
    application.add_handler(CallbackQueryHandler(market_overview_callback, pattern=f"^{MARKET_OVERVIEW}$"))
    
    # Trading Analysis
    application.add_handler(CallbackQueryHandler(spot_analysis_callback, pattern=f"^{SPOT_ANALYSIS}$"))
    application.add_handler(CallbackQueryHandler(futures_analysis_callback, pattern=f"^{FUTURES_ANALYSIS}$"))
    
    # Futures Signals
    application.add_handler(CallbackQueryHandler(multi_coin_signals_callback, pattern=f"^{MULTI_COIN_SIGNALS}$"))
    application.add_handler(CallbackQueryHandler(auto_signal_info_callback, pattern=f"^{AUTO_SIGNAL_INFO}$"))
    
    # Portfolio & Credits
    application.add_handler(CallbackQueryHandler(my_portfolio_callback, pattern=f"^{MY_PORTFOLIO}$"))
    application.add_handler(CallbackQueryHandler(add_coin_callback, pattern=f"^{ADD_COIN}$"))
    application.add_handler(CallbackQueryHandler(check_credits_callback, pattern=f"^{CHECK_CREDITS}$"))
    application.add_handler(CallbackQueryHandler(upgrade_premium_callback, pattern=f"^{UPGRADE_PREMIUM}$"))
    
    # Premium & Referral
    application.add_handler(CallbackQueryHandler(referral_program_callback, pattern=f"^{REFERRAL_PROGRAM}$"))
    application.add_handler(CallbackQueryHandler(premium_earnings_callback, pattern=f"^{PREMIUM_EARNINGS}$"))
    
    # AI CALLBACKS RE-ENABLED with Cerebras (ultra-fast)
    application.add_handler(CallbackQueryHandler(ask_ai_callback, pattern=f"^{ASK_AI}$"))
    application.add_handler(CallbackQueryHandler(ai_chat_prompt_callback, pattern="^ai_chat_prompt$"))
    application.add_handler(CallbackQueryHandler(ai_analyze_prompt_callback, pattern="^ai_analyze_prompt$"))
    application.add_handler(CallbackQueryHandler(ai_market_summary_callback, pattern="^ai_market_summary$"))
    application.add_handler(CallbackQueryHandler(ai_guide_callback, pattern="^ai_guide$"))
    
    # Settings & Language
    application.add_handler(CallbackQueryHandler(change_language_callback, pattern=f"^{CHANGE_LANGUAGE}$"))
    application.add_handler(CallbackQueryHandler(lang_en_callback, pattern="^lang_en$"))
    application.add_handler(CallbackQueryHandler(lang_id_callback, pattern="^lang_id$"))
    
    # Referral
    application.add_handler(CallbackQueryHandler(referral_copy_link_callback, pattern="^referral_copy_link$"))
    
    # Symbol selection
    application.add_handler(CallbackQueryHandler(symbol_callback, pattern=r"^symbol_"))
    
    logger.info("✅ Menu handlers registered successfully")
