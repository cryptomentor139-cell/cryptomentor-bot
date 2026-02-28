"""
CEO Agent (AUTOMATON Induk) - Business Management Module
Handles user follow-up, analytics, and business development for CryptoMentor AI
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from services import get_database

class CEOAgent:
    """
    CEO Agent untuk mengelola bisnis CryptoMentor AI
    
    Tugas utama:
    - Follow-up user baru
    - Analytics & reporting
    - Marketing campaigns
    - User support
    - Business development
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.db = get_database()
        self.is_running = False
        
        # Load system prompt
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'AUTOMATON_INDUK_PROMPT.md')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
            print("✅ CEO Agent: System prompt loaded")
        except Exception as e:
            print(f"⚠️  CEO Agent: Could not load system prompt: {e}")
            self.system_prompt = "CEO Agent for CryptoMentor AI"
        
        print("🤖 CEO Agent initialized")
    
    async def start(self):
        """Start CEO Agent background tasks"""
        if self.is_running:
            print("⚠️  CEO Agent already running")
            return
        
        self.is_running = True
        print("🚀 CEO Agent started")
        
        # Start background tasks
        asyncio.create_task(self._auto_followup_loop())
        asyncio.create_task(self._daily_report_loop())
        asyncio.create_task(self._inactive_user_reengagement_loop())
    
    async def stop(self):
        """Stop CEO Agent"""
        self.is_running = False
        print("🛑 CEO Agent stopped")
    
    # ==================== AUTO FOLLOW-UP ====================
    
    async def _auto_followup_loop(self):
        """Auto follow-up user baru setiap 6 jam"""
        while self.is_running:
            try:
                await self.followup_new_users()
                # Wait 6 hours
                await asyncio.sleep(6 * 60 * 60)
            except Exception as e:
                print(f"❌ CEO Agent follow-up error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def followup_new_users(self):
        """Follow-up user baru yang belum deposit"""
        try:
            # Get users registered in last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Query database for new users
            # This is a simplified version - adjust based on your database schema
            new_users = self.db.get_users_since(cutoff_time) if hasattr(self.db, 'get_users_since') else []
            
            if not new_users:
                print("ℹ️  CEO Agent: No new users to follow-up")
                return
            
            print(f"📧 CEO Agent: Following up {len(new_users)} new users")
            
            for user in new_users:
                try:
                    user_id = user.get('telegram_id')
                    user_name = user.get('first_name', 'User')
                    
                    # Check if user has AUTOMATON credits
                    credits = self.db.get_automaton_credits(user_id) if hasattr(self.db, 'get_automaton_credits') else 0
                    
                    if credits < 3000:  # Belum deposit minimum
                        message = self._generate_followup_message(user_name, user.get('created_at'))
                        
                        await self.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode='MARKDOWN'
                        )
                        
                        print(f"✅ Follow-up sent to {user_name} ({user_id})")
                        
                        # Rate limiting
                        await asyncio.sleep(2)
                
                except Exception as e:
                    print(f"❌ Failed to follow-up user {user_id}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ CEO Agent followup_new_users error: {e}")
    
    def _generate_followup_message(self, user_name: str, signup_date: str) -> str:
        """Generate personalized follow-up message"""
        return f"""Halo {user_name}! 👋

Selamat datang di CryptoMentor AI! Saya CEO Agent yang akan membantu Anda memaksimalkan pengalaman trading.

Saya lihat Anda baru bergabung dengan kami. Ada yang bisa saya bantu?

Beberapa hal yang mungkin Anda ingin tahu:
✅ Cara deposit USDC untuk AUTOMATON credits
✅ Cara spawn AI trading agent pertama Anda
✅ Tips mengoptimalkan performa agent

Jangan ragu untuk bertanya! Saya di sini untuk memastikan kesuksesan Anda. 🚀

Gunakan /menu untuk melihat semua fitur yang tersedia."""
    
    # ==================== DAILY REPORTS ====================
    
    async def _daily_report_loop(self):
        """Generate daily report setiap jam 21:00"""
        while self.is_running:
            try:
                now = datetime.utcnow()
                
                # Calculate next 21:00 UTC
                next_run = now.replace(hour=21, minute=0, second=0, microsecond=0)
                if now.hour >= 21:
                    next_run += timedelta(days=1)
                
                # Wait until next run
                wait_seconds = (next_run - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                # Generate report
                await self.generate_daily_report()
                
            except Exception as e:
                print(f"❌ CEO Agent daily report error: {e}")
                await asyncio.sleep(60)
    
    async def generate_daily_report(self):
        """Generate and send daily business report"""
        try:
            print("📊 CEO Agent: Generating daily report...")
            
            # Collect metrics
            today = datetime.utcnow().date()
            
            metrics = {
                'new_users': self._count_new_users_today(),
                'active_users': self._count_active_users_today(),
                'premium_users': self._count_premium_users(),
                'deposits': self._sum_deposits_today(),
                'revenue': self._calculate_revenue_today(),
                'agents_spawned': self._count_agents_spawned_today(),
                'active_agents': self._count_active_agents()
            }
            
            # Generate report text
            report = self._format_daily_report(metrics, today)
            
            # Send to admins
            admin_ids = [
                int(os.getenv('ADMIN1', 0)),
                int(os.getenv('ADMIN2', 0)),
                int(os.getenv('ADMIN3', 0))
            ]
            
            for admin_id in admin_ids:
                if admin_id > 0:
                    try:
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=report,
                            parse_mode='MARKDOWN'
                        )
                        print(f"✅ Daily report sent to admin {admin_id}")
                    except Exception as e:
                        print(f"❌ Failed to send report to {admin_id}: {e}")
            
            print("✅ CEO Agent: Daily report generated")
            
        except Exception as e:
            print(f"❌ CEO Agent generate_daily_report error: {e}")
    
    def _format_daily_report(self, metrics: Dict, date) -> str:
        """Format daily report message"""
        return f"""📊 **LAPORAN HARIAN CRYPTOMENTOR AI**

📅 Tanggal: {date.strftime('%d %B %Y')}

👥 **USER METRICS:**
• Total Users Baru: {metrics['new_users']}
• Active Users: {metrics['active_users']}
• Premium Users: {metrics['premium_users']}

💰 **REVENUE:**
• Deposits Hari Ini: ${metrics['deposits']:.2f}
• Revenue Hari Ini: ${metrics['revenue']:.2f}

🤖 **AI AGENT:**
• Agents Spawned: {metrics['agents_spawned']}
• Active Agents: {metrics['active_agents']}

📈 **INSIGHTS:**
• Conversion Rate: {self._calculate_conversion_rate():.1f}%
• User Engagement: {self._calculate_engagement_rate():.1f}%

🎯 **ACTION ITEMS:**
1. Follow-up {metrics['new_users']} user baru
2. Re-engage inactive users
3. Monitor agent performance

💡 Gunakan /admin untuk manage platform

---
Generated by CEO Agent 🤖"""
    
    # ==================== INACTIVE USER RE-ENGAGEMENT ====================
    
    async def _inactive_user_reengagement_loop(self):
        """Re-engage inactive users setiap minggu"""
        while self.is_running:
            try:
                await self.reengage_inactive_users()
                # Wait 7 days
                await asyncio.sleep(7 * 24 * 60 * 60)
            except Exception as e:
                print(f"❌ CEO Agent re-engagement error: {e}")
                await asyncio.sleep(60)
    
    async def reengage_inactive_users(self):
        """Send re-engagement message to inactive users"""
        try:
            # Get users inactive for >7 days
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            # This is simplified - adjust based on your database schema
            inactive_users = []  # self.db.get_inactive_users(cutoff_time)
            
            if not inactive_users:
                print("ℹ️  CEO Agent: No inactive users to re-engage")
                return
            
            print(f"📧 CEO Agent: Re-engaging {len(inactive_users)} inactive users")
            
            for user in inactive_users:
                try:
                    user_id = user.get('telegram_id')
                    user_name = user.get('first_name', 'User')
                    
                    message = f"""Halo {user_name}! 👋

Kami kangen Anda! Sudah lama tidak terlihat di CryptoMentor AI.

🎁 **Special Comeback Offer:**
• 200 Bot Credits GRATIS
• Diskon 20% Premium
• Auto Signal trial 7 hari

Kembali sekarang dan nikmati benefitnya! 🚀

Gunakan /menu untuk mulai lagi."""
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='MARKDOWN'
                    )
                    
                    print(f"✅ Re-engagement sent to {user_name} ({user_id})")
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                
                except Exception as e:
                    print(f"❌ Failed to re-engage user {user_id}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ CEO Agent reengage_inactive_users error: {e}")
    
    # ==================== METRICS HELPERS ====================
    
    def _count_new_users_today(self) -> int:
        """Count new users registered today"""
        try:
            # Simplified - adjust based on your database schema
            return 0  # self.db.count_new_users_today()
        except:
            return 0
    
    def _count_active_users_today(self) -> int:
        """Count active users today"""
        try:
            return 0  # self.db.count_active_users_today()
        except:
            return 0
    
    def _count_premium_users(self) -> int:
        """Count total premium users"""
        try:
            return 0  # self.db.count_premium_users()
        except:
            return 0
    
    def _sum_deposits_today(self) -> float:
        """Sum deposits today"""
        try:
            return 0.0  # self.db.sum_deposits_today()
        except:
            return 0.0
    
    def _calculate_revenue_today(self) -> float:
        """Calculate revenue today"""
        try:
            return 0.0  # self.db.calculate_revenue_today()
        except:
            return 0.0
    
    def _count_agents_spawned_today(self) -> int:
        """Count agents spawned today"""
        try:
            return 0  # self.db.count_agents_spawned_today()
        except:
            return 0
    
    def _count_active_agents(self) -> int:
        """Count currently active agents"""
        try:
            return 0  # self.db.count_active_agents()
        except:
            return 0
    
    def _calculate_conversion_rate(self) -> float:
        """Calculate conversion rate (free → premium)"""
        try:
            return 0.0  # (premium_users / total_users) * 100
        except:
            return 0.0
    
    def _calculate_engagement_rate(self) -> float:
        """Calculate user engagement rate"""
        try:
            return 0.0  # (active_users / total_users) * 100
        except:
            return 0.0


# Singleton instance
_ceo_agent = None

def get_ceo_agent(bot) -> CEOAgent:
    """Get singleton CEO Agent instance"""
    global _ceo_agent
    if _ceo_agent is None:
        _ceo_agent = CEOAgent(bot)
    return _ceo_agent
