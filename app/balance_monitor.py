# Balance Monitor Service
# Monitors agent Conway credit balances and sends low balance alerts

import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from app.conway_integration import get_conway_client


class BalanceMonitor:
    """
    Monitors agent balances and sends alerts
    
    Features:
    - Hourly balance checking for all active agents
    - Low balance warnings (< 5000 credits)
    - Critical balance alerts (< 1000 credits)
    - Runtime estimation
    - Telegram notifications
    """
    
    def __init__(self, db, bot=None):
        """
        Initialize balance monitor
        
        Args:
            db: Database instance
            bot: Telegram bot instance (optional, for notifications)
        """
        self.db = db
        self.bot = bot
        self.conway = get_conway_client()
        
        # Alert thresholds
        self.warning_threshold = 5000  # Credits
        self.critical_threshold = 1000  # Credits
        
        # Check interval (1 hour)
        self.check_interval = int(os.getenv('BALANCE_CHECK_INTERVAL', '3600'))  # seconds
        
        # Daily consumption rates by tier (credits/day)
        self.consumption_rates = {
            'normal': 200,
            'low_compute': 100,
            'critical': 50
        }
        
        # Track last alert sent to avoid spam
        self.last_alerts: Dict[str, datetime] = {}
        
        # Running state
        self.is_running = False
        
        print(f"✅ Balance Monitor initialized")
        print(f"   Warning Threshold: {self.warning_threshold} credits")
        print(f"   Critical Threshold: {self.critical_threshold} credits")
        print(f"   Check Interval: {self.check_interval}s ({self.check_interval // 3600}h)")
    
    def estimate_runtime(self, conway_credits: float, tier: str = 'normal') -> float:
        """
        Estimate remaining runtime in days
        
        Args:
            conway_credits: Current credit balance
            tier: Survival tier (normal/low_compute/critical)
            
        Returns:
            Estimated days remaining
        """
        if conway_credits <= 0:
            return 0
        
        daily_rate = self.consumption_rates.get(tier, 200)
        return conway_credits / daily_rate
    
    async def send_low_balance_alert(
        self,
        user_id: int,
        agent_name: str,
        balance: float,
        level: str,
        runtime_days: float
    ):
        """
        Send Telegram notification for low balance
        
        Args:
            user_id: Telegram user ID
            agent_name: Agent name
            balance: Current balance
            level: Alert level (warning/critical)
            runtime_days: Estimated runtime in days
        """
        if not self.bot:
            print(f"⚠️ No bot instance, cannot send alert to user {user_id}")
            return
        
        try:
            if level == 'critical':
                emoji = '🚨'
                title = 'PERINGATAN KRITIS'
                urgency = 'SEGERA'
                message = (
                    f"{emoji} **{title}** {emoji}\n\n"
                    f"🤖 **Agent:** {agent_name}\n"
                    f"💰 **Saldo:** {balance:,.0f} credits\n"
                    f"⏰ **Runtime:** < 1 hari\n\n"
                    f"⚠️ Agent Anda hampir mati! {urgency} deposit USDC untuk menjaga agent tetap hidup.\n\n"
                    f"💡 **Cara Deposit:**\n"
                    f"1. Klik /agent_status untuk melihat deposit address\n"
                    f"2. Kirim USDC ke address tersebut (Base network)\n"
                    f"3. Minimum deposit: 5 USDC\n"
                    f"4. 1 USDC = 100 credits (setelah fee 2%)\n\n"
                    f"📊 Rekomendasi: Deposit minimal 50 USDC untuk 10 hari runtime"
                )
            else:  # warning
                emoji = '⚠️'
                title = 'Peringatan Saldo Rendah'
                message = (
                    f"{emoji} **{title}**\n\n"
                    f"🤖 **Agent:** {agent_name}\n"
                    f"💰 **Saldo:** {balance:,.0f} credits\n"
                    f"⏰ **Runtime:** ~{runtime_days:.1f} hari\n\n"
                    f"💡 Agent Anda akan segera kehabisan bensin. Pertimbangkan untuk deposit USDC.\n\n"
                    f"📊 Rekomendasi: Deposit 20-50 USDC untuk runtime optimal"
                )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            print(f"✅ Sent {level} alert to user {user_id} for agent {agent_name}")
        
        except Exception as e:
            print(f"❌ Error sending alert to user {user_id}: {e}")
    
    async def _check_agent_balance(self, agent: Dict) -> bool:
        """
        Check a single agent's balance and send alerts if needed
        
        Args:
            agent: Agent record from database
            
        Returns:
            True if alert was sent
        """
        try:
            agent_id = agent['id']
            user_id = agent['user_id']
            agent_name = agent['agent_name']
            deposit_address = agent['conway_deposit_address']
            current_balance = agent['conway_credits']
            survival_tier = agent['survival_tier']
            
            # Get fresh balance from Conway
            fresh_balance = self.conway.get_credit_balance(deposit_address)
            if fresh_balance is not None:
                current_balance = fresh_balance
                
                # Update database with fresh balance
                if self.db.supabase_enabled:
                    self.db.supabase_service.table('user_automatons').update({
                        'conway_credits': fresh_balance,
                        'last_active': datetime.now().isoformat()
                    }).eq('id', agent_id).execute()
            
            # Estimate runtime
            runtime_days = self.estimate_runtime(current_balance, survival_tier)
            
            # Check if we need to send an alert
            alert_key = f"{agent_id}_{user_id}"
            last_alert = self.last_alerts.get(alert_key)
            
            # Don't spam alerts - wait at least 6 hours between alerts
            if last_alert:
                hours_since_alert = (datetime.now() - last_alert).total_seconds() / 3600
                if hours_since_alert < 6:
                    return False
            
            # Critical alert (< 1000 credits)
            if 0 < current_balance < self.critical_threshold:
                await self.send_low_balance_alert(
                    user_id=user_id,
                    agent_name=agent_name,
                    balance=current_balance,
                    level='critical',
                    runtime_days=runtime_days
                )
                self.last_alerts[alert_key] = datetime.now()
                return True
            
            # Warning alert (< 5000 credits)
            elif self.critical_threshold <= current_balance < self.warning_threshold:
                await self.send_low_balance_alert(
                    user_id=user_id,
                    agent_name=agent_name,
                    balance=current_balance,
                    level='warning',
                    runtime_days=runtime_days
                )
                self.last_alerts[alert_key] = datetime.now()
                return True
            
            return False
        
        except Exception as e:
            print(f"❌ Error checking agent balance: {e}")
            return False
    
    async def _check_all_agents(self):
        """
        Check all active agents for low balances
        """
        try:
            if not self.db.supabase_enabled:
                print("⚠️ Supabase not enabled, skipping balance check")
                return
            
            # Get all active agents
            result = self.db.supabase_service.table('user_automatons').select('*').eq('status', 'active').execute()
            
            if not result.data:
                print("ℹ️ No active agents to check")
                return
            
            agents = result.data
            print(f"🔍 Checking {len(agents)} active agents...")
            
            alerts_sent = 0
            for agent in agents:
                if await self._check_agent_balance(agent):
                    alerts_sent += 1
            
            if alerts_sent > 0:
                print(f"✅ Sent {alerts_sent} low balance alerts")
            else:
                print(f"✅ All agents have sufficient balance")
        
        except Exception as e:
            print(f"❌ Error checking agents: {e}")
    
    async def start(self):
        """
        Start the balance monitoring service
        
        Runs continuously, checking agents every check_interval seconds
        """
        if self.is_running:
            print("⚠️ Balance monitor is already running")
            return
        
        self.is_running = True
        print(f"🚀 Balance monitor started (checking every {self.check_interval // 3600}h)")
        
        while self.is_running:
            try:
                await self._check_all_agents()
                await asyncio.sleep(self.check_interval)
            
            except Exception as e:
                print(f"❌ Error in balance monitor loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the balance monitoring service"""
        self.is_running = False
        print("🛑 Balance monitor stopped")


# Singleton instance
_balance_monitor = None

def get_balance_monitor(db, bot=None) -> BalanceMonitor:
    """
    Get singleton balance monitor instance
    
    Args:
        db: Database instance
        bot: Telegram bot instance (optional)
        
    Returns:
        BalanceMonitor instance
    """
    global _balance_monitor
    if _balance_monitor is None:
        _balance_monitor = BalanceMonitor(db, bot)
    return _balance_monitor
