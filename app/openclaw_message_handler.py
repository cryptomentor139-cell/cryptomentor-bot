"""
OpenClaw Message Handler - Seamless AI Assistant Chat (DEFAULT MODE)

User bisa langsung ngetik apa saja tanpa command khusus.
Bot akan otomatis create OpenClaw session untuk semua user.
"""

import logging
from typing import Optional
from datetime import datetime
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
        Handle incoming message - AUTO-CREATE OpenClaw session if needed (DEFAULT MODE)
        
        Returns:
            True if message was handled by OpenClaw, False otherwise
        """
        user_id = update.effective_user.id
        message_text = update.message.text if update.message.text else ""
        has_photo = bool(update.message.photo)
        
        # Check if user has active OpenClaw session
        session = self._get_active_session(user_id, context)
        
        if not session:
            # AUTO-CREATE OpenClaw session (DEFAULT MODE)
            # Get or create default assistant for user
            assistant_id = self.manager.get_or_create_assistant(user_id)
            
            if not assistant_id:
                logger.error(f"Failed to create assistant for user {user_id}")
                return False
            
            # Create new session
            session = {
                'assistant_id': assistant_id,
                'conversation_id': None,
                'created_at': datetime.now().isoformat()
            }
            self._save_session(user_id, session, context)
            
            logger.info(f"✅ Auto-created OpenClaw session for user {user_id}")
        
        # User is in OpenClaw mode - handle with AI Assistant
        try:
            # Get assistant and conversation info
            assistant_id = session['assistant_id']
            conversation_id = session.get('conversation_id')
            
            # Check user credits from per-user balance
            from app.openclaw_user_credits import get_user_credits
            from services import get_database
            from decimal import Decimal
            
            db = get_database()
            user_credits = get_user_credits(db, user_id)
            
            # Check if user is admin
            is_admin = self.manager._is_admin(user_id)
            
            if not is_admin and user_credits < Decimal('0.01'):  # Minimum 1 cent
                await update.message.reply_text(
                    "❌ Insufficient Credits\n\n"
                    "You need credits to chat with your AI Assistant.\n\n"
                    "💰 Purchase credits: /subscribe\n"
                    "💳 Check balance: /openclaw_balance\n"
                    "📞 Contact admin: @BillFarr",
                    parse_mode=None
                )
                return True
            
            # Determine loading message based on request type
            loading_emoji = self._get_loading_emoji(message_text, has_photo)
            loading_text = self._get_loading_text(message_text, has_photo)
            
            # Send loading message
            loading_msg = await update.message.reply_text(
                f"{loading_emoji} {loading_text}",
                parse_mode=None
            )
            
            # Show typing indicator
            await update.message.chat.send_action(ChatAction.TYPING)
            
            # Send message to AI Assistant
            response, input_tokens, output_tokens, credits_cost = await self._chat_with_assistant(
                user_id=user_id,
                assistant_id=assistant_id,
                message=message_text,
                conversation_id=conversation_id,
                has_photo=has_photo,
                photo=update.message.photo[-1] if has_photo else None
            )
            
            # Deduct credits from user's balance (skip for admin)
            if not is_admin:
                from app.openclaw_user_credits import deduct_credits
                
                success, new_balance, deduct_msg = deduct_credits(
                    db=db,
                    user_id=user_id,
                    amount=Decimal(str(credits_cost)),
                    assistant_id=assistant_id,
                    conversation_id=conversation_id,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_used="openai/gpt-4.1"
                )
                
                if not success:
                    # Deduction failed - should not happen as we checked before
                    await update.message.reply_text(
                        f"❌ Credit deduction failed: {deduct_msg}\n\n"
                        "Please contact admin: @BillFarr",
                        parse_mode=None
                    )
                    return True
                
                user_credits = new_balance  # Update for display
            
            # Delete loading message
            try:
                await loading_msg.delete()
            except:
                pass  # Ignore if already deleted
            
            # Update conversation ID in session if new
            if not conversation_id:
                session['conversation_id'] = self._get_latest_conversation_id(user_id, assistant_id)
                self._save_session(user_id, session, context)
            
            # Check if tools were used (for admin users)
            tool_usage_info = ""
            if hasattr(self, '_last_tool_calls') and self._last_tool_calls:
                tool_names = [tc['tool'] for tc in self._last_tool_calls]
                tool_usage_info = f"\n🔧 Tools used: {', '.join(tool_names)}"
                # Clear after use
                self._last_tool_calls = []
            
            # Format response with token/credit info
            if is_admin:
                footer = f"\n\n💬 {input_tokens + output_tokens} tokens • 👑 Admin (Free){tool_usage_info}"
            else:
                footer = f"\n\n💰 Cost: ${credits_cost:.4f} • 💳 Balance: ${float(user_credits):.2f}"
            
            # Split long responses if needed
            if len(response) + len(footer) > 4000:
                chunks = self._split_message(response, 3900)
                for i, chunk in enumerate(chunks):
                    if i == len(chunks) - 1:
                        await update.message.reply_text(
                            chunk + footer,
                            parse_mode=None
                        )
                    else:
                        await update.message.reply_text(
                            chunk,
                            parse_mode=None
                        )
            else:
                await update.message.reply_text(
                    response + footer,
                    parse_mode=None
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling OpenClaw message: {e}")
            
            # Try to delete loading message if it exists
            try:
                if 'loading_msg' in locals():
                    await loading_msg.delete()
            except:
                pass
            
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n\n"
                "Please try again or contact support.",
                parse_mode=None
            )
            return True
    
    async def _chat_with_assistant(
        self,
        user_id: int,
        assistant_id: str,
        message: str,
        conversation_id: Optional[str],
        has_photo: bool = False,
        photo = None
    ):
        """
        Send message to AI Assistant (async wrapper)
        Uses agentic loop if available (for admin with tool access)
        
        Returns:
            Tuple of (response, input_tokens, output_tokens, credits_cost)
        """
        # Enhance message with real-time data and image analysis
        try:
            from app.openclaw_enhanced_handler import get_enhanced_handler
            enhanced_handler = get_enhanced_handler(self.manager)
            
            # Get photo file if available
            photo_file = None
            if has_photo and photo:
                photo_file = await photo.get_file()
            
            # Enhance message with crypto data and image analysis
            enhanced_message, context_data = await enhanced_handler.enhance_message_with_data(
                message=message,
                photo=photo_file
            )
            
            # Use enhanced message
            message = enhanced_message
            
            logger.info(f"Enhanced message with context: {list(context_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error enhancing message: {e}")
            # Fallback to original message
            if has_photo and photo:
                message = f"[User sent an image]\n{message if message else 'Please analyze this image'}"
        
        # Check if agentic loop is available (injected from bot.py)
        if hasattr(self, 'agentic_loop') and self.agentic_loop:
            # Use agentic loop with tool calling capabilities
            try:
                response, input_tokens, output_tokens, credits_cost, tool_calls = self.agentic_loop.chat_with_tools(
                    user_id=user_id,
                    assistant_id=assistant_id,
                    message=message,
                    conversation_id=conversation_id
                )
                
                # Store tool calls for display
                self._last_tool_calls = tool_calls if tool_calls else []
                
                return response, input_tokens, output_tokens, credits_cost
            except Exception as e:
                logger.error(f"Agentic loop error, falling back to basic chat: {e}")
                # Fallback to basic chat on error
        
        # Fallback: Use basic chat without tools
        self._last_tool_calls = []  # No tools used in basic chat
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
    
    def _get_loading_emoji(self, message: str, has_photo: bool) -> str:
        """Get appropriate loading emoji based on request type"""
        message_lower = message.lower()
        
        if has_photo:
            return "🖼️"
        elif any(word in message_lower for word in ['chart', 'graph', 'candle']):
            return "📊"
        elif any(word in message_lower for word in ['signal', 'trade', 'buy', 'sell']):
            return "📈"
        elif any(word in message_lower for word in ['analyze', 'analysis', 'study']):
            return "🔍"
        elif any(word in message_lower for word in ['price', 'market', 'trend']):
            return "💹"
        elif any(word in message_lower for word in ['news', 'update', 'latest']):
            return "📰"
        elif any(word in message_lower for word in ['portfolio', 'balance', 'holdings']):
            return "💼"
        elif any(word in message_lower for word in ['risk', 'safe', 'danger']):
            return "⚠️"
        else:
            return "🤖"
    
    def _get_loading_text(self, message: str, has_photo: bool) -> str:
        """Get appropriate loading text based on request type"""
        message_lower = message.lower()
        
        if has_photo:
            return "Processing your image..."
        elif any(word in message_lower for word in ['chart', 'graph', 'candle']):
            return "Analyzing chart..."
        elif any(word in message_lower for word in ['signal', 'trade']):
            return "Generating trading signal..."
        elif any(word in message_lower for word in ['analyze', 'analysis']):
            return "Performing deep analysis..."
        elif any(word in message_lower for word in ['price', 'market']):
            return "Checking market data..."
        elif any(word in message_lower for word in ['news', 'update']):
            return "Fetching latest news..."
        elif any(word in message_lower for word in ['portfolio', 'balance']):
            return "Calculating portfolio..."
        elif any(word in message_lower for word in ['risk', 'safe']):
            return "Assessing risk..."
        elif len(message) > 200:
            return "Processing your detailed request..."
        else:
            return "Thinking..."
    

    def _escape_markdown_v2(self, text: str) -> str:
        """
        Escape special characters for Telegram MarkdownV2
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text safe for Telegram MarkdownV2
        """
        # Characters that need escaping in MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        escaped_text = text
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        
        return escaped_text


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
        "Personal AI Assistant powered by GPT-4.1 with crypto expertise.\n\n"
        "**Features:**\n"
        "• 💬 Natural conversation - just type freely\n"
        "• 🧠 Self-aware - remembers your preferences\n"
        "• 📊 Crypto analysis - charts, signals, trends\n"
        "• 🖼️ Image analysis - send chart screenshots\n"
        "• 🎯 All capabilities included - no skill purchases needed\n"
        "• 🔒 Private - your data is isolated\n\n"
        "**Commands:**\n"
        "• `/openclaw_start` - Activate AI Assistant\n"
        "• `/openclaw_exit` - Deactivate mode\n"
        "• `/openclaw_create <name>` - Create assistant\n"
        "• `/openclaw_buy` - Purchase credits\n"
        "• `/openclaw_balance` - Check credits\n"
        "• `/openclaw_history` - View conversations\n\n"
        "**Pay-Per-Use Pricing:**\n"
        "• No upfront costs - pay only for what you use\n"
        "• Simple question: ~5-10 credits\n"
        "• Chart analysis: ~15-25 credits\n"
        "• Deep analysis: ~30-50 credits\n"
        "• Image processing: ~20-40 credits\n"
        "• Cost shown after each response\n\n"
        "**How to Use:**\n"
        "1. Create assistant: `/openclaw_create Alex`\n"
        "2. Buy credits: `/openclaw_buy`\n"
        "3. Activate: `/openclaw_start`\n"
        "4. Chat freely - send text or images!\n"
        "5. See cost and balance after each response\n\n"
        "**Example:**\n"
        "You: \"Analyze BTC trend\"\n"
        "Bot: 📊 Analyzing chart...\n"
        "Bot: [Detailed analysis]\n"
        "     💰 Cost: 15 credits • 💳 Balance: 9,985\n\n"
        "Questions? Contact admin.",
        parse_mode=ParseMode.MARKDOWN
    )


def get_openclaw_message_handler(openclaw_manager):
    """Factory function to get OpenClawMessageHandler instance"""
    return OpenClawMessageHandler(openclaw_manager)
