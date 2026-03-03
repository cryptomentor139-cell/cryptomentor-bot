"""
OpenClaw Admin Handler - Auto-activate OpenClaw for admins
Admins don't need to use /openclaw_start, they can directly chat
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

logger = logging.getLogger(__name__)


class OpenClawAdminHandler:
    """Handle admin messages with auto-activation"""
    
    def __init__(self, openclaw_manager):
        self.manager = openclaw_manager
    
    async def handle_admin_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """
        Check if message is from admin and auto-activate OpenClaw
        
        Returns:
            True if handled, False otherwise
        """
        user_id = update.effective_user.id
        
        # Check if user is admin
        if not self.manager._is_admin(user_id):
            return False
        
        # Check if already in OpenClaw mode
        session = context.user_data.get('openclaw_session', {})
        if session.get('active'):
            # Already active, let normal handler take over
            return False
        
        # Admin is not in OpenClaw mode - auto-activate!
        try:
            # Get or create admin assistant
            assistants = self.manager.get_user_assistants(user_id)
            
            if not assistants:
                # Create default admin assistant
                assistant = self.manager.create_assistant(
                    user_id=user_id,
                    name="AdminBot",
                    personality="professional"
                )
                assistant_id = assistant['assistant_id']
                
                logger.info(f"Auto-created admin assistant for user {user_id}")
            else:
                # Use first assistant
                assistant_id = assistants[0]['assistant_id']
            
            # Auto-activate session
            context.user_data['openclaw_session'] = {
                'active': True,
                'assistant_id': assistant_id,
                'conversation_id': None,
                'auto_activated': True  # Mark as auto-activated
            }
            
            logger.info(f"Auto-activated OpenClaw for admin {user_id}")
            
            # Send welcome message (only first time)
            if not context.user_data.get('openclaw_admin_welcomed'):
                await update.message.reply_text(
                    "👑 **Admin Mode Auto-Activated**\n\n"
                    "You can now chat directly with OpenClaw.\n"
                    "No commands needed!\n\n"
                    "💡 **Admin Capabilities:**\n"
                    "• Update bot prices\n"
                    "• View statistics\n"
                    "• Deploy changes\n"
                    "• Manage system\n\n"
                    "Just ask me anything!",
                    parse_mode=None
                )
                context.user_data['openclaw_admin_welcomed'] = True
            
            # Return False to let normal OpenClaw handler process the message
            return False
            
        except Exception as e:
            logger.error(f"Error auto-activating admin OpenClaw: {e}")
            return False


def get_openclaw_admin_handler(openclaw_manager):
    """Get OpenClaw admin handler instance"""
    return OpenClawAdminHandler(openclaw_manager)
