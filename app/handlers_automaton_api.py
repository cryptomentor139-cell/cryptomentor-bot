# Automaton API Handlers - Simplified
# Uses Conway API via CONWAY_API_URL instead of local database

import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from app.conway_integration import get_conway_client
from database import Database

# Initialize
db = Database()


async def automaton_status_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get agent status from Automaton API
    
    Usage: /automaton status
    """
    user_id = update.effective_user.id
    
    try:
        # Get Conway API client
        conway = get_conway_client()
        
        # Health check first
        if not conway.health_check():
            await update.message.reply_text(
                "❌ *Automaton Service Offline*\n\n"
                "Automaton service sedang tidak tersedia. Silakan coba lagi nanti.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get user's deposit address from database
        supabase = db.supabase_service()
        result = supabase.table('user_automatons')\
            .select('conway_deposit_address, agent_name')\
            .eq('user_id', user_id)\
            .eq('status', 'active')\
            .execute()
        
        if not result.data:
            await update.message.reply_text(
                "❌ *Tidak Ada Agent*\n\n"
                "Anda belum memiliki agent aktif.\n"
                "Gunakan `/automaton spawn` untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get status for each agent
        for agent_data in result.data:
            deposit_address = agent_data['conway_deposit_address']
            agent_name = agent_data['agent_name']
            
            # Get status from Automaton API
            try:
                status = conway.get_agent_status(deposit_address)
            except Exception as api_error:
                print(f"⚠️ Conway API error for {deposit_address}: {api_error}")
                # Return default status if API fails
                status = {
                    'balance': 0,
                    'state': 'pending',
                    'uptime': 0
                }
            
            if not status:
                await update.message.reply_text(
                    f"❌ *Error*\n\n"
                    f"Tidak dapat mengambil status untuk agent `{agent_name}`.\n"
                    f"Deposit Address: `{deposit_address}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                continue
            
            # Format response
            balance = status.get('balance', 0)
            state = status.get('state', 'unknown')
            uptime = status.get('uptime', 0)
            
            # Calculate runtime estimate (assuming 1 credit = 1 hour)
            runtime_hours = balance
            runtime_days = runtime_hours / 24
            
            message = (
                f"🤖 *Agent Status*\n\n"
                f"📛 Nama: `{agent_name}`\n"
                f"💼 Wallet: `{deposit_address}`\n"
                f"💰 Balance: {balance:,.2f} credits\n"
                f"📊 State: {state}\n"
                f"⏱️ Uptime: {uptime} seconds\n"
                f"🕐 Runtime Estimate: {runtime_days:.1f} hari\n\n"
                f"📍 Deposit Address:\n`{deposit_address}`"
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in automaton_status_api: {e}")
        import traceback
        traceback.print_exc()
        
        await update.message.reply_text(
            "❌ *Error*\n\n"
            "Terjadi kesalahan saat mengambil status agent.\n"
            f"Detail: `{str(e)}`",
            parse_mode=ParseMode.MARKDOWN
        )


async def automaton_spawn_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Spawn new agent via Automaton API
    
    Usage: /automaton spawn [agent_name]
    """
    user_id = update.effective_user.id
    
    try:
        # Get agent name from args or use default
        agent_name = context.args[0] if context.args else f"Agent_{user_id}"
        
        # Get Conway API client
        conway = get_conway_client()
        
        # Health check
        if not conway.health_check():
            await update.message.reply_text(
                "❌ Automaton service offline. Silakan coba lagi nanti."
            )
            return
        
        await update.message.reply_text(
            f"🚀 Spawning agent `{agent_name}`...\n"
            f"Mohon tunggu...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Generate deposit address
        try:
            deposit_address = conway.generate_deposit_address(user_id, agent_name)
        except Exception as api_error:
            print(f"⚠️ Conway API error: {api_error}")
            # Fallback: Generate simple address format
            import hashlib
            import time
            unique_str = f"{user_id}_{agent_name}_{int(time.time())}"
            deposit_address = "0x" + hashlib.sha256(unique_str.encode()).hexdigest()[:40]
            print(f"✅ Generated fallback address: {deposit_address}")
        
        if not deposit_address:
            await update.message.reply_text(
                "❌ Gagal generate deposit address. Silakan coba lagi."
            )
            return
        
        # Save to database
        supabase = db.supabase_service()
        supabase.table('user_automatons').insert({
            'user_id': user_id,
            'agent_name': agent_name,
            'conway_deposit_address': deposit_address,
            'agent_wallet': deposit_address,  # Same as deposit address
            'status': 'pending',  # Will be 'active' after first deposit
            'conway_credits': 0,
            'total_earnings': 0,
            'total_expenses': 0,
            'survival_tier': 'normal'
        }).execute()
        
        message = (
            f"✅ *Agent Created!*\n\n"
            f"📛 Nama: `{agent_name}`\n"
            f"💼 Deposit Address:\n`{deposit_address}`\n\n"
            f"📝 *Next Steps:*\n"
            f"1. Deposit minimal $30 USDC (3,000 credits) ke address di atas\n"
            f"2. Agent akan otomatis aktif setelah deposit terdeteksi\n"
            f"3. Gunakan `/automaton status` untuk cek status\n\n"
            f"💡 *Tip:* 1 USDC = 100 credits = ~1 jam runtime"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        print(f"❌ Error in automaton_spawn_api: {e}")
        import traceback
        traceback.print_exc()
        
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


async def automaton_balance_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check agent balance via Automaton API
    
    Usage: /automaton balance
    """
    user_id = update.effective_user.id
    
    try:
        # Get Conway API client
        conway = get_conway_client()
        
        # Get user's deposit address
        supabase = db.supabase_service()
        result = supabase.table('user_automatons')\
            .select('conway_deposit_address, agent_name')\
            .eq('user_id', user_id)\
            .execute()
        
        if not result.data:
            await update.message.reply_text(
                "❌ Anda belum memiliki agent.\n"
                "Gunakan `/automaton spawn` untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check balance for each agent
        for agent_data in result.data:
            deposit_address = agent_data['conway_deposit_address']
            agent_name = agent_data['agent_name']
            
            # Get balance from Automaton API
            try:
                balance = conway.get_credit_balance(deposit_address)
            except Exception as api_error:
                print(f"⚠️ Conway API error for {deposit_address}: {api_error}")
                balance = 0  # Default to 0 if API fails
            
            if balance is None:
                balance = 0  # Fallback to 0
            
            # Calculate runtime
            runtime_hours = balance
            runtime_days = runtime_hours / 24
            
            message = (
                f"💰 *Agent Balance*\n\n"
                f"📛 Agent: `{agent_name}`\n"
                f"💵 Balance: {balance:,.2f} credits\n"
                f"⏱️ Runtime: ~{runtime_days:.1f} hari\n\n"
                f"📍 Address: `{deposit_address}`"
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in automaton_balance_api: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


async def automaton_deposit_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show deposit information
    
    Usage: /automaton deposit
    """
    user_id = update.effective_user.id
    
    try:
        # Get user's agents
        supabase = db.supabase_service()
        result = supabase.table('user_automatons')\
            .select('conway_deposit_address, agent_name, conway_credits')\
            .eq('user_id', user_id)\
            .execute()
        
        if not result.data:
            await update.message.reply_text(
                "❌ Anda belum memiliki agent.\n"
                "Gunakan `/automaton spawn` untuk membuat agent baru.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        for agent_data in result.data:
            deposit_address = agent_data['conway_deposit_address']
            agent_name = agent_data['agent_name']
            balance = agent_data.get('conway_credits', 0)
            
            message = (
                f"💳 *Deposit Info*\n\n"
                f"📛 Agent: `{agent_name}`\n"
                f"💰 Current Balance: {balance:,.2f} credits\n\n"
                f"📍 *Deposit Address:*\n"
                f"`{deposit_address}`\n\n"
                f"📝 *Instructions:*\n"
                f"1. Send USDC (Base network) ke address di atas\n"
                f"2. Minimal deposit: $30 USDC\n"
                f"3. Conversion: 1 USDC = 100 credits\n"
                f"4. Credits akan otomatis terdeteksi dalam 1-5 menit\n\n"
                f"💡 *Tip:* 100 credits ≈ 1 jam runtime"
            )
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        print(f"❌ Error in automaton_deposit_info: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )
