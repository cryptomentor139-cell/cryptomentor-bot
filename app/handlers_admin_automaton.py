# Admin Automaton Handlers - Admin Dashboard for Automaton Management
# Provides admin commands for monitoring wallets, revenue, and agents

import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import Database
from app.revenue_manager import get_revenue_manager
from datetime import datetime

# Initialize database
db = Database()
revenue_manager = get_revenue_manager(db)


async def admin_wallets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin_wallets command - Wallet summary
    
    Displays:
    - Total number of wallets
    - Total USDT/USDC balances
    - All-time deposits
    - All-time spending
    - Platform revenue
    - Active agents count
    - Survival rate
    """
    user_id = update.effective_user.id
    
    # Check admin permission
    if not db.is_admin(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. Admin only.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase not enabled.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get all custodial wallets
        wallets_result = db.supabase_service.table('custodial_wallets').select('*').execute()
        
        if not wallets_result.data:
            await update.message.reply_text(
                "📊 *Admin: Wallet Summary*\n\n"
                "No custodial wallets found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        wallets = wallets_result.data
        
        # Calculate totals
        total_wallets = len(wallets)
        total_usdt = sum(float(w.get('balance_usdt', 0)) for w in wallets)
        total_usdc = sum(float(w.get('balance_usdc', 0)) for w in wallets)
        total_conway = sum(float(w.get('conway_credits', 0)) for w in wallets)
        total_deposited = sum(float(w.get('total_deposited', 0)) for w in wallets)
        total_spent = sum(float(w.get('total_spent', 0)) for w in wallets)
        
        # Get active agents count
        agents_result = db.supabase_service.table('user_automatons').select('status').execute()
        total_agents = len(agents_result.data) if agents_result.data else 0
        active_agents = sum(1 for a in agents_result.data if a['status'] == 'active') if agents_result.data else 0
        survival_rate = (active_agents / total_agents * 100) if total_agents > 0 else 0
        
        # Get platform revenue
        revenue_result = db.supabase_service.table('platform_revenue').select('amount').execute()
        platform_revenue = sum(float(r['amount']) for r in revenue_result.data) if revenue_result.data else 0
        
        message = (
            f"📊 *Admin: Wallet Summary*\n\n"
            f"👛 *Total Wallets:* {total_wallets}\n\n"
            f"💰 *Balances:*\n"
            f"• USDT: {total_usdt:,.2f}\n"
            f"• USDC: {total_usdc:,.2f}\n"
            f"• Conway Credits: {total_conway:,.0f}\n\n"
            f"📈 *All-Time Stats:*\n"
            f"• Total Deposited: {total_deposited:,.2f} USDC\n"
            f"• Total Spent: {total_spent:,.2f} USDC\n"
            f"• Net Balance: {total_deposited - total_spent:,.2f} USDC\n\n"
            f"💵 *Platform Revenue:* {platform_revenue:,.2f} USDC\n\n"
            f"🤖 *Agents:*\n"
            f"• Total: {total_agents}\n"
            f"• Active: {active_agents}\n"
            f"• Survival Rate: {survival_rate:.1f}%\n\n"
            f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in admin_wallets_command: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )


async def admin_wallet_details_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin_wallet_details <user_id> command
    
    Displays:
    - User wallet details
    - Balance breakdown
    - Deposit history
    - Agent details
    """
    user_id = update.effective_user.id
    
    # Check admin permission
    if not db.is_admin(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. Admin only.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        # Parse user_id argument
        if not context.args:
            await update.message.reply_text(
                "📊 *Admin: Wallet Details*\n\n"
                "Usage: `/admin_wallet_details <user_id>`\n\n"
                "Example: `/admin_wallet_details 123456789`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        target_user_id = int(context.args[0])
        
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase not enabled.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get user wallet
        wallet_result = db.supabase_service.table('custodial_wallets').select('*').eq('user_id', target_user_id).execute()
        
        if not wallet_result.data:
            await update.message.reply_text(
                f"❌ No wallet found for user {target_user_id}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        wallet = wallet_result.data[0]
        
        # Get user agents
        agents_result = db.supabase_service.table('user_automatons').select('*').eq('user_id', target_user_id).execute()
        agents = agents_result.data if agents_result.data else []
        
        # Get deposit history
        deposits_result = db.supabase_service.table('wallet_deposits').select('*').eq('user_id', target_user_id).order('detected_at', desc=True).limit(5).execute()
        deposits = deposits_result.data if deposits_result.data else []
        
        # Format message
        message = (
            f"📊 *Admin: Wallet Details*\n\n"
            f"👤 *User ID:* {target_user_id}\n"
            f"💼 *Wallet:* `{wallet['wallet_address']}`\n\n"
            f"💰 *Balances:*\n"
            f"• USDT: {wallet.get('balance_usdt', 0):,.2f}\n"
            f"• USDC: {wallet.get('balance_usdc', 0):,.2f}\n"
            f"• Conway Credits: {wallet.get('conway_credits', 0):,.0f}\n\n"
            f"📈 *Stats:*\n"
            f"• Total Deposited: {wallet.get('total_deposited', 0):,.2f}\n"
            f"• Total Spent: {wallet.get('total_spent', 0):,.2f}\n"
            f"• Last Deposit: {wallet.get('last_deposit_at', 'Never')[:19] if wallet.get('last_deposit_at') else 'Never'}\n\n"
            f"🤖 *Agents:* {len(agents)}\n"
        )
        
        # Add agent details
        if agents:
            message += "\n*Agent List:*\n"
            for agent in agents:
                status_emoji = '🟢' if agent['status'] == 'active' else '⚫'
                message += f"{status_emoji} {agent['agent_name']} - {agent['conway_credits']:,.0f} credits\n"
        
        # Add recent deposits
        if deposits:
            message += "\n*Recent Deposits:*\n"
            for deposit in deposits:
                message += f"• {deposit['amount']:,.2f} {deposit['token']} - {deposit['detected_at'][:19]}\n"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid user_id. Must be a number.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"❌ Error in admin_wallet_details_command: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )


async def admin_revenue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin_revenue command - Revenue report
    
    Displays:
    - Total revenue
    - Revenue by source (deposit fees, performance fees, spawn fees)
    - Daily/weekly/monthly breakdown
    - Top revenue-generating agents
    """
    user_id = update.effective_user.id
    
    # Check admin permission
    if not db.is_admin(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. Admin only.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        # Parse period argument (default: daily)
        period = 'daily'
        if context.args:
            period = context.args[0].lower()
            if period not in ['daily', 'weekly', 'monthly', 'all']:
                await update.message.reply_text(
                    "❌ Invalid period. Use: daily, weekly, monthly, or all",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
        
        # Get revenue report
        report = revenue_manager.get_revenue_report(period)
        
        if not report['success']:
            await update.message.reply_text(
                f"❌ Error: {report['message']}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Format message
        period_label = period.capitalize()
        message = (
            f"💰 *Admin: Revenue Report ({period_label})*\n\n"
            f"📊 *Total Revenue:* {report['total_revenue']:,.2f} USDC\n\n"
            f"📈 *Revenue by Source:*\n"
            f"• Deposit Fees: {report['deposit_fees']:,.2f} ({report['breakdown']['deposit_fee_pct']:.1f}%)\n"
            f"• Performance Fees: {report['performance_fees']:,.2f} ({report['breakdown']['performance_fee_pct']:.1f}%)\n"
            f"• Spawn Fees: {report['spawn_fees']:,.2f} ({report['breakdown']['spawn_fee_pct']:.1f}%)\n\n"
            f"📝 *Transactions:* {report['transaction_count']}\n"
        )
        
        # Add top agents
        if report['top_agents']:
            message += "\n🏆 *Top Revenue Agents:*\n"
            for i, agent in enumerate(report['top_agents'][:5], 1):
                message += f"{i}. {agent['agent_name']} - {agent['revenue']:,.2f} USDC\n"
        
        message += f"\n🕐 Period: {report['start_date'][:10]} to {report['end_date'][:10]}"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in admin_revenue_command: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )


async def admin_agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin_agents command - Agent statistics
    
    Displays:
    - Total agents
    - Active/paused/dead agents
    - Average balance
    - Survival tier distribution
    - Top performing agents
    """
    user_id = update.effective_user.id
    
    # Check admin permission
    if not db.is_admin(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. Admin only.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase not enabled.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get all agents
        agents_result = db.supabase_service.table('user_automatons').select('*').execute()
        
        if not agents_result.data:
            await update.message.reply_text(
                "🤖 *Admin: Agent Statistics*\n\n"
                "No agents found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        agents = agents_result.data
        
        # Calculate statistics
        total_agents = len(agents)
        active_agents = sum(1 for a in agents if a['status'] == 'active')
        paused_agents = sum(1 for a in agents if a['status'] == 'paused')
        dead_agents = sum(1 for a in agents if a['survival_tier'] == 'dead')
        
        # Survival tier distribution
        tier_counts = {
            'normal': sum(1 for a in agents if a['survival_tier'] == 'normal'),
            'low_compute': sum(1 for a in agents if a['survival_tier'] == 'low_compute'),
            'critical': sum(1 for a in agents if a['survival_tier'] == 'critical'),
            'dead': dead_agents
        }
        
        # Average balance
        total_credits = sum(float(a.get('conway_credits', 0)) for a in agents)
        avg_balance = total_credits / total_agents if total_agents > 0 else 0
        
        # Top performing agents (by net P&L)
        top_agents = sorted(
            agents,
            key=lambda a: float(a.get('total_earnings', 0)) - float(a.get('total_expenses', 0)),
            reverse=True
        )[:5]
        
        message = (
            f"🤖 *Admin: Agent Statistics*\n\n"
            f"📊 *Overview:*\n"
            f"• Total Agents: {total_agents}\n"
            f"• Active: {active_agents}\n"
            f"• Paused: {paused_agents}\n"
            f"• Dead: {dead_agents}\n\n"
            f"💰 *Credits:*\n"
            f"• Total: {total_credits:,.0f}\n"
            f"• Average: {avg_balance:,.0f}\n\n"
            f"📈 *Survival Tiers:*\n"
            f"🟢 Normal: {tier_counts['normal']}\n"
            f"🟡 Low Compute: {tier_counts['low_compute']}\n"
            f"🔴 Critical: {tier_counts['critical']}\n"
            f"⚫ Dead: {tier_counts['dead']}\n"
        )
        
        # Add top performers
        if top_agents:
            message += "\n🏆 *Top Performers (Net P&L):*\n"
            for i, agent in enumerate(top_agents, 1):
                net_pnl = float(agent.get('total_earnings', 0)) - float(agent.get('total_expenses', 0))
                pnl_text = f"+{net_pnl:,.2f}" if net_pnl >= 0 else f"{net_pnl:,.2f}"
                message += f"{i}. {agent['agent_name']} - {pnl_text}\n"
        
        message += f"\n🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in admin_agents_command: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )


async def admin_process_withdrawal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin_process_withdrawal <withdrawal_id> command

    Requirements (Task 16.2):
    - Decrypt private key using wallet_manager (admin only)
    - Sign and broadcast transaction to Polygon network
    - Update withdrawal status to 'completed' in database
    - Record transaction hash in tx_hash field
    - Notify user of successful withdrawal

    Validates: Requirement 12.5
    """
    user_id = update.effective_user.id

    # Check admin permission
    if not db.is_admin(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. Admin only.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    try:
        # Parse withdrawal_id argument
        if not context.args:
            await update.message.reply_text(
                "💸 *Admin: Process Withdrawal*\n\n"
                "Usage: `/admin_process_withdrawal <withdrawal_id>`\n\n"
                "Example: `/admin_process_withdrawal 123e4567-e89b-12d3-a456-426614174000`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        withdrawal_id = context.args[0]

        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase not enabled.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Get withdrawal request
        withdrawal_result = db.supabase_service.table('wallet_withdrawals')\
            .select('*')\
            .eq('id', withdrawal_id)\
            .execute()

        if not withdrawal_result.data:
            await update.message.reply_text(
                f"❌ Withdrawal request not found: {withdrawal_id}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        withdrawal = withdrawal_result.data[0]

        # Check if already processed
        if withdrawal['status'] != 'pending':
            await update.message.reply_text(
                f"❌ Withdrawal already processed.\n\n"
                f"Status: {withdrawal['status']}\n"
                f"TX Hash: {withdrawal.get('tx_hash', 'N/A')}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Get custodial wallet
        wallet_result = db.supabase_service.table('custodial_wallets')\
            .select('*')\
            .eq('id', withdrawal['wallet_id'])\
            .execute()

        if not wallet_result.data:
            await update.message.reply_text(
                f"❌ Custodial wallet not found for withdrawal {withdrawal_id}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        wallet = wallet_result.data[0]

        # Verify balance
        balance_usdc = float(wallet.get('balance_usdc', 0))
        withdrawal_amount = float(withdrawal['amount'])

        if balance_usdc < withdrawal_amount:
            await update.message.reply_text(
                f"❌ Insufficient balance in custodial wallet.\n\n"
                f"Required: {withdrawal_amount:,.2f} USDC\n"
                f"Available: {balance_usdc:,.2f} USDC",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Send processing notification
        await update.message.reply_text(
            f"⏳ Processing withdrawal {withdrawal_id}...\n\n"
            f"Amount: {withdrawal_amount:,.2f} USDC\n"
            f"To: `{withdrawal['to_address']}`\n\n"
            f"Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Import required modules for transaction
        from web3 import Web3
        from cryptography.fernet import Fernet

        # Get encryption key
        encryption_key = os.getenv('WALLET_ENCRYPTION_KEY')
        if not encryption_key:
            await update.message.reply_text(
                "❌ WALLET_ENCRYPTION_KEY not configured.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Decrypt private key
        try:
            cipher = Fernet(encryption_key.encode())
            encrypted_key = wallet['private_key_encrypted']
            private_key = cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            print(f"❌ Error decrypting private key: {e}")
            await update.message.reply_text(
                f"❌ Failed to decrypt private key: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Connect to Polygon network
        polygon_rpc = os.getenv('POLYGON_RPC_URL')
        if not polygon_rpc:
            await update.message.reply_text(
                "❌ POLYGON_RPC_URL not configured.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        w3 = Web3(Web3.HTTPProvider(polygon_rpc))

        if not w3.is_connected():
            await update.message.reply_text(
                "❌ Failed to connect to Polygon network.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Get USDC contract address (Polygon)
        usdc_address = os.getenv(
            'POLYGON_USDC_CONTRACT',
            '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
        )

        # ERC20 transfer ABI
        erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]

        # Create contract instance
        usdc_contract = w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=erc20_abi
        )

        # Prepare transaction
        from_address = Web3.to_checksum_address(wallet['wallet_address'])
        to_address = Web3.to_checksum_address(withdrawal['to_address'])

        # Calculate net amount (withdrawal amount - fee)
        fee = float(withdrawal.get('fee', 1.0))
        net_amount = withdrawal_amount - fee

        # USDC has 6 decimals
        amount_wei = int(net_amount * (10 ** 6))

        # Get account nonce
        nonce = w3.eth.get_transaction_count(from_address)

        # Build transaction
        transaction = usdc_contract.functions.transfer(
            to_address,
            amount_wei
        ).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': 100000,  # Standard ERC20 transfer gas limit
            'gasPrice': w3.eth.gas_price,
            'chainId': 137  # Polygon mainnet
        })

        # Sign transaction
        try:
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        except Exception as e:
            print(f"❌ Error signing transaction: {e}")
            await update.message.reply_text(
                f"❌ Failed to sign transaction: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Broadcast transaction
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            print(f"✅ Transaction broadcast: {tx_hash_hex}")
        except Exception as e:
            print(f"❌ Error broadcasting transaction: {e}")
            await update.message.reply_text(
                f"❌ Failed to broadcast transaction: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Update withdrawal status to 'completed'
        update_result = db.supabase_service.table('wallet_withdrawals')\
            .update({
                'status': 'completed',
                'tx_hash': tx_hash_hex,
                'processed_at': datetime.now().isoformat()
            })\
            .eq('id', withdrawal_id)\
            .execute()

        if not update_result.data:
            print(f"⚠️ Failed to update withdrawal status in database")

        # Update wallet balance
        new_balance = balance_usdc - withdrawal_amount
        db.supabase_service.table('custodial_wallets')\
            .update({
                'balance_usdc': new_balance,
                'total_spent': float(wallet.get('total_spent', 0)) + withdrawal_amount
            })\
            .eq('id', wallet['id'])\
            .execute()

        # Record platform fee revenue
        db.supabase_service.table('platform_revenue').insert({
            'source': 'withdrawal_fee',
            'amount': fee,
            'user_id': withdrawal['user_id'],
            'timestamp': datetime.now().isoformat()
        }).execute()

        # Log activity
        db.log_user_activity(
            withdrawal['user_id'],
            'withdrawal_completed',
            f'Withdrawal completed: {net_amount} USDC to {to_address[:10]}... (TX: {tx_hash_hex[:10]}...)'
        )

        # Notify admin of success
        polygonscan_url = f"https://polygonscan.com/tx/{tx_hash_hex}"
        await update.message.reply_text(
            f"✅ *Withdrawal Processed Successfully*\n\n"
            f"🆔 Request ID: `{withdrawal_id}`\n"
            f"👤 User ID: `{withdrawal['user_id']}`\n"
            f"💵 Amount: {withdrawal_amount:,.2f} USDC\n"
            f"💸 Fee: {fee:,.2f} USDC\n"
            f"💰 Net Sent: {net_amount:,.2f} USDC\n"
            f"📍 To: `{to_address}`\n\n"
            f"🔗 TX Hash:\n`{tx_hash_hex}`\n\n"
            f"🔍 [View on Polygonscan]({polygonscan_url})\n\n"
            f"User has been notified.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

        # Notify user of successful withdrawal
        try:
            await context.bot.send_message(
                chat_id=withdrawal['user_id'],
                text=(
                    f"✅ *Withdrawal Completed*\n\n"
                    f"🆔 Request ID: `{withdrawal_id}`\n"
                    f"💵 Amount: {withdrawal_amount:,.2f} USDC\n"
                    f"💸 Fee: {fee:,.2f} USDC\n"
                    f"💰 You received: {net_amount:,.2f} USDC\n"
                    f"📍 To: `{to_address}`\n\n"
                    f"🔗 TX Hash:\n`{tx_hash_hex}`\n\n"
                    f"🔍 [View on Polygonscan]({polygonscan_url})\n\n"
                    f"Thank you for using our service!"
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"⚠️ Failed to notify user: {e}")

    except Exception as e:
        print(f"❌ Error in admin_process_withdrawal_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Error processing withdrawal: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )




async def admin_process_withdrawal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin_process_withdrawal <withdrawal_id> command
    
    Requirements (Task 16.2):
    - Decrypt private key using wallet_manager (admin only)
    - Sign and broadcast transaction to Polygon network
    - Update withdrawal status to 'completed' in database
    - Record transaction hash in tx_hash field
    - Notify user of successful withdrawal
    
    Validates: Requirement 12.5
    """
    user_id = update.effective_user.id
    
    # Check admin permission
    if not db.is_admin(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. Admin only.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        # Parse withdrawal_id argument
        if not context.args:
            await update.message.reply_text(
                "💸 *Admin: Process Withdrawal*\n\n"
                "Usage: `/admin_process_withdrawal <withdrawal_id>`\n\n"
                "Example: `/admin_process_withdrawal 123e4567-e89b-12d3-a456-426614174000`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        withdrawal_id = context.args[0]
        
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Supabase not enabled.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get withdrawal request
        withdrawal_result = db.supabase_service.table('wallet_withdrawals')\
            .select('*')\
            .eq('id', withdrawal_id)\
            .execute()
        
        if not withdrawal_result.data:
            await update.message.reply_text(
                f"❌ Withdrawal request not found: {withdrawal_id}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        withdrawal = withdrawal_result.data[0]
        
        # Check if already processed
        if withdrawal['status'] != 'pending':
            await update.message.reply_text(
                f"❌ Withdrawal already processed.\n\n"
                f"Status: {withdrawal['status']}\n"
                f"TX Hash: {withdrawal.get('tx_hash', 'N/A')}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get custodial wallet
        wallet_result = db.supabase_service.table('custodial_wallets')\
            .select('*')\
            .eq('id', withdrawal['wallet_id'])\
            .execute()
        
        if not wallet_result.data:
            await update.message.reply_text(
                f"❌ Custodial wallet not found for withdrawal {withdrawal_id}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        wallet = wallet_result.data[0]
        
        # Verify balance
        balance_usdc = float(wallet.get('balance_usdc', 0))
        withdrawal_amount = float(withdrawal['amount'])
        
        if balance_usdc < withdrawal_amount:
            await update.message.reply_text(
                f"❌ Insufficient balance in custodial wallet.\n\n"
                f"Required: {withdrawal_amount:,.2f} USDC\n"
                f"Available: {balance_usdc:,.2f} USDC",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send processing notification
        await update.message.reply_text(
            f"⏳ Processing withdrawal {withdrawal_id}...\n\n"
            f"Amount: {withdrawal_amount:,.2f} USDC\n"
            f"To: `{withdrawal['to_address']}`\n\n"
            f"Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Import required modules for transaction
        from web3 import Web3
        from cryptography.fernet import Fernet
        
        # Get encryption key
        encryption_key = os.getenv('WALLET_ENCRYPTION_KEY')
        if not encryption_key:
            await update.message.reply_text(
                "❌ WALLET_ENCRYPTION_KEY not configured.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Decrypt private key
        try:
            cipher = Fernet(encryption_key.encode())
            encrypted_key = wallet['private_key_encrypted']
            private_key = cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            print(f"❌ Error decrypting private key: {e}")
            await update.message.reply_text(
                f"❌ Failed to decrypt private key: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Connect to Polygon network
        polygon_rpc = os.getenv('POLYGON_RPC_URL')
        if not polygon_rpc:
            await update.message.reply_text(
                "❌ POLYGON_RPC_URL not configured.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        w3 = Web3(Web3.HTTPProvider(polygon_rpc))
        
        if not w3.is_connected():
            await update.message.reply_text(
                "❌ Failed to connect to Polygon network.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get USDC contract address (Polygon)
        usdc_address = os.getenv(
            'POLYGON_USDC_CONTRACT',
            '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
        )
        
        # ERC20 transfer ABI
        erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]
        
        # Create contract instance
        usdc_contract = w3.eth.contract(
            address=Web3.to_checksum_address(usdc_address),
            abi=erc20_abi
        )
        
        # Prepare transaction
        from_address = Web3.to_checksum_address(wallet['wallet_address'])
        to_address = Web3.to_checksum_address(withdrawal['to_address'])
        
        # Calculate net amount (withdrawal amount - fee)
        fee = float(withdrawal.get('fee', 1.0))
        net_amount = withdrawal_amount - fee
        
        # USDC has 6 decimals
        amount_wei = int(net_amount * (10 ** 6))
        
        # Get account nonce
        nonce = w3.eth.get_transaction_count(from_address)
        
        # Build transaction
        transaction = usdc_contract.functions.transfer(
            to_address,
            amount_wei
        ).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': 100000,  # Standard ERC20 transfer gas limit
            'gasPrice': w3.eth.gas_price,
            'chainId': 137  # Polygon mainnet
        })
        
        # Sign transaction
        try:
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        except Exception as e:
            print(f"❌ Error signing transaction: {e}")
            await update.message.reply_text(
                f"❌ Failed to sign transaction: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Broadcast transaction
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            print(f"✅ Transaction broadcast: {tx_hash_hex}")
        except Exception as e:
            print(f"❌ Error broadcasting transaction: {e}")
            await update.message.reply_text(
                f"❌ Failed to broadcast transaction: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Update withdrawal status to 'completed'
        update_result = db.supabase_service.table('wallet_withdrawals')\
            .update({
                'status': 'completed',
                'tx_hash': tx_hash_hex,
                'processed_at': datetime.now().isoformat()
            })\
            .eq('id', withdrawal_id)\
            .execute()
        
        if not update_result.data:
            print(f"⚠️ Failed to update withdrawal status in database")
        
        # Update wallet balance
        new_balance = balance_usdc - withdrawal_amount
        db.supabase_service.table('custodial_wallets')\
            .update({
                'balance_usdc': new_balance,
                'total_spent': float(wallet.get('total_spent', 0)) + withdrawal_amount
            })\
            .eq('id', wallet['id'])\
            .execute()
        
        # Record platform fee revenue
        db.supabase_service.table('platform_revenue').insert({
            'source': 'withdrawal_fee',
            'amount': fee,
            'user_id': withdrawal['user_id'],
            'timestamp': datetime.now().isoformat()
        }).execute()
        
        # Log activity
        db.log_user_activity(
            withdrawal['user_id'],
            'withdrawal_completed',
            f'Withdrawal completed: {net_amount} USDC to {to_address[:10]}... (TX: {tx_hash_hex[:10]}...)'
        )
        
        # Notify admin of success
        polygonscan_url = f"https://polygonscan.com/tx/{tx_hash_hex}"
        await update.message.reply_text(
            f"✅ *Withdrawal Processed Successfully*\n\n"
            f"🆔 Request ID: `{withdrawal_id}`\n"
            f"👤 User ID: `{withdrawal['user_id']}`\n"
            f"💵 Amount: {withdrawal_amount:,.2f} USDC\n"
            f"💸 Fee: {fee:,.2f} USDC\n"
            f"💰 Net Sent: {net_amount:,.2f} USDC\n"
            f"📍 To: `{to_address}`\n\n"
            f"🔗 TX Hash:\n`{tx_hash_hex}`\n\n"
            f"🔍 [View on Polygonscan]({polygonscan_url})\n\n"
            f"User has been notified.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
        # Notify user of successful withdrawal
        try:
            await context.bot.send_message(
                chat_id=withdrawal['user_id'],
                text=(
                    f"✅ *Withdrawal Completed*\n\n"
                    f"🆔 Request ID: `{withdrawal_id}`\n"
                    f"💵 Amount: {withdrawal_amount:,.2f} USDC\n"
                    f"💸 Fee: {fee:,.2f} USDC\n"
                    f"💰 You received: {net_amount:,.2f} USDC\n"
                    f"📍 To: `{to_address}`\n\n"
                    f"🔗 TX Hash:\n`{tx_hash_hex}`\n\n"
                    f"🔍 [View on Polygonscan]({polygonscan_url})\n\n"
                    f"Thank you for using our service!"
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"⚠️ Failed to notify user: {e}")
    
    except Exception as e:
        print(f"❌ Error in admin_process_withdrawal_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Error processing withdrawal: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )
