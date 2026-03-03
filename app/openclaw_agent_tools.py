"""
OpenClaw Agent Tools - Function Calling Implementation
Enables AI to execute actions autonomously
"""

import os
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class OpenClawAgentTools:
    """
    Tool registry and executor for OpenClaw autonomous agent
    Implements function calling for AI to execute actions
    """
    
    def __init__(self, db, telegram_app=None):
        """
        Initialize agent tools
        
        Args:
            db: Database instance
            telegram_app: Telegram application instance (for sending messages)
        """
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor
        self.telegram_app = telegram_app
        
        # Tool registry
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all available tools"""
        
        # Admin tools
        self._register_tool(
            name="get_bot_stats",
            description="Get bot statistics including user counts, revenue, and activity",
            parameters={},
            function=self.get_bot_stats
        )
        
        self._register_tool(
            name="get_current_prices",
            description="Get current subscription and credit prices",
            parameters={},
            function=self.get_current_prices
        )
        
        self._register_tool(
            name="update_price",
            description="Update a price in the system",
            parameters={
                "price_type": {
                    "type": "string",
                    "description": "Type of price (premium_monthly, premium_yearly, openclaw_credits, platform_fee)",
                    "required": True
                },
                "new_value": {
                    "type": "number",
                    "description": "New price value",
                    "required": True
                }
            },
            function=self.update_price
        )
        
        self._register_tool(
            name="broadcast_message",
            description="Send a broadcast message to all users or specific user groups",
            parameters={
                "message": {
                    "type": "string",
                    "description": "Message to broadcast",
                    "required": True
                },
                "target": {
                    "type": "string",
                    "description": "Target audience: 'all', 'premium', 'free', or 'openclaw'",
                    "required": False,
                    "default": "all"
                }
            },
            function=self.broadcast_message
        )
        
        self._register_tool(
            name="generate_deposit_wallet",
            description="Generate a unique deposit wallet address for a user",
            parameters={
                "user_id": {
                    "type": "integer",
                    "description": "Telegram user ID",
                    "required": True
                },
                "network": {
                    "type": "string",
                    "description": "Blockchain network (SOL, ETH, BNB)",
                    "required": False,
                    "default": "SOL"
                }
            },
            function=self.generate_deposit_wallet
        )
        
        self._register_tool(
            name="get_user_info",
            description="Get detailed information about a user",
            parameters={
                "user_id": {
                    "type": "integer",
                    "description": "Telegram user ID",
                    "required": True
                }
            },
            function=self.get_user_info
        )
        
        self._register_tool(
            name="add_credits",
            description="Add OpenClaw credits to a user account",
            parameters={
                "user_id": {
                    "type": "integer",
                    "description": "Telegram user ID",
                    "required": True
                },
                "credits": {
                    "type": "integer",
                    "description": "Number of credits to add",
                    "required": True
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for adding credits",
                    "required": False,
                    "default": "Admin grant"
                }
            },
            function=self.add_credits
        )
        
        self._register_tool(
            name="execute_sql_query",
            description="Execute a SQL query (SELECT only for safety)",
            parameters={
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT statements only)",
                    "required": True
                }
            },
            function=self.execute_sql_query
        )
        
        self._register_tool(
            name="get_system_info",
            description="Get system information including git status and deployment info",
            parameters={},
            function=self.get_system_info
        )
    
    def _register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable
    ):
        """Register a tool in the registry"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": function
        }
        logger.info(f"Registered tool: {name}")
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible tools schema for function calling
        
        Returns:
            List of tool definitions
        """
        tools_schema = []
        
        for tool_name, tool_info in self.tools.items():
            # Convert to OpenAI function calling format
            properties = {}
            required = []
            
            for param_name, param_info in tool_info["parameters"].items():
                properties[param_name] = {
                    "type": param_info["type"],
                    "description": param_info["description"]
                }
                
                if param_info.get("default"):
                    properties[param_name]["default"] = param_info["default"]
                
                if param_info.get("required", False):
                    required.append(param_name)
            
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            
            tools_schema.append(tool_schema)
        
        return tools_schema
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            tool = self.tools[tool_name]
            function = tool["function"]
            
            # Execute the tool
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            result = function(**arguments)
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== TOOL IMPLEMENTATIONS ====================
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        try:
            stats = {}
            
            # Total users
            self.cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = self.cursor.fetchone()[0]
            
            # Premium users
            self.cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE is_premium = TRUE AND premium_expires_at > NOW()
            """)
            stats['premium_users'] = self.cursor.fetchone()[0]
            
            # OpenClaw users
            self.cursor.execute("SELECT COUNT(DISTINCT user_id) FROM openclaw_assistants")
            stats['openclaw_users'] = self.cursor.fetchone()[0]
            
            # Active today
            self.cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM users
                WHERE last_active > NOW() - INTERVAL '1 day'
            """)
            stats['active_today'] = self.cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def get_current_prices(self) -> Dict[str, Any]:
        """Get current prices"""
        try:
            prices = {
                'premium_monthly': float(os.getenv('PREMIUM_MONTHLY_PRICE', '10')),
                'premium_yearly': float(os.getenv('PREMIUM_YEARLY_PRICE', '100')),
                'openclaw_usdc_to_credits': int(os.getenv('OPENCLAW_USDC_TO_CREDITS', '100')),
                'openclaw_platform_fee': float(os.getenv('OPENCLAW_PLATFORM_FEE', '0.20')),
            }
            return prices
        except Exception as e:
            logger.error(f"Error getting prices: {e}")
            return {"error": str(e)}
    
    def update_price(self, price_type: str, new_value: float) -> Dict[str, Any]:
        """Update a price"""
        try:
            valid_types = {
                'premium_monthly': 'PREMIUM_MONTHLY_PRICE',
                'premium_yearly': 'PREMIUM_YEARLY_PRICE',
                'openclaw_credits': 'OPENCLAW_USDC_TO_CREDITS',
                'platform_fee': 'OPENCLAW_PLATFORM_FEE'
            }
            
            if price_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid price type. Valid: {', '.join(valid_types.keys())}"
                }
            
            env_var = valid_types[price_type]
            
            # Update .env file
            success = self._update_env_file(env_var, str(new_value))
            
            if success:
                os.environ[env_var] = str(new_value)
                return {
                    "success": True,
                    "message": f"Updated {price_type} to {new_value}",
                    "next_step": "Changes saved. Deploy to Railway to apply."
                }
            else:
                return {"success": False, "error": "Failed to update .env file"}
                
        except Exception as e:
            logger.error(f"Error updating price: {e}")
            return {"success": False, "error": str(e)}
    
    def broadcast_message(self, message: str, target: str = "all") -> Dict[str, Any]:
        """Broadcast message to users"""
        try:
            # Get target users
            if target == "all":
                self.cursor.execute("SELECT telegram_id FROM users WHERE is_active = TRUE")
            elif target == "premium":
                self.cursor.execute("""
                    SELECT telegram_id FROM users 
                    WHERE is_premium = TRUE AND premium_expires_at > NOW()
                """)
            elif target == "free":
                self.cursor.execute("""
                    SELECT telegram_id FROM users 
                    WHERE is_premium = FALSE OR premium_expires_at < NOW()
                """)
            elif target == "openclaw":
                self.cursor.execute("""
                    SELECT DISTINCT user_id FROM openclaw_assistants
                """)
            else:
                return {"success": False, "error": f"Invalid target: {target}"}
            
            user_ids = [row[0] for row in self.cursor.fetchall()]
            
            return {
                "success": True,
                "message": f"Broadcast prepared for {len(user_ids)} users",
                "user_count": len(user_ids),
                "target": target,
                "note": "Use /admin_broadcast command to actually send (safety measure)"
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_deposit_wallet(self, user_id: int, network: str = "SOL") -> Dict[str, Any]:
        """Generate deposit wallet for user"""
        try:
            # Check if user exists
            self.cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
            if not self.cursor.fetchone():
                return {"success": False, "error": "User not found"}
            
            # Generate wallet (placeholder - integrate with actual wallet generation)
            wallet_address = f"{network}_WALLET_{user_id}_{datetime.now().timestamp()}"
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "network": network,
                "user_id": user_id,
                "note": "Integrate with actual wallet generation service"
            }
            
        except Exception as e:
            logger.error(f"Error generating wallet: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get user information"""
        try:
            self.cursor.execute("""
                SELECT telegram_id, username, first_name, is_premium, 
                       premium_expires_at, created_at, last_active
                FROM users WHERE telegram_id = ?
            """, (user_id,))
            
            user = self.cursor.fetchone()
            if not user:
                return {"success": False, "error": "User not found"}
            
            return {
                "success": True,
                "user_id": user[0],
                "username": user[1],
                "first_name": user[2],
                "is_premium": user[3],
                "premium_expires_at": str(user[4]) if user[4] else None,
                "created_at": str(user[5]),
                "last_active": str(user[6])
            }
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {"success": False, "error": str(e)}
    
    def add_credits(self, user_id: int, credits: int, reason: str = "Admin grant") -> Dict[str, Any]:
        """Add credits to user"""
        try:
            # Add credits
            self.cursor.execute("""
                INSERT INTO openclaw_user_credits (user_id, credits, last_updated)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    credits = credits + ?,
                    last_updated = ?
            """, (user_id, credits, datetime.now(), credits, datetime.now()))
            
            self.conn.commit()
            
            return {
                "success": True,
                "message": f"Added {credits} credits to user {user_id}",
                "reason": reason
            }
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error adding credits: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_sql_query(self, query: str) -> Dict[str, Any]:
        """Execute SQL query (SELECT only)"""
        try:
            query_upper = query.upper().strip()
            
            # Safety check
            if not query_upper.startswith('SELECT'):
                return {
                    "success": False,
                    "error": "Only SELECT queries allowed for safety"
                }
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            return {
                "success": True,
                "rows": len(results),
                "data": [list(row) for row in results[:10]],
                "note": "Showing first 10 rows" if len(results) > 10 else None
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {"success": False, "error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import subprocess
            
            info = {
                "working_directory": os.getcwd(),
                "env_file_exists": os.path.exists('.env'),
                "python_version": subprocess.run(
                    ['python', '--version'],
                    capture_output=True,
                    text=True
                ).stdout.strip(),
            }
            
            return {"success": True, "info": info}
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_env_file(self, key: str, value: str) -> bool:
        """Update .env file"""
        try:
            env_path = '.env'
            
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            found = False
            new_lines = []
            
            for line in lines:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={value}\n")
                    found = True
                else:
                    new_lines.append(line)
            
            if not found:
                new_lines.append(f"{key}={value}\n")
            
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
            
            logger.info(f"Updated .env: {key}={value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating .env: {e}")
            return False


def get_openclaw_agent_tools(db, telegram_app=None):
    """Get OpenClaw agent tools instance"""
    return OpenClawAgentTools(db, telegram_app)
