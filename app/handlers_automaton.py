# Automaton Telegram Bot Handlers
# Handles user interactions for autonomous trading agents

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import Database
from app.automaton_manager import get_automaton_manager
from app.rate_limiter import get_rate_limiter
from app.lineage_integration import (
    on_agent_spawn,
    get_agent_lineage_info,
    get_agent_lineage_tree,
    format_lineage_tree_text
)
from app.admin_status import is_admin

# Initialize database
db = Database()
automaton_manager = get_automaton_manager(db)
rate_limiter = get_rate_limiter(db)


async def spawn_agent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /spawn_agent command - Spawn a new autonomous trading agent
    
    Requirements:
    - Automaton access (Rp2,000,000 one-time fee)
    - Premium status
    - >= 100,000 credits
    - Rate limit: 1 spawn per hour
    """
    user_id = update.effective_user.id
    
    try:
        # Check rate limit FIRST (prevent spam)
        allowed, error_msg = rate_limiter.check_spawn_limit(user_id)
        if not allowed:
            await update.message.reply_text(
                error_msg,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check Automaton access (BYPASS for admins)
        if not is_admin(user_id) and not db.has_automaton_access(user_id):
            await update.message.reply_text(
                "❌ *Akses Automaton Diperlukan*\n\n"
                "Untuk menggunakan fitur AI Agent, Anda perlu membayar biaya satu kali sebesar *Rp2.000.000*.\n\n"
                "Gunakan /subscribe untuk upgrade ke Automaton access.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check premium status (BYPASS for admins)
        if not is_admin(user_id) and not db.is_user_premium(user_id):
            await update.message.reply_text(
                "❌ *Premium Diperlukan*\n\n"
                "Fitur AI Agent hanya tersedia untuk pengguna premium.\n\n"
                "Gunakan /subscribe untuk upgrade.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check minimum deposit requirement ($30 = 3000 credits)
        # This applies to EVERYONE including admin and lifetime premium
        MINIMUM_DEPOSIT_CREDITS = 3000  # $30 USDC = 3000 credits
        
        user_credits = 0
        try:
            if db.supabase_enabled:
                from supabase_client import supabase
                if supabase:
                    # Check user_credits_balance table
                    credits_result = supabase.table('user_credits_balance')\
                        .select('available_credits, total_conway_credits')\
                        .eq('user_id', user_id)\
                        .execute()
                    
                    if credits_result.data:
                        balance = credits_result.data[0]
                        available_credits = float(balance.get('available_credits', 0))
                        total_credits = float(balance.get('total_conway_credits', 0))
                        user_credits = max(available_credits, total_credits)
        except Exception as e:
            print(f"⚠️ Error checking credits: {e}")
        
        # Check minimum deposit (applies to everyone)
        if user_credits < MINIMUM_DEPOSIT_CREDITS:
            await update.message.reply_text(
                f"❌ *Deposit Minimum Diperlukan*\n\n"
                f"Untuk spawn agent, Anda perlu deposit minimal *$30 USDC* (3.000 credits).\n\n"
                f"💰 Credits Anda saat ini: {user_credits:,.0f}\n"
                f"💵 Minimum required: {MINIMUM_DEPOSIT_CREDITS:,}\n"
                f"📊 Kekurangan: {MINIMUM_DEPOSIT_CREDITS - user_credits:,.0f} credits\n\n"
                f"💡 Cara deposit:\n"
                f"1. Gunakan /deposit untuk melihat address\n"
                f"2. Deposit USDC (Base Network)\n"
                f"3. 1 USDC = 100 credits\n"
                f"4. Minimum deposit: $5 USDC\n\n"
                f"Setelah deposit $30, Anda bisa spawn agent!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check spawn fee (100k credits for spawning)
        SPAWN_FEE = 100000
        if user_credits < SPAWN_FEE:
            await update.message.reply_text(
                f"❌ *Kredit Tidak Cukup untuk Spawn*\n\n"
                f"Spawn agent membutuhkan 100.000 kredit.\n"
                f"Kredit Anda: {user_credits:,}\n\n"
                f"Gunakan /credits untuk mendapatkan lebih banyak kredit.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Prompt for agent name
        if not context.args:
            await update.message.reply_text(
                "🤖 *Spawn AI Agent*\n\n"
                "Berikan nama untuk agent Anda:\n\n"
                "`/spawn_agent <nama_agent>`\n\n"
                "Contoh: `/spawn_agent TradingBot1`\n\n"
                f"💰 Biaya: 100.000 kredit\n"
                f"💳 Kredit Anda: {user_credits:,}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get agent name from args
        agent_name = ' '.join(context.args)
        
        # Check if user wants to spawn from parent (optional parent selection)
        parent_agent_id = None
        
        # Get user's existing agents to offer as parent options
        existing_agents = automaton_manager.get_user_agents(user_id)
        
        if existing_agents and len(existing_agents) > 0:
            # User has existing agents - offer parent selection
            keyboard = []
            keyboard.append([InlineKeyboardButton("🆕 No Parent (New Root Agent)", callback_data=f"spawn_noparent_{agent_name}")])
            
            for agent in existing_agents[:5]:  # Limit to 5 agents
                agent_id = agent['agent_id']
                agent_display_name = agent['agent_name']
                keyboard.append([
                    InlineKeyboardButton(
                        f"👶 Spawn from: {agent_display_name}",
                        callback_data=f"spawn_parent_{agent_id}_{agent_name}"
                    )
                ])
            
            await update.message.reply_text(
                f"🤖 *Spawn Agent: {agent_name}*\n\n"
                f"Pilih parent agent (opsional):\n\n"
                f"💡 *Lineage System:*\n"
                f"• Jika Anda spawn dari parent, parent akan mendapat 10% dari earnings agent ini\n"
                f"• Ini berlaku rekursif hingga 10 level\n"
                f"• Pilih 'No Parent' untuk membuat root agent baru\n\n"
                f"💰 Biaya: 100.000 kredit",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # No existing agents, spawn as root
        # Show confirmation
        await update.message.reply_text(
            f"⏳ Spawning agent *{agent_name}*...\n\n"
            f"Mohon tunggu sebentar...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Spawn the agent
        result = automaton_manager.spawn_agent(
            user_id=user_id,
            agent_name=agent_name,
            genesis_prompt="You are an autonomous trading agent. Trade wisely and maximize profits."
        )
        
        if result['success']:
            agent_id = result.get('agent_id')
            
            # Register lineage (no parent for first agent)
            await on_agent_spawn(agent_id, None)
            
            # Success message with agent details
            message = (
                f"✅ *Agent Berhasil Dibuat!*\n\n"
                f"🤖 Nama: `{agent_name}`\n"
                f"💼 Wallet: `{result['agent_wallet']}`\n"
                f"📍 Deposit Address:\n`{result['deposit_address']}`\n\n"
                f"💰 Biaya Spawn: {result['spawn_fee']:,} kredit\n"
                f"💳 Sisa Kredit: {result['remaining_credits']:,}\n\n"
                f"⚠️ *Agent belum aktif!*\n"
                f"Deposit USDT/USDC ke address di atas untuk mengaktifkan agent.\n\n"
                f"Gunakan /deposit untuk melihat QR code dan instruksi deposit."
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Error message
            await update.message.reply_text(
                f"❌ *Gagal Spawn Agent*\n\n"
                f"{result['message']}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in spawn_agent_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat spawn agent. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def agent_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /agent_status command - Show agent status
    
    Displays:
    - Agent name, wallet, credits
    - Survival tier with emoji
    - Last activity, runtime estimate
    - Total earnings, expenses, net P&L
    - Lineage info (parent, children, revenue from children)
    """
    user_id = update.effective_user.id
    
    try:
        # Get user's agents
        agents = automaton_manager.get_user_agents(user_id)
        
        if not agents:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Display status for each agent
        for agent in agents:
            agent_id = agent['agent_id']
            
            # Survival tier emoji
            tier_emoji = {
                'normal': '🟢',
                'low_compute': '🟡',
                'critical': '🔴',
                'dead': '⚫'
            }
            emoji = tier_emoji.get(agent['survival_tier'], '⚪')
            
            # Format P&L
            net_pnl = agent['net_pnl']
            pnl_emoji = '📈' if net_pnl >= 0 else '📉'
            pnl_text = f"+{net_pnl:,.2f}" if net_pnl >= 0 else f"{net_pnl:,.2f}"
            
            # Get lineage info
            lineage_info = get_agent_lineage_info(agent_id)
            
            # Build lineage section
            lineage_text = "\n\n🌳 *Lineage Info*\n"
            if lineage_info.get('parent_name'):
                lineage_text += f"👨 Parent: {lineage_info['parent_name']}\n"
            else:
                lineage_text += f"👨 Parent: None (Root Agent)\n"
            
            lineage_text += f"👶 Children: {lineage_info.get('total_children_count', 0)}\n"
            
            children_revenue = lineage_info.get('total_revenue_from_children', 0)
            if children_revenue > 0:
                lineage_text += f"💰 Revenue from Children: {children_revenue:,.2f} credits\n"
            
            message = (
                f"🤖 *Status Agent*\n\n"
                f"📛 Nama: `{agent['agent_name']}`\n"
                f"💼 Wallet: `{agent['agent_wallet']}`\n"
                f"💰 Conway Credits: {agent['balance']:,.2f}\n\n"
                f"{emoji} *Survival Tier:* {agent['survival_tier'].upper()}\n"
                f"⏱️ Runtime Estimate: {agent['runtime_days']:.1f} hari\n"
                f"🕐 Last Active: {agent['last_active'][:19]}\n\n"
                f"📊 *Performance*\n"
                f"💵 Total Earnings: {agent['total_earnings']:,.2f}\n"
                f"💸 Total Expenses: {agent['total_expenses']:,.2f}\n"
                f"{pnl_emoji} Net P&L: {pnl_text}\n"
                f"{lineage_text}\n"
                f"📍 Deposit Address:\n`{agent['deposit_address']}`"
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in agent_status_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat mengambil status agent. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /deposit command - Show deposit address with QR code
    
    Displays:
    - Wallet address (monospace)
    - QR code URL
    - Supported networks
    - Conversion rates
    - Minimum deposit
    """
    user_id = update.effective_user.id
    
    try:
        # Get user's agents
        agents = automaton_manager.get_user_agents(user_id)
        
        if not agents:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get first agent's deposit address
        agent = agents[0]
        deposit_address = agent['deposit_address']
        
        # Generate QR code URL
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={deposit_address}"
        
        # Deposit instructions (Updated: $30 minimum, Base network only)
        message = (
            f"💰 *Deposit USDC (Base Network)*\n\n"
            f"📍 *Deposit Address:*\n"
            f"`{deposit_address}`\n\n"
            f"📱 *QR Code:*\n"
            f"{qr_url}\n\n"
            f"🌐 *Network:*\n"
            f"• Base Network (WAJIB)\n"
            f"• Biaya gas rendah (~$0.01)\n\n"
            f"💱 *Conversion Rate:*\n"
            f"• 1 USDC = 100 Conway Credits\n"
            f"• $30 USDC = 3.000 Credits\n\n"
            f"⚠️ *Important:*\n"
            f"• Minimum deposit untuk spawn agent: $30 USDC\n"
            f"• HANYA gunakan Base Network\n"
            f"• HANYA kirim USDC (bukan USDT atau token lain)\n"
            f"• Credits akan ditambahkan otomatis setelah 12 konfirmasi\n\n"
            f"💡 *Cara Deposit:*\n"
            f"1. Buka wallet Anda (MetaMask, Trust Wallet, dll)\n"
            f"2. Pastikan network: Base\n"
            f"3. Kirim USDC ke address di atas\n"
            f"4. Tunggu 12 konfirmasi (~5-10 menit)\n"
            f"5. Credits akan otomatis masuk\n\n"
            f"📊 *Minimum untuk Spawn Agent:*\n"
            f"• Deposit: $30 USDC (3.000 credits)\n"
            f"• Spawn fee: 100.000 credits\n"
            f"• Total: ~$1.030 USDC"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in deposit_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat mengambil deposit address. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /balance command - Display Conway credits balance
    
    Shows:
    - Current Conway credits
    - Survival tier and runtime
    - Deposit address for easy funding
    """
    user_id = update.effective_user.id
    
    try:
        # Get user's agents
        agents = automaton_manager.get_user_agents(user_id)
        
        if not agents:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Display balance for each agent
        for agent in agents:
            # Survival tier emoji
            tier_emoji = {
                'normal': '🟢',
                'low_compute': '🟡',
                'critical': '🔴',
                'dead': '⚫'
            }
            emoji = tier_emoji.get(agent['survival_tier'], '⚪')
            
            message = (
                f"💰 *Conway Credits Balance*\n\n"
                f"🤖 Agent: `{agent['agent_name']}`\n"
                f"💵 Balance: {agent['balance']:,.2f} credits\n\n"
                f"{emoji} *Survival Tier:* {agent['survival_tier'].upper()}\n"
                f"⏱️ Runtime Estimate: {agent['runtime_days']:.1f} hari\n\n"
                f"📍 *Deposit Address:*\n"
                f"`{agent['deposit_address']}`\n\n"
                f"💡 Gunakan /deposit untuk instruksi deposit lengkap."
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in balance_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat mengambil balance. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def agent_logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /agent_logs command - Show transaction history with pagination
    
    Displays last 20 transactions:
    - Type (spawn, fund, earn, spend, performance_fee)
    - Amount (green for earnings, red for expenses)
    - Description
    - Timestamp
    """
    user_id = update.effective_user.id
    
    try:
        # Get user's agents
        agents = automaton_manager.get_user_agents(user_id)
        
        if not agents:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get first agent
        agent = agents[0]
        agent_id = agent['agent_id']
        
        # Get transactions from database
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase tidak tersedia.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        result = db.supabase_service.table('automaton_transactions')\
            .select('*')\
            .eq('automaton_id', agent_id)\
            .order('timestamp', desc=True)\
            .limit(20)\
            .execute()
        
        if not result.data:
            await update.message.reply_text(
                f"📜 *Transaction History*\n\n"
                f"🤖 Agent: `{agent['agent_name']}`\n\n"
                f"Belum ada transaksi.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Format transactions
        transactions_text = []
        for tx in result.data:
            tx_type = tx['type']
            amount = tx['amount']
            description = tx.get('description', '')
            timestamp = tx['timestamp'][:19]
            
            # Color code based on type
            if tx_type in ['earn']:
                emoji = '💚'
                amount_text = f"+{amount:,.2f}"
            elif tx_type in ['spend', 'spawn', 'performance_fee']:
                emoji = '❤️'
                amount_text = f"{amount:,.2f}"
            else:
                emoji = '💙'
                amount_text = f"{amount:,.2f}"
            
            tx_text = f"{emoji} *{tx_type.upper()}* {amount_text}\n   {description}\n   {timestamp}"
            transactions_text.append(tx_text)
        
        message = (
            f"📜 *Transaction History*\n\n"
            f"🤖 Agent: `{agent['agent_name']}`\n\n"
            + "\n\n".join(transactions_text)
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in agent_logs_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat mengambil transaction logs. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /withdraw command - Handle withdrawal requests
    
    Requirements (Task 16.1):
    - Rate limit: 3 withdrawals per day
    - Validate withdrawal amount (minimum 10 USDT)
    - Validate user balance (balance_usdc >= amount)
    - Create withdrawal request in wallet_withdrawals table (status 'pending')
    - Deduct 1 USDT flat fee from withdrawal amount
    - Queue for admin processing (notify admin via Telegram)
    
    Validates: Requirements 12.1, 12.2, 12.3, 12.4
    """
    user_id = update.effective_user.id
    
    try:
        # Check rate limit FIRST (prevent abuse)
        allowed, error_msg = rate_limiter.check_withdrawal_limit(user_id)
        if not allowed:
            await update.message.reply_text(
                error_msg,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if user has agents
        agents = automaton_manager.get_user_agents(user_id)
        
        if not agents:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Parse command arguments
        if len(context.args) < 2:
            await update.message.reply_text(
                "💸 *Withdraw USDC*\n\n"
                "Format: `/withdraw <amount> <address>`\n\n"
                "Contoh:\n"
                "`/withdraw 50 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`\n\n"
                "⚠️ *Ketentuan:*\n"
                "• Minimum: 10 USDC\n"
                "• Fee: 1 USDC\n"
                "• Processing time: 1-24 jam",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Parse amount and address
        try:
            amount = float(context.args[0])
            to_address = context.args[1]
        except ValueError:
            await update.message.reply_text(
                "❌ Format tidak valid. Amount harus berupa angka.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Requirement 12.2: Validate minimum withdrawal amount (10 USDC)
        if amount < 10:
            await update.message.reply_text(
                "❌ *Minimum Withdrawal*\n\n"
                "Minimum withdrawal adalah 10 USDC.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Validate address format (basic check)
        if not to_address.startswith('0x') or len(to_address) != 42:
            await update.message.reply_text(
                "❌ *Address Tidak Valid*\n\n"
                "Address harus berupa Ethereum address yang valid (0x...).",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase tidak tersedia.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Requirement 12.1: Check if user has custodial wallet and sufficient balance
        wallet_result = db.supabase_service.table('custodial_wallets')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if not wallet_result.data:
            await update.message.reply_text(
                "❌ *Wallet Tidak Ditemukan*\n\n"
                "Anda belum memiliki custodial wallet. Deposit terlebih dahulu untuk membuat wallet.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        wallet = wallet_result.data[0]
        balance_usdc = float(wallet.get('balance_usdc', 0))
        
        # Requirement 12.1: Validate user balance (balance_usdc >= amount)
        if balance_usdc < amount:
            await update.message.reply_text(
                f"❌ *Saldo Tidak Cukup*\n\n"
                f"Saldo USDC Anda: {balance_usdc:,.2f} USDC\n"
                f"Jumlah withdrawal: {amount:,.2f} USDC\n\n"
                f"Anda memerlukan {amount - balance_usdc:,.2f} USDC lebih banyak.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Requirement 12.3 & 12.4: Create withdrawal request with 1 USDC flat fee
        withdrawal_result = db.supabase_service.table('wallet_withdrawals').insert({
            'wallet_id': wallet['id'],
            'user_id': user_id,
            'amount': amount,
            'token': 'USDC',
            'to_address': to_address,
            'status': 'pending',
            'fee': 1.0
        }).execute()
        
        if not withdrawal_result.data:
            await update.message.reply_text(
                "❌ Gagal membuat withdrawal request. Silakan coba lagi.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        withdrawal_id = withdrawal_result.data[0]['id']
        
        # Log activity
        db.log_user_activity(
            user_id,
            'withdrawal_requested',
            f'Withdrawal request: {amount} USDC to {to_address[:10]}... (ID: {withdrawal_id})'
        )
        
        # Requirement 12.4: Notify admin via Telegram
        await _notify_admin_withdrawal(update.effective_chat.bot, withdrawal_id, user_id, amount, to_address)
        
        # Notify user
        message = (
            f"✅ *Withdrawal Request Created*\n\n"
            f"🆔 Request ID: `{withdrawal_id}`\n"
            f"💵 Amount: {amount:,.2f} USDC\n"
            f"💸 Fee: 1.00 USDC\n"
            f"💰 You will receive: {amount - 1:,.2f} USDC\n"
            f"📍 To: `{to_address}`\n\n"
            f"⏳ Status: Pending\n"
            f"⏱️ Processing time: 1-24 jam\n\n"
            f"Admin akan memproses withdrawal Anda segera."
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in withdraw_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat membuat withdrawal request. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def _notify_admin_withdrawal(bot, withdrawal_id: str, user_id: int, amount: float, to_address: str):
    """
    Notify admin about new withdrawal request
    
    Args:
        bot: Telegram bot instance
        withdrawal_id: Withdrawal request UUID
        user_id: User's Telegram ID
        amount: Withdrawal amount
        to_address: Destination address
    """
    try:
        # Get admin IDs from environment
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if not admin_ids_str:
            print("⚠️ No ADMIN_IDS configured for withdrawal notifications")
            return
        
        admin_ids = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
        
        # Prepare admin notification message
        admin_message = (
            f"🔔 *New Withdrawal Request*\n\n"
            f"🆔 Request ID: `{withdrawal_id}`\n"
            f"👤 User ID: `{user_id}`\n"
            f"💵 Amount: {amount:,.2f} USDC\n"
            f"💸 Fee: 1.00 USDC\n"
            f"💰 Net Amount: {amount - 1:,.2f} USDC\n"
            f"📍 To Address:\n`{to_address}`\n\n"
            f"⏳ Status: Pending\n\n"
            f"Use `/admin_process_withdrawal {withdrawal_id}` to process this request."
        )
        
        # Send to all admins
        for admin_id in admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                print(f"❌ Failed to notify admin {admin_id}: {e}")
    
    except Exception as e:
        print(f"❌ Error notifying admins about withdrawal: {e}")


async def agent_lineage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /agent_lineage command - Display full lineage tree
    
    Shows hierarchical tree of agent's children and descendants
    """
    user_id = update.effective_user.id
    
    try:
        # Get user's agents
        agents = automaton_manager.get_user_agents(user_id)
        
        if not agents:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent. Gunakan /spawn_agent untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Display lineage tree for each agent
        for agent in agents:
            agent_id = agent['agent_id']
            agent_name = agent['agent_name']
            
            # Get lineage tree (max depth 3 for readability)
            tree = await get_agent_lineage_tree(agent_id, max_depth=3)
            
            if not tree:
                await update.message.reply_text(
                    f"🌳 *Lineage Tree: {agent_name}*\n\n"
                    f"No lineage data available.",
                    parse_mode=ParseMode.MARKDOWN
                )
                continue
            
            # Format tree as text
            tree_text = format_lineage_tree_text(tree)
            
            message = (
                f"🌳 *Lineage Tree: {agent_name}*\n\n"
                f"```\n{tree_text}\n```\n\n"
                f"💡 *Lineage System:*\n"
                f"• Parents receive 10% of children's gross earnings\n"
                f"• Revenue sharing is recursive (up to 10 levels)\n"
                f"• Build your agent network for passive income!"
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in agent_lineage_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan saat mengambil lineage tree. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_spawn_parent_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle callback for parent selection during agent spawn
    
    Callback data format:
    - spawn_noparent_<agent_name>
    - spawn_parent_<parent_id>_<agent_name>
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    
    try:
        if callback_data.startswith("spawn_noparent_"):
            # Spawn without parent
            agent_name = callback_data.replace("spawn_noparent_", "")
            parent_agent_id = None
        elif callback_data.startswith("spawn_parent_"):
            # Spawn with parent
            parts = callback_data.replace("spawn_parent_", "").split("_", 1)
            parent_agent_id = parts[0]
            agent_name = parts[1] if len(parts) > 1 else "Agent"
        else:
            await query.edit_message_text("❌ Invalid callback data")
            return
        
        # Show spawning message
        await query.edit_message_text(
            f"⏳ Spawning agent *{agent_name}*...\n\n"
            f"Mohon tunggu sebentar...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Spawn the agent
        result = automaton_manager.spawn_agent(
            user_id=user_id,
            agent_name=agent_name,
            genesis_prompt="You are an autonomous trading agent. Trade wisely and maximize profits."
        )
        
        if result['success']:
            agent_id = result.get('agent_id')
            
            # Register lineage
            await on_agent_spawn(agent_id, parent_agent_id)
            
            # Success message
            parent_text = ""
            if parent_agent_id:
                parent_text = f"\n👨 Parent: Registered\n💡 Parent will receive 10% of this agent's earnings"
            
            message = (
                f"✅ *Agent Berhasil Dibuat!*\n\n"
                f"🤖 Nama: `{agent_name}`\n"
                f"💼 Wallet: `{result['agent_wallet']}`\n"
                f"📍 Deposit Address:\n`{result['deposit_address']}`\n"
                f"{parent_text}\n\n"
                f"💰 Biaya Spawn: {result['spawn_fee']:,} kredit\n"
                f"💳 Sisa Kredit: {result['remaining_credits']:,}\n\n"
                f"⚠️ *Agent belum aktif!*\n"
                f"Deposit USDT/USDC ke address di atas untuk mengaktifkan agent.\n\n"
                f"Gunakan /deposit untuk melihat QR code dan instruksi deposit."
            )
            
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Error message
            await query.edit_message_text(
                f"❌ *Gagal Spawn Agent*\n\n"
                f"{result['message']}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in handle_spawn_parent_callback: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat spawn agent. Silakan coba lagi.",
            parse_mode=ParseMode.MARKDOWN
        )
