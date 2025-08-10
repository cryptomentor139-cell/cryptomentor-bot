import os
from telegram import Update
from telegram.ext import ContextTypes

from app.utils import safe_reply, is_admin

# Import necessary functions from app.supabase_conn and app.chat_store
from app.supabase_conn import sb_list_users
from app.chat_store import get_private_chat_id

async def get_autosignal_audience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get AutoSignal audience info for admin - only Supabase lifetime + admin"""
    user_id = update.message.from_user.id

    if not is_admin(user_id):
        await safe_reply(update.message, "❌ Access denied. Admin only command.")
        return

    try:
        # Get admin IDs from environment
        admin_ids = set()
        for key in ("ADMIN_USER_ID", "ADMIN2_USER_ID", "ADMIN1", "ADMIN2"):
            val = os.getenv(key)
            if val and val.isdigit():
                admin_ids.add(int(val))

        # Get all premium users from Supabase only
        from app.supabase_conn import sb_get_premium_count, sb_get_premium_users
        
        premium_counts = sb_get_premium_count()
        lifetime_users = []
        
        try:
            # Get lifetime users only for audience display
            lifetime_rows = sb_list_users({
                "is_premium": "eq.true",
                "banned": "eq.false", 
                "premium_until": "is.null"
            }, columns="telegram_id,first_name,username")

            # Filter users who have private chat consent
            for row in lifetime_rows:
                tid = row.get("telegram_id")
                if tid and get_private_chat_id(int(tid)) is not None:
                    lifetime_users.append({
                        'telegram_id': tid,
                        'first_name': row.get('first_name', 'Unknown'),
                        'username': row.get('username', 'no_username')
                    })
        except Exception as e:
            print(f"Error getting Supabase premium users: {e}")

        total_eligible = len(admin_ids) + len(lifetime_users)

        message = f"""🛰️ **AutoSignal Audience Report (Supabase Only)**

📊 **Total Eligible**: {total_eligible}

👥 **Breakdown**:
• 👑 Admin users: {len(admin_ids)}
• ⭐ Lifetime premium: {len(lifetime_users)}

📈 **All Premium Stats (Supabase)**:
• 💎 Lifetime: {premium_counts['lifetime']}
• ⏰ Timed Active: {premium_counts['timed']}
• 📊 Total Premium: {premium_counts['total']}

🔍 **AutoSignal Filters**:
• ✅ Not banned (Supabase check)
• ✅ Has private chat consent (/start used)
• ✅ Lifetime premium ONLY (premium_until IS NULL)
• ✅ Admin from environment variables
• 🚫 No local backup/JSON sources

📡 **AutoSignal Config**:
• ⏰ Interval: 30 minutes
• 🎯 Min Confidence: 75%
• 🗄️ Source: Supabase REST API only

**Sample Recipients**:
{[tid for tid in list(admin_ids)[:3] + [u['telegram_id'] for u in lifetime_users[:7]]]}
"""

        await safe_reply(update.message, message)

    except Exception as e:
        await safe_reply(update.message, f"❌ Error getting audience: {str(e)}")
        print(f"Error in get_autosignal_audience: {e}")