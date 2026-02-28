# -*- coding: utf-8 -*-
"""
CryptoMentor AI 3.0 - Menu Callback Handlers
Handles all InlineKeyboard interactions and maps to existing commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from menu_system import (
    MenuBuilder, get_menu_text, MAIN_MENU, PRICE_MARKET, TRADING_ANALYSIS,
    FUTURES_SIGNALS, PORTFOLIO_CREDITS, PREMIUM_REFERRAL, ASK_AI_MENU,
    AI_AGENT_MENU, SETTINGS_MENU, CHECK_PRICE, MARKET_OVERVIEW, SPOT_ANALYSIS,
    FUTURES_ANALYSIS, MULTI_COIN_SIGNALS, AUTO_SIGNAL_INFO, MY_PORTFOLIO,
    ADD_COIN, CHECK_CREDITS, UPGRADE_PREMIUM, REFERRAL_PROGRAM,
    PREMIUM_EARNINGS, ASK_AI, CHANGE_LANGUAGE, TIME_SETTINGS, TIMEZONES, POPULAR_SYMBOLS,
    AUTOMATON_SPAWN, AUTOMATON_STATUS, AUTOMATON_DEPOSIT, AUTOMATON_LOGS
)
import asyncio

class MenuCallbackHandler:
    """Handles all menu callback queries"""

    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback query handler with deduplication"""
        query = update.callback_query
        callback_data = query.data
        
        print(f"🔍 DEBUG: Callback received - data: {callback_data}, user: {query.from_user.id}")
        
        # DEDUPLICATION CHECK - Prevent duplicate processing
        query_id = query.id
        if not hasattr(context, 'bot_data'):
            context.bot_data = {}
        
        processed_queries = context.bot_data.get('processed_queries', set())
        
        if query_id in processed_queries:
            print(f"  Duplicate query detected and skipped: {query_id}")
            # Don't answer again, just return
            return
        
        # Mark as processed IMMEDIATELY
        processed_queries.add(query_id)
        context.bot_data['processed_queries'] = processed_queries
        
        # Clean old queries (keep only last 100 to prevent memory leak)
        if len(processed_queries) > 100:
            # Keep only the most recent 50
            recent = list(processed_queries)[-50:]
            context.bot_data['processed_queries'] = set(recent)
        
        # Answer the callback query to remove loading state (ONCE)
        try:
            await query.answer()
        except Exception as e:
            # Query might be too old or already answered
            if "query is too old" in str(e).lower() or "already" in str(e).lower():
                print(f"  Query already answered or too old: {query_id}")
                return
            # For other errors, log but continue
            print(f"  Error answering query: {e}")
        
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
            elif callback_data == AI_AGENT_MENU:
                await self.show_ai_agent_menu(query, context)
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
            elif callback_data == AUTOMATON_SPAWN:
                await self.handle_automaton_spawn(query, context)
            elif callback_data == AUTOMATON_STATUS:
                await self.handle_automaton_status(query, context)
            elif callback_data == "agent_lineage":
                await self.handle_agent_lineage(query, context)
            elif callback_data == AUTOMATON_DEPOSIT:
                await self.handle_automaton_deposit(query, context)
            elif callback_data == AUTOMATON_LOGS:
                await self.handle_automaton_logs(query, context)
            elif callback_data == "automaton_first_deposit":
                print(f"🔍 DEBUG: Routing to handle_automaton_first_deposit for callback_data: {callback_data}")
                await self.handle_automaton_first_deposit(query, context)
            elif callback_data == "deposit_guide":
                await self.handle_deposit_guide(query, context)
            elif callback_data == "ai_agent_education":
                await self.handle_ai_agent_education(query, context)
            elif callback_data == "ai_agent_faq":
                await self.handle_ai_agent_faq(query, context)
            elif callback_data == "ai_agent_docs":
                await self.handle_ai_agent_docs(query, context)
            elif callback_data == CHANGE_LANGUAGE:
                await self.handle_change_language(query, context)
            elif callback_data == "copy_referral_link":
                await self.handle_copy_referral_link(query, context)
            elif callback_data == "referral_stats":
                await self.handle_referral_stats(query, context)
            elif callback_data == "referral_withdrawal":
                await self.handle_referral_withdrawal(query, context)
            elif callback_data == "referral_guide":
                await self.handle_referral_guide(query, context)
            elif callback_data == "tier_system_guide":
                await self.handle_tier_system_guide(query, context)
            elif callback_data == "advanced_referral_guide":
                await self.handle_advanced_referral_guide(query, context)
            elif callback_data.startswith("set_lang_"):
                await self.handle_set_language(query, context)
            elif callback_data == TIME_SETTINGS:
                await self.handle_time_settings(query, context)
            elif callback_data.startswith("set_tz_"):
                await self.handle_set_timezone(query, context)
            
            # Withdrawal handlers
            elif callback_data == "wd_method_bank":
                await self.handle_withdrawal_method(query, context, 'bank')
            elif callback_data == "wd_method_ewallet":
                await self.handle_withdrawal_method(query, context, 'ewallet')
            elif callback_data == "wd_method_crypto":
                await self.handle_withdrawal_method(query, context, 'crypto')
            elif callback_data == "wd_cancel":
                await self.handle_withdrawal_cancel(query, context)
            elif callback_data.startswith("wd_approve_"):
                await self.handle_admin_withdrawal_approve(query, context)
            elif callback_data.startswith("wd_reject_"):
                await self.handle_admin_withdrawal_reject(query, context)

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
                " Terjadi kesalahan. Silakan coba lagi atau gunakan command manual.",
                reply_markup=MenuBuilder.build_main_menu()
            )

    async def show_main_menu(self, query, context):
        """Show main menu"""
        user_id = query.from_user.id
        from database import Database
        db = Database()
        user_lang = db.get_user_language(user_id)
        
        await query.edit_message_text(
            get_menu_text(MAIN_MENU, user_lang),
            reply_markup=MenuBuilder.build_main_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_price_market_menu(self, query, context):
        """Show price & market submenu"""
        user_id = query.from_user.id
        from database import Database
        db = Database()
        user_lang = db.get_user_language(user_id)
        
        await query.edit_message_text(
            get_menu_text(PRICE_MARKET, user_lang),
            reply_markup=MenuBuilder.build_price_market_menu(),
            parse_mode='MARKDOWN'
        )

    async def show_trading_analysis_menu(self, query, context):
        """Show trading analysis submenu"""
        user_id = query.from_user.id
        from database import Database
        db = Database()
        user_lang = db.get_user_language(user_id)
        
        await query.edit_message_text(
            get_menu_text(TRADING_ANALYSIS, user_lang),
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

    async def show_ai_agent_menu(self, query, context):
        """Show AI Agent submenu - requires lifetime premium"""
        user_id = query.from_user.id
        from database import Database
        from app.admin_status import is_admin
        from app.database import get_user_data
        db = Database()
        user_lang = db.get_user_language(user_id)
        
        # Check if user is admin or lifetime premium
        is_admin_user = is_admin(user_id)
        is_lifetime = False
        
        try:
            if db.supabase_enabled:
                from supabase_client import supabase
                if supabase:
                    user_result = supabase.table('users')\
                        .select('premium_tier')\
                        .eq('user_id', user_id)\
                        .execute()
                    
                    if user_result.data:
                        premium_tier = user_result.data[0].get('premium_tier', '')
                        is_lifetime = (premium_tier == 'lifetime')
        except Exception as e:
            print(f"⚠️ Error checking premium tier: {e}")
        
        # ✅ BETA TEST: AI Agent terbuka untuk SEMUA user
        # Tidak ada pembatasan lifetime premium
        # User hanya perlu deposit untuk spawn agent
        
        # User can access AI Agent menu, check deposit status
        # Check if user has made deposit (minimum $10 = 1000 credits)
        MINIMUM_DEPOSIT_CREDITS = 1000  # $10 USDC = 1000 credits
        has_deposit = False
        user_credits = 0
        
        try:
            if db.supabase_enabled:
                # Import supabase client directly
                from supabase_client import supabase
                
                if supabase:
                    # Check user_credits_balance table for any credits
                    credits_result = supabase.table('user_credits_balance')\
                        .select('available_credits, total_conway_credits')\
                        .eq('user_id', user_id)\
                        .execute()
                    
                    if credits_result.data:
                        balance = credits_result.data[0]
                        available_credits = float(balance.get('available_credits', 0))
                        total_credits = float(balance.get('total_conway_credits', 0))
                        user_credits = max(available_credits, total_credits)
                        
                        # User has sufficient deposit if >= $30 (3000 credits)
                        has_deposit = (user_credits >= MINIMUM_DEPOSIT_CREDITS)
                        print(f"✅ User {user_id} credits check: available={available_credits}, total={total_credits}, has_deposit={has_deposit}")
        except Exception as e:
            print(f"⚠️ Error checking deposit status in user_credits_balance: {e}")
            # Fallback: check old custodial_wallets table for backward compatibility
            try:
                from supabase_client import supabase
                if supabase:
                    wallet_result = supabase.table('custodial_wallets')\
                        .select('balance_usdc, conway_credits')\
                        .eq('user_id', user_id)\
                        .execute()
                    
                    if wallet_result.data:
                        wallet = wallet_result.data[0]
                        balance_usdc = float(wallet.get('balance_usdc', 0))
                        conway_credits = float(wallet.get('conway_credits', 0))
                        user_credits = max(balance_usdc * 100, conway_credits)  # 1 USDC = 100 credits
                        has_deposit = (user_credits >= MINIMUM_DEPOSIT_CREDITS)
                        print(f"✅ User {user_id} fallback check: usdc={balance_usdc}, credits={conway_credits}, has_deposit={has_deposit}")
            except Exception as fallback_error:
                print(f"⚠️ Fallback check also failed: {fallback_error}")
        
        # If no sufficient deposit, show deposit-required menu
        if not has_deposit:
            if user_lang == 'id':
                welcome_text = f"""🤖 **Selamat Datang di AI Agent!**

✅ **Status:** Lifetime Premium Active

💰 **Apa itu AI Agent?**
AI Agent adalah autonomous trading agent yang menggunakan Conway credits sebagai bahan bakar untuk beroperasi.

💵 **Minimum Deposit: $10 USDC**
⚠️ **CATATAN PENTING:**
$10 USDC ini BUKAN pure dana trading, melainkan *bensin operasional AI Agent* Anda.

🔋 **Penggunaan $10 USDC untuk:**
• 💻 *Compute Resources:* Server processing untuk AI analysis
• 🧠 *AI Model Inference:* Biaya running AI decision-making
• 📊 *Real-time Data:* Akses market data & price feeds
• 🔄 *API Calls:* Komunikasi dengan exchange & blockchain
• 📡 *Network Fees:* Gas fees untuk on-chain operations
• 💾 *Storage:* Menyimpan trading history & analytics

📊 **Status Deposit Anda:**
💵 Credits saat ini: {user_credits:,.0f}
🎯 Minimum untuk mulai: 1,000 credits ($10)

💡 **Rekomendasi Deposit:**
• $10 USDC: Testing/trial (1,000 credits) - Minimum
• $20 USDC: Learning phase (2,000 credits)
• $50 USDC: Trading serius (5,000 credits) ⭐ RECOMMENDED
• $100+ USDC: Trading optimal (10,000+ credits)

⚠️ **Mengapa $50+ Disarankan?**
• AI butuh resources untuk analisis mendalam
• API calls untuk data real-time
• Komputasi untuk decision making
• Buffer untuk operasional 24/7

📝 **Cara Deposit:**
1. Klik tombol "💰 Deposit Sekarang" di bawah
2. Deposit USDC (Base Network) ke address yang diberikan
3. Screenshot bukti transfer
4. Kirim ke admin untuk verifikasi
5. Credits akan ditambahkan manual (< 1 jam)

💱 **Conversion Rate:**
💵 1 USDC = 100 Conway Credits
💰 $10 USDC = 1,000 Credits (minimum)
💰 $50 USDC = 5,000 Credits (recommended)

🌐 **Network:**
⛓️ Base Network (WAJIB)

📌 **Catatan:**
• Platform fee: 2% dari deposit
• Operational costs: ~100-500 credits/day
• Semakin besar modal, semakin optimal AI bekerja"""
            else:
                welcome_text = f"""🤖 **Welcome to AI Agent!**

✅ **Status:** Lifetime Premium Active

💰 **What is AI Agent?**
AI Agent is an autonomous trading agent that uses Conway credits as fuel to operate.

💵 **Minimum Deposit: $10 USDC**
⚠️ **IMPORTANT NOTE:**
$10 USDC is NOT pure trading capital, but *operational fuel* for your AI Agent.

🔋 **$10 USDC Usage:**
• 💻 *Compute Resources:* Server processing for AI analysis
• 🧠 *AI Model Inference:* Cost of running AI decision-making
• 📊 *Real-time Data:* Access to market data & price feeds
• 🔄 *API Calls:* Communication with exchanges & blockchain
• 📡 *Network Fees:* Gas fees for on-chain operations
• 💾 *Storage:* Storing trading history & analytics

📊 **Your Deposit Status:**
💵 Current credits: {user_credits:,.0f}
🎯 Minimum to start: 1,000 credits ($10)

💡 **Recommended Deposits:**
• $10 USDC: Testing/trial (1,000 credits) - Minimum
• $20 USDC: Learning phase (2,000 credits)
• $50 USDC: Serious trading (5,000 credits) ⭐ RECOMMENDED
• $100+ USDC: Optimal trading (10,000+ credits)

⚠️ **Why $50+ Recommended?**
• AI needs resources for deep analysis
• API calls for real-time data
• Computation for decision making
• Buffer for 24/7 operations

📝 **How to Deposit:**
1. Click "💰 Deposit Now" button below
2. Deposit USDC (Base Network) to given address
3. Screenshot transfer proof
4. Send to admin for verification
5. Credits will be added manually (< 1 hour)

💱 **Conversion Rate:**
💵 1 USDC = 100 Conway Credits
💰 $10 USDC = 1,000 Credits (minimum)
💰 $50 USDC = 5,000 Credits (recommended)

🌐 **Network:**
⛓️ Base Network (REQUIRED)

📌 **Notes:**
• Platform fee: 2% of deposit
• Operational costs: ~100-500 credits/day
• Larger capital = more optimal AI performance"""
            
            # Build deposit-first menu with education button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("🎓 Pelajari AI Agent" if user_lang == 'id' else "🎓 Learn About AI Agent", 
                                     callback_data="ai_agent_education")],
                [InlineKeyboardButton("💰 Deposit Sekarang" if user_lang == 'id' else "💰 Deposit Now", 
                                     callback_data="automaton_first_deposit")],
                [InlineKeyboardButton("📚 Cara Deposit" if user_lang == 'id' else "📚 How to Deposit", 
                                     callback_data="deposit_guide")],
                [InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", 
                                     callback_data=MAIN_MENU)]
            ]
            
            await query.edit_message_text(
                welcome_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )
        else:
            # User has deposit, show full menu
            await query.edit_message_text(
                get_menu_text(AI_AGENT_MENU, user_lang),
                reply_markup=MenuBuilder.build_ai_agent_menu(),
                parse_mode='MARKDOWN'
            )

    async def show_settings_menu(self, query, context):
        """Show settings submenu"""
        await query.edit_message_text(
            get_menu_text(SETTINGS_MENU),
            reply_markup=MenuBuilder.build_settings_menu(),
            parse_mode='MARKDOWN'
        )

    async def handle_time_settings(self, query, context):
        """Show timezone selection menu"""
        user_id = query.from_user.id
        from database import Database
        db = Database()
        current_tz = db.get_user_timezone(user_id)
        tz_info = TIMEZONES.get(current_tz, TIMEZONES['WIB'])
        
        await query.edit_message_text(
            f" **Time Settings**\n\n"
            f" **Current Timezone:** {tz_info['name']}\n\n"
            f"Select your preferred timezone:\n\n"
            f" **Indonesia:**\n"
            f" WIB - Jakarta, Sumatra, Java (UTC+7)\n"
            f" WITA - Bali, Makassar (UTC+8)\n"
            f" WIT - Papua (UTC+9)\n\n"
            f" **Other Countries:**\n"
            f" Singapore, Malaysia (UTC+8)\n"
            f" Dubai (UTC+4)\n"
            f" UK (UTC+0)\n"
            f" US East/West (UTC-5/-8)",
            reply_markup=MenuBuilder.build_timezone_menu(),
            parse_mode='MARKDOWN'
        )

    async def handle_set_timezone(self, query, context):
        """Handle timezone selection"""
        user_id = query.from_user.id
        tz_code = query.data.replace("set_tz_", "")
        
        if tz_code not in TIMEZONES:
            await query.answer("Invalid timezone", show_alert=True)
            return
        
        from database import Database
        db = Database()
        db.set_user_timezone(user_id, tz_code)
        
        tz_info = TIMEZONES[tz_code]
        from datetime import datetime, timedelta
        user_time = (datetime.utcnow() + timedelta(hours=tz_info['offset'])).strftime('%H:%M:%S')
        
        await query.edit_message_text(
            f" **Timezone Updated!**\n\n"
            f" **Your Timezone:** {tz_info['name']}\n"
            f" **City:** {tz_info['city']}\n"
            f"⏰ **Current Time:** {user_time}\n\n"
            f"All timestamps will now display in your selected timezone.",
            reply_markup=MenuBuilder.build_settings_menu(),
            parse_mode='MARKDOWN'
        )

    async def handle_check_price(self, query, context):
        """Handle check price action - show symbol selection"""
        context.user_data['current_action'] = 'price'
        context.user_data['awaiting_symbol'] = True

        await query.edit_message_text(
            " **Check Price** - Select a cryptocurrency:\n\n"
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
            " **Spot Analysis (SnD)** - 20 Credits\n\n"
            "Select a cryptocurrency for comprehensive analysis:",
            reply_markup=MenuBuilder.build_symbol_selection(),
            parse_mode='MARKDOWN'
        )

    async def handle_futures_analysis(self, query, context):
        """Handle futures analysis - show symbol selection"""
        context.user_data['current_action'] = 'futures'
        context.user_data['awaiting_symbol'] = True

        await query.edit_message_text(
            " **Futures Analysis (SnD)** - 20 Credits\n\n"
            "Select a cryptocurrency for futures trading analysis:",
            reply_markup=MenuBuilder.build_symbol_selection(),
            parse_mode='MARKDOWN'
        )

    async def handle_multi_coin_signals(self, query, context):
        """Handle multi-coin signals with enhanced SnD analysis - NON-BLOCKING"""
        import asyncio
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        # Check and deduct credits (60 for Multi-Coin Signals)
        try:
            from app.credits_guard import require_credits
            ok, remain, msg = require_credits(user_id, 60)
            if not ok:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(" Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                    [InlineKeyboardButton(" Back", callback_data=FUTURES_SIGNALS)]
                ])
                await query.edit_message_text(
                    text=f" {msg}\n\n Upgrade ke Premium untuk akses unlimited!",
                    reply_markup=keyboard
                )
                return
            print(f" Credit deducted for user {user_id}: 60 credits (multi-coin), remaining: {remain}", flush=True)
        except Exception as e:
            print(f" Credit check error for user {user_id}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                text=" Sistem kredit sedang bermasalah. Silakan coba lagi nanti.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Back", callback_data=FUTURES_SIGNALS)]])
            )
            return
        
        await query.edit_message_text("⏳ Generating futures signals with Supply & Demand analysis...\n\n Proses berjalan di background, bot tetap responsif untuk user lain.")

        # Run heavy operation in background task to not block other users
        async def generate_signals_background():
            try:
                from ai_assistant import AIAssistant
                from crypto_api import crypto_api
                
                ai = AIAssistant()
                
                # Generate enhanced futures signals with SnD integration
                signals_text = await ai.generate_futures_signals(
                    language='id',
                    crypto_api=crypto_api,
                    query_args=['4h']  # Default to 4h timeframe
                )
                
                # Send the signals
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=signals_text,
                    parse_mode='MARKDOWN'
                )
                
            except Exception as e:
                print(f" Multi-coin signal error for user {user_id}: {e}", flush=True)
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f" Error generating signals: {str(e)[:100]}...\n\nPlease try again in a few seconds.",
                        parse_mode='MARKDOWN'
                    )
                except:
                    pass
        
        # Create background task - this returns immediately, allowing other users to use bot
        asyncio.create_task(generate_signals_background())

    async def handle_auto_signal_info(self, query, context):
        """Handle auto signal info"""
        info_text = """ **Auto Signal Information**

[AUTO] **What is Auto Signal?**
Automated trading signals delivered directly to your chat every 5 minutes when high-confidence opportunities are detected.

 **Features:**
 Real-time signal delivery
 Supply & Demand analysis
 Multiple timeframes
 Professional entry/exit points
 Risk management included

 **Availability:**
Currently available for **Lifetime Premium users only**

 **How to Access:**
Upgrade to Lifetime Premium via `/subscribe` to unlock this exclusive feature.

 **Signal Quality:**
 Minimum 75% confidence
 Advanced SnD algorithms
 Anti-spam protection
 Quality over quantity approach"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(" Back to Futures Menu", callback_data=FUTURES_SIGNALS)]
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
            " **Add Coin to Portfolio**\n\n"
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
        """Handle referral program - show comprehensive referral info"""
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "User"
        
        # Get bot username for referral link
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username or "CryptoMentorAI_bot"
        
        try:
            from database import Database
            db = Database()
            
            # Ensure user exists
            existing_user = db.get_user(user_id)
            if not existing_user:
                db.create_user(user_id, query.from_user.username, 
                             query.from_user.first_name, 
                             query.from_user.last_name)
            
            # Get user referral codes
            referral_codes = db.get_user_referral_codes(user_id)
            if not referral_codes:
                await query.edit_message_text(" Error loading referral data. Please try /start first.")
                return
                
            free_referral_code = referral_codes.get('free_referral_code', 'INVALID')
            premium_referral_code = referral_codes.get('premium_referral_code', 'INVALID')
            
            # Get stats
            earnings_summary = db.get_referral_earnings_summary(user_id)
            tier_info = db.get_user_tier(user_id)
            
            # Build links
            free_link = f"https://t.me/{bot_username}?start=ref_{free_referral_code}"
            premium_link = f"https://t.me/{bot_username}?start=prem_{premium_referral_code}"
            
            # Calculate next tier requirement
            next_requirement = 10 if tier_info['level']==1 else 25 if tier_info['level']==2 else 50 if tier_info['level']==3 else 100 if tier_info['level']==4 else 100
            progress = min(100, (earnings_summary['total_referrals'] / next_requirement * 100))
            
            referral_text = f""" **REFERRAL PROGRAM - {tier_info['tier']} TIER**

 **{user_name}** | Level {tier_info['level']}/5

 **YOUR REFERRAL LINKS:**

 **FREE REFERRAL:**
