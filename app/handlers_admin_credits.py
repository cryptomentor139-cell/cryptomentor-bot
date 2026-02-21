# Admin Credits Management Handlers
# Manual credit addition for deposits

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import Database
from app.admin_status import is_admin

db = Database()


async def admin_add_automaton_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command to manually add AUTOMATON credits to user (for AI Agent)
    
    Usage: /admin_add_automaton_credits <user_id> <amount> <note>
    Example: /admin_add_automaton_credits 123456789 3000 "Deposit $30 USDC verified"
    
    NOTE: This is for AUTOMATON credits (AI Agent), NOT regular bot credits!
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Command ini hanya untuk admin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Parse arguments
    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 *Format Command:*\n\n"
            "`/admin_add_automaton_credits <user_id> <amount> <note>`\n\n"
            "*Contoh:*\n"
            "`/admin_add_automaton_credits 123456789 3000 Deposit $30 USDC verified`\n\n"
            "*Parameter:*\n"
            "• user_id: Telegram user ID\n"
            "• amount: Jumlah AUTOMATON credits (1 USDC = 100 credits)\n"
            "• note: Catatan deposit (opsional, bisa lebih dari 1 kata)\n\n"
            "⚠️ *PENTING:* Command ini untuk AUTOMATON credits (AI Agent), bukan credits bot biasa!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        amount = float(context.args[1])
        note = ' '.join(context.args[2:]) if len(context.args) > 2 else "Manual credit addition by admin"
        
        # Validate amount
        if amount <= 0:
            await update.message.reply_text(
                "❌ Amount harus lebih dari 0.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if user exists
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Database tidak tersedia.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if user exists in database
        user_result = db.supabase_service.table('users')\
            .select('user_id, username, first_name')\
            .eq('user_id', target_user_id)\
            .execute()
        
        if not user_result.data:
            await update.message.reply_text(
                f"❌ User dengan ID `{target_user_id}` tidak ditemukan.\n\n"
                f"Pastikan user sudah pernah /start bot.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        user_info = user_result.data[0]
        username = user_info.get('username', 'N/A')
        first_name = user_info.get('first_name', 'User')
        
        # Get or create user_credits_balance
        credits_result = db.supabase_service.table('user_credits_balance')\
            .select('*')\
            .eq('user_id', target_user_id)\
            .execute()
        
        if credits_result.data:
            # Update existing balance
            current_balance = credits_result.data[0]
            old_available = float(current_balance.get('available_credits', 0))
            old_total = float(current_balance.get('total_conway_credits', 0))
            
            new_available = old_available + amount
            new_total = old_total + amount
            
            db.supabase_service.table('user_credits_balance').update({
                'available_credits': new_available,
                'total_conway_credits': new_total
            }).eq('user_id', target_user_id).execute()
            
            # Log transaction
            db.supabase_service.table('credit_transactions').insert({
                'user_id': target_user_id,
                'amount': amount,
                'type': 'admin_deposit',
                'description': note,
                'admin_id': user_id
            }).execute()
            
            # Send confirmation to admin
            await update.message.reply_text(
                f"✅ *AUTOMATON Credits Berhasil Ditambahkan!*\n\n"
                f"👤 *User Info:*\n"
                f"• ID: `{target_user_id}`\n"
                f"• Username: @{username}\n"
                f"• Name: {first_name}\n\n"
                f"💰 *AUTOMATON Credits Update:*\n"
                f"• Sebelum: {old_available:,.0f} credits\n"
                f"• Ditambah: +{amount:,.0f} credits\n"
                f"• Sesudah: {new_available:,.0f} credits\n\n"
                f"📝 *Note:* {note}\n\n"
                f"⚠️ Ini adalah AUTOMATON credits untuk AI Agent\n"
                f"User akan menerima notifikasi.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Send notification to user
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"✅ *Deposit AUTOMATON Berhasil Diverifikasi!*\n\n"
                         f"💰 AUTOMATON Credits telah ditambahkan ke akun Anda:\n"
                         f"• Jumlah: +{amount:,.0f} credits\n"
                         f"• Balance baru: {new_available:,.0f} credits\n\n"
                         f"📝 Note: {note}\n\n"
                         f"🤖 Credits ini khusus untuk AI Agent (autonomous trading)\n\n"
                         f"🎯 *Langkah Selanjutnya:*\n"
                         f"Klik tombol *🤖 AI Agent* di menu utama untuk spawn agent Anda!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                print(f"⚠️ Could not send notification to user {target_user_id}: {e}")
                await update.message.reply_text(
                    f"⚠️ Credits ditambahkan tapi notifikasi ke user gagal dikirim.",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            # Create new balance entry
            db.supabase_service.table('user_credits_balance').insert({
                'user_id': target_user_id,
                'available_credits': amount,
                'total_conway_credits': amount
            }).execute()
            
            # Log transaction
            db.supabase_service.table('credit_transactions').insert({
                'user_id': target_user_id,
                'amount': amount,
                'type': 'admin_deposit',
                'description': note,
                'admin_id': user_id
            }).execute()
            
            # Send confirmation to admin
            await update.message.reply_text(
                f"✅ *AUTOMATON Credits Berhasil Ditambahkan!*\n\n"
                f"👤 *User Info:*\n"
                f"• ID: `{target_user_id}`\n"
                f"• Username: @{username}\n"
                f"• Name: {first_name}\n\n"
                f"💰 *AUTOMATON Credits Created:*\n"
                f"• Balance baru: {amount:,.0f} credits\n\n"
                f"📝 *Note:* {note}\n\n"
                f"⚠️ Ini adalah AUTOMATON credits untuk AI Agent\n"
                f"User akan menerima notifikasi.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Send notification to user
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"✅ *Deposit AUTOMATON Berhasil Diverifikasi!*\n\n"
                         f"💰 AUTOMATON Credits telah ditambahkan ke akun Anda:\n"
                         f"• Jumlah: +{amount:,.0f} credits\n"
                         f"• Balance baru: {amount:,.0f} credits\n\n"
                         f"📝 Note: {note}\n\n"
                         f"🤖 Credits ini khusus untuk AI Agent (autonomous trading)\n\n"
                         f"🎯 *Langkah Selanjutnya:*\n"
                         f"Klik tombol *🤖 AI Agent* di menu utama untuk spawn agent Anda!",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                print(f"⚠️ Could not send notification to user {target_user_id}: {e}")
                await update.message.reply_text(
                    f"⚠️ Credits ditambahkan tapi notifikasi ke user gagal dikirim.",
                    parse_mode=ParseMode.MARKDOWN
                )
        
    except ValueError:
        await update.message.reply_text(
            "❌ Format tidak valid.\n\n"
            "• user_id harus berupa angka\n"
            "• amount harus berupa angka",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"❌ Error in admin_add_automaton_credits_command: {e}")
        await update.message.reply_text(
            f"❌ Terjadi kesalahan: {str(e)[:100]}",
            parse_mode=ParseMode.MARKDOWN
        )


async def admin_check_automaton_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command to check user AUTOMATON credits (for AI Agent)
    
    Usage: /admin_check_automaton_credits <user_id>
    
    NOTE: This checks AUTOMATON credits (AI Agent), NOT regular bot credits!
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Command ini hanya untuk admin.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Parse arguments
    if len(context.args) < 1:
        await update.message.reply_text(
            "📝 *Format Command:*\n\n"
            "`/admin_check_automaton_credits <user_id>`\n\n"
            "*Contoh:*\n"
            "`/admin_check_automaton_credits 123456789`\n\n"
            "⚠️ *PENTING:* Command ini untuk cek AUTOMATON credits (AI Agent), bukan credits bot biasa!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        
        if not db.supabase_enabled:
            await update.message.reply_text(
                "❌ Database tidak tersedia.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get user info
        user_result = db.supabase_service.table('users')\
            .select('user_id, username, first_name, premium_tier')\
            .eq('user_id', target_user_id)\
            .execute()
        
        if not user_result.data:
            await update.message.reply_text(
                f"❌ User dengan ID `{target_user_id}` tidak ditemukan.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        user_info = user_result.data[0]
        username = user_info.get('username', 'N/A')
        first_name = user_info.get('first_name', 'User')
        premium_tier = user_info.get('premium_tier', 'none')
        
        # Get credits balance
        credits_result = db.supabase_service.table('user_credits_balance')\
            .select('*')\
            .eq('user_id', target_user_id)\
            .execute()
        
        if credits_result.data:
            balance = credits_result.data[0]
            available = float(balance.get('available_credits', 0))
            total = float(balance.get('total_conway_credits', 0))
            
            await update.message.reply_text(
                f"👤 *User Info:*\n"
                f"• ID: `{target_user_id}`\n"
                f"• Username: @{username}\n"
                f"• Name: {first_name}\n"
                f"• Premium: {premium_tier}\n\n"
                f"💰 *AUTOMATON Credits Balance:*\n"
                f"• Available: {available:,.0f} credits\n"
                f"• Total: {total:,.0f} credits\n\n"
                f"📊 *Status:*\n"
                f"• Minimum untuk spawn: 3.000 credits\n"
                f"• Status: {'✅ Cukup' if available >= 3000 else '❌ Kurang'}\n\n"
                f"⚠️ Ini adalah AUTOMATON credits untuk AI Agent",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"👤 *User Info:*\n"
                f"• ID: `{target_user_id}`\n"
                f"• Username: @{username}\n"
                f"• Name: {first_name}\n"
                f"• Premium: {premium_tier}\n\n"
                f"💰 *AUTOMATON Credits Balance:*\n"
                f"• Available: 0 credits\n"
                f"• Total: 0 credits\n\n"
                f"❌ User belum pernah deposit.\n\n"
                f"⚠️ Ini adalah AUTOMATON credits untuk AI Agent",
                parse_mode=ParseMode.MARKDOWN
            )
        
    except ValueError:
        await update.message.reply_text(
            "❌ user_id harus berupa angka.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"❌ Error in admin_check_automaton_credits_command: {e}")
        await update.message.reply_text(
            f"❌ Terjadi kesalahan: {str(e)[:100]}",
            parse_mode=ParseMode.MARKDOWN
        )
