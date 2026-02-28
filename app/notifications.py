# Notification System - Telegram Notifications for Automaton Events
# All messages in Indonesian with Markdown formatting

from typing import Optional
from telegram import Bot
from telegram.constants import ParseMode


class AutomatonNotifications:
    """
    Handles all Telegram notifications for Automaton events
    
    Features:
    - Deposit confirmations
    - Spawn confirmations
    - Low balance warnings
    - Critical balance alerts
    - Dead agent notifications
    - All messages in Indonesian
    """
    
    def __init__(self, bot: Bot):
        """
        Initialize notification system
        
        Args:
            bot: Telegram Bot instance
        """
        self.bot = bot
        print("✅ Automaton Notifications initialized")
    
    async def send_deposit_confirmation(
        self,
        user_id: int,
        amount: float,
        token: str,
        conway_credits: float,
        agent_name: Optional[str] = None
    ):
        """
        Send deposit confirmation notification
        
        Args:
            user_id: Telegram user ID
            amount: Deposit amount
            token: Token type (USDT/USDC)
            conway_credits: Conway credits credited
            agent_name: Optional agent name
        """
        try:
            agent_text = f" untuk agent *{agent_name}*" if agent_name else ""
            
            message = (
                f"✅ *Deposit Berhasil!*\n\n"
                f"💰 Jumlah: {amount:,.2f} {token}\n"
                f"⚡ Conway Credits: +{conway_credits:,.0f}\n"
                f"{agent_text}\n\n"
                f"🎉 Agent Anda sekarang memiliki lebih banyak bensin untuk trading!\n\n"
                f"Gunakan /agent_status untuk melihat status terbaru."
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            print(f"✅ Sent deposit confirmation to user {user_id}")
        
        except Exception as e:
            print(f"❌ Error sending deposit confirmation: {e}")
    
    async def send_spawn_confirmation(
        self,
        user_id: int,
        agent_name: str,
        agent_wallet: str,
        deposit_address: str,
        spawn_fee: int,
        remaining_credits: int
    ):
        """
        Send agent spawn confirmation notification
        
        Args:
            user_id: Telegram user ID
            agent_name: Agent name
            agent_wallet: Agent wallet address
            deposit_address: Conway deposit address
            spawn_fee: Spawn fee deducted
            remaining_credits: Remaining user credits
        """
        try:
            message = (
                f"🎉 *Agent Berhasil Dibuat!*\n\n"
                f"🤖 *Nama Agent:* {agent_name}\n"
                f"💼 *Wallet:* `{agent_wallet}`\n"
                f"📍 *Deposit Address:*\n`{deposit_address}`\n\n"
                f"💰 *Biaya Spawn:* {spawn_fee:,} kredit\n"
                f"💳 *Sisa Kredit Anda:* {remaining_credits:,}\n\n"
                f"⚠️ *Agent belum aktif!*\n"
                f"Deposit USDT/USDC ke address di atas untuk mengaktifkan agent Anda.\n\n"
                f"💡 *Langkah Selanjutnya:*\n"
                f"1. Gunakan /deposit untuk melihat QR code\n"
                f"2. Kirim USDT/USDC (min 5 USDC)\n"
                f"3. Agent akan aktif otomatis setelah deposit\n\n"
                f"Selamat! Agent Anda siap untuk trading! 🚀"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            print(f"✅ Sent spawn confirmation to user {user_id}")
        
        except Exception as e:
            print(f"❌ Error sending spawn confirmation: {e}")
    
    async def send_low_balance_warning(
        self,
        user_id: int,
        agent_name: str,
        balance: float,
        runtime_days: float
    ):
        """
        Send low balance warning (< 5000 credits)
        
        Args:
            user_id: Telegram user ID
            agent_name: Agent name
            balance: Current balance
            runtime_days: Estimated runtime in days
        """
        try:
            message = (
                f"⚠️ *Peringatan: Saldo Rendah*\n\n"
                f"🤖 *Agent:* {agent_name}\n"
                f"💰 *Saldo:* {balance:,.0f} credits\n"
                f"⏰ *Runtime Tersisa:* ~{runtime_days:.1f} hari\n\n"
                f"💡 Agent Anda akan segera kehabisan bensin!\n\n"
                f"*Rekomendasi:*\n"
                f"Deposit 20-50 USDC untuk runtime optimal.\n\n"
                f"Gunakan /deposit untuk melihat deposit address."
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            print(f"✅ Sent low balance warning to user {user_id}")
        
        except Exception as e:
            print(f"❌ Error sending low balance warning: {e}")
    
    async def send_critical_balance_alert(
        self,
        user_id: int,
        agent_name: str,
        balance: float
    ):
        """
        Send critical balance alert (< 1000 credits)
        
        Args:
            user_id: Telegram user ID
            agent_name: Agent name
            balance: Current balance
        """
        try:
            message = (
                f"🚨 *PERINGATAN KRITIS!* 🚨\n\n"
                f"🤖 *Agent:* {agent_name}\n"
                f"💰 *Saldo:* {balance:,.0f} credits\n"
                f"⏰ *Runtime:* < 1 hari\n\n"
                f"⚠️ *Agent Anda hampir mati!*\n\n"
                f"*SEGERA deposit USDC untuk menjaga agent tetap hidup!*\n\n"
                f"💡 *Cara Deposit:*\n"
                f"1. Gunakan /deposit untuk melihat address\n"
                f"2. Kirim USDC (min 5 USDC)\n"
                f"3. Gunakan Polygon/Base network\n"
                f"4. Credits akan ditambahkan otomatis\n\n"
                f"📊 *Rekomendasi:* Deposit minimal 50 USDC untuk 10 hari runtime.\n\n"
                f"Jangan biarkan agent Anda mati! 💀"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            print(f"✅ Sent critical balance alert to user {user_id}")
        
        except Exception as e:
            print(f"❌ Error sending critical balance alert: {e}")
    
    async def send_dead_agent_notification(
        self,
        user_id: int,
        agent_name: str
    ):
        """
        Send dead agent notification (0 credits)
        
        Args:
            user_id: Telegram user ID
            agent_name: Agent name
        """
        try:
            message = (
                f"💀 *Agent Mati!*\n\n"
                f"🤖 *Agent:* {agent_name}\n"
                f"💰 *Saldo:* 0 credits\n"
                f"📊 *Status:* DEAD\n\n"
                f"⚠️ Agent Anda telah kehabisan bensin dan berhenti beroperasi.\n\n"
                f"*Untuk mengaktifkan kembali:*\n"
                f"1. Deposit USDC ke agent address\n"
                f"2. Agent akan restart otomatis\n"
                f"3. Minimum deposit: 5 USDC\n\n"
                f"Gunakan /deposit untuk melihat deposit address.\n\n"
                f"💡 Tip: Deposit lebih banyak untuk menghindari agent mati lagi!"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            print(f"✅ Sent dead agent notification to user {user_id}")
        
        except Exception as e:
            print(f"❌ Error sending dead agent notification: {e}")
    
    async def send_performance_fee_notification(
        self,
        user_id: int,
        agent_name: str,
        profit: float,
        fee_amount: float,
        remaining_credits: float
    ):
        """
        Send performance fee collection notification
        
        Args:
            user_id: Telegram user ID
            agent_name: Agent name
            profit: Profit amount
            fee_amount: Fee collected
            remaining_credits: Remaining credits after fee
        """
        try:
            message = (
                f"💰 *Performance Fee Collected*\n\n"
                f"🤖 *Agent:* {agent_name}\n"
                f"📈 *Profit:* {profit:,.2f} USDT\n"
                f"💸 *Fee (20%):* {fee_amount:,.2f} credits\n"
                f"💳 *Sisa Credits:* {remaining_credits:,.0f}\n\n"
                f"🎉 Selamat! Agent Anda menghasilkan profit!\n\n"
                f"Platform mengambil 20% dari profit sebagai performance fee."
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            print(f"✅ Sent performance fee notification to user {user_id}")
        
        except Exception as e:
            print(f"❌ Error sending performance fee notification: {e}")


# Singleton instance
_notifications = None

def get_notifications(bot: Bot) -> AutomatonNotifications:
    """
    Get singleton notifications instance
    
    Args:
        bot: Telegram Bot instance
        
    Returns:
        AutomatonNotifications instance
    """
    global _notifications
    if _notifications is None:
        _notifications = AutomatonNotifications(bot)
    return _notifications
