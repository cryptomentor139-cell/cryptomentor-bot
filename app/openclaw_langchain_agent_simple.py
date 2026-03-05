"""
OpenClaw Simple LangChain Agent with Function Calling
Real-time crypto data integration
"""

import os
import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
import httpx
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.chat_message_histories import SQLChatMessageHistory

from app.openclaw_langchain_db import get_openclaw_db

logger = logging.getLogger(__name__)


# Define tools for LLM
@tool
def get_crypto_price(symbol: str) -> str:
    """
    Get current cryptocurrency price and market data.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL', 'BNB')
    
    Returns:
        Current price, 24h change, and market cap
    """
    try:
        # Normalize symbol
        symbol = symbol.upper().strip()
        
        # Map common symbols to CoinGecko IDs
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'NEAR': 'near',
            'APT': 'aptos',
            'ARB': 'arbitrum',
            'OP': 'optimism'
        }
        
        coin_id = symbol_map.get(symbol, symbol.lower())
        
        # Fetch from CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        response = httpx.get(url, params=params, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            
            if coin_id in data:
                price_data = data[coin_id]
                price = price_data.get('usd', 0)
                change_24h = price_data.get('usd_24h_change', 0)
                volume_24h = price_data.get('usd_24h_vol', 0)
                market_cap = price_data.get('usd_market_cap', 0)
                
                result = f"💰 {symbol} Market Data:\n"
                result += f"Price: ${price:,.2f}\n"
                result += f"24h Change: {change_24h:+.2f}%\n"
                result += f"24h Volume: ${volume_24h:,.0f}\n"
                
                if market_cap:
                    result += f"Market Cap: ${market_cap:,.0f}"
                
                return result
            else:
                return f"❌ Cryptocurrency '{symbol}' not found"
        else:
            return f"❌ Error fetching price data (Status: {response.status_code})"
    
    except Exception as e:
        logger.error(f"Error getting crypto price: {e}")
        return f"❌ Error: {str(e)}"


@tool
def get_binance_price(symbol: str) -> str:
    """
    Get real-time price from Binance exchange.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
    
    Returns:
        Current price and 24h statistics from Binance
    """
    try:
        # Normalize symbol
        symbol = symbol.upper().strip()
        
        # Add USDT if not present
        if not symbol.endswith('USDT'):
            symbol = f"{symbol}USDT"
        
        # Fetch from Binance
        url = f"https://api.binance.com/api/v3/ticker/24hr"
        params = {'symbol': symbol}
        
        response = httpx.get(url, params=params, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            
            price = float(data['lastPrice'])
            change = float(data['priceChangePercent'])
            high = float(data['highPrice'])
            low = float(data['lowPrice'])
            volume = float(data['volume'])
            
            result = f"📊 {symbol} Binance Data:\n"
            result += f"Price: ${price:,.2f}\n"
            result += f"24h Change: {change:+.2f}%\n"
            result += f"24h High: ${high:,.2f}\n"
            result += f"24h Low: ${low:,.2f}\n"
            result += f"24h Volume: {volume:,.2f}"
            
            return result
        else:
            return f"❌ Symbol '{symbol}' not found on Binance"
    
    except Exception as e:
        logger.error(f"Error getting Binance price: {e}")
        return f"❌ Error: {str(e)}"


@tool
def get_multiple_crypto_prices(symbols: List[str]) -> str:
    """
    Get prices for multiple cryptocurrencies at once.
    
    Args:
        symbols: List of crypto symbols (e.g., ['BTC', 'ETH', 'SOL'])
    
    Returns:
        Prices for all requested cryptocurrencies
    """
    try:
        # Map symbols to CoinGecko IDs
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network'
        }
        
        # Convert symbols to coin IDs
        coin_ids = []
        for sym in symbols:
            sym_upper = sym.upper().strip()
            coin_id = symbol_map.get(sym_upper, sym.lower())
            coin_ids.append(coin_id)
        
        # Fetch from CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = httpx.get(url, params=params, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            
            result = "💰 Crypto Market Overview:\n\n"
            
            for i, coin_id in enumerate(coin_ids):
                if coin_id in data:
                    price_data = data[coin_id]
                    price = price_data.get('usd', 0)
                    change = price_data.get('usd_24h_change', 0)
                    
                    symbol = symbols[i].upper()
                    result += f"{symbol}: ${price:,.2f} ({change:+.2f}%)\n"
            
            return result
        else:
            return f"❌ Error fetching prices"
    
    except Exception as e:
        logger.error(f"Error getting multiple prices: {e}")
        return f"❌ Error: {str(e)}"


@tool
def check_user_balance(user_id: int) -> str:
    """
    Check a user's credit balance (admin tool).
    
    Args:
        user_id: Telegram user ID to check
    
    Returns:
        User's current credit balance
    """
    try:
        from app.openclaw_langchain_db import get_openclaw_db
        db = get_openclaw_db()
        credits = db.get_user_credits(user_id)
        
        return f"User {user_id} balance: ${credits:.2f} USD credits"
    
    except Exception as e:
        logger.error(f"Error checking user balance: {e}")
        return f"❌ Error: {str(e)}"


@tool
def get_system_statistics() -> str:
    """
    Get OpenClaw system statistics (admin only).
    
    Returns:
        System-wide statistics including total users, credits, and usage
    """
    try:
        from app.openclaw_langchain_db import get_openclaw_db
        db = get_openclaw_db()
        stats = db.get_system_stats()
        
        result = "📊 OpenClaw System Statistics:\n\n"
        result += f"Total Users: {stats['user_count']}\n"
        result += f"Total Credits: ${stats['total_credits']:.2f}\n"
        result += f"Total Allocated: ${stats['total_allocated']:.2f}\n"
        result += f"Total Used: ${stats['total_used']:.2f}\n"
        
        if stats['user_count'] > 0:
            avg = stats['total_credits'] / stats['user_count']
            result += f"Average per User: ${avg:.2f}"
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return f"❌ Error: {str(e)}"


