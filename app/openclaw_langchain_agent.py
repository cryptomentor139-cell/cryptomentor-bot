"""
OpenClaw LangChain Agent
AI agent with tool calling for crypto analysis and credit management
"""

import os
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationBufferMemory

from app.openclaw_langchain_db import get_openclaw_db

logger = logging.getLogger(__name__)


class OpenClawAgent:
    """
    LangChain-powered OpenClaw AI Agent
    Handles crypto analysis, credit management, and user interactions
    """
    
    def __init__(self):
        """Initialize OpenClaw agent with tools and memory"""
        
        # Get database instance
        self.db = get_openclaw_db()
        
        # Initialize LLM (via OpenRouter)
        api_key = os.getenv('OPENCLAW_API_KEY')
        if not api_key:
            raise ValueError("OPENCLAW_API_KEY not found in environment")
        
        self.llm = ChatAnthropic(
            model="openai/gpt-4.1",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=2000
        )
        
        # Define tools
        self.tools = self._create_tools()
        
        # Create prompt
        self.prompt = self._create_prompt()
        
        # Create agent
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
        
        logger.info("OpenClaw LangChain agent initialized successfully")
    
    def _create_tools(self) -> List[Tool]:
        """Create agent tools"""
        
        return [
            Tool(
                name="check_balance",
                func=self._check_balance,
                description=(
                    "Check user's credit balance. "
                    "Use when user asks about their balance, credits, or how much they have. "
                    "Input: user_id (integer)"
                )
            ),
            Tool(
                name="get_crypto_price",
                func=self._get_crypto_price,
                description=(
                    "Get current cryptocurrency price from CoinGecko. "
                    "Use when user asks about price, value, or market data. "
                    "Input: crypto symbol (e.g., 'bitcoin', 'ethereum', 'btc', 'eth')"
                )
            ),
            Tool(
                name="analyze_market",
                func=self._analyze_market,
                description=(
                    "Provide market analysis and insights for a cryptocurrency. "
                    "Use when user asks for analysis, trends, or market insights. "
                    "Input: crypto symbol"
                )
            ),
            Tool(
                name="get_system_stats",
                func=self._get_system_stats,
                description=(
                    "Get system-wide statistics (admin only). "
                    "Shows total users, credits allocated, and usage. "
                    "Input: none"
                )
            )
        ]
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create agent prompt template"""
        
        system_message = """You are OpenClaw, an advanced AI crypto analyst and assistant.

Your capabilities:
- Analyze cryptocurrency markets and provide insights
- Check user credit balances
- Provide trading signals and market analysis
- Answer questions about crypto, blockchain, and trading

Guidelines:
- Be professional, helpful, and accurate
- Use tools when needed to get real-time data
- Explain your analysis clearly
- Warn about risks when discussing trading
- Be concise but informative

When users ask about their balance or credits, use the check_balance tool.
When users ask about crypto prices, use the get_crypto_price tool.
When users ask for analysis, use the analyze_market tool.

Always provide value and actionable insights."""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def _check_balance(self, user_id: str) -> str:
        """Tool: Check user balance"""
        try:
            user_id_int = int(user_id)
            credits = self.db.get_user_credits(user_id_int)
            
            return f"Your current balance: ${credits:.2f} USD credits"
        
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return f"Error checking balance: {str(e)}"
    
    def _get_crypto_price(self, symbol: str) -> str:
        """Tool: Get crypto price from CoinGecko"""
        try:
            import httpx
            
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
                    return f"Cryptocurrency '{symbol}' not found. Try using full name (e.g., 'bitcoin' instead of 'btc')"
            else:
                return f"Error fetching price data (status: {response.status_code})"
        
        except Exception as e:
            logger.error(f"Error getting crypto price: {e}")
            return f"Error getting price: {str(e)}"
    
    def _analyze_market(self, symbol: str) -> str:
        """Tool: Provide market analysis"""
        try:
            # Get current price first
            price_info = self._get_crypto_price(symbol)
            
            # Add analysis context
            analysis = f"Market Analysis for {symbol.upper()}:\n\n"
            analysis += price_info + "\n\n"
            analysis += "Analysis: Based on current market data, "
            
            # Simple trend analysis based on 24h change
            if "24h Change:" in price_info:
                if "+%" in price_info:
                    analysis += "the market shows bullish momentum. "
                elif "-%" in price_info:
                    analysis += "the market shows bearish pressure. "
                else:
                    analysis += "the market is relatively stable. "
            
            analysis += "\n\nNote: This is a basic analysis. For detailed technical analysis, consider multiple timeframes and indicators."
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
            return f"Error analyzing market: {str(e)}"
    
    def _get_system_stats(self, _: str = "") -> str:
        """Tool: Get system statistics"""
        try:
            stats = self.db.get_system_stats()
            
            result = "OpenClaw System Statistics:\n\n"
            result += f"Total Users: {stats['user_count']}\n"
            result += f"Total Credits: ${stats['total_credits']:.2f}\n"
            result += f"Total Allocated: ${stats['total_allocated']:.2f}\n"
            result += f"Total Used: ${stats['total_used']:.2f}\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return f"Error getting stats: {str(e)}"
    
    def get_memory(self, user_id: int) -> ConversationBufferMemory:
        """
        Get conversation memory for user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            ConversationBufferMemory instance
        """
        return ConversationBufferMemory(
            chat_memory=self.db.get_user_history(user_id),
            return_messages=True,
            memory_key="chat_history",
            input_key="input",
            output_key="output"
        )
    
    async def chat(
        self,
        user_id: int,
        message: str,
        deduct_credits: bool = True
    ) -> Dict[str, Any]:
        """
        Process user message with agent
        
        Args:
            user_id: Telegram user ID
            message: User message
            deduct_credits: Whether to deduct credits for this message
            
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
            
            # Get memory
            memory = self.get_memory(user_id)
            
            # Invoke agent
            result = await self.executor.ainvoke({
                "input": message,
                "chat_history": memory.chat_memory.messages
            })
            
            response = result.get("output", "I apologize, but I couldn't process your request.")
            
            # Deduct credits (estimate $0.01-0.05 per message)
            credits_used = Decimal('0.02')  # Default cost
            
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
                'response': response,
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
_agent_instance: Optional[OpenClawAgent] = None


def get_openclaw_agent() -> OpenClawAgent:
    """
    Get global OpenClaw agent instance
    
    Returns:
        OpenClawAgent instance
    """
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = OpenClawAgent()
    
    return _agent_instance