`{free_link}`
 Reward: {5 + int(5 * tier_info['bonus']/100)} credits per referral

 **PREMIUM REFERRAL:**
`{premium_link}`  
 Reward: Rp {int(10000 * tier_info['money_multiplier']):,} per premium subscriber

 **PERFORMANCE DASHBOARD:**

 Total Referrals: {earnings_summary['total_referrals']:>15} 
 Free Referrals: {earnings_summary['free_referrals']:>16} 
 Premium Referrals: {earnings_summary['premium_referrals']:>13} 
 Credits Earned: {earnings_summary['credit_earnings']:>16} 
 Money Earned: Rp {earnings_summary['money_earnings']:>13,} 


 **{tier_info['tier']} TIER STATUS:**
 Credit Bonus: +{tier_info['bonus']}%
 Money Multiplier: {tier_info['money_multiplier']}x
 Progress to next tier: {progress:.1f}%
{'' * int(progress/10)}{'' * (10-int(progress/10))} {earnings_summary['total_referrals']}/{next_requirement}

 **EARNING STRATEGIES:**
1. Share free link in crypto groups
2. Premium link for serious traders
3. Build long-term referral network
4. Higher tiers unlock bigger rewards"""
            
            # Create buttons
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [
                    InlineKeyboardButton(" Detailed Stats", callback_data="referral_stats"),
                    InlineKeyboardButton(" Strategy Guide", callback_data="referral_guide")
                ],
                [
                    InlineKeyboardButton(" Tier System", callback_data="tier_system_guide"),
                    InlineKeyboardButton(" Withdrawal", callback_data="referral_withdrawal")
                ],
                [
                    InlineKeyboardButton(" Back to Menu", callback_data=PREMIUM_REFERRAL)
                ]
            ]
            
            await query.edit_message_text(
                referral_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )
            
        except Exception as e:
            print(f"Error in referral program handler: {e}")
            await query.edit_message_text(
                f" Error loading referral data: {str(e)[:100]}\n\n"
                f"Please try /referral command directly.",
                parse_mode='MARKDOWN'
            )

    async def handle_premium_earnings(self, query, context):
        """Handle premium earnings"""
        # For now, show a message since this command might not exist
        earnings_text = """ **Premium Earnings Dashboard**

 **Referral Earnings:**
 Total Referrals: 0
 Credits Earned: 0
 Money Earned: Rp 0

 **How to Earn:**
1. Share your referral link from `/referral`
2. When referred users subscribe premium, you earn money
3. All users give you credits immediately

 **Current Status:**
