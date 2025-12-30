# -*- coding: utf-8 -*-
"""
CryptoMentor AI 2.0 - Menu Callback Handlers
Handles all InlineKeyboard interactions and maps to existing commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from menu_system import (
    MenuBuilder, get_menu_text, MAIN_MENU, PRICE_MARKET, TRADING_ANALYSIS,
    FUTURES_SIGNALS, PORTFOLIO_CREDITS, PREMIUM_REFERRAL, ASK_AI_MENU,
    SETTINGS_MENU, CHECK_PRICE, MARKET_OVERVIEW, SPOT_ANALYSIS,
    FUTURES_ANALYSIS, MULTI_COIN_SIGNALS, AUTO_SIGNAL_INFO, MY_PORTFOLIO,
    ADD_COIN, CHECK_CREDITS, UPGRADE_PREMIUM, REFERRAL_PROGRAM,
    PREMIUM_EARNINGS, ASK_AI, CHANGE_LANGUAGE, POPULAR_SYMBOLS
)
import asyncio

class MenuCallbackHandler:
    """Handles all menu callback queries"""

    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback query handler"""
        query = update.callback_query
        await query.answer()

        callback_data = query.data
        user_id = query.from_user.id

        try:
            # Main menu navigation
            if callback_data == MAIN_MENU:
                await self.show_main_menu(query, context)
            elif callback_data == PRICE_MARKET:
                await self.show_price_market_menu(query, context)
            elif callback_data == TRADING_ANALYSIS:
                await self.show_trading_analysis_menu(query, context)
            elif callback_data == FUTURES_SIGNALS:
                await self.show_futures_signals_menu(query, context)
            elif callback_data == PORTFOLIO_CREDITS:
                await self.show_portfolio_credits_menu(query, context)
            elif callback_data == PREMIUM_REFERRAL:
                await self.show_premium_referral_menu(query, context)
            elif callback_data == ASK_AI_MENU:
                await self.show_ask_ai_menu(query, context)
            elif callback_data == SETTINGS_MENU:
                await self.show_settings_menu(query, context)

            # Action handlers
            elif callback_data == CHECK_PRICE:
                await self.handle_check_price(query, context)
            elif callback_data == MARKET_OVERVIEW:
                await self.handle_market_overview(query, context)
            elif callback_data == SPOT_ANALYSIS:
                await self.handle_spot_analysis(query, context)
            elif callback_data == FUTURES_ANALYSIS:
                await self.handle_futures_analysis(query, context)
            elif callback_data == MULTI_COIN_SIGNALS:
                await self.handle_multi_coin_signals(query, context)
            elif callback_data == AUTO_SIGNAL_INFO:
                await self.handle_auto_signal_info(query, context)
            elif callback_data == MY_PORTFOLIO:
                await self.handle_my_portfolio(query, context)
            elif callback_data == ADD_COIN:
                await self.handle_add_coin(query, context)
            elif callback_data == CHECK_CREDITS:
                await self.handle_check_credits(query, context)
            elif callback_data == UPGRADE_PREMIUM:
                await self.handle_upgrade_premium(query, context)
            elif callback_data == REFERRAL_PROGRAM:
                await self.handle_referral_program(query, context)
            elif callback_data == PREMIUM_EARNINGS:
                await self.handle_premium_earnings(query, context)
            elif callback_data == ASK_AI:
                await self.handle_ask_ai(query, context)
            elif callback_data == CHANGE_LANGUAGE:
                await self.handle_change_language(query, context)
            elif callback_data == "copy_referral_link":
                await self.handle_copy_referral_link(query, context)
            elif callback_data == "referral_stats":
                await self.handle_referral_stats(query, context)
            elif callback_data == "referral_withdrawal":
                await self.handle_referral_withdrawal(query, context)


            # Symbol selection handlers
            elif callback_data.startswith('symbol_'):
                await self.handle_symbol_selection(query, context)
            elif callback_data == 'manual_symbol':
                await self.handle_manual_symbol(query, context)
            elif callback_data.startswith('futures_'):
                await self.handle_futures_timeframe_selection(query, context)
            elif callback_data.startswith('price_'):
                await self.handle_price_symbol_selection(query, context)
            elif callback_data.startswith('analyze_'):
                await self.handle_analyze_symbol_selection(query, context)

        except Exception as e:
            print(f"Error in callback handler: {e}")
            await query.edit_message_text(
                "❌ Terjadi kesalahan. Silakan coba lagi atau gunakan command manual.",
                reply_markup=MenuBuilder.build_main_menu()
            )

    async def show_main_menu(self, query, context):
        """Show main menu"""
        await query.edit_message_text(
            get_menu_text(MAIN_MENU),
            reply_markup=MenuBuilder.build_main_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_price_market_menu(self, query, context):
        """Show price & market submenu"""
        await query.edit_message_text(
            get_menu_text(PRICE_MARKET),
            reply_markup=MenuBuilder.build_price_market_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_trading_analysis_menu(self, query, context):
        """Show trading analysis submenu"""
        await query.edit_message_text(
            get_menu_text(TRADING_ANALYSIS),
            reply_markup=MenuBuilder.build_trading_analysis_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_futures_signals_menu(self, query, context):
        """Show futures signals submenu"""
        await query.edit_message_text(
            get_menu_text(FUTURES_SIGNALS),
            reply_markup=MenuBuilder.build_futures_signals_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_portfolio_credits_menu(self, query, context):
        """Show portfolio & credits submenu"""
        await query.edit_message_text(
            get_menu_text(PORTFOLIO_CREDITS),
            reply_markup=MenuBuilder.build_portfolio_credits_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_premium_referral_menu(self, query, context):
        """Show premium & referral submenu"""
        await query.edit_message_text(
            get_menu_text(PREMIUM_REFERRAL),
            reply_markup=MenuBuilder.build_premium_referral_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_ask_ai_menu(self, query, context):
        """Show ask AI submenu"""
        await query.edit_message_text(
            get_menu_text(ASK_AI_MENU),
            reply_markup=MenuBuilder.build_ask_ai_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_settings_menu(self, query, context):
        """Show settings submenu"""
        await query.edit_message_text(
            get_menu_text(SETTINGS_MENU),
            reply_markup=MenuBuilder.build_settings_menu(),
            parse_mode='MARKDOWN'
        )

    async def handle_check_price(self, query, context):
        """Handle check price action - show symbol selection"""
        context.user_data['current_action'] = 'price'
        context.user_data['awaiting_symbol'] = True

        await query.edit_message_text(
            "🔹 **Check Price** - Select a cryptocurrency:\n\n"
            "Choose from popular options below or type manually:",
            reply_markup=MenuBuilder.build_symbol_selection(),
            parse_mode='MARKDOWN'
        )

    async def handle_market_overview(self, query, context):
        """Handle market overview - trigger /market command"""
        await query.edit_message_text("⏳ Loading market overview...")

        # Create fake update to trigger market command
        from telegram import User, Chat
        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        # Call market command directly
        await self.bot.market_command(fake_update, context)

    async def handle_spot_analysis(self, query, context):
        """Handle spot analysis - show symbol selection"""
        context.user_data['current_action'] = 'analyze'
        context.user_data['awaiting_symbol'] = True

        await query.edit_message_text(
            "📊 **Spot Analysis (SnD)** - 20 Credits\n\n"
            "Select a cryptocurrency for comprehensive analysis:",
            reply_markup=MenuBuilder.build_symbol_selection(),
            parse_mode='MARKDOWN'
        )

    async def handle_futures_analysis(self, query, context):
        """Handle futures analysis - show symbol selection"""
        context.user_data['current_action'] = 'futures'
        context.user_data['awaiting_symbol'] = True

        await query.edit_message_text(
            "📉 **Futures Analysis (SnD)** - 20 Credits\n\n"
            "Select a cryptocurrency for futures trading analysis:",
            reply_markup=MenuBuilder.build_symbol_selection(),
            parse_mode='MARKDOWN'
        )

    async def handle_multi_coin_signals(self, query, context):
        """Handle multi-coin signals - trigger /futures_signals"""
        await query.edit_message_text("⏳ Generating futures signals...")

        # Create fake update to trigger futures_signals command
        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        # Call futures_signals command directly
        await self.bot.futures_signals_command(fake_update, context)

    async def handle_auto_signal_info(self, query, context):
        """Handle auto signal info"""
        info_text = """👑 **Auto Signal Information**

🤖 **What is Auto Signal?**
Automated trading signals delivered directly to your chat every 5 minutes when high-confidence opportunities are detected.

🎯 **Features:**
• Real-time signal delivery
• Supply & Demand analysis
• Multiple timeframes
• Professional entry/exit points
• Risk management included

🔒 **Availability:**
Currently available for **Lifetime Premium users only**

💎 **How to Access:**
Upgrade to Lifetime Premium via `/subscribe` to unlock this exclusive feature.

📊 **Signal Quality:**
• Minimum 75% confidence
• Advanced SnD algorithms
• Anti-spam protection
• Quality over quantity approach"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Futures Menu", callback_data=FUTURES_SIGNALS)]
        ])

        await query.edit_message_text(
            info_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def handle_my_portfolio(self, query, context):
        """Handle my portfolio - trigger /portfolio"""
        await query.edit_message_text("⏳ Loading your portfolio...")

        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.portfolio_command(fake_update, context)

    async def handle_add_coin(self, query, context):
        """Handle add coin - start step-by-step process"""
        context.user_data['current_action'] = 'add_coin'
        context.user_data['awaiting_symbol'] = True
        context.user_data['step'] = 'symbol'

        await query.edit_message_text(
            "➕ **Add Coin to Portfolio**\n\n"
            "Step 1/2: Select the cryptocurrency to add:",
            reply_markup=MenuBuilder.build_symbol_selection(),
            parse_mode='MARKDOWN'
        )

    async def handle_check_credits(self, query, context):
        """Handle check credits - trigger /credits"""
        await query.edit_message_text("⏳ Checking your credits...")

        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.credits_command(fake_update, context)

    async def handle_upgrade_premium(self, query, context):
        """Handle upgrade premium - trigger /subscribe"""
        await query.edit_message_text("⏳ Loading premium options...")

        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.subscribe_command(fake_update, context)

    async def handle_referral_program(self, query, context):
        """Handle referral program - trigger /referral"""
        await query.edit_message_text("⏳ Loading referral information...")

        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.referral_command(fake_update, context)

    async def handle_premium_earnings(self, query, context):
        """Handle premium earnings"""
        # For now, show a message since this command might not exist
        earnings_text = """💰 **Premium Earnings Dashboard**

🎯 **Referral Earnings:**
• Total Referrals: 0
• Credits Earned: 0
• Money Earned: Rp 0

💡 **How to Earn:**
1. Share your referral link from `/referral`
2. When referred users subscribe premium, you earn money
3. All users give you credits immediately

📊 **Current Status:**
Premium users earn Rp 10,000 per premium referral

🔧 **Note:** Full earnings dashboard coming in future updates!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Premium Menu", callback_data=PREMIUM_REFERRAL)]
        ])

        await query.edit_message_text(
            earnings_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def handle_ask_ai(self, query, context):
        """Handle ask AI - prompt for question"""
        context.user_data['current_action'] = 'ask_ai'
        context.user_data['awaiting_question'] = True

        prompt_text = """💬 **Ask CryptoMentor AI**

Type your question about cryptocurrency, trading, or blockchain technology.

📚 **Examples:**
• "What is DeFi?"
• "Explain Bitcoin halving"
• "How to read candlestick charts?"
• "What is supply and demand in trading?"

💡 Just type your question in the next message!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data=ASK_AI_MENU)]
        ])

        await query.edit_message_text(
            prompt_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def handle_change_language(self, query, context):
        """Handle change language - trigger /language"""
        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.language_command(fake_update, context)

    async def handle_symbol_selection(self, query, context):
        """Handle symbol selection from popular symbols"""
        symbol = query.data.replace('symbol_', '')
        current_action = context.user_data.get('current_action', '')

        if current_action == 'price':
            await self.execute_price_command(query, context, symbol)
        elif current_action == 'analyze':
            await self.execute_analyze_command(query, context, symbol)
        elif current_action == 'futures':
            await self.show_futures_timeframe_selection(query, context, symbol)
        elif current_action == 'add_coin':
            await self.handle_add_coin_amount(query, context, symbol)

    async def handle_manual_symbol(self, query, context):
        """Handle manual symbol input"""
        current_action = context.user_data.get('current_action', '')
        context.user_data['awaiting_manual_symbol'] = True

        action_text = {
            'price': 'check price for',
            'analyze': 'analyze',
            'futures': 'futures analysis for',
            'add_coin': 'add to portfolio'
        }.get(current_action, 'process')

        prompt_text = f"""⌨️ **Manual Symbol Input**

Type the cryptocurrency symbol you want to {action_text}.

💡 **Examples:** BTC, ETH, DOGE, SHIB, etc.

Just type the symbol in your next message!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data=MAIN_MENU)]
        ])

        await query.edit_message_text(
            prompt_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def show_futures_timeframe_selection(self, query, context, symbol):
        """Show timeframe selection for futures analysis"""
        await query.edit_message_text(
            f"📉 **Futures Analysis for {symbol}**\n\n"
            f"Select your preferred timeframe:",
            reply_markup=MenuBuilder.build_timeframe_selection(symbol),
            parse_mode='MARKDOWN'
        )

    async def handle_futures_timeframe_selection(self, query, context):
        """Handle futures timeframe selection"""
        # Parse callback data: futures_SYMBOL_TIMEFRAME
        parts = query.data.split('_')
        if len(parts) >= 3:
            symbol = parts[1]
            timeframe = parts[2]

            await query.edit_message_text("⏳ Analyzing futures data...")

            # Use existing futures callback from bot.py
            await self.bot.handle_callback_query(
                Update(update_id=999999, callback_query=query),
                context
            )

    async def handle_add_coin_amount(self, query, context, symbol):
        """Handle amount input for add coin"""
        context.user_data['symbol'] = symbol
        context.user_data['step'] = 'amount'
        context.user_data['awaiting_amount'] = True

        prompt_text = f"""➕ **Add {symbol} to Portfolio**

Step 2/2: Enter the amount of {symbol} you own.

💡 **Examples:**
• 0.5 (for 0.5 {symbol})
• 100 (for 100 {symbol})
• 0.001234 (for small amounts)

Just type the number in your next message!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data=PORTFOLIO_CREDITS)]
        ])

        await query.edit_message_text(
            prompt_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def execute_price_command(self, query, context, symbol):
        """Execute price command for selected symbol"""
        await query.edit_message_text(f"⏳ Fetching {symbol} price...")

        # Create fake context with args
        context.args = [symbol]
        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.price_command(fake_update, context)

    async def execute_analyze_command(self, query, context, symbol):
        """Execute analyze command for selected symbol"""
        await query.edit_message_text(f"⏳ Analyzing {symbol}...")

        # Create fake context with args
        context.args = [symbol]
        fake_update = Update(
            update_id=999999,
            message=query.message,
            callback_query=query
        )

        await self.bot.analyze_command(fake_update, context)

    async def handle_copy_referral_link(self, query, context):
        """Handle copy referral link"""
        user_id = query.from_user.id
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username or "CryptoMentorAI_bot"
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

        await query.answer(
            f"✅ Link copied!\n{referral_link}",
            show_alert=True
        )

    async def handle_referral_stats(self, query, context):
        """Handle detailed referral statistics"""
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "User"

        # Get detailed stats from database
        total_referrals = 0
        active_referrals = 0
        total_earnings = 0
        this_month_earnings = 0

        try:
            from database import Database
            db = Database()
            stats = db.get_detailed_referral_stats(user_id)
            total_referrals = stats.get('total_referrals', 0)
            active_referrals = stats.get('active_referrals', 0)
            total_earnings = stats.get('total_earnings', 0)
            this_month_earnings = stats.get('this_month_earnings', 0)
        except:
            pass

        # Determine tier
        tier_info = self.get_referral_tier(total_referrals)

        stats_text = f"""📊 **STATISTIK REFERRAL DETAIL**

👤 **{user_name}** (ID: {user_id})

🎯 **Performance Overview:**
• Total Referrals: {total_referrals}
• Active Referrals (30 hari): {active_referrals}
• Conversion Rate: {(active_referrals/max(total_referrals,1)*100):.1f}%
• Success Rate: {'🟢 Excellent' if total_referrals > 10 else '🟡 Good' if total_referrals > 5 else '🔴 Needs Improvement'}

💰 **Earnings Summary:**
• Bulan Ini: Rp {this_month_earnings:,}
• Total Lifetime: Rp {total_earnings:,}
• Rata-rata per Referral: Rp {(total_earnings/max(total_referrals,1)):,.0f}
• Status Withdrawal: {'✅ Available' if total_earnings >= 50000 else '⏳ Minimum Rp 50,000'}

{tier_info}

📈 **Tips Meningkatkan Performa:**
• Share link di 3+ grup crypto berbeda
• Buat tutorial penggunaan bot
• Ajak teman yang aktif trading
• Konsisten share 1x setiap hari

🎁 **Bonus Berikutnya:**
• {10-total_referrals%10} referral lagi untuk bonus tier!
• Target: {((total_referrals//10)+1)*10} referrals

⚡ **Quick Actions:**
• Copy link dan share sekarang
• Invite 5 teman untuk bonus instant credits
• Upgrade ke premium untuk earning 2x lipat"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("📋 Copy Link", callback_data="copy_referral_link")],
            [InlineKeyboardButton("🔙 Back", callback_data="referral_program")],
        ]

        await query.edit_message_text(
            text=stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

    async def handle_referral_withdrawal(self, query, context):
        """Handle referral withdrawal request"""
        user_id = query.from_user.id

        try:
            from database import Database
            db = Database()
            stats = db.get_referral_stats(user_id)
            total_earnings = stats.get('total_earnings', 0)
        except:
            total_earnings = 0

        if total_earnings < 50000:
            await query.answer(
                f"⚠️ Minimum withdrawal Rp 50,000\nSaldo Anda: Rp {total_earnings:,}",
                show_alert=True
            )
            return

        withdrawal_text = f"""💰 **WITHDRAWAL REFERRAL EARNINGS**

💳 **Saldo Tersedia:** Rp {total_earnings:,}

📝 **Metode Withdrawal:**
• Bank Transfer (BCA, BNI, BRI, Mandiri)
• E-Wallet (OVO, DANA, GoPay)
• Crypto (USDT TRC20)

⏱️ **Processing Time:**
• Bank Transfer: 1-3 hari kerja
• E-Wallet: Instant - 24 jam  
• Crypto: 2-6 jam

💼 **Syarat Withdrawal:**
• Minimum: Rp 50,000
• Fee admin: Rp 2,500 (bank) / Rp 1,000 (e-wallet) / 1 USDT (crypto)
• KYC: Wajib untuk withdrawal pertama

📋 **Cara Request Withdrawal:**
1. Hubungi admin: @cryptomentor_admin
2. Kirim: "WITHDRAWAL + JUMLAH + METODE"
3. Upload bukti identitas (KTP/SIM)
4. Tunggu konfirmasi dan transfer

⚠️ **Penting:**
• Pastikan data bank/e-wallet benar
• Screenshot chat ini sebagai bukti
• Withdrawal processed maksimal 7 hari kerja"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/cryptomentor_admin")],
            [InlineKeyboardButton("📊 Check Balance", callback_data="referral_stats")],
            [InlineKeyboardButton("🔙 Back", callback_data="referral_program")],
        ]

        await query.edit_message_text(
            text=withdrawal_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

    def get_referral_tier(self, total_referrals):
        """Get referral tier information"""
        if total_referrals >= 50:
            return """💎 **DIAMOND TIER** (50+ referrals)
• +25% bonus credits
• Lifetime premium benefits  
• Exclusive Diamond community
• Priority customer support"""
        elif total_referrals >= 26:
            return """🥇 **GOLD TIER** (26-50 referrals)
• +15% bonus credits
• VIP support channel
• Premium features trial
• Gold badge di profile"""
        elif total_referrals >= 11:
            return """🥈 **SILVER TIER** (11-25 referrals)
• +10% bonus credits
• Early access features
• Silver badge di profile
• Beta tester access"""
        elif total_referrals >= 1:
            return """🥉 **BRONZE TIER** (1-10 referrals)
• +5% bonus credits
• Bronze badge di profile
• Member community access"""
        else:
            return """⭐ **STARTER TIER** (0 referrals)
• Ready to earn rewards
• Join sekarang dan mulai earning!"""


def register_menu_handlers(application, bot_instance):
    """Register all menu callback handlers"""
    menu_handler = MenuCallbackHandler(bot_instance)

    # Register the main callback handler
    application.add_handler(
        CallbackQueryHandler(menu_handler.handle_callback_query)
    )

    print("✅ Menu system handlers registered successfully")