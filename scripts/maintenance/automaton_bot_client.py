"""
Automaton Bot Client - Final Version
Simple & reliable client untuk integrate Automaton ke bot Telegram
Menggunakan send-task.js yang proven working
"""

import subprocess
import time
import sqlite3
from pathlib import Path

class AutomatonBotClient:
    def __init__(self, automaton_dir="C:/Users/dragon/automaton"):
        self.automaton_dir = Path(automaton_dir)
        self.db_path = "C:/root/.automaton/state.db"
        self.send_task_script = self.automaton_dir / "send-task.js"
        
        if not self.send_task_script.exists():
            raise FileNotFoundError(f"send-task.js not found: {self.send_task_script}")
    
    def get_ai_signal(self, symbol, timeout=90):
        """
        Get AI trading signal untuk crypto symbol
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "BTC/USDT")
            timeout: Max wait time in seconds
        
        Returns:
            dict: {
                'success': bool,
                'signal': str,  # Full AI response
                'error': str (if failed)
            }
        """
        # Create task prompt
        task = f"""
Analyze {symbol} cryptocurrency market. Provide:

1. **Market Sentiment**: Bullish/Bearish/Neutral
2. **Recommendation**: BUY/SELL/HOLD
3. **Confidence**: 0-100%
4. **Key Reasons**: 3 main points
5. **Entry Price**: Suggested entry
6. **Stop Loss**: Risk management level
7. **Take Profit**: Target price

Format dalam Bahasa Indonesia, gunakan emoji, singkat dan jelas untuk Telegram users.
"""
        
        return self._send_and_wait(task, timeout)
    
    def ask_ai(self, question, timeout=60):
        """
        Ask AI any question about crypto
        
        Args:
            question: User's question
            timeout: Max wait time
        
        Returns:
            dict: {'success': bool, 'answer': str, 'error': str}
        """
        task = f"Answer this crypto question concisely in Bahasa Indonesia: {question}"
        return self._send_and_wait(task, timeout)
    
    def _send_and_wait(self, task, timeout):
        """
        Send task via send-task.js and wait for response
        """
        try:
            # Send task
            result = subprocess.run(
                ['node', 'send-task.js', task],
                cwd=str(self.automaton_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'Failed to send task: {result.stderr}'
                }
            
            # Extract task ID
            task_id = self._extract_task_id(result.stdout)
            if not task_id:
                return {
                    'success': False,
                    'error': 'Could not extract task ID'
                }
            
            # Wait for response
            response = self._wait_for_response(task_id, timeout)
            
            if response:
                return {
                    'success': True,
                    'signal': response,
                    'task_id': task_id
                }
            else:
                return {
                    'success': False,
                    'error': 'AI timeout. Automaton mungkin sedang sibuk atau tidak running.'
                }
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'send-task.js timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_task_id(self, output):
        """Extract task ID from send-task.js output"""
        for line in output.split('\n'):
            if 'Task ID:' in line:
                return line.split('Task ID:')[1].strip()
        return None
    
    def _wait_for_response(self, task_id, timeout):
        """Wait for Automaton to process and respond"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if processed
                cursor.execute("""
                    SELECT processed_at FROM inbox_messages WHERE id = ?
                """, (task_id,))
                
                result = cursor.fetchone()
                
                if result and result[0]:
                    # Get response
                    cursor.execute("""
                        SELECT thinking FROM turns 
                        WHERE timestamp > (SELECT received_at FROM inbox_messages WHERE id = ?)
                        ORDER BY timestamp DESC LIMIT 1
                    """, (task_id,))
                    
                    turn = cursor.fetchone()
                    conn.close()
                    
                    if turn:
                        return turn[0]
                
                conn.close()
                time.sleep(3)
                
            except Exception as e:
                print(f"Error waiting for response: {e}")
                time.sleep(3)
        
        return None
    
    def check_status(self):
        """Check if Automaton is online"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM turns")
            total_turns = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT timestamp FROM turns 
                ORDER BY timestamp DESC LIMIT 1
            """)
            last_activity = cursor.fetchone()
            
            conn.close()
            
            # Check if active (last activity within 5 minutes)
            if last_activity:
                from datetime import datetime, timedelta
                last_time = datetime.fromisoformat(last_activity[0].replace('Z', '+00:00'))
                is_active = (datetime.now(last_time.tzinfo) - last_time) < timedelta(minutes=5)
            else:
                is_active = False
            
            return {
                'online': is_active,
                'total_turns': total_turns,
                'last_activity': last_activity[0] if last_activity else None
            }
        except Exception as e:
            return {
                'online': False,
                'error': str(e)
            }


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("TEST AUTOMATON BOT CLIENT - FINAL VERSION")
    print("=" * 60)
    
    client = AutomatonBotClient()
    
    # Test 1: Check status
    print("\n1. Checking Automaton status...")
    status = client.check_status()
    print(f"   Online: {status['online']}")
    print(f"   Total turns: {status.get('total_turns', 'N/A')}")
    print(f"   Last activity: {status.get('last_activity', 'N/A')}")
    
    # Test 2: Get AI signal
    print("\n2. Getting AI signal for BTCUSDT...")
    print("   (This will take 30-90 seconds...)")
    
    result = client.get_ai_signal("BTCUSDT", timeout=90)
    
    if result['success']:
        print("   ✅ Success!")
        print(f"   Signal preview: {result['signal'][:200]}...")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("READY FOR BOT INTEGRATION!")
    print("=" * 60)
    print("\nCopy file ini ke bot V3 kamu dan import:")
    print("  from automaton_bot_client import AutomatonBotClient")
    print("  client = AutomatonBotClient()")
    print("  result = client.get_ai_signal('BTCUSDT')")