Premium users earn Rp 10,000 per premium referral

 **Note:** Full earnings dashboard coming in future updates!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(" Back to Premium Menu", callback_data=PREMIUM_REFERRAL)]
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

        prompt_text = """ **Ask CryptoMentor AI**

Type your question about cryptocurrency, trading, or blockchain technology.

 **Examples:**
 "What is DeFi?"
 "Explain Bitcoin halving"
 "How to read candlestick charts?"
 "What is supply and demand in trading?"

 Just type your question in the next message!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(" Cancel", callback_data=ASK_AI_MENU)]
        ])

        await query.edit_message_text(
            prompt_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def handle_automaton_spawn(self, query, context):
        """Handle Spawn Agent button - direct command execution"""
        try:
            from app.handlers_automaton import spawn_agent_command
            from datetime import datetime
            
            # Answer callback first
            await query.answer()
            
            # Send new message instead of editing (cleaner UX)
            await query.message.reply_text(
                "⏳ Preparing to spawn agent...\n\n"
                "Please type the agent name you want to create.",
                parse_mode='MARKDOWN'
            )
            
            # Set context for next message with timestamp
            context.user_data['awaiting_agent_name'] = True
            context.user_data['action'] = 'spawn_agent'
            context.user_data['state_timestamp'] = datetime.utcnow().isoformat()
            
        except Exception as e:
            print(f" Error in handle_automaton_spawn: {e}")
            import traceback
            traceback.print_exc()
            await query.message.reply_text(
                f" Error: {str(e)[:100]}\n\n"
                f"Please use /spawn_agent command directly.",
                parse_mode='MARKDOWN'
            )

    async def handle_automaton_status(self, query, context):
        """Handle Agent Status button - show agent status"""
        try:
            from app.handlers_automaton import agent_status_command
            from telegram import Update
            
            # Answer callback
            await query.answer()
            
            # Create Update-like object that handlers can use
            # We'll pass query but handlers need to check for callback_query
            class UpdateWrapper:
                def __init__(self, callback_query):
                    self.callback_query = callback_query
                    self.effective_user = callback_query.from_user
                    self.effective_chat = callback_query.message.chat
                    self.message = callback_query.message
            
            wrapped_update = UpdateWrapper(query)
            await agent_status_command(wrapped_update, context)
            
        except Exception as e:
            print(f"⚠️ Error in handle_automaton_status: {e}")
            import traceback
            traceback.print_exc()
            
            user_id = query.from_user.id
            from database import Database
            db = Database()
            user_lang = db.get_user_language(user_id)
            
            error_msg = "❌ Terjadi kesalahan. Silakan gunakan command /agent_status" if user_lang == 'id' else "❌ Error occurred. Please use /agent_status command"
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", callback_data=AI_AGENT_MENU)]]
            
            await query.edit_message_text(
                error_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )

    async def handle_automaton_deposit(self, query, context):
        """Handle Fund Agent button - show deposit info for existing agents OR first deposit"""
        user_id = query.from_user.id
        
        try:
            await query.answer()
            
            from database import Database
            from app.automaton_manager import get_automaton_manager
            import os
            
            db = Database()
            user_lang = db.get_user_language(user_id)
            
            # Get automaton manager instance
            automaton_manager = get_automaton_manager(db)
            
            # Get user's agents
            agents = automaton_manager.get_user_agents(user_id)
            
            if not agents:
                # User doesn't have agent yet - show CENTRALIZED WALLET for first deposit
                print(f"🔍 User {user_id} has no agents, showing centralized wallet for first deposit")
                
                # Get centralized wallet address from environment
                centralized_wallet = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
                
                # Generate QR code URL
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={centralized_wallet}"
                
                # Show centralized wallet deposit instructions
                if user_lang == 'id':
                    message = (
                        f"💰 *Deposit USDC (Base Network)*\n\n"
                        f"📍 *Deposit Address (Centralized):*\n"
                        f"`{centralized_wallet}`\n\n"
                        f"📱 *QR Code:*\n"
                        f"[Klik untuk melihat QR Code]({qr_url})\n\n"
                        f"⚠️ *PENTING - Anda Belum Punya Agent*\n"
                        f"• Deposit ke address ini untuk mendapatkan credits\n"
                        f"• Setelah deposit, admin akan verifikasi dan tambahkan credits\n"
                        f"• Dengan credits, Anda bisa spawn AI Agent\n\n"
                        f"🌐 *Network:*\n"
                        f"• Base Network (WAJIB)\n"
                        f"• Biaya gas rendah (~$0.01)\n\n"
                        f"💱 *Conversion Rate:*\n"
                        f"• 1 USDC = 100 Conway Credits\n"
                        f"• $30 USDC = 3.000 Credits\n"
                        f"• $100 USDC = 10.000 Credits\n\n"
                        f"💵 *Minimum Deposit: $30 USDC*\n"
                        f"⚠️ *CATATAN PENTING:*\n"
                        f"• $30 BUKAN pure dana trading\n"
                        f"• Termasuk biaya operasional AI Agent\n"
                        f"• Termasuk biaya API untuk trading\n"
                        f"• Termasuk biaya komputasi AI\n\n"
                        f"💡 *Rekomendasi:*\n"
                        f"• Untuk trading serius: Minimal $100\n"
                        f"• $30 hanya untuk testing/trial\n"
                        f"• Semakin besar modal, semakin optimal AI bekerja\n\n"
                        f"📝 *Cara Deposit:*\n"
                        f"1. Copy address di atas atau scan QR code\n"
                        f"2. Buka wallet Anda (MetaMask, Trust Wallet, dll)\n"
                        f"3. Pastikan network: Base\n"
                        f"4. Kirim minimal $30 USDC ke address di atas\n"
                        f"5. Screenshot bukti transfer\n"
                        f"6. Kirim ke admin untuk verifikasi\n"
                        f"7. Credits akan ditambahkan manual (< 1 jam)"
                    )
                else:
                    message = (
                        f"💰 *Deposit USDC (Base Network)*\n\n"
                        f"📍 *Deposit Address (Centralized):*\n"
                        f"`{centralized_wallet}`\n\n"
                        f"📱 *QR Code:*\n"
                        f"[Click to view QR Code]({qr_url})\n\n"
                        f"⚠️ *IMPORTANT - You Don't Have an Agent Yet*\n"
                        f"• Deposit to this address to get credits\n"
                        f"• After deposit, admin will verify and add credits\n"
                        f"• With credits, you can spawn an AI Agent\n\n"
                        f"🌐 *Network:*\n"
                        f"• Base Network (REQUIRED)\n"
                        f"• Low gas fees (~$0.01)\n\n"
                        f"💱 *Conversion Rate:*\n"
                        f"• 1 USDC = 100 Conway Credits\n"
                        f"• $30 USDC = 3,000 Credits\n"
                        f"• $100 USDC = 10,000 Credits\n\n"
                        f"💵 *Minimum Deposit: $30 USDC*\n"
                        f"⚠️ *IMPORTANT NOTE:*\n"
                        f"• $30 is NOT pure trading capital\n"
                        f"• Includes AI Agent operational costs\n"
                        f"• Includes API fees for trading\n"
                        f"• Includes AI computation costs\n\n"
                        f"💡 *Recommendation:*\n"
                        f"• For serious trading: Minimum $100\n"
                        f"• $30 only for testing/trial\n"
                        f"• Larger capital = more optimal AI performance\n\n"
                        f"📝 *How to Deposit:*\n"
                        f"1. Copy address above or scan QR code\n"
                        f"2. Open your wallet (MetaMask, Trust Wallet, etc)\n"
                        f"3. Make sure network: Base\n"
                        f"4. Send minimum $30 USDC to the address above\n"
                        f"5. Screenshot transfer proof\n"
                        f"6. Send to admin for verification\n"
                        f"7. Credits will be added manually (< 1 hour)"
                    )
                
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                keyboard = [
                    [InlineKeyboardButton("📤 Kirim Bukti ke Admin" if user_lang == 'id' else "📤 Send Proof to Admin", 
                                         url="https://t.me/BillFarr")],
                    [InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", 
                                         callback_data=AI_AGENT_MENU)]
                ]
                
                await query.edit_message_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='MARKDOWN'
                )
                return
            
            # User HAS agent - show agent-specific deposit address
            agent = agents[0]
            deposit_address = agent.get('deposit_address', '')
            
            if not deposit_address:
                error_msg = "❌ Agent deposit address tidak ditemukan." if user_lang == 'id' else "❌ Agent deposit address not found."
                
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [[InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", callback_data=AI_AGENT_MENU)]]
                
                await query.edit_message_text(
                    error_msg,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='MARKDOWN'
                )
                return
            
            # Generate QR code URL
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={deposit_address}"
            
            # Deposit instructions for agent
            if user_lang == 'id':
                message = (
                    f"💰 *Deposit USDC (Base Network)*\n\n"
                    f"📍 *Deposit Address (Agent):*\n"
                    f"`{deposit_address}`\n\n"
                    f"📱 *QR Code:*\n"
                    f"[Klik untuk melihat QR Code]({qr_url})\n\n"
                    f"🌐 *Network:*\n"
                    f"• Base Network (WAJIB)\n"
                    f"• Biaya gas rendah (~$0.01)\n\n"
                    f"💱 *Conversion Rate:*\n"
                    f"• 1 USDC = 100 Conway Credits\n"
                    f"• $30 USDC = 3.000 Credits\n\n"
                    f"⚠️ *Penting:*\n"
                    f"• HANYA gunakan Base Network\n"
                    f"• HANYA kirim USDC (bukan USDT atau token lain)\n"
                    f"• Credits akan ditambahkan otomatis setelah 12 konfirmasi\n\n"
                    f"💡 *Cara Deposit:*\n"
                    f"1. Buka wallet Anda (MetaMask, Trust Wallet, dll)\n"
                    f"2. Pastikan network: Base\n"
                    f"3. Kirim USDC ke address di atas\n"
                    f"4. Tunggu 12 konfirmasi (~5-10 menit)\n"
                    f"5. Credits akan otomatis masuk"
                )
            else:
                message = (
                    f"💰 *Deposit USDC (Base Network)*\n\n"
                    f"📍 *Deposit Address (Agent):*\n"
                    f"`{deposit_address}`\n\n"
                    f"📱 *QR Code:*\n"
                    f"[Click to view QR Code]({qr_url})\n\n"
                    f"🌐 *Network:*\n"
                    f"• Base Network (REQUIRED)\n"
                    f"• Low gas fees (~$0.01)\n\n"
                    f"💱 *Conversion Rate:*\n"
                    f"• 1 USDC = 100 Conway Credits\n"
                    f"• $30 USDC = 3,000 Credits\n\n"
                    f"⚠️ *Important:*\n"
                    f"• ONLY use Base Network\n"
                    f"• ONLY send USDC (not USDT or other tokens)\n"
                    f"• Credits will be added automatically after 12 confirmations\n\n"
                    f"💡 *How to Deposit:*\n"
                    f"1. Open your wallet (MetaMask, Trust Wallet, etc)\n"
                    f"2. Make sure network: Base\n"
                    f"3. Send USDC to the address above\n"
                    f"4. Wait for 12 confirmations (~5-10 minutes)\n"
                    f"5. Credits will be added automatically"
                )
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", callback_data=AI_AGENT_MENU)]]
            
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )
            
        except Exception as e:
            print(f"⚠️ Error in handle_automaton_deposit: {e}")
            import traceback
            traceback.print_exc()
            
            from database import Database
            db = Database()
            user_lang = db.get_user_language(user_id)
            
            error_msg = "❌ Terjadi kesalahan saat mengambil deposit address. Silakan coba lagi." if user_lang == 'id' else "❌ Error occurred while getting deposit address. Please try again."
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", callback_data=AI_AGENT_MENU)]]
            
            await query.edit_message_text(
                error_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )

    async def handle_automaton_logs(self, query, context):
        """Handle Agent Logs button - show agent logs"""
        try:
            from app.handlers_automaton import agent_logs_command
            
            # Answer callback
            await query.answer()
            
            # Create Update-like object
            class UpdateWrapper:
                def __init__(self, callback_query):
                    self.callback_query = callback_query
                    self.effective_user = callback_query.from_user
                    self.effective_chat = callback_query.message.chat
                    self.message = callback_query.message
            
            wrapped_update = UpdateWrapper(query)
            await agent_logs_command(wrapped_update, context)
            
        except Exception as e:
            print(f"⚠️ Error in handle_automaton_logs: {e}")
            import traceback
            traceback.print_exc()
            
            user_id = query.from_user.id
            from database import Database
            db = Database()
            user_lang = db.get_user_language(user_id)
            
            error_msg = "❌ Terjadi kesalahan. Silakan gunakan command /agent_logs" if user_lang == 'id' else "❌ Error occurred. Please use /agent_logs command"
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", callback_data=AI_AGENT_MENU)]]
            
            await query.edit_message_text(
                error_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )

    async def handle_agent_lineage(self, query, context):
        """Handle Agent Lineage button - show agent lineage"""
        try:
            from app.handlers_automaton import agent_lineage_command
            
            # Answer callback
            await query.answer()
            
            # Create Update-like object
            class UpdateWrapper:
                def __init__(self, callback_query):
                    self.callback_query = callback_query
                    self.effective_user = callback_query.from_user
                    self.effective_chat = callback_query.message.chat
                    self.message = callback_query.message
            
            wrapped_update = UpdateWrapper(query)
            await agent_lineage_command(wrapped_update, context)
            
        except Exception as e:
            print(f"⚠️ Error in handle_agent_lineage: {e}")
            import traceback
            traceback.print_exc()
            
            user_id = query.from_user.id
            from database import Database
            db = Database()
            user_lang = db.get_user_language(user_id)
            
            error_msg = "❌ Terjadi kesalahan. Silakan gunakan command /agent_lineage" if user_lang == 'id' else "❌ Error occurred. Please use /agent_lineage command"
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("🔙 Kembali" if user_lang == 'id' else "🔙 Back", callback_data=AI_AGENT_MENU)]]
            
            await query.edit_message_text(
                error_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )
            traceback.print_exc()
            await query.message.reply_text(
                f" Error: {str(e)[:100]}\n\n"
                f"Please use /agent_lineage command directly.",
                parse_mode='MARKDOWN'
            )

    async def handle_change_language(self, query, context):
        """Handle language change with interactive buttons"""
        user_id = query.from_user.id
        
        try:
            from database import Database
            db = Database()
            current_lang = db.get_user_language(user_id) or 'id'
            current_name = {'en': 'English', 'id': 'Bahasa Indonesia'}.get(current_lang, 'Bahasa Indonesia')
        except:
            current_lang = 'id'
            current_name = 'Bahasa Indonesia'

        if current_lang == 'id':
            language_text = f""" **Pengaturan Bahasa**

 **Bahasa Saat Ini:** {current_name} (`{current_lang}`)

 **Bahasa Tersedia:**
  English - Fitur lengkap
  Bahasa Indonesia - Fitur lengkap

 **Pilih bahasa yang Anda inginkan:**"""
        else:
            language_text = f""" **Language Settings**

 **Current Language:** {current_name} (`{current_lang}`)

 **Available Languages:**
  English - Full features
  Bahasa Indonesia - Fitur lengkap

 **Select your preferred language:**"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton(" English", callback_data="set_lang_en"),
                InlineKeyboardButton(" Bahasa Indonesia", callback_data="set_lang_id")
            ],
            [InlineKeyboardButton(" Back to Settings", callback_data=SETTINGS_MENU)]
        ]

        await query.edit_message_text(
            language_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

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

        prompt_text = f"""⌨ **Manual Symbol Input**

Type the cryptocurrency symbol you want to {action_text}.

 **Examples:** BTC, ETH, DOGE, SHIB, etc.

Just type the symbol in your next message!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(" Cancel", callback_data=MAIN_MENU)]
        ])

        await query.edit_message_text(
            prompt_text,
            reply_markup=back_button,
            parse_mode='MARKDOWN'
        )

    async def show_futures_timeframe_selection(self, query, context, symbol):
        """Show timeframe selection for futures analysis"""
        await query.edit_message_text(
            f" <b>Futures Analysis: {symbol}</b>\n\n"
            f"Select timeframe: 15m, 30m, 1h, 4h, 1d",
            reply_markup=MenuBuilder.build_timeframe_selection(symbol),
            parse_mode='HTML'
        )

    async def handle_futures_timeframe_selection(self, query, context):
        """Handle futures timeframe selection with sentiment-based entry recommendations - NON-BLOCKING"""
        import asyncio
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        # Check and deduct credits (20 for Futures Analysis)
        try:
            from app.credits_guard import require_credits
            ok, remain, msg = require_credits(user_id, 20)
            if not ok:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(" Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                    [InlineKeyboardButton(" Back", callback_data=TRADING_ANALYSIS)]
                ])
                await query.edit_message_text(
                    text=f" {msg}\n\n Upgrade ke Premium untuk akses unlimited!",
                    reply_markup=keyboard
                )
                return
            print(f" Credit deducted for user {user_id}: 20 credits (futures analysis), remaining: {remain}", flush=True)
        except Exception as e:
            print(f" Credit check error for user {user_id}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                text=" Sistem kredit sedang bermasalah. Silakan coba lagi nanti.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Back", callback_data=TRADING_ANALYSIS)]])
            )
            return
        
        # Parse callback data: futures_SYMBOL_TIMEFRAME
        parts = query.data.split('_')
        if len(parts) >= 3:
            symbol = parts[1]
            timeframe = parts[2]

            # Ensure symbol has USDT
            if not 'USDT' in symbol:
                symbol = symbol + 'USDT'

            await query.edit_message_text(
                f"⏳ Analyzing {symbol} {timeframe} with Supply & Demand zones...\n\n Bot tetap responsif untuk user lain.",
                parse_mode=None
            )

            # Run analysis in background task
            async def run_futures_analysis():
                try:
                    from snd_zone_detector import detect_snd_zones

                    # Get SnD zones (run in thread to avoid blocking)
                    snd_result = await asyncio.to_thread(detect_snd_zones, symbol, timeframe, 100)
                    
                    if 'error' in snd_result:
                        await context.bot.edit_message_text(
                            chat_id=chat_id, message_id=message_id,
                            text=f"Error: {snd_result['error']}", parse_mode=None
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

                    avg_demand = sum(z.midpoint for z in demand_zones) / len(demand_zones) if demand_zones else 0
                    avg_supply = sum(z.midpoint for z in supply_zones) / len(supply_zones) if supply_zones else 0
                    
                    if avg_demand and avg_supply:
                        mid_range = (avg_demand + avg_supply) / 2
                        if current_price > mid_range * 1.02:
                            sentiment, sentiment_emoji = "BULLISH", "🟢"
                        elif current_price < mid_range * 0.98:
                            sentiment, sentiment_emoji = "BEARISH", ""
                        else:
                            sentiment, sentiment_emoji = "SIDEWAYS", "🟡"
                    else:
                        sentiment, sentiment_emoji = "NEUTRAL", ""

                    display_symbol = symbol.replace('USDT', '')
                    response = f" FUTURES ANALYSIS: {display_symbol} ({timeframe.upper()})\n\n Current Price: {fmt_price(current_price)}\n{sentiment_emoji} Market Sentiment: {sentiment}\n\n"

                    if sentiment == "BULLISH":
                        response += " RECOMMENDED: LIMIT LONG at Demand Zone\n\n"
                        if demand_zones:
                            best_zone = demand_zones[0]
                            zone_width = best_zone.high - best_zone.low
                            sl = best_zone.low - (zone_width * 0.75)
                            tp1 = current_price + (current_price - best_zone.midpoint) * 1.5
                            tp2 = current_price + (current_price - best_zone.midpoint) * 2.5
                            response += f"🟢 ENTRY ZONE (LONG):\n Demand Zone: {fmt_price(best_zone.low)} - {fmt_price(best_zone.high)}\n Strength: {best_zone.strength:.0f}%\n Stop Loss: {fmt_price(sl)}\n TP1: {fmt_price(tp1)}\n TP2: {fmt_price(tp2)}\n\n"
                        else:
                            response += " No demand zones found for LONG entry\n\n"
                    elif sentiment == "BEARISH":
                        response += " RECOMMENDED: LIMIT SHORT at Supply Zone\n\n"
                        if supply_zones:
                            best_zone = supply_zones[0]
                            zone_width = best_zone.high - best_zone.low
                            sl = best_zone.high + (zone_width * 0.75)
                            tp1 = current_price - (best_zone.midpoint - current_price) * 1.5
                            tp2 = current_price - (best_zone.midpoint - current_price) * 2.5
                            response += f" ENTRY ZONE (SHORT):\n Supply Zone: {fmt_price(best_zone.low)} - {fmt_price(best_zone.high)}\n Strength: {best_zone.strength:.0f}%\n Stop Loss: {fmt_price(sl)}\n TP1: {fmt_price(tp1)}\n TP2: {fmt_price(tp2)}\n\n"
                        else:
                            response += " No supply zones found for SHORT entry\n\n"
                    else:
                        response += " RECOMMENDED: Wait for Breakout\n\n Market is ranging - wait for clear direction\n\n"
                        if demand_zones:
                            best_demand = demand_zones[0]
                            response += f"🟢 If Bullish Breakout → LONG at:\n Demand: {fmt_price(best_demand.low)} - {fmt_price(best_demand.high)}\n\n"
                        if supply_zones:
                            best_supply = supply_zones[0]
                            response += f" If Bearish Breakout → SHORT at:\n Supply: {fmt_price(best_supply.low)} - {fmt_price(best_supply.high)}\n\n"

                    response += " RISK MANAGEMENT:\n Use LIMIT orders at zone levels\n Do NOT use market orders\n Risk max 1-2% per trade\n Always set Stop Loss\n\n Wait for price to enter zone before placing order"

                    await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=response, parse_mode=None)

                except Exception as e:
                    print(f" Futures analysis error: {e}", flush=True)
                    try:
                        await context.bot.edit_message_text(
                            chat_id=chat_id, message_id=message_id,
                            text=f"Error: {str(e)[:100]}\n\nPlease try again", parse_mode=None
                        )
                    except:
                        pass

            # Create background task - returns immediately
            asyncio.create_task(run_futures_analysis())

    async def handle_add_coin_amount(self, query, context, symbol):
        """Handle amount input for add coin"""
        context.user_data['symbol'] = symbol
        context.user_data['step'] = 'amount'
        context.user_data['awaiting_amount'] = True

        prompt_text = f""" **Add {symbol} to Portfolio**

Step 2/2: Enter the amount of {symbol} you own.

 **Examples:**
 0.5 (for 0.5 {symbol})
 100 (for 100 {symbol})
 0.001234 (for small amounts)

Just type the number in your next message!"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(" Cancel", callback_data=PORTFOLIO_CREDITS)]
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
        """Execute Spot Signal analysis with tiered DCA zones - NON-BLOCKING"""
        import asyncio
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        # Check and deduct credits (20 for Spot Analysis)
        try:
            from app.credits_guard import require_credits
            ok, remain, msg = require_credits(user_id, 20)
            if not ok:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(" Upgrade Premium", callback_data=UPGRADE_PREMIUM)],
                    [InlineKeyboardButton(" Back", callback_data=TRADING_ANALYSIS)]
                ])
                await query.edit_message_text(
                    text=f" {msg}\n\n Upgrade ke Premium untuk akses unlimited!",
                    reply_markup=keyboard
                )
                return
            print(f" Credit deducted for user {user_id}: 20 credits (spot analysis), remaining: {remain}", flush=True)
        except Exception as e:
            print(f" Credit check error for user {user_id}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                text=" Sistem kredit sedang bermasalah. Silakan coba lagi nanti.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Back", callback_data=TRADING_ANALYSIS)]])
            )
            return
        
        # Ensure symbol has USDT
        if not any(symbol.endswith(pair) for pair in ['USDT', 'BUSD', 'USDC']):
            symbol += 'USDT'
        
        timeframe = "1h"
        
        await query.edit_message_text(
            f" <b>Analyzing {symbol}...</b>\n\n Fetching Binance data...\n Detecting S&D zones...\n\n Bot tetap responsif untuk user lain.",
            parse_mode='HTML'
        )
        
        # Run analysis in background task
        async def run_spot_analysis():
            try:
                from snd_zone_detector import detect_snd_zones
                
                # Get SnD analysis (run in thread to avoid blocking)
                snd_result = await asyncio.to_thread(detect_snd_zones, symbol, timeframe, 100)
                
                if 'error' in snd_result:
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f" <b>Error:</b> {snd_result['error']}\n\n Try a different symbol like BTC, ETH, etc.",
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
                
                avg_demand = sum(z.midpoint for z in demand_zones) / len(demand_zones) if demand_zones else 0
                avg_supply = sum(z.midpoint for z in supply_zones) / len(supply_zones) if supply_zones else 0
                
                if avg_demand and avg_supply:
                    mid_range = (avg_demand + avg_supply) / 2
                    if current_price > mid_range * 1.02: trend = "Bullish"
                    elif current_price < mid_range * 0.98: trend = "Bearish"
                    else: trend = "Sideways"
                else:
                    trend = "Neutral"
                
                avg_strength = sum(z.strength for z in demand_zones) / len(demand_zones) if demand_zones else 0
                if avg_strength >= 60: volume_status = "Accumulation"
                elif avg_strength >= 40: volume_status = "Neutral"
                else: volume_status = "Distribution"
                
                zone_count = len(demand_zones) + len(supply_zones)
                base_confidence = min(85, 50 + (zone_count * 5))
                if demand_zones: base_confidence += min(15, demand_zones[0].strength / 5)
                confidence = min(95, base_confidence)
                
                display_symbol = symbol.replace('USDT', '')
                response = f" <b>Spot Signal – {display_symbol} ({timeframe.upper()})</b>\n\n <b>Price:</b> {fmt_price(current_price)}\n\n🟢 <b>BUY ZONES</b>\n"
                
                zone_labels = [("A", "Strong", "40%"), ("B", "Discount", "35%"), ("C", "Deep", "25%")]
                sorted_demands = sorted(demand_zones, key=lambda z: abs(current_price - z.midpoint))
                
                if sorted_demands:
                    for i, (label, desc, alloc) in enumerate(zone_labels):
                        if i < len(sorted_demands):
                            zone = sorted_demands[i]
                            zone_width = zone.high - zone.low
                            tp1 = zone.high + (zone_width * 1.5)
                            tp2 = zone.high + (zone_width * 3.0)
                            strength = zone.strength if hasattr(zone, 'strength') else 50
                            response += f"\n<b>Zone {label}</b> – {desc}\nEntry: {fmt_price(zone.low)} – {fmt_price(zone.high)}\nAllocation: {alloc}\nTP1: {fmt_price(tp1)}\nTP2: {fmt_price(tp2)}\nStrength: {strength:.0f}%\n"
                else:
                    response += "\n⏳ No active demand zones detected\n"
                
                response += "\n <b>SELL ZONE</b>\n"
                if supply_zones:
                    best_supply = supply_zones[0]
                    response += f"{fmt_price(best_supply.low)} – {fmt_price(best_supply.high)} (Take Profit)\n"
                else:
                    response += "No active supply zone\n"
                
                response += f"\n <b>Context:</b>\n Trend: {trend}\n Volume: {volume_status}\n\n <b>Confidence:</b> {confidence:.0f}%\n <b>Strategy:</b> DCA on demand zones\n\n<i> Spot only  Entry range, not market buy</i>"
                
                # Add AI reasoning for premium users
                try:
                    from deepseek_ai import DeepSeekAI
                    ai = DeepSeekAI()
                    
                    # Prepare signal data for AI
                    buy_zones_data = []
                    for i, (label, desc, alloc) in enumerate(zone_labels):
                        if i < len(sorted_demands):
                            zone = sorted_demands[i]
                            zone_width = zone.high - zone.low
                            tp1 = zone.high + (zone_width * 1.5)
                            tp2 = zone.high + (zone_width * 3.0)
                            strength = zone.strength if hasattr(zone, 'strength') else 50
                            
                            buy_zones_data.append({
                                'label': label,
                                'low': zone.low,
                                'high': zone.high,
                                'allocation': alloc,
                                'strength': strength,
                                'tp1': tp1,
                                'tp2': tp2
                            })
                    
                    sell_zone_data = None
                    if supply_zones:
                        best_supply = supply_zones[0]
                        sell_zone_data = {
                            'low': best_supply.low,
                            'high': best_supply.high
                        }
                    
                    signal_data = {
                        'current_price': current_price,
                        'trend': trend,
                        'volume_status': volume_status,
                        'confidence': confidence,
                        'buy_zones': buy_zones_data,
                        'sell_zone': sell_zone_data
                    }
                    
                    # Generate AI reasoning
                    ai_reasoning = await ai.generate_spot_signal_reasoning(symbol, signal_data)
                    response += ai_reasoning
                    
                except Exception as e:
                    print(f"Error adding AI reasoning to spot signal: {e}")
                
                await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=response, parse_mode='HTML')
            
            except Exception as e:
                print(f" Spot analysis error: {e}", flush=True)
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id, message_id=message_id,
                        text=f" <b>Error</b>: {str(e)[:100]}\n\n Please try again or check symbol format",
                        parse_mode='HTML'
                    )
                except:
                    pass
        
        # Create background task - returns immediately
        asyncio.create_task(run_spot_analysis())

    async def handle_copy_referral_link(self, query, context):
        """Handle copy referral link"""
        user_id = query.from_user.id
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username or "CryptoMentorAI_bot"
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

        await query.answer(
            f" Link copied!\n{referral_link}",
            show_alert=True
        )

    async def handle_referral_stats(self, query, context):
        """Handle detailed referral statistics with advanced tier system"""
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "User"

        # Get detailed stats from database
        total_referrals = 0
        active_referrals = 0
        total_earnings = 0
        this_month_earnings = 0
        premium_referrals = 0

        try:
            from database import Database
            db = Database()
            stats = db.get_detailed_referral_stats(user_id)
            total_referrals = stats.get('total_referrals', 0)
            active_referrals = stats.get('active_referrals', 0)
            total_earnings = stats.get('total_earnings', 0)
            this_month_earnings = stats.get('this_month_earnings', 0)
            
            # Get premium referral count
            earnings_summary = db.get_referral_earnings_summary(user_id)
            premium_referrals = earnings_summary.get('premium_referrals', 0)
        except:
            pass

        # Get current tier and progress
        current_tier = self.get_referral_tier_info(total_referrals)
        next_tier = self.get_next_tier_info(total_referrals)
        
        # Calculate earnings potential
        credit_value = (total_referrals - premium_referrals) * 5  # 5 credits per free referral
        money_value = total_earnings
        estimated_monthly = self.calculate_monthly_potential(total_referrals, active_referrals)

        stats_text = f""" **REFERRAL DASHBOARD - {current_tier['name']} TIER**

 **{user_name}** | Level {current_tier['level']}/5

 **PERFORMANCE METRICS:**

 Total Referrals: {total_referrals:>15} 
 Free Referrals: {total_referrals - premium_referrals:>16} 
 Premium Referrals: {premium_referrals:>13} 
 Success Rate: {(active_referrals/max(total_referrals,1)*100):>17.1f}% 


 **CURRENT TIER: {current_tier['name']}**
{current_tier['icon']} **Benefits:**
 Credit Bonus: +{current_tier['bonus']}% pada setiap referral
 Money Multiplier: {current_tier['money_multiplier']}x cash rewards
 Badge: {current_tier['badge']}
 Special Access: {current_tier['access']}

 **PROGRESSION TO {next_tier['name']}:**
Progress: {total_referrals}/{next_tier['requirement']} ({(total_referrals/next_tier['requirement']*100):.1f}%)
{'' * int(total_referrals/next_tier['requirement']*10)}{'' * (10-int(total_referrals/next_tier['requirement']*10))}
Needed: {max(0, next_tier['requirement'] - total_referrals)} more referrals

 **EARNINGS OVERVIEW:**
 Credits Earned: {credit_value:,} credits (≈ Rp {credit_value * 500:,})
 Cash Earned: Rp {money_value:,}
 Bulan Ini: Rp {this_month_earnings:,}
 Estimated Monthly: Rp {estimated_monthly:,}

 **GROWTH STRATEGY:**
{self.get_tier_specific_tips(current_tier['level'])}

 **REWARDS UNLOCKED:**
{self.get_rewards_display(current_tier['level'], total_referrals)}

 **TIER BONUSES AKTIF:**
 Credit boost: {current_tier['bonus']}% extra
 Withdrawal priority: {current_tier['withdrawal_priority']}
 Customer support: {current_tier['support_level']}"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton(" Copy Link", callback_data="copy_referral_link"),
             InlineKeyboardButton(" Tips & Guide", callback_data="referral_guide")],
            [InlineKeyboardButton(" Tier Guide", callback_data="tier_system_guide"),
             InlineKeyboardButton(" Withdrawal", callback_data="referral_withdrawal")],
            [InlineKeyboardButton(" Back", callback_data="referral_program")],
        ]

        await query.edit_message_text(
            text=stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

    async def handle_referral_withdrawal(self, query, context):
        """Handle referral withdrawal request - Step 1: Show balance and options"""
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "User"

        try:
            from database import Database
            db = Database()
            stats = db.get_referral_stats(user_id)
            total_earnings = stats.get('total_earnings', 0)
        except:
            total_earnings = 0

        if total_earnings < 50000:
            await query.answer(
                f"Minimum withdrawal Rp 50,000\nSaldo Anda: Rp {total_earnings:,}",
                show_alert=True
            )
            return

        # Check for pending withdrawal
        import json
        import os
        pending_file = os.path.join(os.path.dirname(__file__), 'pending_withdrawals.json')
        has_pending = False
        if os.path.exists(pending_file):
            with open(pending_file, 'r') as f:
                pending_data = json.load(f)
            if str(user_id) in pending_data and pending_data[str(user_id)].get('status') == 'pending':
                has_pending = True
                pending_info = pending_data[str(user_id)]

        if has_pending:
            withdrawal_text = f"""⏳ <b>WITHDRAWAL REQUEST PENDING</b>

 <b>User:</b> {user_name}
 <b>UID:</b> <code>{user_id}</code>

 <b>Jumlah:</b> Rp {pending_info.get('amount', 0):,}
 <b>Metode:</b> {pending_info.get('method', 'N/A')}
 <b>Detail:</b> {pending_info.get('account_info', 'N/A')}
 <b>Tanggal Request:</b> {pending_info.get('requested_at', 'N/A')[:10]}