class OpenClawSimpleAgent:
    """
    Simplified OpenClaw AI Agent with function calling
    """
    
    def __init__(self):
        """Initialize OpenClaw agent"""
        
        # Get database instance
        self.db = get_openclaw_db()
        
        # Initialize LLM (via OpenRouter) with function calling
        api_key = os.getenv('OPENCLAW_API_KEY')
        if not api_key:
            raise ValueError("OPENCLAW_API_KEY not found in environment")
        
        # Define base tools (available to all users)
        self.base_tools = [
            get_crypto_price,
            get_binance_price,
            get_multiple_crypto_prices
        ]
        
        # Define admin tools (only for admins)
        self.admin_tools = [
            check_user_balance,
            get_system_statistics
        ]
        
        # All tools combined
        self.all_tools = self.base_tools + self.admin_tools
        
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
        
        logger.info("OpenClaw Simple Agent initialized with function calling")
    
    def get_llm_with_tools(self, is_admin: bool = False):
        """Get LLM with appropriate tools based on user role"""
        if is_admin:
            # Admin gets all tools
            return self.llm.bind_tools(self.all_tools)
        else:
            # Regular users get base tools only
            return self.llm.bind_tools(self.base_tools)
    
    def get_system_prompt(self, is_admin: bool = False) -> str:
        """Get system prompt"""
        admin_context = ""
        if is_admin:
            admin_context = """

🔑 ADMIN MODE ACTIVE:
- You are interacting with a SYSTEM ADMINISTRATOR
- This user has UNLIMITED CREDITS and FULL ACCESS to all features
- No credit checks or limitations apply to this user
- You can provide extended analysis and unlimited responses
- Admin has access to all system commands and features
"""
        
        return f"""You are OpenClaw, an advanced AI crypto analyst and assistant.

Your capabilities:
- Analyze cryptocurrency markets with REAL-TIME data
- Check user credit balances
- Provide trading signals and market analysis
- Answer questions about crypto, blockchain, and trading

IMPORTANT: When users ask about crypto prices or market data:
1. ALWAYS use the get_crypto_price() function to get real-time data
2. Use get_binance_price() for exchange-specific data
3. Use get_multiple_crypto_prices() when comparing multiple coins
4. NEVER make up or guess prices - always fetch real data

Guidelines:
- Be professional, helpful, and accurate
- Provide real-time data when possible
- Explain your analysis clearly
- Warn about risks when discussing trading
- Be concise but informative{admin_context}

Example responses:
- "Let me check the current BTC price..." → call get_crypto_price("BTC")
- "I'll get the latest market data..." → call appropriate function
- Always show the data you fetched in your response"""
    
    def get_user_history(self, user_id: int) -> SQLChatMessageHistory:
        """Get conversation history for user"""
        return self.db.get_user_history(user_id)
    
    async def chat(
        self,
        user_id: int,
        message: str,
        deduct_credits: bool = True,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Process user message with function calling
        
        Args:
            user_id: Telegram user ID
            message: User message
            deduct_credits: Whether to deduct credits
            is_admin: Whether user is admin (unlimited credits)
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Admin bypass: no credit check for admins
            if not is_admin and deduct_credits:
                credits = self.db.get_user_credits(user_id)
                if credits <= 0:
                    return {
                        'success': False,
                        'response': "❌ Insufficient credits. Please contact admin to add credits.",
                        'credits_used': 0
                    }
            
            # Get conversation history
            history = self.get_user_history(user_id)
            
            # Build messages with admin-aware system prompt
            messages = [
                SystemMessage(content=self.get_system_prompt(is_admin=is_admin))
            ]
            
            # Add history (last 10 messages)
            for msg in history.messages[-10:]:
                messages.append(msg)
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Get LLM with appropriate tools based on admin status
            llm_with_tools = self.get_llm_with_tools(is_admin=is_admin)
            
            # Get response from LLM with tools
            response = await llm_with_tools.ainvoke(messages)
            
            # Check if LLM wants to call tools
            if response.tool_calls:
                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    logger.info(f"Calling tool: {tool_name} with args: {tool_args}")
                    
                    # Find and execute the tool
                    tool_result = None
                    available_tools = self.all_tools if is_admin else self.base_tools
                    
                    for tool in available_tools:
                        if tool.name == tool_name:
                            tool_result = tool.invoke(tool_args)
                            break
                    
                    if tool_result is None:
                        tool_result = f"❌ Tool '{tool_name}' not available or not authorized"
                    
                    # Add tool response to messages
                    messages.append(response)
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id']
                    ))
                
                # Get final response after tool execution
                final_response = await self.llm.ainvoke(messages)
                response_text = final_response.content
            else:
                response_text = response.content
            
            # Save to history
            history.add_user_message(message)
            history.add_ai_message(response_text)
            
            # Deduct credits (estimate $0.02 per message)
            # Admin bypass: no credit deduction for admins
            credits_used = Decimal('0.02')
            
            if not is_admin and deduct_credits:
                deduct_result = self.db.deduct_credits(
                    user_id=user_id,
                    amount=credits_used,
                    reason=f"OpenClaw chat: {message[:50]}"
                )
                
                if not deduct_result['success']:
                    logger.warning(f"Failed to deduct credits for user {user_id}: {deduct_result.get('error')}")
            elif is_admin:
                logger.info(f"Admin {user_id} chat processed. No credits deducted (admin privilege)")
                credits_used = Decimal('0')  # No cost for admin
            
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
