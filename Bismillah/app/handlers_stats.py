
<file_path>Bismillah/app/handlers_stats.py</file_path>
<line_number>1</line_number>
from telegram import Update
from telegram.ext import ContextTypes
from app.lib.guards import admin_guard
from app.supabase_conn import sb_count_users
from app.safe_send import safe_reply

@admin_guard
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user statistics from Supabase"""
    try:
        # Get counts from Supabase
        total_users = sb_count_users()  # All users
        premium_active = sb_count_users(premium_active=True)
        lifetime = sb_count_users(lifetime=True)
        
        message = f"""📊 **User Statistics (Supabase)**

👥 **Total Users**: {total_users:,}
⭐ **Premium Active** (incl. lifetime): {premium_active:,}
🌟 **Lifetime Premium**: {lifetime:,}
📊 **Free Users**: {total_users - premium_active:,}

💡 **Note**: Counts sourced directly from Supabase database
🕐 **Real-time**: Data refreshed on each query"""

        await safe_reply(update.effective_message, message)
        
    except Exception as e:
        await safe_reply(update.effective_message, f"❌ Stats error: {e}")

@admin_guard 
async def cmd_premium_breakdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get detailed premium user breakdown"""
    try:
        from app.supabase_conn import sb_list_users
        from datetime import datetime, timezone
        
        # Get premium users with details
        premium_users = sb_list_users({
            "is_premium": "eq.true",
            "banned": "eq.false"
        }, columns="telegram_id,premium_until,created_at", limit=100)
        
        lifetime_count = 0
        timed_count = 0
        expired_count = 0
        now = datetime.now(timezone.utc)
        
        for user in premium_users:
            premium_until = user.get('premium_until')
            if premium_until is None:
                lifetime_count += 1
            else:
                try:
                    until_dt = datetime.fromisoformat(premium_until.replace('Z', '+00:00'))
                    if until_dt >= now:
                        timed_count += 1
                    else:
                        expired_count += 1
                except:
                    expired_count += 1
        
        message = f"""📊 **Premium User Breakdown**

🌟 **Lifetime Premium**: {lifetime_count:,}
⏰ **Timed Premium (Active)**: {timed_count:,}
❌ **Expired Premium**: {expired_count:,}
📊 **Total Premium Records**: {len(premium_users):,}

✅ **Active Premium Total**: {lifetime_count + timed_count:,}"""

        await safe_reply(update.effective_message, message)
        
    except Exception as e:
        await safe_reply(update.effective_message, f"❌ Premium breakdown error: {e}")
