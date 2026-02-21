# Background Services - Orchestration for Automaton Services
# Manages deposit monitor, balance monitor, and performance fee collector

import asyncio
import os
from typing import Optional
from telegram import Bot
from app.deposit_monitor import get_deposit_monitor
from app.balance_monitor import get_balance_monitor
from app.revenue_manager import get_revenue_manager


class BackgroundServices:
    """
    Orchestrates all background services for Automaton
    
    Services:
    - Deposit Monitor (30s interval)
    - Balance Monitor (1h interval)
    - Performance Fee Collector (5m interval)
    """
    
    def __init__(self, database, bot: Optional[Bot] = None):
        """
        Initialize background services
        
        Args:
            database: Database instance
            bot: Telegram Bot instance (optional, for notifications)
        """
        self.db = database
        self.bot = bot
        
        # Initialize services
        self.deposit_monitor = get_deposit_monitor(database)
        self.balance_monitor = get_balance_monitor(database, bot)
        self.revenue_manager = get_revenue_manager(database)
        
        # Service tasks
        self.deposit_task = None
        self.balance_task = None
        self.fee_collector_task = None
        
        # Running state
        self.is_running = False
        
        # Intervals (seconds)
        self.deposit_interval = int(os.getenv('DEPOSIT_CHECK_INTERVAL', '30'))
        self.balance_interval = int(os.getenv('BALANCE_CHECK_INTERVAL', '3600'))  # 1 hour
        self.fee_collector_interval = int(os.getenv('FEE_COLLECTOR_INTERVAL', '300'))  # 5 minutes
        
        print("✅ Background Services initialized")
        print(f"   Deposit Monitor: {self.deposit_interval}s")
        print(f"   Balance Monitor: {self.balance_interval}s ({self.balance_interval // 3600}h)")
        print(f"   Fee Collector: {self.fee_collector_interval}s ({self.fee_collector_interval // 60}m)")
    
    async def _run_deposit_monitor(self):
        """
        Run deposit monitor service
        
        Checks all custodial wallets for deposits every 30 seconds
        """
        print("🚀 Deposit Monitor service started")
        
        while self.is_running:
            try:
                await self.deposit_monitor._check_all_wallets()
                await asyncio.sleep(self.deposit_interval)
            
            except Exception as e:
                print(f"❌ Error in deposit monitor: {e}")
                await asyncio.sleep(self.deposit_interval)
    
    async def _run_balance_monitor(self):
        """
        Run balance monitor service
        
        Checks all active agents for low balances every 1 hour
        """
        print("🚀 Balance Monitor service started")
        
        while self.is_running:
            try:
                await self.balance_monitor._check_all_agents()
                await asyncio.sleep(self.balance_interval)
            
            except Exception as e:
                print(f"❌ Error in balance monitor: {e}")
                await asyncio.sleep(self.balance_interval)
    
    async def _run_fee_collector(self):
        """
        Run performance fee collector service
        
        Collects performance fees from profitable agents every 5 minutes
        """
        print("🚀 Performance Fee Collector service started")
        
        while self.is_running:
            try:
                await self._collect_performance_fees()
                await asyncio.sleep(self.fee_collector_interval)
            
            except Exception as e:
                print(f"❌ Error in fee collector: {e}")
                await asyncio.sleep(self.fee_collector_interval)
    
    async def _collect_performance_fees(self):
        """
        Collect performance fees from all profitable agents
        
        Checks all agents with positive earnings and collects 20% fee
        """
        try:
            if not self.db.supabase_enabled:
                return
            
            # Get all active agents with positive earnings
            result = self.db.supabase_service.table('user_automatons')\
                .select('*')\
                .eq('status', 'active')\
                .gt('total_earnings', 0)\
                .execute()
            
            if not result.data:
                return
            
            agents = result.data
            fees_collected = 0
            
            for agent in agents:
                agent_id = agent['id']
                total_earnings = float(agent.get('total_earnings', 0))
                total_expenses = float(agent.get('total_expenses', 0))
                
                # Calculate net profit
                net_profit = total_earnings - total_expenses
                
                if net_profit > 0:
                    # Check if we've already collected fees for this profit
                    # (by checking if there's a performance_fee transaction)
                    fee_result = self.db.supabase_service.table('automaton_transactions')\
                        .select('amount')\
                        .eq('automaton_id', agent_id)\
                        .eq('type', 'performance_fee')\
                        .execute()
                    
                    total_fees_collected = sum(abs(float(f['amount'])) for f in fee_result.data) if fee_result.data else 0
                    
                    # Calculate expected fee (20% of net profit)
                    expected_fee = net_profit * 0.20
                    
                    # If we haven't collected enough fees yet
                    if total_fees_collected < expected_fee:
                        fee_to_collect = expected_fee - total_fees_collected
                        
                        # Collect the fee
                        result = await self.revenue_manager.collect_performance_fee(
                            agent_id=agent_id,
                            profit=net_profit,
                            description=f'Performance fee (20% of {net_profit:,.2f} profit)'
                        )
                        
                        if result['success']:
                            fees_collected += result['fee_amount']
                            print(f"✅ Collected {result['fee_amount']:,.2f} credits from agent {agent_id}")
            
            if fees_collected > 0:
                print(f"💰 Total performance fees collected: {fees_collected:,.2f} credits")
        
        except Exception as e:
            print(f"❌ Error collecting performance fees: {e}")
    
    async def start(self):
        """
        Start all background services
        
        Launches:
        - Deposit monitor (30s interval)
        - Balance monitor (1h interval)
        - Performance fee collector (5m interval)
        """
        if self.is_running:
            print("⚠️ Background services are already running")
            return
        
        self.is_running = True
        print("🚀 Starting background services...")
        
        # Start deposit monitor
        self.deposit_task = asyncio.create_task(self._run_deposit_monitor())
        
        # Start balance monitor
        self.balance_task = asyncio.create_task(self._run_balance_monitor())
        
        # Start fee collector
        self.fee_collector_task = asyncio.create_task(self._run_fee_collector())
        
        print("✅ All background services started")
    
    async def stop(self):
        """
        Stop all background services gracefully
        
        Cancels all running tasks and waits for cleanup
        """
        if not self.is_running:
            print("⚠️ Background services are not running")
            return
        
        print("🛑 Stopping background services...")
        self.is_running = False
        
        # Cancel all tasks
        tasks = [self.deposit_task, self.balance_task, self.fee_collector_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print("✅ All background services stopped")
    
    async def health_check(self) -> dict:
        """
        Check health status of all services
        
        Returns:
            Dict with service status
        """
        return {
            'running': self.is_running,
            'deposit_monitor': not self.deposit_task.done() if self.deposit_task else False,
            'balance_monitor': not self.balance_task.done() if self.balance_task else False,
            'fee_collector': not self.fee_collector_task.done() if self.fee_collector_task else False
        }


# Singleton instance
_background_services = None

def get_background_services(database, bot: Optional[Bot] = None) -> BackgroundServices:
    """
    Get singleton background services instance
    
    Args:
        database: Database instance
        bot: Telegram Bot instance (optional)
        
    Returns:
        BackgroundServices instance
    """
    global _background_services
    if _background_services is None:
        _background_services = BackgroundServices(database, bot)
    return _background_services
