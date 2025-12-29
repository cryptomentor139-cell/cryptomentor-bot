
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

# Import existing components
from snd_zone_detector import detect_snd_zones
from app.supabase_repo import get_supabase_client
from app.users_repo import get_vuser_by_telegram_id

logger = logging.getLogger(__name__)

class LifetimeAutoSignalSystem:
    """Auto-signal system exclusively for LIFETIME premium users"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.is_running = False
        
        # Signal configuration
        self.target_symbols = [
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'MATIC', 'AVAX', 'UNI',
            'LINK', 'LTC', 'ATOM', 'ICP', 'NEAR', 'APT', 'FTM', 'ALGO', 'VET', 'FLOW'
        ]
        self.min_signal_confidence = 75
        self.max_signals_per_batch = 3
        
        logger.info(f"🎯 Lifetime Auto-Signal System initialized for {len(self.target_symbols)} coins")

    async def start_scheduler(self):
        """Start the auto-signal scheduler"""
        if self.is_running:
            logger.warning("Auto-signal scheduler already running")
            return
            
        try:
            # Schedule signals every 4 hours for lifetime users
            self.scheduler.add_job(
                self.scan_and_broadcast_signals,
                CronTrigger(hour='0,4,8,12,16,20', minute=0),  # Every 4 hours
                id='lifetime_auto_signals',
                name='Lifetime Auto Signals',
                replace_existing=True
            )
            
            # Schedule daily premium market summary
            self.scheduler.add_job(
                self.send_daily_market_summary,
                CronTrigger(hour=6, minute=0),  # 6 AM UTC daily
                id='daily_market_summary',
                name='Daily Market Summary for Lifetime Users',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Lifetime Auto-Signal Scheduler started")
            logger.info("📅 Signals scheduled every 4 hours")
            logger.info("📊 Daily market summary at 6 AM UTC")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise

    async def stop_scheduler(self):
        """Stop the auto-signal scheduler"""
        if not self.is_running:
            return
            
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("🛑 Lifetime Auto-Signal Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")

    async def get_lifetime_users(self) -> List[int]:
        """Get all LIFETIME premium users from Supabase"""
        try:
            supabase = get_supabase_client()
            
            # Query for lifetime users only
            result = supabase.table("v_users").select("telegram_id").eq("is_lifetime", True).eq("premium_active", True).execute()
            
            if not result.data:
                logger.warning("No lifetime users found")
                return []
            
            user_ids = [row["telegram_id"] for row in result.data if row["telegram_id"]]
            logger.info(f"📊 Found {len(user_ids)} lifetime users eligible for auto-signals")
            
            return user_ids
            
        except Exception as e:
            logger.error(f"❌ Error fetching lifetime users: {e}")
            return []

    async def scan_and_broadcast_signals(self):
        """Main function to scan for SnD signals and broadcast to lifetime users"""
        start_time = datetime.now(timezone.utc)
        logger.info(f"🔍 Starting auto-signal scan at {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            # Get lifetime users first
            lifetime_users = await self.get_lifetime_users()
            if not lifetime_users:
                logger.warning("⚠️ No lifetime users found, skipping signal broadcast")
                return

            # Scan for high-quality SnD signals
            signals = await self.scan_for_snd_signals()
            
            if not signals:
                logger.info("📊 No high-quality signals found in this scan")
                return

            # Broadcast signals to lifetime users
            success_count = await self.broadcast_signals(signals, lifetime_users)
            
            scan_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"✅ Auto-signal scan completed in {scan_duration:.1f}s")
            logger.info(f"📤 Sent {len(signals)} signals to {success_count}/{len(lifetime_users)} lifetime users")
            
        except Exception as e:
            logger.error(f"❌ Auto-signal scan failed: {e}")
            import traceback
            traceback.print_exc()

    async def scan_for_snd_signals(self) -> List[Dict[str, Any]]:
        """Scan symbols for high-quality SnD signals"""
        signals = []
        
        for symbol in self.target_symbols:
            try:
                # Use existing SnD zone detection
                snd_result = detect_snd_zones(f"{symbol}USDT", "1h", limit=100)
                
                if 'error' in snd_result:
                    continue
                
                # Check if we have a valid entry signal
                if (snd_result.get('entry_signal') and 
                    snd_result.get('signal_strength', 0) >= self.min_signal_confidence):
                    
                    signal_data = {
                        'symbol': symbol,
                        'direction': snd_result['entry_signal'].replace('_DEMAND', '').replace('_SUPPLY', ''),
                        'signal_type': snd_result['entry_signal'],
                        'confidence': snd_result['signal_strength'],
                        'current_price': snd_result['current_price'],
                        'entry_price': snd_result['entry_price'],
                        'stop_loss': snd_result['stop_loss'],
                        'take_profit': snd_result['take_profit'],
                        'active_demand': snd_result.get('active_demand'),
                        'active_supply': snd_result.get('active_supply'),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    
                    signals.append(signal_data)
                    logger.info(f"✅ High-quality signal found: {symbol} {signal_data['direction']} ({signal_data['confidence']:.1f}%)")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error scanning {symbol}: {e}")
                continue
        
        # Sort by confidence and return top signals
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        return signals[:self.max_signals_per_batch]

    async def broadcast_signals(self, signals: List[Dict[str, Any]], lifetime_users: List[int]) -> int:
        """Broadcast signals to lifetime users with priority delivery"""
        if not signals or not lifetime_users:
            return 0
        
        message = self.format_lifetime_signals_message(signals)
        success_count = 0
        
        for user_id in lifetime_users:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                success_count += 1
                
                # Rate limiting to avoid Telegram API limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Failed to send signal to lifetime user {user_id}: {e}")
                continue
        
        return success_count

    def format_lifetime_signals_message(self, signals: List[Dict[str, Any]]) -> str:
        """Format signals message for lifetime users"""
        current_time = datetime.now(timezone.utc)
        
        message = f"""🚨 <b>LIFETIME AUTO SIGNALS</b> 🚨

