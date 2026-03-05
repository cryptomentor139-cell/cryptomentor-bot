"""
OpenClaw Simple LangChain Agent
Simplified implementation without complex agent framework
"""

import os
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
import httpx

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory

from app.openclaw_langchain_db import get_openclaw_db

logger = logging.getLogger(__name__)


class OpenClawSimpleAgent:
    """
    Simplified OpenClaw AI Agent
    Direct LLM calls with manual tool handling
    """
    
    def __init__(self):
        """Initialize OpenClaw agent"""
        
        # Get database instance
        self.db = get_openclaw_db()
        
        # Initialize LLM (via OpenRouter)
        api_key = os.getenv('OPENCLAW_API_KEY')
        if not api_key:
            raise ValueError("OPENCLAW_API_KEY not found in environment")
        
        self.llm = ChatOpenAI(
            model="openai/gpt-4.1",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=2000,
            default_headers={
                "HTTP-Referer": "https://github.com/cryptomentor-bot",
                "X-Title": "CryptoMentor OpenClaw"
            }
        )
        
        logger.info("OpenClaw Simple Agent initialized successfully")
    
    def get_system_prompt(self) -> str:
        """Get system prompt"""
        return """You are OpenClaw, an advanced AI crypto analyst and assistant.

Your capabilities:
- Analyze cryptocurrency markets and provide insights
- Check user credit balances
- Provide trading signals and market analysis
- Answer questions about crypto, blockchain, and trading

Guidelines:
- Be professional, helpful, and accurate
- Provide real-time data when possible
- Explain your analysis clearly
- Warn about risks when discussing trading
- Be concise but informative

When users ask about prices, provide current market data.
When users ask for analysis, give detailed insights.
Always provide value and actionable information."""
    
    def get_crypto_price(self, symbol: str) -> str:
        """Get crypto price from CoinGecko"""
        try:
            # Normalize symbol
            symbol = symbol.lower().strip()
            
            # Map common symbols
            symbol_map = {
                'btc': 'bitcoin',
                'eth': 'ethereum',
                'bnb': 'binancecoin',
                'sol': 'solana',
                'ada': 'cardano',
                'xrp': 'ripple',
                'dot': 'polkadot',
                'doge': 'dogecoin',
                'avax': 'avalanche-2',
                'matic': 'matic-network'
            }
            
            coin_id = symbol_map.get(symbol, symbol)
            
            # Fetch price from CoinGecko
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            response = httpx.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                
                if coin_id in data:
                    price_data = data[coin_id]
                    price = price_data.get('usd', 0)
                    change_24h = price_data.get('usd_24h_change', 0)
                    market_cap = price_data.get('usd_market_cap', 0)
                    
                    result = f"{symbol.upper()} Price: ${price:,.2f}\n"
                    result += f"24h Change: {change_24h:+.2f}%\n"
                    
                    if market_cap:
                        result += f"Market Cap: ${market_cap:,.0f}"
                    
                    return result
                else:
                    return f"Cryptocurrency '{symbol}' not found"
            else:
                return f"Error fetching price data"
        
        except Exception as e:
            logger.error(f"Error getting crypto price: {e}")
            return f"Error getting price: {str(e)}"
    
    def get_user_history(self, user_id: int) -> SQLChatMessageHistory:
        """Get conversation history for user"""
        return self.db.get_user_history(user_id)
    
    async def chat(
        self,
        user_id: int,
        message: str,
        deduct_credits: bool = True
    ) -> Dict[str, Any]:
        """
        Process user message
        
        Args:
            user_id: Telegram user ID
            message: User message
            deduct_credits: Whether to deduct credits
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Check credits if needed
            if deduct_credits:
                credits = self.db.get_user_credits(user_id)
                if credits <= 0:
                    return {
                        'success': False,
                        'response': "❌ Insufficient credits. Please contact admin to add credits.",
                        'credits_used': 0
                    }
            
            # Get conversation history
            history = self.get_user_history(user_id)
            
            # Check if message is about crypto price
            message_lower = message.lower()
            price_keywords = ['price', 'cost', 'value', 'worth', 'how much']
            crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'coin']
            
            # If asking about price, get real-time data
            price_context = ""
            if any(kw in message_lower for kw in price_keywords):
                for crypto in ['bitcoin', 'ethereum', 'btc', 'eth']:
                    if crypto in message_lower:
                        price_data = self.get_crypto_price(crypto)
                        price_context = f"\n\nCurrent Market Data:\n{price_data}\n"
                        break
            
            # Build messages
            messages = [
                SystemMessage(content=self.get_system_prompt())
            ]
            
            # Add history (last 10 messages)
            for msg in history.messages[-10:]:
                messages.append(msg)
            
            # Add current message with price context if available
            user_message = message
            if price_context:
                user_message += price_context
            
            messages.append(HumanMessage(content=user_message))
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            response_text = response.content
            
            # Save to history
            history.add_user_message(message)
            history.add_ai_message(response_text)
            
            # Deduct credits (estimate $0.02 per message)
            credits_used = Decimal('0.02')
            
            if deduct_credits:
                deduct_result = self.db.deduct_credits(
                    user_id=user_id,
                    amount=credits_used,
                    reason=f"OpenClaw chat: {message[:50]}"
                )
                
                if not deduct_result['success']:
                    logger.warning(f"Failed to deduct credits for user {user_id}: {deduct_result.get('error')}")
            
            logger.info(f"User {user_id} chat processed. Credits used: ${credits_used:.4f}")
            
            return {
                'success': True,
                'response': response_text,
                'credits_used': float(credits_used)
            }
        
        except Exception as e:
            logger.error(f"Error in agent chat: {e}", exc_info=True)
            return {
                'success': False,
                'response': "I apologize, but I encountered an error. Please try again or contact support.",
                'error': str(e),
                'credits_used': 0
            }


# Global agent instance
_agent_instance: Optional[OpenClawSimpleAgent] = None


def get_openclaw_agent() -> OpenClawSimpleAgent:
    """
    Get global OpenClaw agent instance
    
    Returns:
        OpenClawSimpleAgent instance
    """
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = OpenClawSimpleAgent()
    
    return _agent_instance
