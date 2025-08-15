
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.lib.guards import admin_guard
from app.safe_send import safe_reply
from app.db_admin import sb_health, sb_counts_safe, build_sql_fix

@admin_guard
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel showing DB status and user counts"""
    try:
        ok, detail = sb_health()
        counts, missing = sb_counts_safe()
        
        msg = (
            f"🔧 **Admin Panel (DB)**\n\n"
            f"**Health:** {'✅ OK' if ok else '❌ FAIL'} ({detail})\n\n"
            f"**User Statistics:**\n"
            f"— registered: {counts.get('registered', 0)}\n"
            f"— premium_active: {counts.get('premium_active', 0)}\n"
            f"— lifetime: {counts.get('lifetime', 0)}\n"
            f"— banned: {counts.get('banned', 0)}\n"
            f"— referred: {counts.get('referred', 0)}\n"
            f"— registered_by_start: {counts.get('registered_by_start', 0)}\n"
        )
        
        if missing:
            sql = build_sql_fix(missing)
            msg += f"\n⚠️ **Missing columns:** {', '.join(missing)}"
            msg += f"\n\n🛠️ **SQL Fix** (jalankan di Supabase SQL Editor):\n```sql\n{sql}\n```"
        else:
            msg += "\n✅ **Schema OK** (no missing columns)"
            
    except Exception as e:
        msg = f"❌ **Admin Panel Error**\n\n{str(e)}"
    
    await safe_reply(update.effective_message, msg, parse_mode='Markdown')

def register_admin_panel(application):
    """Register admin panel handler"""
    application.add_handler(CommandHandler("admin", cmd_admin))