⏰ <b>Signal Time:</b> {current_time.strftime('%H:%M UTC')}
👑 <b>Exclusive for LIFETIME Users</b>
📊 <b>Supply & Demand Analysis</b>

"""

        for i, signal in enumerate(signals, 1):
            direction_emoji = "🟢" if signal['direction'] == 'BUY' else "🔴"
            confidence_emoji = "🔥" if signal['confidence'] >= 85 else "⭐"
            
            message += f"""<b>{i}. {signal['symbol']}/USDT</b> {direction_emoji}

{confidence_emoji} <b>Signal:</b> {signal['direction']}
💪 <b>Confidence:</b> {signal['confidence']:.1f}%
💰 <b>Entry:</b> ${signal['entry_price']:.6f}
🛑 <b>Stop Loss:</b> ${signal['stop_loss']:.6f}
🎯 <b>Take Profit:</b> ${signal['take_profit']:.6f}
📈 <b>Current:</b> ${signal['current_price']:.6f}

"""

        message += f"""⚡ <b>LIFETIME PRIORITY FEATURES:</b>
• First to receive premium signals
• Supply & Demand zone analysis
• Higher accuracy threshold ({self.min_signal_confidence}%+)
• 24/7 automated scanning

⚠️ <b>Risk Management:</b>
• Use proper position sizing
• Follow stop-loss levels
• DYOR before trading

🔔 Next signals in ~4 hours
👑 Thank you for being a LIFETIME member!"""

        return message

    async def send_daily_market_summary(self):
        """Send daily market summary to lifetime users"""
        try:
            lifetime_users = await self.get_lifetime_users()
            if not lifetime_users:
                return
            
            # Get market data for summary
            market_summary = await self.generate_market_summary()
            
            for user_id in lifetime_users:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=market_summary,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to send daily summary to {user_id}: {e}")
                    continue
            
            logger.info(f"📊 Daily market summary sent to {len(lifetime_users)} lifetime users")
            
        except Exception as e:
            logger.error(f"❌ Daily market summary failed: {e}")

    async def generate_market_summary(self) -> str:
        """Generate daily market summary for lifetime users"""
        current_time = datetime.now(timezone.utc)
        
        return f"""📊 <b>DAILY MARKET SUMMARY</b>

🌅 <b>Morning Briefing:</b> {current_time.strftime('%Y-%m-%d')}
👑 <b>Exclusive for LIFETIME Members</b>

<b>🎯 Today's Focus Areas:</b>
• Major support/resistance levels
• High-volume breakout candidates  
• Supply & demand zone updates
• Futures market sentiment

<b>⚡ Auto-Signal Status:</b>
✅ Active - Scanning every 4 hours
📊 Monitoring {len(self.target_symbols)} premium assets
🎯 Minimum confidence: {self.min_signal_confidence}%

<b>💡 Trading Reminders:</b>
• Check economic calendar
• Monitor Bitcoin dominance
• Respect risk management rules
• Stay updated on market news

<b>🔔 Next Signal Scan:</b> Within 4 hours
👑 Thank you for your lifetime membership!

<i>This summary is exclusive to LIFETIME users</i>"""

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the auto-signal system"""
        return {
            'is_running': self.is_running,
            'target_symbols': len(self.target_symbols),
            'min_confidence': self.min_signal_confidence,
            'max_signals_per_batch': self.max_signals_per_batch,
            'scheduler_jobs': len(self.scheduler.get_jobs()) if self.scheduler else 0,
            'next_scan': self.scheduler.get_job('lifetime_auto_signals').next_run_time if self.scheduler and self.is_running else None
        }

# Integration functions
async def start_lifetime_auto_signals(bot: Bot) -> LifetimeAutoSignalSystem:
    """Initialize and start the lifetime auto-signal system"""
    system = LifetimeAutoSignalSystem(bot)
    await system.start_scheduler()
    return system

async def stop_lifetime_auto_signals(system: LifetimeAutoSignalSystem):
    """Stop the lifetime auto-signal system"""
    if system:
        await system.stop_scheduler()
