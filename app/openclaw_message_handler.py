"""
OpenClaw Message Handler - Seamless AI Assistant Chat

User bisa langsung ngetik apa saja tanpa command khusus.
Bot akan otomatis detect apakah user sedang dalam mode OpenClaw atau tidak.
"""

import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction

logger = logging.getLogger(__name__)


class OpenClawMessageHandler:
    """Handle seamless OpenClaw AI Assistant conversations"""
    
    def __init__(self, openclaw_manager):
        """
        Initialize handler
        
        Args:
            openclaw_manager: OpenClawManager instance
        """
        self.manager = openclaw_manager
    
    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """
        Handle incoming message - check if user is in OpenClaw mode
        
        Returns:
            True if message was handled by OpenClaw, False otherwise
        """
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if user has active OpenClaw session
        session = self._get_active_session(user_id, context)
        
        if not session:
            # User not in OpenClaw mode
            return False
        
        # User is in OpenClaw mode - handle with AI Assistant
        try:
            # Show typing indicator
            await update.message.chat.send_action(ChatAction.TYPING)
            
            # Get assistant and conversation info
            assistant_id = session['assistant_id']
            conversation_id = session.get('conversation_id')
            
            # Check user credits
            user_credits = self.manager.get_user_credits(user_id)
            
            # Check if user is admin
            is_admin = self.manager._is_admin(user_id)
            
            if not is_admin and user_credits < 1:
                await update.message.reply_text(
                    "❌ **Insufficient Credits**\n\n"
                    "You need credits to chat with your AI Assistant.\n\n"
                    "💰 Purchase credits: /openclaw_buy\n"
                    "🔙 Exit OpenClaw mode: /openclaw_exit",
                    parse_mode=ParseMode.MARKDOWN
                )
                return True
            
            # Send message to AI Assistant
            response, input_tokens, output_tokens, credits_cost = await self._chat_with_assistant(
                user_id=user_id,
                assistant_id=assistant_id,
                message=message_text,
                conversation_id=conversation_id
            )
            
            # Update conversation ID in session if new
            if not conversation_id:
                # Get the conversation ID from the response
                # (it was created in the chat method)
                session['conversation_id'] = self._get_latest_conversation_id(user_id, assistant_id)
                self._save_session(user_id, session, context)
            
            # Check if user is admin
            is_admin = self.manager._is_admin(user_id)
            
            # Format response with token/credit info
            if is_admin:
                footer = f"\n\n💬 {input_tokens + output_tokens} tokens • 👑 Admin (Free)"
            else:
                footer = f"\n\n💬 {input_tokens + output_tokens} tokens • 💰 {credits_cost} credits • Balance: {user_credits - credits_cost}"
            
            # Split long responses if needed
            if len(response) + len(footer) > 4000:
                # Send response in chunks
                chunks = self._split_message(response, 3900)
                for i, chunk in enumerate(chunks):
                    if i == len(chunks) - 1:
                        # Add footer to last chunk
                        await update.message.reply_text(
                            chunk + footer,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    else:
                        await update.message.reply_text(
                            chunk,
                            parse_mode=ParseMode.MARKDOWN
                        )
            else:
                await update.message.reply_text(
                    response + footer,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling OpenClaw message: {e}")
            await update.message.reply_text(
                f"❌ **Error**: {str(e)}\n\n"
                "Please try again or contact support.",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
    
    async def _chat_with_assistant(
        self,
        user_id: int,
        assistant_id: str,
        message: str,
        conversation_id: Optional[str]
    ):
        """
        Send message to AI Assistant (async wrapper)
        
        Returns:
            Tuple of (response, input_tokens, output_tokens, credits_cost)
        """
        # OpenClawManager.chat is synchronous, but we can call it directly
        # since it's fast enough (Claude API is async internally)
        return self.manager.chat(
            user_id=user_id,
            assistant_id=assistant_id,
            message=message,
            conversation_id=conversation_id
        )
    
    def _get_active_session(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> Optional[dict]:
        """
        Get user's active OpenClaw session
        
        Returns:
            Session dict or None if not in OpenClaw mode
        """
        # Check context.user_data for session
        if 'openclaw_session' in context.user_data:
            session = context.user_data['openclaw_session']
            if session.get('active', False):
                return session
        
        return None
    
    def _save_session(self, user_id: int, session: dict, context: ContextTypes.DEFAULT_TYPE):
        """Save session to context"""
        context.user_data['openclaw_session'] = session
    
    def _get_latest_conversation_id(self, user_id: int, assistant_id: str) -> Optional[str]:
        """Get latest conversation ID for user and assistant"""
        conversations = self.manager.get_user_conversations(
            user_id=user_id,
            assistant_id=assistant_id,
            limit=1
        )
        
        if conversations:
            return conversations[0]['conversation_id']
        
        return None
    
    def _split_message(self, text: str, max_length: int = 3900) -> list:
        """Split long message into chunks"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


# Command handlers for OpenClaw mode control

async def openclaw_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start OpenClaw mode - activate AI Assistant"""
    user_id = update.effective_user.id
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Check if user has any assistants
    assistants = manager.get_user_assistants(user_id)
    
    if not assistants:
        await update.message.reply_text(
            "🤖 **Welcome to OpenClaw AI Assistant!**\n\n"
            "You don't have an AI Assistant yet.\n\n"
            "Create one with: /openclaw_create\n"
            "Or learn more: /openclaw_help",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # If user has only one assistant, activate it
    if len(assistants) == 1:
        assistant = assistants[0]
        
        # Activate session
        context.user_data['openclaw_session'] = {
            'active': True,
            'assistant_id': assistant['assistant_id'],
            'conversation_id': None  # Will be created on first message
        }
        
        # Check credits
        credits = manager.get_user_credits(user_id)
        
        await update.message.reply_text(
            f"✅ **OpenClaw Mode Activated**\n\n"
            f"🤖 Assistant: {assistant['name']}\n"
            f"💰 Credits: {credits}\n\n"
            f"💬 **You can now chat freely!**\n"
            f"Just type your message - no commands needed.\n\n"
            f"🔙 Exit mode: /openclaw_exit\n"
            f"💰 Buy credits: /openclaw_buy\n"
            f"📊 View history: /openclaw_history",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # User has multiple assistants - show selection
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        for assistant in assistants:
            keyboard.append([
                InlineKeyboardButton(
                    f"🤖 {assistant['name']}",
                    callback_data=f"openclaw_select_{assistant['assistant_id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="openclaw_cancel")])
        
        await update.message.reply_text(
            "🤖 **Select AI Assistant**\n\n"
            "Choose which assistant to activate:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )


async def openclaw_exit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exit OpenClaw mode"""
    # Deactivate session
    if 'openclaw_session' in context.user_data:
        context.user_data['openclaw_session']['active'] = False
    
    await update.message.reply_text(
        "👋 **OpenClaw Mode Deactivated**\n\n"
        "You can now use regular bot commands.\n\n"
        "🔄 Reactivate: /openclaw_start",
        parse_mode=ParseMode.MARKDOWN
    )


async def openclaw_create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create new AI Assistant"""
    user_id = update.effective_user.id
    
    # Check if user provided name
    if not context.args:
        await update.message.reply_text(
            "🤖 **Create AI Assistant**\n\n"
            "Usage: `/openclaw_create <name> [personality]`\n\n"
            "Example:\n"
            "• `/openclaw_create Alex`\n"
            "• `/openclaw_create Sarah professional`\n"
            "• `/openclaw_create Bob creative`\n\n"
            "Personalities: friendly, professional, creative",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    name = context.args[0]
    personality = context.args[1] if len(context.args) > 1 else 'friendly'
    
    from services import get_database
    from app.openclaw_manager import get_openclaw_manager
    
    db = get_database()
    manager = get_openclaw_manager(db)
    
    # Check if user is admin
    is_admin = manager._is_admin(user_id)
    
    try:
        assistant = manager.create_assistant(
            user_id=user_id,
            name=name,
            personality=personality
        )
        
        if is_admin:
            await update.message.reply_text(
                f"✅ **AI Assistant Created!**\n\n"
                f"🤖 Name: {assistant['name']}\n"
                f"🎭 Personality: {assistant['personality']}\n"
                f"🆔 ID: `{assistant['assistant_id']}`\n"
                f"👑 **Admin Mode: Unlimited Access**\n\n"
                f"💬 Start chatting: /openclaw_start",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"✅ **AI Assistant Created!**\n\n"
                f"🤖 Name: {assistant['name']}\n"
                f"🎭 Personality: {assistant['personality']}\n"
                f"🆔 ID: `{assistant['assistant_id']}`\n\n"
                f"💬 Start chatting: /openclaw_start\n"
                f"💰 Buy credits: /openclaw_buy",
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Error**: {str(e)}",
            parse_mode=ParseMode.MARKDOWN
        )


async def openclaw_buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show credit purchase options"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [
            InlineKeyboardButton("10 USDC (800 credits)", callback_data="openclaw_buy_10"),
            InlineKeyboardButton("50 USDC (4,000 credits)", callback_data="openclaw_buy_50")
        ],
        [
            InlineKeyboardButton("100 USDC (8,000 credits)", callback_data="openclaw_buy_100"),
            InlineKeyboardButton("500 USDC (40,000 credits)", callback_data="openclaw_buy_500")
        ],
        [InlineKeyboardButton("💰 Custom Amount", callback_data="openclaw_buy_custom")]
    ]
    
    await update.message.reply_text(
        "💰 **Purchase OpenClaw Credits**\n\n"
        "**Pricing:**\n"
        "• 1 USDC = 100 credits (after 20% platform fee)\n"
        "• Platform fee: 20% for sustainability\n"
        "• You receive: 80% in credits\n\n"
        "**Example:**\n"
        "• Purchase: 100 USDC\n"
        "• Platform fee: 20 USDC (20%)\n"
        "• You get: 8,000 credits (80 USDC)\n\n"
        "**Usage:**\n"
        "• Average chat: 2-5 credits\n"
        "• 8,000 credits ≈ 2,000-4,000 conversations\n\n"
        "Select amount below:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


async def openclaw_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show OpenClaw help"""
    await update.message.reply_text(
        "🤖 **OpenClaw AI Assistant - Help**\n\n"
        "**What is OpenClaw?**\n"
        "Personal AI Assistant powered by Claude Sonnet 4.5 with self-awareness.\n\n"
        "**Features:**\n"
        "• 💬 Natural conversation - just type freely\n"
        "• 🧠 Self-aware - remembers your preferences\n"
        "• 📚 Context-aware - references past discussions\n"
        "• 🎯 Task execution - helps with anything\n"
        "• 🔒 Private - your data is isolated\n\n"
        "**Commands:**\n"
        "• `/openclaw_start` - Activate AI Assistant\n"
        "• `/openclaw_exit` - Deactivate mode\n"
        "• `/openclaw_create <name>` - Create assistant\n"
        "• `/openclaw_buy` - Purchase credits\n"
        "• `/openclaw_balance` - Check credits\n"
        "• `/openclaw_history` - View conversations\n\n"
        "**Pricing:**\n"
        "• 20% platform fee on purchases\n"
        "• 80% goes to your credits\n"
        "• ~2-5 credits per conversation\n\n"
        "**How to Use:**\n"
        "1. Create assistant: `/openclaw_create Alex`\n"
        "2. Buy credits: `/openclaw_buy`\n"
        "3. Activate: `/openclaw_start`\n"
        "4. Chat freely - no commands needed!\n\n"
        "Questions? Contact admin.",
        parse_mode=ParseMode.MARKDOWN
    )


def get_openclaw_message_handler(openclaw_manager):
    """Factory function to get OpenClawMessageHandler instance"""
    return OpenClawMessageHandler(openclaw_manager)
