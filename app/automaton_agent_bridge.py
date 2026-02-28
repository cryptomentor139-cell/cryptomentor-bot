"""
Automaton Agent Bridge
Connects Telegram bot with Automaton dashboard for autonomous trading
ONLY for Lifetime Premium users

NOTE: Requires Automaton dashboard to be accessible (local or deployed)
"""

import os
import json
import subprocess
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

class AutomatonAgentBridge:
    """
    Bridge between Telegram bot and Automaton dashboard
    Manages autonomous trading agents for LIFETIME PREMIUM users only
    """
    
    def __init__(self, db, automaton_manager, automaton_dir=None):
        """
        Initialize bridge
        
        Args:
            db: Database instance
            automaton_manager: AutomatonManager instance
            automaton_dir: Path to Automaton directory (optional, from env)
        """
        self.db = db
        self.automaton_manager = automaton_manager
        
        # Get Automaton directory from environment or default
        if automaton_dir is None:
            automaton_dir = os.getenv('AUTOMATON_DIR', 'C:/Users/dragon/automaton')
        
        self.automaton_dir = Path(automaton_dir)
        self.send_task_script = self.automaton_dir / "send-task.js"
        self.automaton_available = self.send_task_script.exists()
        
        if self.automaton_available:
            print("✅ Automaton Agent Bridge initialized (Lifetime Premium only)")
            print(f"   Automaton dir: {self.automaton_dir}")
        else:
            print("⚠️  Automaton Agent Bridge initialized (Automaton NOT available)")
            print(f"   Expected location: {self.automaton_dir}")
            print("   Autonomous trading will be disabled")
    
    def _check_lifetime_premium(self, user_id: int) -> bool:
        """Check if user has lifetime premium"""
        try:
            if self.db.supabase_enabled:
                result = self.db.supabase_service.table('users')\
                    .select('premium_tier')\
                    .eq('user_id', user_id)\
                    .execute()
                
                if result.data:
                    tier = result.data[0].get('premium_tier', '')
                    return tier == 'lifetime'
            return False
        except Exception as e:
            print(f"❌ Error checking lifetime premium: {e}")
            return False
    
    def _send_task_to_automaton(self, task_content: str) -> Dict[str, Any]:
        """Send task to Automaton dashboard via send-task.js"""
        try:
            if not self.send_task_script.exists():
                return {
                    'success': False,
                    'error': 'send-task.js not found'
                }
            
            result = subprocess.run(
                ['node', 'send-task.js', task_content],
                cwd=str(self.automaton_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"send-task.js failed: {result.stderr}"
                }
            
            # Extract task ID from output
            task_id = None
            for line in result.stdout.split('\n'):
                if 'Task ID:' in line:
                    task_id = line.split('Task ID:')[1].strip()
                    break
            
            return {
                'success': True,
                'task_id': task_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def spawn_autonomous_agent(
        self,
        user_id: int,
        agent_name: str,
        initial_balance: float,
        strategy: str = "conservative",
        risk_level: str = "low"
    ) -> Dict[str, Any]:
        """
        Spawn autonomous trading agent with Automaton dashboard
        ONLY for Lifetime Premium users
        
        Args:
            user_id: Telegram user ID
            agent_name: Name for the agent
            initial_balance: Initial USDC balance
            strategy: Trading strategy (conservative/moderate/aggressive)
            risk_level: Risk level (low/medium/high)
        
        Returns:
            Dict with success status and agent info
        """
        try:
            # Check if Automaton is available
            if not self.automaton_available:
                return {
                    'success': False,
                    'message': 'Automaton dashboard tidak tersedia. Autonomous trading sementara disabled.'
                }
            
            # Check if user has lifetime premium
            if not self._check_lifetime_premium(user_id):
                return {
                    'success': False,
                    'message': 'Autonomous trading hanya untuk Lifetime Premium users'
                }
            
            # 1. Spawn agent via automaton_manager
            result = self.automaton_manager.spawn_agent(
                user_id=user_id,
                agent_name=agent_name,
                genesis_prompt=self._generate_genesis_prompt(
                    agent_name, strategy, risk_level, initial_balance
                )
            )
            
            if not result['success']:
                return result
            
            agent_id = result['agent_id']
            
            # 2. Send initialization task to Automaton dashboard
            init_task = self._create_agent_init_task(
                agent_id=agent_id,
                agent_name=agent_name,
                balance=initial_balance,
                strategy=strategy,
                risk_level=risk_level
            )
            
            automaton_result = self._send_task_to_automaton(init_task)
            
            if automaton_result['success']:
                # Store task ID in database
                if self.db.supabase_enabled:
                    self.db.supabase_service.table('user_automatons').update({
                        'automaton_ai_task_id': automaton_result.get('task_id'),
                        'trading_enabled': False,  # Disabled by default, user must enable
                        'strategy': strategy,
                        'risk_level': risk_level
                    }).eq('id', agent_id).execute()
            
            result['automaton_linked'] = automaton_result['success']
            result['strategy'] = strategy
            result['risk_level'] = risk_level
            
            return result
        
        except Exception as e:
            print(f"❌ Error spawning autonomous agent: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def _generate_genesis_prompt(
        self,
        agent_name: str,
        strategy: str,
        risk_level: str,
        initial_balance: float
    ) -> str:
        """Generate genesis prompt for autonomous trading agent"""
        
        strategy_desc = {
            'conservative': 'Fokus pada preservasi modal. Hanya ambil trade dengan probabilitas tinggi dan stop loss ketat.',
            'moderate': 'Balance antara growth dan safety. Ambil calculated risks dengan risk management yang proper.',
            'aggressive': 'Maksimalkan returns. Ambil lebih banyak trade dengan risk/reward ratio yang lebih tinggi.'
        }
        
        risk_desc = {
            'low': 'Max 2% risk per trade. Daily loss limit: 5%',
            'medium': 'Max 5% risk per trade. Daily loss limit: 10%',
            'high': 'Max 10% risk per trade. Daily loss limit: 20%'
        }
        
        return f"""You are {agent_name}, an autonomous trading agent for crypto markets.

Initial Balance: {initial_balance} USDC
Strategy: {strategy.upper()} - {strategy_desc.get(strategy, '')}
Risk Level: {risk_level.upper()} - {risk_desc.get(risk_level, '')}

Your mission:
1. Analyze crypto markets continuously (BTC, ETH, major altcoins)
2. Identify profitable trading opportunities using technical analysis
3. Execute trades automatically when conditions are met
4. Manage risk strictly according to your parameters
5. Report all activities and decisions to user

Trading Rules:
- ALWAYS follow risk management rules
- NEVER exceed max trade size
- ALWAYS use stop loss
- Stop trading if daily loss limit reached
- Log every trade decision with reasoning

You have FULL AUTONOMY to execute trades within your risk parameters.
Trade wisely and protect capital above all."""
    
    def _create_agent_init_task(
        self,
        agent_id: str,
        agent_name: str,
        balance: float,
        strategy: str,
        risk_level: str
    ) -> str:
        """Create initialization task for Automaton dashboard"""
        
        return f"""Initialize autonomous trading agent:

Agent ID: {agent_id}
Name: {agent_name}
Balance: {balance} USDC
Strategy: {strategy}
Risk Level: {risk_level}

You are now active as {agent_name}. Your role is to:

1. Monitor crypto markets (BTC, ETH, major altcoins) continuously
2. Analyze trading opportunities using technical analysis
3. Execute trades AUTOMATICALLY when conditions are favorable
4. Always include: Entry price, Stop loss, Take profit levels, Risk/Reward ratio
5. Log all trades with reasoning

IMPORTANT: You have FULL AUTONOMY to execute trades within risk parameters.
No user approval needed - you are an AUTONOMOUS agent.

Start by analyzing current market conditions and execute your first trade when ready."""
    
    def send_trading_instruction(
        self,
        agent_id: str,
        instruction: str
    ) -> Dict[str, Any]:
        """
        Send trading instruction to autonomous agent
        
        Args:
            agent_id: Agent UUID
            instruction: Instruction text
        
        Returns:
            Dict with success status
        """
        try:
            # Get agent info
            agent = self.automaton_manager.get_agent_status(agent_id)
            if not agent:
                return {
                    'success': False,
                    'message': 'Agent not found'
                }
            
            # Check if user has lifetime premium
            if not self._check_lifetime_premium(agent['user_id']):
                return {
                    'success': False,
                    'message': 'Lifetime Premium required'
                }
            
            # Create task with agent context
            task = f"""Agent: {agent['agent_name']} (ID: {agent_id})
Balance: {agent['balance']} USDC

Instruction from user: {instruction}

Please execute this instruction and report the result."""
            
            result = self._send_task_to_automaton(task)
            
            return result
        
        except Exception as e:
            print(f"❌ Error sending instruction: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def enable_trading(self, agent_id: str, user_id: int) -> Dict[str, Any]:
        """Enable autonomous trading for agent (Lifetime Premium only)"""
        try:
            # Check lifetime premium
            if not self._check_lifetime_premium(user_id):
                return {
                    'success': False,
                    'message': 'Lifetime Premium required for autonomous trading'
                }
            
            if self.db.supabase_enabled:
                self.db.supabase_service.table('user_automatons').update({
                    'trading_enabled': True
                }).eq('id', agent_id).execute()
                
                return {
                    'success': True,
                    'message': 'Autonomous trading enabled'
                }
            return {
                'success': False,
                'message': 'Database not available'
            }
        except Exception as e:
            print(f"❌ Error enabling trading: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def disable_trading(self, agent_id: str) -> Dict[str, Any]:
        """Disable autonomous trading for agent"""
        try:
            if self.db.supabase_enabled:
                self.db.supabase_service.table('user_automatons').update({
                    'trading_enabled': False
                }).eq('id', agent_id).execute()
                
                return {
                    'success': True,
                    'message': 'Autonomous trading disabled'
                }
            return {
                'success': False,
                'message': 'Database not available'
            }
        except Exception as e:
            print(f"❌ Error disabling trading: {e}")
            return {
                'success': False,
                'message': str(e)
            }


# Singleton instance
_bridge = None

def get_automaton_agent_bridge(db, automaton_manager):
    """Get singleton bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = AutomatonAgentBridge(db, automaton_manager)
    return _bridge
