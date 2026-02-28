"""
Weekly Report Generator - Generate dan kirim laporan mingguan ke admin
"""
import os
from datetime import datetime, timedelta
from telegram import Bot
import logging

logger = logging.getLogger(__name__)

class WeeklyReportGenerator:
    """Generate laporan mingguan winrate signal"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_ids = self._load_admin_ids()
    
    def _load_admin_ids(self):
        """Load admin IDs dari environment"""
        admin_ids = []
        for key in ['ADMIN1', 'ADMIN2', 'ADMIN3', 'ADMIN_IDS']:
            value = os.getenv(key)
            if value:
                try:
                    if ',' in value:
                        admin_ids.extend([int(aid.strip()) for aid in value.split(',') if aid.strip()])
                    else:
                        admin_ids.append(int(value))
                except ValueError:
                    continue
        return list(set(admin_ids))
    
    async def generate_report(self):
        """Generate laporan mingguan"""
        from app.signal_logger import signal_logger
        
        stats = signal_logger.get_weekly_stats()
        
        # Format tanggal
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        report = f"""📊 **LAPORAN MINGGUAN SIGNAL**
🗓️ Periode: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}

━━━━━━━━━━━━━━━━━━━━━━

📈 **PERFORMA SIGNAL:**
• Total Signal: {stats['total_signals']}
• Win: {stats['wins']} ✅
• Loss: {stats['losses']} ❌
• Winrate: {stats['winrate']}% 🎯
• Avg PnL: {stats['avg_pnl']:+.2f}%

━━━━━━━━━━━━━━━━━━━━━━

👥 **AKTIVITAS USER:**
• Total Prompts: {stats['total_prompts']}
• Rata-rata per hari: {stats['total_prompts'] // 7}

━━━━━━━━━━━━━━━━━━━━━━

📊 **ANALISIS:**
"""
        
        # Analisis winrate
        if stats['winrate'] >= 70:
            report += "✅ Performa EXCELLENT! Signal sangat akurat.\n"
        elif stats['winrate'] >= 60:
            report += "✅ Performa GOOD. Signal cukup reliable.\n"
        elif stats['winrate'] >= 50:
            report += "⚠️ Performa AVERAGE. Perlu improvement.\n"
        else:
            report += "❌ Performa POOR. Perlu review strategi.\n"
        
        # Analisis PnL
        if stats['avg_pnl'] > 5:
            report += "💰 Profit margin sangat bagus!\n"
        elif stats['avg_pnl'] > 2:
            report += "💰 Profit margin cukup baik.\n"
        elif stats['avg_pnl'] > 0:
            report += "💰 Profit margin kecil tapi positif.\n"
        else:
            report += "⚠️ Rata-rata loss, perlu perbaikan.\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━

🎯 **REKOMENDASI:**
"""
        
        if stats['total_signals'] < 10:
            report += "• Tingkatkan jumlah signal untuk data lebih akurat\n"
        
        if stats['winrate'] < 60:
            report += "• Review parameter Supply & Demand zones\n"
            report += "• Pertimbangkan filter volume lebih ketat\n"
        
        if stats['avg_pnl'] < 2:
            report += "• Optimalkan risk/reward ratio\n"
            report += "• Review target TP dan SL\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━

📅 Laporan dibuat: {end_date.strftime('%d/%m/%Y %H:%M')} WIB
🤖 CryptoMentor AI Bot
"""
        
        return report
    
    async def send_to_admins(self, report: str):
        """Kirim laporan ke semua admin"""
        if not self.bot_token:
            logger.error("Bot token not found")
            return
        
        bot = Bot(token=self.bot_token)
        
        for admin_id in self.admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=report,
                    parse_mode='MARKDOWN'
                )
                logger.info(f"✅ Report sent to admin {admin_id}")
            except Exception as e:
                logger.error(f"Failed to send report to {admin_id}: {e}")
    
    async def generate_and_send(self):
        """Generate dan kirim laporan"""
        try:
            report = await self.generate_report()
            await self.send_to_admins(report)
            logger.info("✅ Weekly report generated and sent")
        except Exception as e:
            logger.error(f"Failed to generate/send report: {e}")

# Global instance
weekly_reporter = WeeklyReportGenerator()
