"""
Automaton Auto Trade Client
Client untuk mengelola auto trading dengan Automaton AI
"""

import subprocess
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, Optional

class AutomatonAutoTradeClient:
    def __init__(self, db_path: str = r"C:\root\.automaton\state.db"):
        self.db_path = db_path
        self.automaton_dir = r"C:\Users\dragon\automaton"
        self.send_task_script = str(Path(self.automaton_dir) / "send-task.js")
        
    def _send_task(self, task: str, timeout: int = 120) -> Dict:
        """Send task to Automaton and wait for response"""
        try:
            # Send task using send-task.js
            result = subprocess.run(
                ['node', self.send_task_script, task],
                cwd=self.automaton_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Failed to send task: {result.stderr}"
                }
            
            # Extract task ID from output
            output = result.stdout
            task_id = None
            for line in output.split('\n'):
                if 'Task ID:' in line or 'task_id' in line.lower():
                    # Extract ID from line
                    parts = line.split(':')
                    if len(parts) > 1:
                        task_id = parts[-1].strip()
                        break
            
            if not task_id:
                return {
                    'success': False,
                    'error': "Could not extract task ID from response"
                }
            
            # Wait for response with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                response = self._check_task_response(task_id)
                if response:
                    return {
                        'success': True,
                        'response': response,
                        'task_id': task_id
                    }
                time.sleep(5)  # Check every 5 seconds
            
            return {
                'success': False,
                'error': f"Timeout waiting for response (waited {timeout}s)",
                'task_id': task_id
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': "Task sending timeout"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error sending task: {str(e)}"
            }
    
    def _check_task_response(self, task_id: str) -> Optional[str]:
        """Check if Automaton has responded to task"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check outbox_messages for response
            cursor.execute("""
                SELECT content FROM outbox_messages 
                WHERE content LIKE ? 
                ORDER BY created_at DESC LIMIT 1
            """, (f'%{task_id}%',))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            print(f"Error checking response: {e}")
            return None
    
    def start_autotrade(self, user_id: int, amount: float, wallet_address: str) -> Dict:
        """
        Start auto trading for a user
        
        Args:
            user_id: Telegram user ID
            amount: USDC amount to trade
            wallet_address: User's wallet address for deposits/withdrawals
        
        Returns:
            Dict with success status and response
        """
        task = f"""START AUTO TRADE for user {user_id}

Initial deposit: {amount} USDC
User wallet: {wallet_address}

Your mission:
1. Manage this {amount} USDC portfolio autonomously
2. Trade on DEX (Uniswap, PancakeSwap) to generate profit
3. Use technical analysis, on-chain data, and market sentiment
4. Risk management rules:
   - Max 20% of portfolio per trade
   - Stop loss at -5% per trade
   - Daily loss limit: -10% of portfolio
   - Only trade liquid pairs (>$1M liquidity)
5. Target: 5-10% monthly return
6. Track all trades in your memory with user_id: {user_id}
7. Report daily performance summary

Strategy:
- Focus on major pairs: ETH/USDC, BTC/USDC, high-cap altcoins
- Use momentum + mean reversion strategies
- Monitor whale movements and social sentiment
- Take profit at +8-10%, cut losses at -5%

Begin trading now. Respond with:
- Trading strategy summary
- First trade plan
- Risk assessment
"""
        
        return self._send_task(task, timeout=120)
    
    def get_autotrade_status(self, user_id: int) -> Dict:
        """
        Get auto trade status for a user
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Dict with portfolio status
        """
        task = f"""REPORT AUTO TRADE STATUS for user {user_id}

Provide detailed report including:
1. Current portfolio balance (USDC)
2. Total profit/loss ($ and %)
3. Number of trades executed
4. Win rate
5. Active positions (if any)
6. Best performing trade
7. Worst performing trade
8. Overall performance assessment

Format response clearly for user to understand.
"""
        
        return self._send_task(task, timeout=60)
    
    def withdraw_autotrade(self, user_id: int) -> Dict:
        """
        Process withdrawal for a user
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Dict with withdrawal details
        """
        task = f"""PROCESS WITHDRAWAL for user {user_id}

Steps:
1. Close all active positions at current market price
2. Calculate final portfolio value
3. Calculate total profit/loss
4. Calculate fee (25% of profit only, not from initial deposit)
5. Calculate final amount to return to user
6. Prepare withdrawal transaction

Respond with:
- Initial deposit amount
- Final portfolio value
- Total profit/loss
- Fee amount (25% of profit)
- Net amount to return to user
- Withdrawal transaction details

DO NOT actually execute withdrawal yet, just prepare the details.
"""
        
        return self._send_task(task, timeout=90)
    
    def check_automaton_status(self) -> Dict:
        """Check if Automaton is online and responsive"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check latest heartbeat
            cursor.execute("""
                SELECT state, credits_cents, created_at 
                FROM heartbeats 
                ORDER BY created_at DESC LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                state, credits, timestamp = result
                return {
                    'online': True,
                    'state': state,
                    'credits': credits / 100,  # Convert cents to dollars
                    'last_heartbeat': timestamp
                }
            else:
                return {
                    'online': False,
                    'error': 'No heartbeat found'
                }
                
        except Exception as e:
            return {
                'online': False,
                'error': f"Error checking status: {str(e)}"
            }
    
    def get_trade_history(self, user_id: int, limit: int = 10) -> Dict:
        """
        Get trade history for a user
        
        Args:
            user_id: Telegram user ID
            limit: Number of recent trades to retrieve
        
        Returns:
            Dict with trade history
        """
        task = f"""SHOW TRADE HISTORY for user {user_id}

List the last {limit} trades with:
- Date/time
- Symbol
- Side (buy/sell)
- Amount
- Entry price
- Exit price (if closed)
- Profit/loss
- Status (open/closed)

Format as a clear table or list.
"""
        
        return self._send_task(task, timeout=60)


# Example usage
if __name__ == "__main__":
    client = AutomatonAutoTradeClient()
    
    # Check if Automaton is online
    print("Checking Automaton status...")
    status = client.check_automaton_status()
    print(f"Status: {json.dumps(status, indent=2)}")
    
    if status.get('online'):
        print("\n✅ Automaton is online!")
        print(f"Credits: ${status['credits']:.2f}")
        print(f"State: {status['state']}")
        
        # Example: Start auto trade
        print("\n🚀 Testing auto trade start...")
        result = client.start_autotrade(
            user_id=123456789,
            amount=50.0,
            wallet_address="0x1234567890abcdef1234567890abcdef12345678"
        )
        
        if result['success']:
            print(f"\n✅ Auto trade started!")
            print(f"Response: {result['response'][:500]}...")
        else:
            print(f"\n❌ Error: {result['error']}")
    else:
        print("\n❌ Automaton is offline!")
        print("Please start Automaton first: node dist/index.js --run")