⏳ <b>Status:</b> Menunggu verifikasi admin

Anda sudah memiliki request withdrawal yang pending.
Mohon tunggu admin memproses request Anda."""

            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton(" Cancel Request", callback_data="wd_cancel")],
                [InlineKeyboardButton(" Back", callback_data="referral_program")],
            ]
            await query.edit_message_text(
                text=withdrawal_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            return

        withdrawal_text = f""" <b>WITHDRAWAL REFERRAL EARNINGS</b>

 <b>User:</b> {user_name}
 <b>UID:</b> <code>{user_id}</code>

 <b>Saldo Tersedia:</b> Rp {total_earnings:,}

 <b>Pilih Metode Withdrawal:</b>

 <b>Bank Transfer</b>
 Fee: Rp 2,500
 Processing: 1-3 hari kerja

 <b>E-Wallet</b> (OVO/DANA/GoPay)
 Fee: Rp 1,000
 Processing: Instant - 24 jam

 <b>Crypto</b> (USDT BEP20)
 Fee: 1 USDT
 Processing: 2-6 jam

 <b>Minimum withdrawal:</b> Rp 50,000"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton(" Bank Transfer", callback_data="wd_method_bank")],
            [InlineKeyboardButton(" E-Wallet", callback_data="wd_method_ewallet")],
            [InlineKeyboardButton(" Crypto USDT", callback_data="wd_method_crypto")],
            [InlineKeyboardButton(" Back", callback_data="referral_program")],
        ]

        await query.edit_message_text(
            text=withdrawal_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    async def handle_withdrawal_method(self, query, context, method):
        """Handle withdrawal method selection - Ask for account details"""
        user_id = query.from_user.id
        
        try:
            from database import Database
            db = Database()
            stats = db.get_referral_stats(user_id)
            total_earnings = stats.get('total_earnings', 0)
        except:
            total_earnings = 0

        method_info = {
            'bank': {'name': 'Bank Transfer', 'fee': 2500, 'icon': '', 'placeholder': 'Nama Bank + No Rekening + Nama Pemilik\nContoh: BCA 1234567890 John Doe'},
            'ewallet': {'name': 'E-Wallet', 'fee': 1000, 'icon': '', 'placeholder': 'Jenis E-Wallet + Nomor\nContoh: DANA 081234567890'},
            'crypto': {'name': 'Crypto USDT BEP20', 'fee': 15000, 'icon': '', 'placeholder': 'Alamat Wallet BEP20\nContoh: 0x1234...abcd'}
        }
        
        info = method_info.get(method, method_info['bank'])
        net_amount = total_earnings - info['fee']
        
        # Store the method selection in context
        context.user_data['withdrawal_method'] = method
        context.user_data['withdrawal_amount'] = total_earnings
        context.user_data['withdrawal_fee'] = info['fee']
        context.user_data['awaiting_withdrawal_details'] = True
        
        text = f"""{info['icon']} <b>WITHDRAWAL via {info['name']}</b>

 <b>Saldo:</b> Rp {total_earnings:,}
 <b>Fee:</b> Rp {info['fee']:,}
 <b>Yang Diterima:</b> Rp {net_amount:,}

 <b>Kirim detail akun Anda:</b>
{info['placeholder']}

 <b>PENTING:</b> Pastikan data benar karena tidak bisa diubah setelah submit!"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton(" Cancel", callback_data="referral_withdrawal")],
        ]

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
        await query.answer("Silakan kirim detail akun pembayaran Anda")

    async def process_withdrawal_details(self, update, context):
        """Process user's withdrawal account details"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"
        username = update.effective_user.username or "no_username"
        account_info = update.message.text
        
        method = context.user_data.get('withdrawal_method', 'bank')
        amount = context.user_data.get('withdrawal_amount', 0)
        fee = context.user_data.get('withdrawal_fee', 0)
        net_amount = amount - fee
        
        # Clear the awaiting state
        context.user_data['awaiting_withdrawal_details'] = False
        
        method_names = {'bank': 'Bank Transfer', 'ewallet': 'E-Wallet', 'crypto': 'Crypto USDT BEP20'}
        method_name = method_names.get(method, 'Bank Transfer')
        
        # Save to pending withdrawals
        import json
        import os
        from datetime import datetime
        
        pending_file = os.path.join(os.path.dirname(__file__), 'pending_withdrawals.json')
        
        if os.path.exists(pending_file):
            with open(pending_file, 'r') as f:
                pending_data = json.load(f)
        else:
            pending_data = {}
        
        pending_data[str(user_id)] = {
            'user_id': user_id,
            'user_name': user_name,
            'username': username,
            'amount': amount,
            'fee': fee,
            'net_amount': net_amount,
            'method': method_name,
            'account_info': account_info,
            'status': 'pending',
            'requested_at': datetime.utcnow().isoformat()
        }
        
        with open(pending_file, 'w') as f:
            json.dump(pending_data, f, indent=2)
        
        # Notify user
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        user_text = f""" <b>WITHDRAWAL REQUEST SUBMITTED!</b>

 <b>UID:</b> <code>{user_id}</code>
 <b>Jumlah:</b> Rp {amount:,}
 <b>Fee:</b> Rp {fee:,}
 <b>Yang Diterima:</b> Rp {net_amount:,}

 <b>Metode:</b> {method_name}
 <b>Detail:</b> {account_info}

⏳ <b>Status:</b> Menunggu verifikasi admin

Admin akan memproses withdrawal Anda dalam 1-3 hari kerja.
Anda akan menerima notifikasi setelah pembayaran dikirim."""

        keyboard = [[InlineKeyboardButton(" Menu Utama", callback_data="main_menu")]]
        
        await update.message.reply_text(
            text=user_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
        # Notify all admins
        import os
        admin_ids = []
        admin1 = os.environ.get('ADMIN1')
        admin2 = os.environ.get('ADMIN2')
        admin3 = os.environ.get('ADMIN3')
        if admin1: admin_ids.append(int(admin1))
        if admin2: admin_ids.append(int(admin2))
        if admin3: admin_ids.append(int(admin3))
        
        admin_text = f""" <b>NEW WITHDRAWAL REQUEST</b>

 <b>User:</b> {user_name} (@{username})
 <b>UID:</b> <code>{user_id}</code>

 <b>Jumlah:</b> Rp {amount:,}
 <b>Fee:</b> Rp {fee:,}
 <b>Net Amount:</b> Rp {net_amount:,}

 <b>Metode:</b> {method_name}
 <b>Detail Akun:</b>
<code>{account_info}</code>

 <b>Tanggal:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"""

        admin_keyboard = [
            [InlineKeyboardButton(" Approve (Sudah Transfer)", callback_data=f"wd_approve_{user_id}")],
            [InlineKeyboardButton(" Reject", callback_data=f"wd_reject_{user_id}")],
        ]
        
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_text,
                    reply_markup=InlineKeyboardMarkup(admin_keyboard),
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")
        
        return True

    async def handle_withdrawal_cancel(self, query, context):
        """Cancel user's pending withdrawal request"""
        user_id = query.from_user.id
        
        import json
        import os
        pending_file = os.path.join(os.path.dirname(__file__), 'pending_withdrawals.json')
        
        if os.path.exists(pending_file):
            with open(pending_file, 'r') as f:
                pending_data = json.load(f)
            
            if str(user_id) in pending_data:
                del pending_data[str(user_id)]
                with open(pending_file, 'w') as f:
                    json.dump(pending_data, f, indent=2)
                
                await query.answer("Request withdrawal dibatalkan", show_alert=True)
            else:
                await query.answer("Tidak ada request withdrawal pending", show_alert=True)
        
        # Go back to referral program
        await self.handle_referral_program(query, context)

    async def handle_admin_withdrawal_approve(self, query, context):
        """Admin approves withdrawal - Reset user's premium_earnings"""
        admin_id = query.from_user.id
        callback_data = query.data
        
        # Extract user_id from callback
        target_user_id = int(callback_data.replace("wd_approve_", ""))
        
        import json
        import os
        from datetime import datetime
        
        pending_file = os.path.join(os.path.dirname(__file__), 'pending_withdrawals.json')
        
        if not os.path.exists(pending_file):
            await query.answer("No pending withdrawals found", show_alert=True)
            return
        
        with open(pending_file, 'r') as f:
            pending_data = json.load(f)
        
        if str(target_user_id) not in pending_data:
            await query.answer("Withdrawal request not found or already processed", show_alert=True)
            return
        
        withdrawal_info = pending_data[str(target_user_id)]
        
        # Reset user's premium_earnings to 0 in both local DB and Supabase
        try:
            from database import Database
            db = Database()
            db.cursor.execute("""
                UPDATE users SET premium_earnings = 0 WHERE telegram_id = ?
            """, (target_user_id,))
            db.conn.commit()
            local_status = "Local DB reset"
        except Exception as e:
            local_status = f"Local DB error: {str(e)[:30]}"
        
        try:
            from supabase_client import supabase
            if supabase:
                supabase.table('users').update({
                    'premium_earnings': 0
                }).eq('telegram_id', target_user_id).execute()
                supabase_status = "Supabase reset"
            else:
                supabase_status = "Supabase not connected"
        except Exception as e:
            supabase_status = f"Supabase error: {str(e)[:30]}"
        
        # Mark as completed and remove from pending
        withdrawal_info['status'] = 'approved'
        withdrawal_info['approved_at'] = datetime.utcnow().isoformat()
        withdrawal_info['approved_by'] = admin_id
        
        # Save to history (optional)
        history_file = os.path.join(os.path.dirname(__file__), 'withdrawal_history.json')
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        else:
            history_data = []
        history_data.append(withdrawal_info)
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Remove from pending
        del pending_data[str(target_user_id)]
        with open(pending_file, 'w') as f:
            json.dump(pending_data, f, indent=2)
        
        # Update admin message
        await query.edit_message_text(
            f" <b>WITHDRAWAL APPROVED</b>\n\n"
            f" User: {withdrawal_info.get('user_name', 'N/A')} (@{withdrawal_info.get('username', 'N/A')})\n"
            f" UID: <code>{target_user_id}</code>\n\n"
            f" Amount: Rp {withdrawal_info.get('amount', 0):,}\n"
            f" Method: {withdrawal_info.get('method', 'N/A')}\n"
            f" Account: {withdrawal_info.get('account_info', 'N/A')}\n\n"
            f" Premium earnings reset to Rp 0\n"
            f" {local_status} | {supabase_status}\n"
            f" Approved: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
            parse_mode='HTML'
        )
        
        # Notify user
        try:
            user_text = f""" <b>WITHDRAWAL APPROVED!</b>

 Pembayaran Anda telah diproses!

 <b>Jumlah:</b> Rp {withdrawal_info.get('amount', 0):,}
 <b>Fee:</b> Rp {withdrawal_info.get('fee', 0):,}
 <b>Diterima:</b> Rp {withdrawal_info.get('net_amount', 0):,}

 <b>Metode:</b> {withdrawal_info.get('method', 'N/A')}
 <b>Ke:</b> {withdrawal_info.get('account_info', 'N/A')}

 <b>Saldo Premium Earnings:</b> Rp 0
(Reset setelah withdrawal)

Terima kasih telah menggunakan CryptoMentor AI!
Terus ajak teman untuk mendapatkan lebih banyak earnings!"""

            await context.bot.send_message(
                chat_id=target_user_id,
                text=user_text,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Failed to notify user {target_user_id}: {e}")
        
        await query.answer("Withdrawal approved and user notified!", show_alert=True)

    async def handle_admin_withdrawal_reject(self, query, context):
        """Admin rejects withdrawal request"""
        admin_id = query.from_user.id
        callback_data = query.data
        
        # Extract user_id from callback
        target_user_id = int(callback_data.replace("wd_reject_", ""))
        
        import json
        import os
        from datetime import datetime
        
        pending_file = os.path.join(os.path.dirname(__file__), 'pending_withdrawals.json')
        
        if not os.path.exists(pending_file):
            await query.answer("No pending withdrawals found", show_alert=True)
            return
        
        with open(pending_file, 'r') as f:
            pending_data = json.load(f)
        
        if str(target_user_id) not in pending_data:
            await query.answer("Withdrawal request not found or already processed", show_alert=True)
            return
        
        withdrawal_info = pending_data[str(target_user_id)]
        
        # Remove from pending (earnings NOT reset)
        del pending_data[str(target_user_id)]
        with open(pending_file, 'w') as f:
            json.dump(pending_data, f, indent=2)
        
        # Update admin message
        await query.edit_message_text(
            f" <b>WITHDRAWAL REJECTED</b>\n\n"
            f" User: {withdrawal_info.get('user_name', 'N/A')} (@{withdrawal_info.get('username', 'N/A')})\n"
            f" UID: <code>{target_user_id}</code>\n\n"
            f" Amount: Rp {withdrawal_info.get('amount', 0):,}\n"
            f" Method: {withdrawal_info.get('method', 'N/A')}\n\n"
            f" Premium earnings NOT reset (user can request again)\n"
            f" Rejected: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
            parse_mode='HTML'
        )
        
        # Notify user
        try:
            user_text = f""" <b>WITHDRAWAL REJECTED</b>

Maaf, request withdrawal Anda ditolak oleh admin.

 <b>Jumlah:</b> Rp {withdrawal_info.get('amount', 0):,}
 <b>Metode:</b> {withdrawal_info.get('method', 'N/A')}

 <b>Alasan yang mungkin:</b>
 Detail akun tidak valid
 Informasi tidak lengkap
 Perlu verifikasi tambahan

 <b>Saran:</b>
Silakan hubungi admin untuk klarifikasi atau submit ulang dengan data yang benar.

Saldo premium earnings Anda TIDAK berubah.
Anda dapat mengajukan withdrawal lagi."""

            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton(" Request Ulang", callback_data="referral_withdrawal")]]
            
            await context.bot.send_message(
                chat_id=target_user_id,
                text=user_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Failed to notify user {target_user_id}: {e}")
        
        await query.answer("Withdrawal rejected and user notified!", show_alert=True)

    def get_referral_tier_info(self, total_referrals):
        """Get comprehensive referral tier information"""
        if total_referrals >= 100:
            return {
                'name': 'DIAMOND', 'level': 5, 'bonus': 30, 'money_multiplier': 3.0,
                'icon': '', 'badge': ' Diamond Elite',
                'access': 'VIP Community + Direct Admin Access',
                'withdrawal_priority': 'Instant (0-2 hours)',
                'support_level': 'White-glove Priority Support'
            }
        elif total_referrals >= 50:
            return {
                'name': 'GOLD', 'level': 4, 'bonus': 20, 'money_multiplier': 2.5,
                'icon': '', 'badge': ' Gold Champion',
                'access': 'Premium Community + Beta Features',
                'withdrawal_priority': 'Fast Track (2-6 hours)',
                'support_level': 'Priority Support'
            }
        elif total_referrals >= 25:
            return {
                'name': 'SILVER', 'level': 3, 'bonus': 15, 'money_multiplier': 2.0,
                'icon': '', 'badge': ' Silver Elite',
                'access': 'Silver Community + Early Access',
                'withdrawal_priority': 'Accelerated (6-12 hours)',
                'support_level': 'Enhanced Support'
            }
        elif total_referrals >= 10:
            return {
                'name': 'BRONZE', 'level': 2, 'bonus': 10, 'money_multiplier': 1.5,
                'icon': '', 'badge': ' Bronze Achiever',
                'access': 'Member Community',
                'withdrawal_priority': 'Standard (12-24 hours)',
                'support_level': 'Standard Support'
            }
        else:
            return {
                'name': 'STARTER', 'level': 1, 'bonus': 5, 'money_multiplier': 1.0,
                'icon': '', 'badge': ' Rising Star',
                'access': 'Basic Community',
                'withdrawal_priority': 'Normal (24-48 hours)',
                'support_level': 'Community Support'
            }

    def get_next_tier_info(self, total_referrals):
        """Get information about next tier"""
        if total_referrals >= 100:
            return {'name': 'DIAMOND ELITE', 'requirement': 200}
        elif total_referrals >= 50:
            return {'name': 'DIAMOND', 'requirement': 100}
        elif total_referrals >= 25:
            return {'name': 'GOLD', 'requirement': 50}
        elif total_referrals >= 10:
            return {'name': 'SILVER', 'requirement': 25}
        else:
            return {'name': 'BRONZE', 'requirement': 10}

    def calculate_monthly_potential(self, total_referrals, active_referrals):
        """Calculate estimated monthly earning potential"""
        if total_referrals == 0:
            return 0
        
        # Base calculation: assume 10% of referrals become premium monthly
        conversion_rate = 0.10
        avg_premium_value = 15000  # Average premium subscription value
        
        # Tier multiplier
        tier = self.get_referral_tier_info(total_referrals)
        multiplier = tier['money_multiplier']
        
        estimated = total_referrals * conversion_rate * avg_premium_value * 0.1 * multiplier
        return int(estimated)

    def get_tier_specific_tips(self, tier_level):
        """Get tier-specific growth tips"""
        tips = {
            1: " **STARTER STRATEGY:**\n Share di 2-3 grup crypto\n Ajak 5 teman trading pertama\n Focus quality over quantity",
            2: " **BRONZE GROWTH:**\n Expand ke 5+ crypto communities\n Create tutorial content\n Build personal crypto network",
            3: " **SILVER SCALING:**\n Launch referral campaign\n Partner dengan crypto influencers\n Host crypto learning sessions",
            4: " **GOLD MASTERY:**\n Build referral sub-network\n Mentor bronze/silver members\n Create premium content strategy",
            5: " **DIAMOND EXCELLENCE:**\n Lead community initiatives\n Develop scalable systems\n Mentor entire referral network"
        }
        return tips.get(tier_level, tips[1])

    def get_rewards_display(self, tier_level, total_referrals):
        """Display unlocked rewards"""
        rewards = []
        
        if tier_level >= 1:
            rewards.append(" 5 credits per free referral")
        if tier_level >= 2:
            rewards.append(" 10% bonus credits")
            rewards.append(" Bronze badge & community access")
        if tier_level >= 3:
            rewards.append(" 15% bonus credits")
            rewards.append(" Early access to features")
        if tier_level >= 4:
            rewards.append(" 20% bonus credits")
            rewards.append(" VIP support channel")
        if tier_level >= 5:
            rewards.append(" 30% bonus credits")
            rewards.append(" Direct admin access")
            
        # Milestone rewards
        milestones = [
            (5, " 50 bonus credits"),
            (15, " 100 bonus credits + 1 day premium"),
            (30, " 1 week premium trial"),
            (75, " 1 month premium"),
        ]
        
        for milestone, reward in milestones:
            if total_referrals >= milestone:
                rewards.append(f" {reward}")
        
        return "\n".join(rewards) if rewards else " Complete first referral to unlock rewards"

    async def handle_referral_guide(self, query, context):
        """Show comprehensive referral guide"""
        guide_text = """ **PANDUAN REFERRAL MASTER**

 **STRATEGI DASAR:**

**1. TARGET AUDIENCE YANG TEPAT** 
 Trader crypto pemula (butuh guidance)
 Member grup crypto aktif
 Followers crypto influencers
 Teman yang tertarik investasi

**2. PLATFORM SHARING OPTIMAL** 
 WhatsApp: Personal approach, trust tinggi
 Telegram Groups: Crypto communities
 Discord: Gaming + crypto communities  
 Twitter/X: Crypto Twitter audience
 Instagram Stories: Visual appeal

**3. CONTENT STRATEGY** 
 Screenshot profit dari bot signals
 Tutorial cara pakai bot (video)
 Testimonial hasil trading
 Before/After portfolio growth
 Educational crypto content

**4. TIMING YANG TEPAT** ⏰
 Bull market: Share profit screenshots
 Bear market: Share risk management tips
 News events: Share quick analysis
 Weekend: Educational content
 Asian hours: Indonesian audience

**5. CONVERSION TACTICS** 
 Offer free 1-on-1 crypto guidance
 Share exclusive trading tips
 Create beginner-friendly tutorials
 Build trust through consistency
 Follow up dengan referrals

 **PRO TIPS:**
 Authenticity > Hard selling
 Educational content builds trust  
 Personal success story works best
 Community building = long-term success
 Quality referrals > Quantity spam"""

        keyboard = [
            [InlineKeyboardButton(" Advanced Strategies", callback_data="advanced_referral_guide")],
            [InlineKeyboardButton(" Back to Stats", callback_data="referral_stats")],
        ]

        await query.edit_message_text(
            text=guide_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

    async def handle_tier_system_guide(self, query, context):
        """Show comprehensive tier system guide"""
        tier_guide = """ **TIER SYSTEM GUIDE - PATH TO DIAMOND**

 **TIER OVERVIEW:**

** STARTER (0 referrals)**
 Bonus: 5% extra credits
 Rewards: Learning phase
 Goal: First 10 referrals

** BRONZE (10-24 referrals)** 
 Bonus: 10% extra credits + 1.5x money
 Rewards: Community access
 Goal: Build foundation network

** SILVER (25-49 referrals)**
 Bonus: 15% extra credits + 2x money  
 Rewards: Early feature access
 Goal: Scale & systematize

** GOLD (50-99 referrals)**
 Bonus: 20% extra credits + 2.5x money
 Rewards: VIP community + priority support
 Goal: Leadership & mentoring

** DIAMOND (100+ referrals)**
 Bonus: 30% extra credits + 3x money
 Rewards: Elite access + admin connection
 Goal: Master referral ecosystem

 **PROGRESSION STRATEGY:**

**Phase 1: Foundation (0→10)**
 Duration: 2-4 weeks
 Focus: Friends & family
 Method: Personal recommendation

**Phase 2: Growth (10→25)**  
 Duration: 1-2 months
 Focus: Community expansion
 Method: Content + networking

**Phase 3: Scale (25→50)**
 Duration: 2-3 months  
 Focus: System building
 Method: Partnerships + automation

**Phase 4: Mastery (50→100)**
 Duration: 3-6 months
 Focus: Leadership
 Method: Team building + mentoring

 **EARNING POTENTIAL:**
 STARTER: ~Rp 50K/month
 BRONZE: ~Rp 200K/month
 SILVER: ~Rp 500K/month  
 GOLD: ~Rp 1.5M/month
 DIAMOND: ~Rp 5M+/month

*Estimasi berdasarkan 10% conversion rate ke premium*"""

        keyboard = [
            [InlineKeyboardButton(" My Progress", callback_data="referral_stats")],
            [InlineKeyboardButton(" Strategy Guide", callback_data="referral_guide")],
        ]

        await query.edit_message_text(
            text=tier_guide,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

    async def handle_advanced_referral_guide(self, query, context):
        """Show advanced referral strategies"""
        advanced_guide = """ **ADVANCED REFERRAL MASTERY**

 **PSYCHOLOGICAL TRIGGERS:**

**1. SCARCITY & URGENCY** ⏰
 "Limited 100 credits bonus berakhir minggu ini"
 "Premium trial hanya untuk 50 orang pertama"
 "Exclusive early access buat referral hari ini"

**2. SOCIAL PROOF** 
 Screenshot testimonial success stories
 "Join 10,000+ active traders di Indonesia"
 Share leaderboard achievements

**3. RECIPROCITY PRINCIPLE** 
 Berikan free value dulu (tips, analysis)
 Free crypto education sebelum referral
 Help solve their trading problems first

**4. AUTHORITY POSITIONING** 
 Share your trading wins/credentials
 Educational content yang valuable
 Position as crypto mentor/guide

 **CONVERSION OPTIMIZATION:**

**A. LANDING EXPERIENCE**
 Personal onboarding untuk setiap referral
 Custom welcome message
 Free consultation offer

**B. RETENTION STRATEGY**  
 Weekly check-in dengan referrals
 Share exclusive trading insights
 Build long-term relationships

**C. UPSELLING FUNNEL**
 Free user → Credits exhausted → Premium push
 Social proof dari existing premium users
 Limited-time upgrade discounts

 **TRACKING & ANALYTICS:**

**Conversion Metrics:**
 Click-through rate dari link
 Free registration rate
 Premium conversion rate
 Monthly retention rate

**Optimization Points:**
 A/B test different messaging
 Track which platforms perform best  
 Identify highest-value referral sources
 Optimize timing untuk maximum impact

 **AUTOMATION TOOLS:**

 Auto-follow up messages
 Scheduled content sharing
 Referral performance tracking
 Reward notifications

 **DIAMOND-TIER SECRETS:**
 Build referral teams (MLM-style)
 Create crypto trading courses
 Host exclusive webinars
 Partner dengan crypto projects
 Develop personal brand as crypto expert"""

        keyboard = [
            [InlineKeyboardButton(" Basic Guide", callback_data="referral_guide")],
            [InlineKeyboardButton(" Tier System", callback_data="tier_system_guide")],
            [InlineKeyboardButton(" Back to Stats", callback_data="referral_stats")],
        ]

        await query.edit_message_text(
            text=advanced_guide,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='MARKDOWN'
        )

    async def handle_set_language(self, query, context):
        """Handle language selection from buttons"""
        user_id = query.from_user.id
        lang_code = query.data.split('_')[-1]  # Extract 'en' or 'id' from 'set_lang_en'
        
        if lang_code not in ['en', 'id']:
            await query.answer(" Invalid language selection", show_alert=True)
            return
            
        try:
            from database import Database
            db = Database()
            
            # Update user language
            success = db.update_user_language(user_id, lang_code)
            
            if success:
                lang_names = {'en': 'English', 'id': 'Bahasa Indonesia'}
                
                if lang_code == 'id':
                    success_msg = f""" **Bahasa berhasil diubah ke {lang_names[lang_code]}!**

 **Perubahan yang aktif:**
 Menu dan pesan dalam Bahasa Indonesia  
 Analisis trading dalam bahasa Indonesia
 Support customer dalam bahasa Indonesia

 **Catatan:** Bot sekarang akan merespons dalam Bahasa Indonesia."""
                    await query.answer(" Bahasa berhasil diubah ke Bahasa Indonesia!")
                else:
                    success_msg = f""" **Language changed to {lang_names[lang_code]}!**

 **Active Changes:**
 Menus and messages in English
 Trading analysis in English  
 Customer support in English

 **Note:** Bot will now respond in English."""
                    await query.answer(" Language changed to English!")
                
                # Show success message with proper language
                await query.edit_message_text(
                    success_msg,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(" Kembali ke Pengaturan" if lang_code == 'id' else " Back to Settings", callback_data=SETTINGS_MENU)]]),
                    parse_mode='MARKDOWN'
                )
                
            else:
                await query.answer(" Gagal mengubah bahasa. Silakan coba lagi." if lang_code == 'id' else " Failed to update language. Please try again.", show_alert=True)
                
        except Exception as e:
            print(f"Error setting language: {e}")
            await query.answer(" Error mengubah bahasa. Silakan coba lagi." if lang_code == 'id' else " Error updating language. Please try again.", show_alert=True)

    async def handle_automaton_first_deposit(self, query, context):
        """
        Handle first deposit flow for AI Agent access - CENTRALIZED WALLET
        
        Shows centralized wallet address for deposits. All users deposit to the same wallet
        which is connected to Conway Dashboard for automatic credit conversion.
        """
        print(f"🔍 DEBUG: handle_automaton_first_deposit called for user {query.from_user.id}")
        user_id = query.from_user.id
        from database import Database
        db = Database()
        user_lang = db.get_user_language(user_id)
        print(f"🔍 DEBUG: User language: {user_lang}")
        
        try:
            # Check if Supabase is enabled
            if not db.supabase_enabled:
                error_msg = " Database tidak tersedia. Silakan coba lagi nanti." if user_lang == 'id' else " Database unavailable. Please try again later."
                await query.edit_message_text(error_msg, parse_mode='MARKDOWN')
                return
            
            # Get centralized wallet address from environment
            import os
            centralized_wallet = os.getenv('CENTRALIZED_WALLET_ADDRESS', '0x63116672bef9f26fd906cd2a57550f7a13925822')
            
            # Record that user clicked deposit button (pending deposit)
            try:
                # Check if user already has pending deposit
                existing = db.supabase_service.table('pending_deposits')\
                    .select('*')\
                    .eq('user_id', user_id)\
                    .execute()
                
                if not existing.data:
                    # Create new pending deposit record
                    db.supabase_service.table('pending_deposits').insert({
                        'user_id': user_id,
                        'telegram_username': query.from_user.username,
                        'telegram_first_name': query.from_user.first_name,
                        'status': 'waiting'
                    }).execute()
                    print(f" Created pending deposit record for user {user_id}")
            except Exception as e:
                print(f"  Warning: Could not create pending deposit record: {e}")
                # Continue anyway, this is not critical
            
            # Generate QR code URL
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={centralized_wallet}"
            
            # Format deposit instructions based on language (Updated: Manual verification by admin)
            if user_lang == 'id':
                deposit_text = f"""💰 **Deposit USDC (Base Network)**

🎯 **TUJUAN TRANSFER:**
📍 **Address Tujuan:**
`{centralized_wallet}`

📱 **QR Code:**
[Klik untuk melihat QR Code]({qr_url})

⚠️ **PENTING - Baca Sebelum Transfer:**
✅ Kirim USDC ke address di atas
✅ HANYA gunakan Base Network
✅ Setelah transfer, kirim bukti ke admin untuk verifikasi
✅ Credits akan ditambahkan manual oleh admin

🌐 **Network:**
✅ Base Network (WAJIB)
⚡ Biaya gas rendah (~$0.01)

💱 **Conversion Rate:**
💵 1 USDC = 100 Conway Credits
💵 $10 USDC = 1.000 Credits

💰 **MINIMAL DEPOSIT: $10 USDC**
⚠️ **Perlu Diketahui:**
$10 bukan pure modal trading AI, tapi ada campuran:
• Modal trading AI Agent Anda
• Biaya operasional AI (bensin Automaton = USDC)
• Biaya infrastruktur Conway + Railway

🤖 **Minimum untuk Spawn Agent:**
💰 Deposit minimum: $10 USDC (1.000 credits)
✅ Spawn: GRATIS (no spawn fee)
📊 Total dibutuhkan: $10 USDC

📋 **Cara Kerja Deposit:**
1. Anda kirim USDC (Base Network) ke address di atas
2. Screenshot bukti transfer (transaction hash)
3. Klik tombol "📤 Kirim Bukti Transfer" di bawah
4. Kirim screenshot ke admin
5. Admin akan verifikasi dan tambahkan credits
6. Anda akan menerima notifikasi saat credits masuk

📝 **Langkah-langkah Deposit:**
1. Copy address di atas atau scan QR code
2. Buka wallet Anda (MetaMask, Trust Wallet, dll)
3. Pastikan network: Base
4. Kirim minimal $10 USDC ke address di atas
5. Screenshot bukti transfer
6. Klik "📤 Kirim Bukti Transfer" dan kirim ke admin
7. Tunggu verifikasi admin (biasanya < 1 jam)

📌 **Catatan:**
⚠️ Semua user (termasuk admin) bisa deposit minimal $10
✅ Ini fase BETA TEST - akses terbuka untuk semua
❌ JANGAN kirim ke network lain (dana akan hilang!)
💾 Simpan transaction hash untuk tracking"""
            else:
                deposit_text = f"""💰 **Deposit USDC (Base Network)**

🎯 **TRANSFER DESTINATION:**
📍 **Destination Address:**
`{centralized_wallet}`

📱 **QR Code:**
[Click to view QR Code]({qr_url})

⚠️ **IMPORTANT - Read Before Transfer:**
✅ Send USDC to the address above
✅ ONLY use Base Network
✅ After transfer, send proof to admin for verification
✅ Credits will be added manually by admin

🌐 **Network:**
✅ Base Network (REQUIRED)
⚡ Low gas fees (~$0.01)

💱 **Conversion Rate:**
💵 1 USDC = 100 Conway Credits
💵 $10 USDC = 1,000 Credits

💰 **MINIMUM DEPOSIT: $10 USDC**
⚠️ **Please Note:**
$10 is not pure AI trading capital, it includes:
• Your AI Agent trading capital
• AI operational costs (Automaton fuel = USDC)
• Conway + Railway infrastructure fees

🤖 **Minimum for Spawn Agent:**
💰 Minimum deposit: $10 USDC (1,000 credits)
✅ Spawn: FREE (no spawn fee)
📊 Total needed: $10 USDC

📋 **How Deposit Works:**
1. You send USDC (Base Network) to the address above
2. Screenshot transfer proof (transaction hash)
3. Click "📤 Send Transfer Proof" button below
4. Send screenshot to admin
5. Admin will verify and add credits
6. You will receive notification when credits arrive

📝 **Deposit Steps:**
1. Copy address above or scan QR code
2. Open your wallet (MetaMask, Trust Wallet, etc)
3. Make sure network: Base
4. Send minimum $10 USDC to the address above
5. Screenshot transfer proof
6. Click "📤 Send Transfer Proof" and send to admin
7. Wait for admin verification (usually < 1 hour)

📌 **Notes:**
⚠️ All users (including admin) can deposit minimum $10
✅ This is BETA TEST phase - open access for everyone
❌ DO NOT send to other networks (funds will be lost!)
💾 Save transaction hash for tracking"""
            
            # Build keyboard with send proof button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Get admin contact info
            admin_ids_str = os.getenv('ADMIN_IDS', '')
            admin_contact = ""
            if admin_ids_str:
                # Get first admin ID for contact
                first_admin_id = admin_ids_str.split(',')[0].strip()
                admin_contact = f"tg://user?id={first_admin_id}"
            
            keyboard = [
                [InlineKeyboardButton(" Kirim Bukti Transfer ke Admin" if user_lang == 'id' else " Send Transfer Proof to Admin", 
                                     url=admin_contact if admin_contact else "https://t.me/")],
                [InlineKeyboardButton(" Cara Deposit" if user_lang == 'id' else " How to Deposit", 
                                     callback_data="deposit_guide")],
                [InlineKeyboardButton(" Kembali" if user_lang == 'id' else " Back", 
                                     callback_data=AI_AGENT_MENU)]
            ]
            
            await query.edit_message_text(
                deposit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )
            
        except Exception as e:
            print(f" Error in handle_automaton_first_deposit: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = f" Terjadi kesalahan. Silakan coba lagi atau hubungi support." if user_lang == 'id' else f" Error occurred. Please try again or contact support."
            
            keyboard = [[InlineKeyboardButton(" Kembali" if user_lang == 'id' else " Back", callback_data=AI_AGENT_MENU)]]
            await query.edit_message_text(
                error_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )

    async def handle_deposit_guide(self, query, context):
        """
        Display comprehensive deposit guide
        
        Shows step-by-step instructions, supported networks, conversion rates,
        minimum deposit, and troubleshooting tips.
        """
        user_id = query.from_user.id
        from database import Database
        db = Database()
        user_lang = db.get_user_language(user_id)
        
        try:
            # Format guide based on language (Updated: Manual verification by admin)
            if user_lang == 'id':
                guide_text = """ **Panduan Deposit USDC (Base Network)**

 **Langkah-langkah Deposit:**

1⃣ **Klik " Deposit Sekarang"**
    Anda akan menerima alamat wallet
    Salin alamat atau scan QR code

2⃣ **Pilih Network: Base**
    HANYA gunakan Base Network
    Biaya gas rendah (~$0.01)
    Network lain TIDAK didukung

3⃣ **Kirim USDC**
    Minimum: $30 USDC (untuk spawn agent)
    HANYA USDC (bukan USDT atau token lain)
    Gunakan wallet Anda (MetaMask, Trust Wallet, dll)
    Pastikan network: Base

4⃣ **Screenshot Bukti Transfer**
    Ambil screenshot transaction hash
    Atau screenshot dari wallet Anda
    Pastikan terlihat: amount, network, address tujuan

5⃣ **Kirim ke Admin**
    Klik tombol " Kirim Bukti Transfer"
    Kirim screenshot ke admin
    Sertakan User ID Telegram Anda: `{user_id}`
    Admin akan verifikasi dalam < 1 jam

6⃣ **Tunggu Verifikasi**
    Admin akan cek transaksi di blockchain
    Credits akan ditambahkan manual
    Anda akan menerima notifikasi
    Cek balance dengan /balance

 **Conversion Rate:**
 1 USDC = 100 Conway Credits
 $30 USDC = 3.000 Credits

 **Minimum untuk Spawn Agent:**
 Deposit minimum: $10 USDC (1.000 credits)
 Spawn: GRATIS (no spawn fee)
 Total dibutuhkan: $10 USDC

 **Network:**
  Base Network (WAJIB)
  Polygon (Tidak didukung)
  Arbitrum (Tidak didukung)
  Ethereum Mainnet (Tidak didukung)
  BSC (Tidak didukung)

 **Troubleshooting:**

**Q: Deposit belum masuk?**
A: Pastikan Anda sudah kirim bukti transfer ke admin. Admin akan verifikasi dalam < 1 jam.

**Q: Salah network?**
A: Dana akan hilang! HANYA gunakan Base Network.

**Q: Minimum deposit?**
A: $30 USDC untuk spawn agent. Deposit di bawah ini tidak cukup.

**Q: Berapa lama proses?**
A: Setelah kirim bukti ke admin, biasanya < 1 jam untuk verifikasi.

**Q: Bisa pakai USDT?**
A: TIDAK. Hanya USDC yang didukung.

**Q: Bagaimana cara kirim bukti?**
A: Klik tombol " Kirim Bukti Transfer" di menu deposit, lalu kirim screenshot ke admin.

 **Tips:**
 Selalu cek alamat sebelum kirim
 Pastikan network: Base
 HANYA kirim USDC
 Minimum $30 untuk spawn agent
 Simpan transaction hash untuk tracking
 Sertakan User ID saat kirim bukti: `{user_id}`

 **Catatan Penting:**
 Admin & Lifetime Premium juga perlu deposit $30
 Setelah deposit $30, Anda bisa spawn agent
 Deposit di network lain akan hilang!
 Verifikasi manual untuk keamanan maksimal"""
            else:
                guide_text = """ **USDC Deposit Guide (Base Network)**

 **Deposit Steps:**

1⃣ **Click " Deposit Now"**
    You'll receive a wallet address
    Copy address or scan QR code

2⃣ **Select Network: Base**
    ONLY use Base Network
    Low gas fees (~$0.01)
    Other networks NOT supported

3⃣ **Send USDC**
    Minimum: $30 USDC (to spawn agent)
    ONLY USDC (not USDT or other tokens)
    Use your wallet (MetaMask, Trust Wallet, etc)
    Make sure network: Base

4⃣ **Screenshot Transfer Proof**
    Take screenshot of transaction hash
    Or screenshot from your wallet
    Make sure visible: amount, network, destination address

5⃣ **Send to Admin**
    Click " Send Transfer Proof" button
    Send screenshot to admin
    Include your Telegram User ID: `{user_id}`
    Admin will verify within < 1 hour

6⃣ **Wait for Verification**
    Admin will check transaction on blockchain
    Credits will be added manually
    You will receive notification
    Check balance with /balance

 **Conversion Rate:**
 1 USDC = 100 Conway Credits
 $30 USDC = 3,000 Credits

 **Minimum for Spawn Agent:**
 Minimum deposit: $10 USDC (1,000 credits)
 Spawn: FREE (no spawn fee)
 Total needed: $10 USDC

 **Network:**
  Base Network (REQUIRED)
  Polygon (Not supported)
  Arbitrum (Not supported)
  Ethereum Mainnet (Not supported)
  BSC (Not supported)

 **Troubleshooting:**

**Q: Deposit not received?**
A: Make sure you sent transfer proof to admin. Admin will verify within < 1 hour.

**Q: Wrong network?**
A: Funds will be lost! ONLY use Base Network.

**Q: Minimum deposit?**
A: $30 USDC to spawn agent. Deposits below this are insufficient.

**Q: How long does it take?**
A: After sending proof to admin, usually < 1 hour for verification.

**Q: Can I use USDT?**
A: NO. Only USDC is supported.

**Q: How to send proof?**
A: Click " Send Transfer Proof" button in deposit menu, then send screenshot to admin.

 **Tips:**
 Always verify address before sending
 Make sure network: Base
 ONLY send USDC
 Minimum $30 to spawn agent
 Save transaction hash for tracking
 Include User ID when sending proof: `{user_id}`

 **Important Notes:**
 Admin & Lifetime Premium also need $30 deposit
 After $30 deposit, you can spawn agent
 Deposits on other networks will be lost!
 Manual verification for maximum security"""
            
            # Build keyboard
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton(" Kembali ke Deposit" if user_lang == 'id' else " Back to Deposit", 
                                     callback_data="automaton_first_deposit")],
                [InlineKeyboardButton(" Menu Utama" if user_lang == 'id' else " Main Menu", 
                                     callback_data=MAIN_MENU)]
            ]
            
            await query.edit_message_text(
                guide_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )
            
        except Exception as e:
            print(f" Error in handle_deposit_guide: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = " Terjadi kesalahan. Silakan coba lagi." if user_lang == 'id' else " An error occurred. Please try again."
            
            keyboard = [[InlineKeyboardButton(" Kembali" if user_lang == 'id' else " Back", callback_data=AI_AGENT_MENU)]]
            await query.edit_message_text(
                error_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='MARKDOWN'
            )

    async def handle_ai_agent_education(self, query, context):
        """
        Handle AI Agent education callback - show comprehensive education
        """
        from app.handlers_ai_agent_education import _show_education_content
        await _show_education_content(query, context)

    async def handle_ai_agent_faq(self, query, context):
        """
        Handle AI Agent FAQ callback
        """
        from app.handlers_ai_agent_education import show_ai_agent_faq
        await show_ai_agent_faq(query, context)

    async def handle_ai_agent_docs(self, query, context):
        """
        Handle AI Agent documentation callback
        """
        from app.handlers_ai_agent_education import show_ai_agent_docs
        await show_ai_agent_docs(query, context)


def register_menu_handlers(application, bot_instance):
    """Register all menu callback handlers with proper pattern to avoid conflicts"""
    menu_handler = MenuCallbackHandler(bot_instance)

    # Register the main callback handler with negative lookahead to exclude admin_ and signal_tf_
    # This prevents conflicts with other handlers
    application.add_handler(
        CallbackQueryHandler(
            menu_handler.handle_callback_query,
            pattern=r'^(?!admin_|signal_tf_|spawn_).*'  # Exclude admin_, signal_tf_, and spawn_ patterns
        )
    )

    print(" Menu system handlers registered successfully (with conflict prevention)")