"""
Handler untuk cancel AI requests
"""
from telegram import Update
from telegram.ext import ContextTypes

async def handle_cancel_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk cancel button pada AI analysis
    Callback data format: cancel_ai_{user_id}
    """
    query = update.callback_query
    await query.answer()
    
    try:
        # Extract user_id from callback data
        callback_data = query.data
        if not callback_data.startswith('cancel_ai_'):
            return
        
        user_id_str = callback_data.replace('cancel_ai_', '')
        requested_user_id = int(user_id_str)
        actual_user_id = update.effective_user.id
        
        # Verify user is cancelling their own request
        if requested_user_id != actual_user_id:
            await query.edit_message_text(
                "❌ Anda tidak bisa cancel request user lain!",
                parse_mode='Markdown'
            )
            return
        
        # Import active requests tracker
        from app.handlers_deepseek import active_ai_requests
        
        # Check if request exists
        if user_id_str not in active_ai_requests and requested_user_id not in active_ai_requests:
            await query.edit_message_text(
                "⚠️ Request sudah selesai atau tidak ditemukan",
                parse_mode='Markdown'
            )
            return
        
        # Get request info (try both string and int keys)
        request_info = active_ai_requests.get(user_id_str) or active_ai_requests.get(requested_user_id)
        
        if request_info:
            # Set cancel event
            cancel_event = request_info.get('cancel_event')
            if cancel_event:
                cancel_event.set()
                
                symbol = request_info.get('symbol', 'Unknown')
                
                await query.edit_message_text(
                    f"❌ **Analisis {symbol} dibatalkan**\n\n"
                    "Silakan coba lagi dengan /ai <symbol>",
                    parse_mode='Markdown'
                )
                
                print(f"✅ AI request cancelled by user {actual_user_id}")
            else:
                await query.edit_message_text(
                    "⚠️ Tidak bisa cancel request ini",
                    parse_mode='Markdown'
                )
        else:
            await query.edit_message_text(
                "⚠️ Request sudah selesai",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        print(f"Error in handle_cancel_ai: {e}")
        await query.edit_message_text(
            "❌ Error saat cancel request",
            parse_mode='Markdown'
        )
