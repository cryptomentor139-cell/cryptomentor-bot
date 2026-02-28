"""
Isolated AI Manager - Fair profit distribution per user
Each user gets their own AI instance with isolated balance
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IsolatedAIManager:
    """Manages isolated AI instances per user for fair profit distribution"""
    
    def __init__(self, db):
        self.db = db
    
    def create_user_main_agent(
        self, 
        user_id: int, 
        initial_balance: float,
        agent_id: Optional[str] = None
    ) -> Dict:
        """
        Create main AI agent for user (Generation 1)
        
        Args:
            user_id: User ID
            initial_balance: User's deposit amount
            agent_id: Optional custom agent ID from Automaton
            
        Returns:
            Dict with agent info
        """
        try:
            # Check if user already has main agent
            existing = self.db.execute(
                """
                SELECT agent_id FROM automaton_agents 
                WHERE user_id = ? AND generation = 1 AND status = 'active'
                """,
                (user_id,)
            ).fetchone()
            
            if existing:
                logger.warning(f"User {user_id} already has main agent: {existing['agent_id']}")
                return self.get_agent_info(existing['agent_id'])
            
            # Generate agent_id if not provided
            if not agent_id:
                import uuid
                agent_id = f"AI-{user_id}-{uuid.uuid4().hex[:8]}"
            
            # Create main agent
            self.db.execute(
                """
                INSERT INTO automaton_agents (
                    agent_id, user_id, parent_agent_id, generation,
                    isolated_balance, total_earnings, spawn_threshold,
                    status, created_at
                ) VALUES (?, ?, NULL, 1, ?, 0, NULL, 'active', ?)
                """,
                (agent_id, user_id, initial_balance, datetime.now())
            )
            self.db.commit()
            
            logger.info(f"Created main AI agent {agent_id} for user {user_id} with balance {initial_balance}")
            
            return self.get_agent_info(agent_id)
            
        except Exception as e:
            logger.error(f"Error creating main agent for user {user_id}: {e}")
            self.db.rollback()
            raise
    
    def spawn_child_agent(
        self,
        parent_agent_id: str,
        child_balance: float,
        spawn_reason: str = "AI decided to spawn"
    ) -> Dict:
        """
        Spawn child agent from parent's earnings
        
        Args:
            parent_agent_id: Parent agent ID
            child_balance: Balance allocated to child from parent earnings
            spawn_reason: Reason for spawning
            
        Returns:
            Dict with child agent info
        """
        try:
            # Get parent info
            parent = self.db.execute(
                """
                SELECT user_id, generation, isolated_balance, total_earnings
                FROM automaton_agents WHERE agent_id = ?
                """,
                (parent_agent_id,)
            ).fetchone()
            
            if not parent:
                raise ValueError(f"Parent agent {parent_agent_id} not found")
            
            # Verify parent has enough earnings
            if parent['total_earnings'] < child_balance:
                raise ValueError(
                    f"Parent earnings {parent['total_earnings']} < child balance {child_balance}"
                )
            
            # Generate child agent ID
            import uuid
            child_agent_id = f"AI-{parent['user_id']}-G{parent['generation']+1}-{uuid.uuid4().hex[:8]}"
            
            # Create child agent
            self.db.execute(
                """
                INSERT INTO automaton_agents (
                    agent_id, user_id, parent_agent_id, generation,
                    isolated_balance, total_earnings, spawn_threshold,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, 0, NULL, 'active', ?)
                """,
                (
                    child_agent_id,
                    parent['user_id'],
                    parent_agent_id,
                    parent['generation'] + 1,
                    child_balance,
                    datetime.now()
                )
            )
            
            # Deduct from parent's earnings (not balance)
            self.db.execute(
                """
                UPDATE automaton_agents 
                SET total_earnings = total_earnings - ?
                WHERE agent_id = ?
                """,
                (child_balance, parent_agent_id)
            )
            
            # Log spawn transaction
            self.db.execute(
                """
                INSERT INTO automaton_transactions (
                    agent_id, transaction_type, amount, balance_after,
                    description, created_at
                ) VALUES (?, 'spawn_child', ?, ?, ?, ?)
                """,
                (
                    parent_agent_id,
                    -child_balance,
                    parent['isolated_balance'],  # Balance unchanged
                    f"Spawned child {child_agent_id}: {spawn_reason}",
                    datetime.now()
                )
            )
            
            self.db.commit()
            
            logger.info(
                f"Spawned child agent {child_agent_id} from parent {parent_agent_id} "
                f"with balance {child_balance}"
            )
            
            return self.get_agent_info(child_agent_id)
            
        except Exception as e:
            logger.error(f"Error spawning child from {parent_agent_id}: {e}")
            self.db.rollback()
            raise
    
    def record_agent_profit(
        self,
        agent_id: str,
        profit_amount: float,
        trade_details: Optional[str] = None
    ) -> None:
        """
        Record profit earned by AI agent
        
        Args:
            agent_id: Agent ID
            profit_amount: Profit amount (can be negative for loss)
            trade_details: Optional trade details
        """
        try:
            # Update agent balance and earnings
            self.db.execute(
                """
                UPDATE automaton_agents 
                SET 
                    isolated_balance = isolated_balance + ?,
                    total_earnings = total_earnings + ?
                WHERE agent_id = ?
                """,
                (profit_amount, profit_amount, agent_id)
            )
            
            # Get updated balance
            result = self.db.execute(
                "SELECT isolated_balance FROM automaton_agents WHERE agent_id = ?",
                (agent_id,)
            ).fetchone()
            
            # Log transaction
            self.db.execute(
                """
                INSERT INTO automaton_transactions (
                    agent_id, transaction_type, amount, balance_after,
                    description, created_at
                ) VALUES (?, 'profit', ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    profit_amount,
                    result['isolated_balance'],
                    trade_details or f"Trading profit: {profit_amount}",
                    datetime.now()
                )
            )
            
            self.db.commit()
            
            logger.info(f"Recorded profit {profit_amount} for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Error recording profit for {agent_id}: {e}")
            self.db.rollback()
            raise
    
    def get_user_ai_portfolio(self, user_id: int) -> Dict:
        """
        Get complete AI portfolio for user
        
        Returns:
            Dict with portfolio summary and agent hierarchy
        """
        try:
            # Get portfolio summary (compatible with SQLite and PostgreSQL)
            summary = self.db.execute(
                """
                SELECT 
                    COALESCE(SUM(isolated_balance), 0) as total_balance,
                    COALESCE(SUM(total_earnings), 0) as total_earnings,
                    COUNT(*) as agent_count,
                    MIN(CASE WHEN generation = 1 THEN agent_id END) as main_agent_id
                FROM automaton_agents
                WHERE user_id = ? AND status = 'active'
                """,
                (user_id,)
            ).fetchone()
            
            if not summary or summary['agent_count'] == 0:
                return {
                    'total_balance': 0,
                    'total_earnings': 0,
                    'agent_count': 0,
                    'main_agent_id': None,
                    'agents': []
                }
            
            # Get all agents with hierarchy
            agents = self.db.execute(
                """
                SELECT * FROM user_ai_hierarchy
                WHERE user_id = ?
                ORDER BY generation, created_at
                """,
                (user_id,)
            ).fetchall()
            
            return {
                'total_balance': float(summary['total_balance']),
                'total_earnings': float(summary['total_earnings']),
                'agent_count': summary['agent_count'],
                'main_agent_id': summary['main_agent_id'],
                'agents': [dict(agent) for agent in agents]
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio for user {user_id}: {e}")
            raise
    
    def get_agent_info(self, agent_id: str) -> Dict:
        """Get detailed info for specific agent"""
        try:
            agent = self.db.execute(
                """
                SELECT * FROM user_ai_hierarchy
                WHERE agent_id = ?
                """,
                (agent_id,)
            ).fetchone()
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            return dict(agent)
            
        except Exception as e:
            logger.error(f"Error getting agent info for {agent_id}: {e}")
            raise
    
    def check_spawn_eligibility(self, agent_id: str) -> Tuple[bool, Optional[float]]:
        """
        Check if agent is eligible to spawn child
        
        Returns:
            (eligible, suggested_child_balance)
        """
        try:
            agent = self.db.execute(
                """
                SELECT total_earnings, isolated_balance, generation
                FROM automaton_agents WHERE agent_id = ?
                """,
                (agent_id,)
            ).fetchone()
            
            if not agent:
                return False, None
            
            # Simple heuristic: can spawn if earnings >= 50% of balance
            # In reality, Automaton AI decides this
            earnings_threshold = agent['isolated_balance'] * 0.5
            
            if agent['total_earnings'] >= earnings_threshold:
                # Suggest allocating 20% of earnings to child
                suggested_balance = agent['total_earnings'] * 0.2
                return True, suggested_balance
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking spawn eligibility for {agent_id}: {e}")
            return False, None


def get_isolated_ai_manager(db):
    """Factory function to get IsolatedAIManager instance"""
    return IsolatedAIManager(db)
