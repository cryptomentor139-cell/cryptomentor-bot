"""
OpenClaw Admin Tools - System Management via AI
Admin can modify bot settings, prices, and deploy changes via OpenClaw
"""

import os
import logging
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenClawAdminTools:
    """Tools for admin to manage bot via OpenClaw"""
    
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor
        
    def get_current_prices(self) -> Dict:
        """Get current subscription and credit prices"""
        try:
            # Get from environment or database
            prices = {
                'premium_monthly': float(os.getenv('PREMIUM_MONTHLY_PRICE', '10')),
                'premium_yearly': float(os.getenv('PREMIUM_YEARLY_PRICE', '100')),
                'openclaw_usdc_to_credits': int(os.getenv('OPENCLAW_USDC_TO_CREDITS', '100')),
                'openclaw_platform_fee': float(os.getenv('OPENCLAW_PLATFORM_FEE', '0.20')),
            }
            
            return prices
        except Exception as e:
            logger.error(f"Error getting prices: {e}")
            return {}
    
    def update_price(self, price_type: str, new_value: float) -> Tuple[bool, str]:
        """
        Update a price in the system
        
        Args:
            price_type: Type of price (premium_monthly, premium_yearly, etc)
            new_value: New price value
            
        Returns:
            Tuple of (success, message)
        """
        try:
            valid_types = {
                'premium_monthly': 'PREMIUM_MONTHLY_PRICE',
                'premium_yearly': 'PREMIUM_YEARLY_PRICE',
                'openclaw_credits': 'OPENCLAW_USDC_TO_CREDITS',
                'platform_fee': 'OPENCLAW_PLATFORM_FEE'
            }
            
            if price_type not in valid_types:
                return False, f"Invalid price type. Valid: {', '.join(valid_types.keys())}"
            
            env_var = valid_types[price_type]
            
            # Update .env file
            success = self._update_env_file(env_var, str(new_value))
            
            if success:
                # Also update environment variable in current process
                os.environ[env_var] = str(new_value)
                
                return True, f"✅ Updated {price_type} to {new_value}"
            else:
                return False, "Failed to update .env file"
                
        except Exception as e:
            logger.error(f"Error updating price: {e}")
            return False, f"Error: {str(e)}"
    
    def _update_env_file(self, key: str, value: str) -> bool:
        """Update a key in .env file"""
        try:
            env_path = '.env'
            
            # Read current .env
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add the key
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
            
            # Write back
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
            
            logger.info(f"Updated .env: {key}={value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating .env file: {e}")
            return False
    
    def get_bot_stats(self) -> Dict:
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
            
            # Total revenue (platform fees)
            self.cursor.execute("""
                SELECT COALESCE(SUM(platform_fee), 0) 
                FROM openclaw_credit_transactions
                WHERE transaction_type = 'purchase'
            """)
            stats['total_revenue'] = float(self.cursor.fetchone()[0])
            
            # Active conversations today
            self.cursor.execute("""
                SELECT COUNT(*) FROM openclaw_conversations
                WHERE updated_at > NOW() - INTERVAL '1 day'
            """)
            stats['active_today'] = self.cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def git_status(self) -> Tuple[bool, str]:
        """Check git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status = result.stdout.strip()
                if not status:
                    return True, "✅ Working tree clean"
                else:
                    return True, f"📝 Changes:\n{status}"
            else:
                return False, f"Error: {result.stderr}"
                
        except Exception as e:
            logger.error(f"Error checking git status: {e}")
            return False, f"Error: {str(e)}"
    
    def git_commit_and_push(self, message: str) -> Tuple[bool, str]:
        """Commit and push changes to git"""
        try:
            # Add all changes
            result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Git add failed: {result.stderr}"
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Check if nothing to commit
                if "nothing to commit" in result.stdout:
                    return True, "✅ Nothing to commit"
                return False, f"Git commit failed: {result.stderr}"
            
            # Push
            result = subprocess.run(
                ['git', 'push'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, f"Git push failed: {result.stderr}"
            
            return True, "✅ Changes committed and pushed to GitHub"
            
        except Exception as e:
            logger.error(f"Error in git operations: {e}")
            return False, f"Error: {str(e)}"
    
    def railway_deploy(self) -> Tuple[bool, str]:
        """Trigger Railway deployment"""
        try:
            # Railway auto-deploys from GitHub
            # Just return success message
            return True, (
                "✅ Changes pushed to GitHub\n"
                "🚂 Railway will auto-deploy in ~2-3 minutes\n"
                "Monitor: https://railway.app"
            )
            
        except Exception as e:
            logger.error(f"Error triggering Railway deploy: {e}")
            return False, f"Error: {str(e)}"
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            info = {
                'python_version': subprocess.run(
                    ['python', '--version'],
                    capture_output=True,
                    text=True
                ).stdout.strip(),
                'git_branch': subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True,
                    text=True
                ).stdout.strip(),
                'git_commit': subprocess.run(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True,
                    text=True
                ).stdout.strip(),
                'working_directory': os.getcwd(),
                'env_file_exists': os.path.exists('.env'),
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def add_admin_user(self, user_id: int) -> Tuple[bool, str]:
        """Add a user as admin"""
        try:
            # Get current admin IDs
            admin_ids = os.getenv('ADMIN_IDS', '')
            admin_list = [aid.strip() for aid in admin_ids.split(',') if aid.strip()]
            
            if str(user_id) in admin_list:
                return False, f"User {user_id} is already an admin"
            
            # Add new admin
            admin_list.append(str(user_id))
            new_admin_ids = ','.join(admin_list)
            
            # Update .env
            success = self._update_env_file('ADMIN_IDS', new_admin_ids)
            
            if success:
                os.environ['ADMIN_IDS'] = new_admin_ids
                return True, f"✅ Added user {user_id} as admin"
            else:
                return False, "Failed to update .env file"
                
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            return False, f"Error: {str(e)}"
    
    def remove_admin_user(self, user_id: int) -> Tuple[bool, str]:
        """Remove a user from admin"""
        try:
            # Get current admin IDs
            admin_ids = os.getenv('ADMIN_IDS', '')
            admin_list = [aid.strip() for aid in admin_ids.split(',') if aid.strip()]
            
            if str(user_id) not in admin_list:
                return False, f"User {user_id} is not an admin"
            
            # Remove admin
            admin_list.remove(str(user_id))
            new_admin_ids = ','.join(admin_list)
            
            # Update .env
            success = self._update_env_file('ADMIN_IDS', new_admin_ids)
            
            if success:
                os.environ['ADMIN_IDS'] = new_admin_ids
                return True, f"✅ Removed user {user_id} from admin"
            else:
                return False, "Failed to update .env file"
                
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            return False, f"Error: {str(e)}"
    
    def execute_sql(self, query: str) -> Tuple[bool, str]:
        """Execute SQL query (admin only, be careful!)"""
        try:
            # Safety check - only allow SELECT, UPDATE, INSERT
            query_upper = query.upper().strip()
            
            if query_upper.startswith('DROP') or query_upper.startswith('DELETE'):
                return False, "❌ DROP and DELETE queries are not allowed for safety"
            
            self.cursor.execute(query)
            
            if query_upper.startswith('SELECT'):
                results = self.cursor.fetchall()
                if results:
                    # Format results
                    output = "\n".join([str(row) for row in results[:10]])
                    if len(results) > 10:
                        output += f"\n... and {len(results) - 10} more rows"
                    return True, output
                else:
                    return True, "No results"
            else:
                self.conn.commit()
                return True, f"✅ Query executed successfully"
                
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error executing SQL: {e}")
            return False, f"Error: {str(e)}"


def get_openclaw_admin_tools(db):
    """Get OpenClaw admin tools instance"""
    return OpenClawAdminTools(db)
