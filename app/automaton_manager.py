# Automaton Manager - Agent Lifecycle Management
# Handles spawning, status tracking, and agent management

import os
import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime
from conway_integration import get_conway_client

class AutomatonManager:
    """
    Manages autonomous trading agent lifecycle
    
    Features:
    - Spawn agents for premium users
    - Track agent status and balance
    - Calculate survival tiers
    - Estimate runtime
    - Record transactions
    """
    
    def __init__(self, db):
        """
        Initialize Automaton Manager
        
        Args:
            db: Database instance (Supabase-enabled)
        """
        self.db = db
        self.conway = get_conway_client()
        
        # Spawn fee (100,000 credits)
        self.spawn_fee_credits = 100000
        
        # Survival tier thresholds
        self.tier_thresholds = {
            'normal': 10000,      # >= 10,000 credits
            'low_compute': 5000,  # 5,000 - 9,999 credits
            'critical': 1000,     # 1,000 - 4,999 credits
            'dead': 0             # < 1,000 credits
        }
        
        print("✅ Automaton Manager initialized")
    
    def spawn_agent(
        self,
        user_id: int,
        agent_name: str,
        genesis_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn a new autonomous trading agent
        
        Requirements:
        - User must be premium
        - User must have >= 100,000 credits
        
        Args:
            user_id: Telegram user ID
            agent_name: Name for the agent
            genesis_prompt: Initial instructions (optional)
            
        Returns:
            Dict with 'success', 'agent_id', 'deposit_address', 'message'
        """
        try:
            # 1. Check Automaton access (Rp2,000,000 one-time fee)
            if not self.db.has_automaton_access(user_id):
                return {
                    'success': False,
                    'message': 'Automaton access required. Pay Rp2,000,000 one-time fee via /subscribe'
                }
            
            # 2. Verify user is premium
            user = self.db.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            if not self.db.is_user_premium(user_id):
                return {
                    'success': False,
                    'message': 'Premium subscription required to spawn agents'
                }
            
            # 3. Check user credits
            user_credits = user.get('credits', 0)
            if user_credits < self.spawn_fee_credits:
                return {
                    'success': False,
                    'message': f'Insufficient credits. Need {self.spawn_fee_credits:,} credits, you have {user_credits:,}'
                }
            
            # 4. Generate deposit address via Conway
            deposit_address = self.conway.generate_deposit_address(user_id, agent_name)
            if not deposit_address:
                return {
                    'success': False,
                    'message': 'Failed to generate deposit address. Please try again.'
                }
            
            # 5. Create agent wallet (unique identifier)
            agent_wallet = f"agent_{uuid.uuid4().hex[:16]}"
            
            # 6. Insert into database (Supabase)
            try:
                if self.db.supabase_enabled:
                    result = self.db.supabase_service.table('user_automatons').insert({
                        'user_id': user_id,
                        'agent_wallet': agent_wallet,
                        'agent_name': agent_name,
                        'conway_deposit_address': deposit_address,
                        'genesis_prompt': genesis_prompt or "You are an autonomous trading agent. Trade wisely and maximize profits.",
                        'conway_credits': 0,
                        'survival_tier': 'dead',  # Starts dead until funded
                        'status': 'active',
                        'created_at': datetime.now().isoformat(),
                        'last_active': datetime.now().isoformat()
                    }).execute()
                    
                    if not result.data:
                        raise Exception("Failed to insert agent into database")
                    
                    agent_id = result.data[0]['id']
                else:
                    return {
                        'success': False,
                        'message': 'Supabase not enabled'
                    }
            
            except Exception as db_error:
                print(f"❌ Database error: {db_error}")
                return {
                    'success': False,
                    'message': f'Database error: {str(db_error)}'
                }
            
            # 7. Deduct spawn fee from user credits
            new_credits = user_credits - self.spawn_fee_credits
            if self.db.supabase_enabled:
                self.db.supabase_service.table('users').update({
                    'credits': new_credits
                }).eq('telegram_id', user_id).execute()
            
            # 8. Record spawn transaction
            self._record_transaction(
                agent_id=agent_id,
                transaction_type='spawn',
                amount=-self.spawn_fee_credits,
                description=f'Agent spawn fee: {agent_name}'
            )
            
            # 9. Record platform revenue
            self._record_revenue(
                source='spawn_fee',
                amount=self.spawn_fee_credits,
                agent_id=agent_id,
                user_id=user_id
            )
            
            # 10. Log activity
            self.db.log_user_activity(
                user_id,
                'agent_spawned',
                f'Spawned agent: {agent_name} (fee: {self.spawn_fee_credits:,} credits)'
            )
            
            print(f"✅ Agent spawned: {agent_name} for user {user_id}")
            
            return {
                'success': True,
                'agent_id': agent_id,
                'agent_wallet': agent_wallet,
                'deposit_address': deposit_address,
                'spawn_fee': self.spawn_fee_credits,
                'remaining_credits': new_credits,
                'message': 'Agent spawned successfully! Fund your agent to activate.'
            }
        
        except Exception as e:
            print(f"❌ Error spawning agent: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an agent
        
        Args:
            agent_id: Agent UUID
            
        Returns:
            Dict with agent status or None if not found
        """
        try:
            if not self.db.supabase_enabled:
                return None
            
            # Get agent from database
            result = self.db.supabase_service.table('user_automatons').select('*').eq('id', agent_id).execute()
            
            if not result.data:
                return None
            
            agent = result.data[0]
            
            # Get balance from Conway
            conway_balance = self.conway.get_credit_balance(agent['conway_deposit_address'])
            if conway_balance is not None:
                # Update database with latest balance
                self.db.supabase_service.table('user_automatons').update({
                    'conway_credits': conway_balance,
                    'last_active': datetime.now().isoformat()
                }).eq('id', agent_id).execute()
                
                agent['conway_credits'] = conway_balance
            
            # Calculate survival tier
            survival_tier = self._calculate_survival_tier(agent['conway_credits'])
            if survival_tier != agent['survival_tier']:
                # Update tier in database
                self.db.supabase_service.table('user_automatons').update({
                    'survival_tier': survival_tier
                }).eq('id', agent_id).execute()
                
                agent['survival_tier'] = survival_tier
            
            # Estimate runtime
            runtime_days = self._estimate_runtime(agent['conway_credits'])
            
            return {
                'agent_id': agent['id'],
                'agent_name': agent['agent_name'],
                'agent_wallet': agent['agent_wallet'],
                'deposit_address': agent['conway_deposit_address'],
                'balance': agent['conway_credits'],
                'survival_tier': survival_tier,
                'status': agent['status'],
                'runtime_days': runtime_days,
                'total_earnings': agent['total_earnings'],
                'total_expenses': agent['total_expenses'],
                'net_pnl': agent['total_earnings'] - agent['total_expenses'],
                'created_at': agent['created_at'],
                'last_active': agent['last_active']
            }
        
        except Exception as e:
            print(f"❌ Error getting agent status: {e}")
            return None
    
    def get_user_agents(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all agents for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of agent status dicts
        """
        try:
            if not self.db.supabase_enabled:
                return []
            
            # Get all agents for user
            result = self.db.supabase_service.table('user_automatons').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                return []
            
            agents = []
            for agent in result.data:
                status = self.get_agent_status(agent['id'])
                if status:
                    agents.append(status)
            
            return agents
        
        except Exception as e:
            print(f"❌ Error getting user agents: {e}")
            return []
    
    def _calculate_survival_tier(self, credits: float) -> str:
        """
        Calculate survival tier based on credit balance
        
        Tiers:
        - normal: >= 10,000 credits
        - low_compute: 5,000 - 9,999 credits
        - critical: 1,000 - 4,999 credits
        - dead: < 1,000 credits
        
        Args:
            credits: Current credit balance
            
        Returns:
            Tier name
        """
        if credits >= self.tier_thresholds['normal']:
            return 'normal'
        elif credits >= self.tier_thresholds['low_compute']:
            return 'low_compute'
        elif credits >= self.tier_thresholds['critical']:
            return 'critical'
        else:
            return 'dead'
    
    def _estimate_runtime(self, credits: float, daily_consumption: float = 200) -> float:
        """
        Estimate remaining runtime in days
        
        Args:
            credits: Current credit balance
            daily_consumption: Estimated daily consumption (default: 200)
            
        Returns:
            Estimated days remaining
        """
        if credits <= 0:
            return 0
        
        return credits / daily_consumption
    
    def _record_transaction(
        self,
        agent_id: str,
        transaction_type: str,
        amount: float,
        description: Optional[str] = None
    ) -> bool:
        """
        Record transaction in database
        
        Args:
            agent_id: Agent UUID
            transaction_type: Type (spawn, deposit, earn, spend, performance_fee)
            amount: Transaction amount
            description: Optional description
            
        Returns:
            True if successful
        """
        try:
            if not self.db.supabase_enabled:
                return False
            
            self.db.supabase_service.table('automaton_transactions').insert({
                'automaton_id': agent_id,
                'type': transaction_type,
                'amount': amount,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }).execute()
            
            return True
        
        except Exception as e:
            print(f"❌ Error recording transaction: {e}")
            return False
    
    def _record_revenue(
        self,
        source: str,
        amount: float,
        agent_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Record platform revenue
        
        Args:
            source: Revenue source (spawn_fee, deposit_fee, performance_fee)
            amount: Revenue amount
            agent_id: Optional agent ID
            user_id: Optional user ID
            
        Returns:
            True if successful
        """
        try:
            if not self.db.supabase_enabled:
                return False
            
            self.db.supabase_service.table('platform_revenue').insert({
                'source': source,
                'amount': amount,
                'agent_id': agent_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }).execute()
            
            return True
        
        except Exception as e:
            print(f"❌ Error recording revenue: {e}")
            return False


# Singleton instance
_automaton_manager = None

def get_automaton_manager(db):
    """
    Get singleton Automaton Manager instance
    
    Args:
        db: Database instance
        
    Returns:
        AutomatonManager instance
    """
    global _automaton_manager
    if _automaton_manager is None:
        _automaton_manager = AutomatonManager(db)
    return _automaton_manager
