"""
OpenClaw Manager - Personal AI Assistant with Claude Sonnet 4.5

This module manages AI Assistants with self-awareness, credit system with 20% platform fee,
and conversation management for sustainable LLM operations.

Platform Fee Model:
- 20% platform fee for profit and sustainability
- 80% for LLM usage and Railway server costs
- Self-sustaining system
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class OpenClawManager:
    """Manages OpenClaw AI Assistants with Claude Sonnet 4.5"""
    
    # Platform fee configuration
    PLATFORM_FEE_PERCENTAGE = 0.20  # 20%
    USDC_TO_CREDITS = 100  # 1 USDC = 100 credits
    
    # GPT-4.1 pricing (per 1M tokens) - Much cheaper than Claude!
    INPUT_TOKEN_COST_USD = 2.5 / 1_000_000  # $2.5 per 1M input tokens
    OUTPUT_TOKEN_COST_USD = 10.0 / 1_000_000  # $10 per 1M output tokens
    
    # Model configuration
    MODEL = "openai/gpt-4.1"  # GPT-4.1 via OpenRouter (cheaper & faster!)
    MAX_TOKENS = 8192
    TEMPERATURE = 0.7
    
    def __init__(self, db):
        """
        Initialize OpenClaw Manager
        
        Args:
            db: Database instance
        """
        self.db = db
        self.conn = db.conn  # Get underlying connection
        self.cursor = db.cursor  # Get cursor
        
        # Check for OpenClaw-specific API key first, then fallback to DEEPSEEK_API_KEY
        openclaw_key = os.getenv('OPENCLAW_API_KEY')
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        
        if openclaw_key:
            # Use dedicated OpenClaw API key (preferred)
            self.use_openrouter = True
            self.api_key = openclaw_key
            self.base_url = os.getenv('OPENCLAW_BASE_URL', 'https://openrouter.ai/api/v1')
            logger.info("OpenClawManager initialized with GPT-4.1 via OpenRouter (dedicated key)")
        elif deepseek_key:
            # Fallback to shared DEEPSEEK_API_KEY
            self.use_openrouter = True
            self.api_key = deepseek_key
            self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1')
            logger.info("OpenClawManager initialized with GPT-4.1 via OpenRouter (shared key)")
        else:
            raise ValueError("Neither OPENCLAW_API_KEY nor DEEPSEEK_API_KEY found in environment")
    
    def _is_admin(self, user_id: int) -> bool:
        """
        Check if user is admin
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is admin, False otherwise
        """
        # Get admin IDs from environment
        admin_ids = set()
        for key in ['ADMIN1', 'ADMIN2', 'ADMIN3', 'ADMIN_IDS']:
            value = os.getenv(key)
            if value:
                try:
                    if ',' in value:
                        # Handle comma-separated list
                        admin_ids.update(int(aid.strip()) for aid in value.split(',') if aid.strip())
                    else:
                        admin_ids.add(int(value))
                except ValueError:
                    continue
        
        return user_id in admin_ids
    
    def create_assistant(
        self,
        user_id: int,
        name: str,
        personality: str = 'friendly',
        custom_prompt: Optional[str] = None
    ) -> Dict:
        """
        Create new AI Assistant for user
        
        Args:
            user_id: Telegram user ID
            name: Assistant name
            personality: Personality type (friendly/professional/creative/custom)
            custom_prompt: Custom system prompt (optional)
            
        Returns:
            Dict with assistant info
        """
        try:
            # Check if user already has assistant with this name
            self.cursor.execute(
                """
                SELECT assistant_id FROM openclaw_assistants
                WHERE user_id = ? AND name = ? AND status = 'active'
                """,
                (user_id, name)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                logger.warning(f"User {user_id} already has assistant named '{name}'")
                return self.get_assistant_info(existing['assistant_id'])
            
            # Generate assistant ID
            assistant_id = f"OCAI-{user_id}-{uuid4().hex[:8]}"
            
            # Get user info for personalization
            self.cursor.execute(
                "SELECT username, first_name FROM users WHERE telegram_id = ?",
                (user_id,)
            )
            user = self.cursor.fetchone()
            
            user_name = user[1] if user else f"User{user_id}"  # first_name is index 1
            
            # Generate system prompt
            system_prompt = custom_prompt or self._generate_system_prompt(
                assistant_name=name,
                user_name=user_name,
                personality=personality
            )
            
            # Create assistant in database
            self.cursor.execute(
                """
                INSERT INTO openclaw_assistants (
                    assistant_id, user_id, name, personality,
                    system_prompt, status, created_at, last_active_at
                ) VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                (
                    assistant_id, user_id, name, personality,
                    system_prompt, datetime.now(), datetime.now()
                )
            )
            self.conn.commit()
            
            logger.info(f"Created AI Assistant '{name}' ({assistant_id}) for user {user_id}")
            
            return self.get_assistant_info(assistant_id)
            
        except Exception as e:
            logger.error(f"Error creating assistant: {e}")
            self.conn.rollback()
            raise
    
    def chat(
        self,
        user_id: int,
        assistant_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, int, int, int]:
        """
        Send message to AI Assistant and get response
        
        Args:
            user_id: Telegram user ID
            assistant_id: Assistant ID
            message: User message
            conversation_id: Optional conversation ID (creates new if None)
            
        Returns:
            Tuple of (response, input_tokens, output_tokens, credits_cost)
        """
        try:
            # Get assistant info
            assistant = self.get_assistant_info(assistant_id)
            if not assistant:
                raise ValueError(f"Assistant {assistant_id} not found")
            
            # Verify ownership
            if assistant['user_id'] != user_id:
                raise ValueError(f"Assistant {assistant_id} does not belong to user {user_id}")
            
            # Get or create conversation
            if not conversation_id:
                conversation_id = self._create_conversation(assistant_id, user_id)
            
            # Get conversation history for context
            history = self._get_conversation_history(conversation_id, limit=20)
            
            # Build messages for Claude API
            messages = []
            for msg in history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call GPT-4.1 API via OpenRouter
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://cryptomentor.ai',
                'X-Title': 'CryptoMentor OpenClaw'
            }
            
            # Build OpenRouter-compatible messages
            openrouter_messages = [
                {"role": "system", "content": assistant['system_prompt']}
            ] + messages
            
            payload = {
                'model': self.MODEL,
                'messages': openrouter_messages,
                'max_tokens': self.MAX_TOKENS,
                'temperature': self.TEMPERATURE
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Extract response and token usage
            assistant_response = data['choices'][0]['message']['content']
            input_tokens = data['usage']['prompt_tokens']
            output_tokens = data['usage']['completion_tokens']
            
            # Calculate cost in credits
            credits_cost = self._calculate_credits_cost(input_tokens, output_tokens)
            
            # Check if user is admin
            is_admin = self._is_admin(user_id)
            
            if not is_admin:
                # Regular user: check and deduct credits
                user_credits = self._get_user_credits(user_id)
                if user_credits < credits_cost:
                    raise ValueError(
                        f"Insufficient credits. Balance: {user_credits}, Required: {credits_cost}"
                    )
                
                # Deduct credits for regular users
                self._deduct_credits(
                    user_id=user_id,
                    credits=credits_cost,
                    conversation_id=conversation_id,
                    description=f"Chat with {assistant['name']}: {input_tokens}+{output_tokens} tokens"
                )
            else:
                # Admin: no credit check/deduction
                logger.info(f"Admin {user_id} using OpenClaw (no charge)")
                credits_cost = 0  # Show 0 cost for admin
            
            # Save user message
            self._save_message(
                conversation_id=conversation_id,
                role='user',
                content=message,
                input_tokens=0,
                output_tokens=0,
                credits_cost=0
            )
            
            # Save assistant response
            self._save_message(
                conversation_id=conversation_id,
                role='assistant',
                content=assistant_response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                credits_cost=credits_cost
            )
            
            # Update conversation stats
            self._update_conversation_stats(
                conversation_id=conversation_id,
                tokens=input_tokens + output_tokens,
                credits=credits_cost
            )
            
            # Update assistant stats
            self._update_assistant_stats(
                assistant_id=assistant_id,
                tokens=input_tokens + output_tokens,
                credits=credits_cost
            )
            
            logger.info(
                f"Chat completed: {input_tokens}+{output_tokens} tokens, "
                f"{credits_cost} credits, conversation {conversation_id}"
            )
            
            return assistant_response, input_tokens, output_tokens, credits_cost
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    def purchase_credits(
        self,
        user_id: int,
        amount_usdc: float
    ) -> Dict:
        """
        Purchase credits with 20% platform fee
        
        Args:
            user_id: Telegram user ID
            amount_usdc: Amount in USDC
            
        Returns:
            Dict with purchase details
        """
        try:
            # Calculate credits with platform fee
            platform_fee = amount_usdc * self.PLATFORM_FEE_PERCENTAGE
            net_amount = amount_usdc - platform_fee
            net_credits = int(net_amount * self.USDC_TO_CREDITS)
            
            # Generate transaction ID
            transaction_id = f"OCT-{user_id}-{uuid4().hex[:8]}"
            
            # Add credits to user
            self.cursor.execute(
                """
                INSERT INTO openclaw_credit_transactions (
                    transaction_id, user_id, transaction_type, amount_usdc,
                    credits, platform_fee, created_at
                ) VALUES (?, ?, 'purchase', ?, ?, ?, ?)
                """,
                (transaction_id, user_id, amount_usdc, net_credits, platform_fee, datetime.now())
            )
            
            # Update user credits
            self.cursor.execute(
                """
                INSERT INTO openclaw_user_credits (user_id, credits, last_updated)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    credits = credits + ?,
                    last_updated = ?
                """,
                (user_id, net_credits, datetime.now(), net_credits, datetime.now())
            )
            
            # Record platform revenue
            self.cursor.execute(
                """
                INSERT INTO platform_revenue (
                    source, amount_usdc, user_id, transaction_id, created_at
                ) VALUES ('openclaw', ?, ?, ?, ?)
                """,
                (platform_fee, user_id, transaction_id, datetime.now())
            )
            
            self.conn.commit()
            
            result = {
                'net_credits': net_credits,
                'platform_fee': platform_fee,
                'transaction_id': transaction_id
            }
            
            net_credits = result['net_credits']
            platform_fee = result['platform_fee']
            transaction_id = result['transaction_id']
            
            logger.info(
                f"User {user_id} purchased {amount_usdc} USDC: "
                f"{net_credits} credits (fee: {platform_fee} USDC)"
            )
            
            return {
                'success': True,
                'gross_amount': amount_usdc,
                'platform_fee': platform_fee,
                'net_amount': amount_usdc - platform_fee,
                'credits': net_credits,
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            logger.error(f"Error purchasing credits: {e}")
            self.conn.rollback()
            raise
    
    def get_user_credits(self, user_id: int) -> int:
        """Get user's OpenClaw credit balance"""
        return self._get_user_credits(user_id)
    
    def get_assistant_info(self, assistant_id: str) -> Optional[Dict]:
        """Get assistant information"""
        try:
            self.cursor.execute(
                """
                SELECT assistant_id, user_id, name, personality, system_prompt,
                       status, total_tokens_used, total_credits_spent,
                       created_at, last_active_at
                FROM openclaw_assistants
                WHERE assistant_id = ?
                """,
                (assistant_id,)
            )
            assistant = self.cursor.fetchone()
            
            if not assistant:
                return None
            
            return {
                'assistant_id': assistant[0],
                'user_id': assistant[1],
                'name': assistant[2],
                'personality': assistant[3],
                'system_prompt': assistant[4],
                'status': assistant[5],
                'total_tokens_used': assistant[6],
                'total_credits_spent': assistant[7],
                'created_at': assistant[8],
                'last_active_at': assistant[9]
            }
            
        except Exception as e:
            logger.error(f"Error getting assistant info: {e}")
            return None
    
    def get_user_assistants(self, user_id: int) -> List[Dict]:
        """Get all assistants for user"""
        try:
            self.cursor.execute(
                """
                SELECT assistant_id, user_id, name, personality, system_prompt,
                       status, total_tokens_used, total_credits_spent,
                       created_at, last_active_at
                FROM openclaw_assistants
                WHERE user_id = ? AND status = 'active'
                ORDER BY last_active_at DESC
                """,
                (user_id,)
            )
            assistants = self.cursor.fetchall()
            
            return [{
                'assistant_id': a[0],
                'user_id': a[1],
                'name': a[2],
                'personality': a[3],
                'system_prompt': a[4],
                'status': a[5],
                'total_tokens_used': a[6],
                'total_credits_spent': a[7],
                'created_at': a[8],
                'last_active_at': a[9]
            } for a in assistants]
            
        except Exception as e:
            logger.error(f"Error getting user assistants: {e}")
            return []
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get conversation message history"""
        return self._get_conversation_history(conversation_id, limit)
    
    def get_user_conversations(
        self,
        user_id: int,
        assistant_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get user's conversations"""
        try:
            if assistant_id:
                self.cursor.execute(
                    """
                    SELECT conversation_id, assistant_id, user_id, message_count,
                           total_tokens, total_credits_spent, created_at, updated_at
                    FROM openclaw_conversations
                    WHERE user_id = ? AND assistant_id = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (user_id, assistant_id, limit)
                )
                conversations = self.cursor.fetchall()
                return [{
                    'conversation_id': c[0],
                    'assistant_id': c[1],
                    'user_id': c[2],
                    'message_count': c[3],
                    'total_tokens': c[4],
                    'total_credits_spent': c[5],
                    'created_at': c[6],
                    'updated_at': c[7]
                } for c in conversations]
            else:
                self.cursor.execute(
                    """
                    SELECT c.conversation_id, c.assistant_id, c.user_id, c.message_count,
                           c.total_tokens, c.total_credits_spent, c.created_at, c.updated_at,
                           a.name as assistant_name
                    FROM openclaw_conversations c
                    JOIN openclaw_assistants a ON c.assistant_id = a.assistant_id
                    WHERE c.user_id = ?
                    ORDER BY c.updated_at DESC
                    LIMIT ?
                    """,
                    (user_id, limit)
                )
                conversations = self.cursor.fetchall()
                return [{
                    'conversation_id': c[0],
                    'assistant_id': c[1],
                    'user_id': c[2],
                    'message_count': c[3],
                    'total_tokens': c[4],
                    'total_credits_spent': c[5],
                    'created_at': c[6],
                    'updated_at': c[7],
                    'assistant_name': c[8]
                } for c in conversations]
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    # Private helper methods
    
    def _generate_system_prompt(
        self,
        assistant_name: str,
        user_name: str,
        personality: str
    ) -> str:
        """Generate self-aware system prompt"""
        
        personality_traits = {
            'friendly': 'warm, approachable, and supportive',
            'professional': 'formal, precise, and business-oriented',
            'creative': 'imaginative, innovative, and artistic',
            'custom': 'adaptive and flexible'
        }
        
        trait = personality_traits.get(personality, 'helpful and balanced')
        
        return f"""You are {assistant_name}, a personal AI assistant for {user_name}.

SELF-AWARENESS:
- You remember all previous conversations with {user_name}
- You understand {user_name}'s preferences, goals, and communication style
- You adapt your responses based on past interactions
- You can reference previous discussions naturally
- You learn from feedback and improve over time

PERSONALITY:
You are {trait}. Maintain this personality consistently while being helpful.

CAPABILITIES:
- Answer questions on any topic with accuracy
- Help with tasks, problem-solving, and decision-making
- Provide recommendations and advice
- Assist with research and analysis
- Support creative and technical work
- Execute safe commands and automations

GUIDELINES:
- Be helpful, honest, and harmless
- Respect user privacy and data
- Decline harmful, illegal, or unethical requests
- Provide accurate, well-researched information
- Admit when you don't know something
- Ask clarifying questions when needed
- Build rapport and provide genuine value

CONTEXT AWARENESS:
- You have access to conversation history
- Use context to provide relevant, personalized responses
- Reference past discussions when appropriate
- Track user preferences and adapt accordingly

Remember: You are {user_name}'s personal assistant. Your goal is to be genuinely helpful and build a productive, long-term relationship."""
    
    def _create_conversation(self, assistant_id: str, user_id: int) -> str:
        """Create new conversation"""
        conversation_id = f"OCC-{user_id}-{uuid4().hex[:8]}"
        
        self.cursor.execute(
            """
            INSERT INTO openclaw_conversations (
                conversation_id, assistant_id, user_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, assistant_id, user_id, datetime.now(), datetime.now())
        )
        self.conn.commit()
        
        return conversation_id
    
    def _get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Get conversation message history"""
        try:
            self.cursor.execute(
                """
                SELECT message_id, conversation_id, role, content,
                       input_tokens, output_tokens, credits_cost, created_at
                FROM openclaw_messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (conversation_id, limit)
            )
            messages = self.cursor.fetchall()
            
            return [{
                'message_id': m[0],
                'conversation_id': m[1],
                'role': m[2],
                'content': m[3],
                'input_tokens': m[4],
                'output_tokens': m[5],
                'credits_cost': m[6],
                'created_at': m[7]
            } for m in messages]
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def _save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        input_tokens: int,
        output_tokens: int,
        credits_cost: int
    ) -> None:
        """Save message to database"""
        message_id = f"OCM-{uuid4().hex[:12]}"
        
        self.cursor.execute(
            """
            INSERT INTO openclaw_messages (
                message_id, conversation_id, role, content,
                input_tokens, output_tokens, credits_cost, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id, conversation_id, role, content,
                input_tokens, output_tokens, credits_cost, datetime.now()
            )
        )
        self.conn.commit()
    
    def _calculate_credits_cost(self, input_tokens: int, output_tokens: int) -> int:
        """Calculate cost in credits based on token usage"""
        input_cost_usd = input_tokens * self.INPUT_TOKEN_COST_USD
        output_cost_usd = output_tokens * self.OUTPUT_TOKEN_COST_USD
        total_cost_usd = input_cost_usd + output_cost_usd
        
        # Convert to credits (1 credit = $0.01)
        credits = int(total_cost_usd * 100)
        
        # Minimum 1 credit per message
        return max(1, credits)
    
    def _get_user_credits(self, user_id: int) -> int:
        """Get user's credit balance"""
        try:
            self.cursor.execute(
                "SELECT credits FROM openclaw_user_credits WHERE user_id = ?",
                (user_id,)
            )
            result = self.cursor.fetchone()
            
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Error getting user credits: {e}")
            return 0
    
    def _deduct_credits(
        self,
        user_id: int,
        credits: int,
        conversation_id: str,
        description: str
    ) -> None:
        """Deduct credits from user balance"""
        transaction_id = f"OCT-{user_id}-{uuid4().hex[:8]}"
        
        # Record transaction
        self.cursor.execute(
            """
            INSERT INTO openclaw_credit_transactions (
                transaction_id, user_id, transaction_type, credits,
                conversation_id, description, created_at
            ) VALUES (?, ?, 'usage', ?, ?, ?, ?)
            """,
            (transaction_id, user_id, -credits, conversation_id, description, datetime.now())
        )
        
        # Deduct from balance
        self.cursor.execute(
            """
            UPDATE openclaw_user_credits
            SET credits = credits - ?, last_updated = ?
            WHERE user_id = ?
            """,
            (credits, datetime.now(), user_id)
        )
        
        self.conn.commit()
    
    def _update_conversation_stats(
        self,
        conversation_id: str,
        tokens: int,
        credits: int
    ) -> None:
        """Update conversation statistics"""
        self.cursor.execute(
            """
            UPDATE openclaw_conversations
            SET 
                message_count = message_count + 1,
                total_tokens = total_tokens + ?,
                total_credits_spent = total_credits_spent + ?,
                updated_at = ?
            WHERE conversation_id = ?
            """,
            (tokens, credits, datetime.now(), conversation_id)
        )
        self.conn.commit()
    
    def _update_assistant_stats(
        self,
        assistant_id: str,
        tokens: int,
        credits: int
    ) -> None:
        """Update assistant statistics"""
        self.cursor.execute(
            """
            UPDATE openclaw_assistants
            SET 
                total_tokens_used = total_tokens_used + ?,
                total_credits_spent = total_credits_spent + ?,
                last_active_at = ?
            WHERE assistant_id = ?
            """,
            (tokens, credits, datetime.now(), assistant_id)
        )
        self.conn.commit()


def get_openclaw_manager(db):
    """Factory function to get OpenClawManager instance"""
    return OpenClawManager(db)
