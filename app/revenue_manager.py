# Revenue Manager - Platform Fee Collection and Reporting
# Handles deposit fees, performance fees, and revenue analytics

import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class RevenueManager:
    """
    Manages platform revenue collection and reporting
    
    Features:
    - Deposit fee calculation (2%)
    - Performance fee calculation (20%)
    - Fee collection from agent credits
    - Revenue reporting (daily/weekly/monthly)
    - Top revenue-generating agents
    """
    
    def __init__(self, db):
        """
        Initialize Revenue Manager
        
        Args:
            db: Database instance (Supabase-enabled)
        """
        self.db = db
        
        # Fee rates
        self.deposit_fee_rate = 0.02  # 2%
        self.performance_fee_rate = 0.20  # 20%
        
        print("✅ Revenue Manager initialized")
        print(f"   Deposit Fee: {self.deposit_fee_rate * 100}%")
        print(f"   Performance Fee: {self.performance_fee_rate * 100}%")
    
    def calculate_deposit_fee(self, amount: float) -> Tuple[float, float]:
        """
        Calculate 2% deposit fee
        
        Args:
            amount: Deposit amount in USDC
            
        Returns:
            Tuple of (net_amount, fee_amount)
        """
        fee_amount = amount * self.deposit_fee_rate
        net_amount = amount - fee_amount
        
        return (net_amount, fee_amount)
    
    def calculate_performance_fee(self, profit: float) -> float:
        """
        Calculate 20% performance fee
        
        Args:
            profit: Realized profit amount
            
        Returns:
            Performance fee amount
        """
        if profit <= 0:
            return 0
        
        return profit * self.performance_fee_rate
    
    async def collect_performance_fee(
        self,
        agent_id: str,
        profit: float,
        description: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Collect 20% performance fee from agent profits
        
        Steps:
        1. Calculate 20% of profit
        2. Transfer fee from agent credits
        3. Record transaction
        4. Update platform revenue
        
        Args:
            agent_id: Agent UUID
            profit: Realized profit amount
            description: Optional description
            
        Returns:
            Dict with 'success', 'fee_amount', 'message'
        """
        try:
            if not self.db.supabase_enabled:
                return {
                    'success': False,
                    'message': 'Supabase not enabled'
                }
            
            # Calculate fee
            fee_amount = self.calculate_performance_fee(profit)
            
            if fee_amount <= 0:
                return {
                    'success': False,
                    'message': 'No profit to collect fee from'
                }
            
            # Get agent record
            result = self.db.supabase_service.table('user_automatons').select('*').eq('id', agent_id).execute()
            
            if not result.data:
                return {
                    'success': False,
                    'message': 'Agent not found'
                }
            
            agent = result.data[0]
            user_id = agent['user_id']
            current_credits = agent['conway_credits']
            
            # Check if agent has enough credits for fee
            if current_credits < fee_amount:
                print(f"⚠️ Agent {agent_id} has insufficient credits for performance fee")
                # Record as pending fee collection
                return {
                    'success': False,
                    'message': 'Insufficient credits for fee',
                    'fee_amount': fee_amount,
                    'pending': True
                }
            
            # Deduct fee from agent credits
            new_credits = current_credits - fee_amount
            self.db.supabase_service.table('user_automatons').update({
                'conway_credits': new_credits
            }).eq('id', agent_id).execute()
            
            # Record transaction in automaton_transactions
            self.db.supabase_service.table('automaton_transactions').insert({
                'automaton_id': agent_id,
                'type': 'performance_fee',
                'amount': -fee_amount,
                'description': description or f'Performance fee (20% of {profit:,.2f} profit)',
                'timestamp': datetime.now().isoformat()
            }).execute()
            
            # Record in platform_revenue
            self.db.supabase_service.table('platform_revenue').insert({
                'source': 'performance_fee',
                'amount': fee_amount,
                'agent_id': agent_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }).execute()
            
            print(f"✅ Collected performance fee: {fee_amount:,.2f} credits from agent {agent_id}")
            
            # LINEAGE INTEGRATION: Distribute 10% of gross profit to parent
            # Import here to avoid circular dependency
            from app.lineage_integration import on_performance_fee_collected
            await on_performance_fee_collected(agent_id, profit, fee_amount)
            
            return {
                'success': True,
                'fee_amount': fee_amount,
                'remaining_credits': new_credits,
                'message': 'Performance fee collected successfully'
            }
        
        except Exception as e:
            print(f"❌ Error collecting performance fee: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    async def record_deposit_fee(
        self,
        user_id: int,
        deposit_amount: float,
        fee_amount: float,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Record deposit fee in platform_revenue
        
        Args:
            user_id: Telegram user ID
            deposit_amount: Original deposit amount
            fee_amount: Fee amount collected
            agent_id: Optional agent ID
            
        Returns:
            True if successful
        """
        try:
            if not self.db.supabase_enabled:
                return False
            
            self.db.supabase_service.table('platform_revenue').insert({
                'source': 'deposit_fee',
                'amount': fee_amount,
                'agent_id': agent_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }).execute()
            
            print(f"✅ Recorded deposit fee: {fee_amount:,.2f} USDC from user {user_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error recording deposit fee: {e}")
            return False
    
    def get_revenue_report(self, period: str = 'daily') -> Dict[str, any]:
        """
        Generate revenue report for period
        
        Args:
            period: Report period (daily/weekly/monthly/all)
            
        Returns:
            Dict with revenue breakdown
        """
        try:
            if not self.db.supabase_enabled:
                return {
                    'success': False,
                    'message': 'Supabase not enabled'
                }
            
            # Calculate date range
            now = datetime.now()
            if period == 'daily':
                start_date = now - timedelta(days=1)
            elif period == 'weekly':
                start_date = now - timedelta(days=7)
            elif period == 'monthly':
                start_date = now - timedelta(days=30)
            else:  # all
                start_date = datetime(2020, 1, 1)  # Far past
            
            # Get all revenue records in period
            result = self.db.supabase_service.table('platform_revenue').select('*').gte(
                'timestamp', start_date.isoformat()
            ).execute()
            
            if not result.data:
                return {
                    'success': True,
                    'period': period,
                    'total_revenue': 0,
                    'deposit_fees': 0,
                    'performance_fees': 0,
                    'spawn_fees': 0,
                    'transaction_count': 0,
                    'top_agents': []
                }
            
            records = result.data
            
            # Calculate totals by source
            deposit_fees = sum(r['amount'] for r in records if r['source'] == 'deposit_fee')
            performance_fees = sum(r['amount'] for r in records if r['source'] == 'performance_fee')
            spawn_fees = sum(r['amount'] for r in records if r['source'] == 'spawn_fee')
            total_revenue = deposit_fees + performance_fees + spawn_fees
            
            # Get top revenue-generating agents
            agent_revenue = {}
            for record in records:
                if record['agent_id']:
                    agent_id = record['agent_id']
                    agent_revenue[agent_id] = agent_revenue.get(agent_id, 0) + record['amount']
            
            # Sort and get top 10
            top_agents = sorted(
                agent_revenue.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Get agent names for top agents
            top_agents_with_names = []
            for agent_id, revenue in top_agents:
                agent_result = self.db.supabase_service.table('user_automatons').select(
                    'agent_name, user_id'
                ).eq('id', agent_id).execute()
                
                if agent_result.data:
                    agent = agent_result.data[0]
                    top_agents_with_names.append({
                        'agent_id': agent_id,
                        'agent_name': agent['agent_name'],
                        'user_id': agent['user_id'],
                        'revenue': revenue
                    })
            
            return {
                'success': True,
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
                'total_revenue': total_revenue,
                'deposit_fees': deposit_fees,
                'performance_fees': performance_fees,
                'spawn_fees': spawn_fees,
                'transaction_count': len(records),
                'top_agents': top_agents_with_names,
                'breakdown': {
                    'deposit_fee_pct': (deposit_fees / total_revenue * 100) if total_revenue > 0 else 0,
                    'performance_fee_pct': (performance_fees / total_revenue * 100) if total_revenue > 0 else 0,
                    'spawn_fee_pct': (spawn_fees / total_revenue * 100) if total_revenue > 0 else 0
                }
            }
        
        except Exception as e:
            print(f"❌ Error generating revenue report: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_agent_revenue_contribution(self, agent_id: str) -> Dict[str, any]:
        """
        Get total revenue contribution from a specific agent
        
        Args:
            agent_id: Agent UUID
            
        Returns:
            Dict with agent revenue details
        """
        try:
            if not self.db.supabase_enabled:
                return {
                    'success': False,
                    'message': 'Supabase not enabled'
                }
            
            # Get all revenue from this agent
            result = self.db.supabase_service.table('platform_revenue').select('*').eq(
                'agent_id', agent_id
            ).execute()
            
            if not result.data:
                return {
                    'success': True,
                    'agent_id': agent_id,
                    'total_revenue': 0,
                    'spawn_fee': 0,
                    'performance_fees': 0,
                    'transaction_count': 0
                }
            
            records = result.data
            
            spawn_fee = sum(r['amount'] for r in records if r['source'] == 'spawn_fee')
            performance_fees = sum(r['amount'] for r in records if r['source'] == 'performance_fee')
            total_revenue = spawn_fee + performance_fees
            
            return {
                'success': True,
                'agent_id': agent_id,
                'total_revenue': total_revenue,
                'spawn_fee': spawn_fee,
                'performance_fees': performance_fees,
                'transaction_count': len(records)
            }
        
        except Exception as e:
            print(f"❌ Error getting agent revenue: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }


# Singleton instance
_revenue_manager = None

def get_revenue_manager(db):
    """
    Get singleton Revenue Manager instance
    
    Args:
        db: Database instance
        
    Returns:
        RevenueManager instance
    """
    global _revenue_manager
    if _revenue_manager is None:
        _revenue_manager = RevenueManager(db)
    return _revenue_manager
