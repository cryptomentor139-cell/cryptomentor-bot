"""
Handler commands untuk admin melihat winrate dan tracking signal
Updated untuk menggunakan local G: drive sync
"""
from telegram import Update
from telegram.ext import ContextTypes
from app.signal_tracker_integration import get_current_winrate
from app.weekly_report import weekly_reporter
import os
import logging

logger = logging.getLogger(__name__)

async def cmd_winrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /winrate - Lihat winrate signal saat ini"""
    user_id = update.effective_user.id
    
    # Check if admin
    admin_ids = [int(x) for x in [
        os.getenv('ADMIN1', 0),
        os.getenv('ADMIN2', 0),
        os.getenv('ADMIN3', 0)
    ] if x]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Command ini hanya untuk admin")
        return
    
    # Get stats
    days = int(context.args[0]) if context.args else 7
    stats = get_current_winrate(days)
    
    if not stats:
        await update.message.reply_text("❌ Gagal mengambil data winrate")
        return
    
    response = f"""📊 **WINRATE SIGNAL ({days} HARI TERAKHIR)**

━━━━━━━━━━━━━━━━━━━━━━

📈 **STATISTIK:**
• Total Signal: {stats['total_signals']}
• Win: {stats['wins']} ✅
• Loss: {stats['losses']} ❌
• Winrate: {stats['winrate']}% 🎯
• Avg PnL: {stats['avg_pnl']:+.2f}%

━━━━━━━━━━━━━━━━━━━━━━

💡 **Tips:**
• Gunakan `/winrate 30` untuk 30 hari
• Gunakan `/weekly_report` untuk laporan lengkap
"""
    
    await update.message.reply_text(response, parse_mode='MARKDOWN')

async def cmd_weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /weekly_report - Generate laporan mingguan manual"""
    user_id = update.effective_user.id
    
    # Check if admin
    import os
    admin_ids = [int(x) for x in [
        os.getenv('ADMIN1', 0),
        os.getenv('ADMIN2', 0),
        os.getenv('ADMIN3', 0)
    ] if x]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Command ini hanya untuk admin")
        return
    
    await update.message.reply_text("⏳ Generating weekly report...")
    
    try:
        report = await weekly_reporter.generate_report()
        await update.message.reply_text(report, parse_mode='MARKDOWN')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cmd_upload_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /upload_logs - Sync logs ke G: drive atau Supabase"""
    user_id = update.effective_user.id
    
    # Check if admin
    import os
    admin_ids = [int(x) for x in [
        os.getenv('ADMIN1', 0),
        os.getenv('ADMIN2', 0),
        os.getenv('ADMIN3', 0)
    ] if x]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Command ini hanya untuk admin")
        return
    
    await update.message.reply_text("⏳ Syncing logs...")
    
    try:
        use_gdrive = os.getenv('USE_GDRIVE', 'true').lower() == 'true'
        
        if use_gdrive and os.path.exists('G:/'):
            # Local: Sync to G: drive
            from app.local_gdrive_sync import local_gdrive_sync
            
            if not local_gdrive_sync.enabled:
                await update.message.reply_text(
                    "❌ G: drive not available\n\n"
                    "Pastikan Google Drive for Desktop sudah running"
                )
                return
            
            synced, failed = local_gdrive_sync.sync_all_logs()
            await update.message.reply_text(
                f"✅ G: Drive Sync complete!\n\n"
                f"📊 Synced: {synced} files\n"
                f"❌ Failed: {failed} files"
            )
        else:
            # Railway: Upload to Supabase
            from app.supabase_storage import supabase_storage
            
            if not supabase_storage.enabled:
                await update.message.reply_text(
                    "❌ Supabase Storage not configured\n\n"
                    "Set USE_SUPABASE_STORAGE=true in environment"
                )
                return
            
            uploaded, failed = supabase_storage.upload_all_logs()
            await update.message.reply_text(
                f"✅ Supabase Upload complete!\n\n"
                f"📊 Uploaded: {uploaded} files\n"
                f"❌ Failed: {failed} files"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cmd_signal_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /signal_stats - Statistik detail signal"""
    user_id = update.effective_user.id
    
    # Check if admin
    import os
    admin_ids = [int(x) for x in [
        os.getenv('ADMIN1', 0),
        os.getenv('ADMIN2', 0),
        os.getenv('ADMIN3', 0)
    ] if x]
    
    if user_id not in admin_ids:
        await update.message.reply_text("❌ Command ini hanya untuk admin")
        return
    
    from app.signal_logger import signal_logger
    from app.local_gdrive_sync import local_gdrive_sync
    from pathlib import Path
    
    # Count files
    log_dir = Path("signal_logs")
    prompt_files = list(log_dir.glob("prompts_*.jsonl"))
    
    total_prompts = 0
    for file in prompt_files:
        with open(file, "r") as f:
            total_prompts += sum(1 for _ in f)
    
    # Get active signals
    active_file = log_dir / "active_signals.jsonl"
    active_count = 0
    if active_file.exists():
        with open(active_file, "r") as f:
            active_count = sum(1 for _ in f)
    
    # Get completed signals
    completed_file = log_dir / "completed_signals.jsonl"
    completed_count = 0
    if completed_file.exists():
        with open(completed_file, "r") as f:
            completed_count = sum(1 for _ in f)
    
    # Get storage status
    use_gdrive = os.getenv('USE_GDRIVE', 'true').lower() == 'true'
    
    if use_gdrive and os.path.exists('G:/'):
        # Local: G: drive
        from app.local_gdrive_sync import local_gdrive_sync
        sync_status = local_gdrive_sync.get_sync_status()
        storage_type = "G: Drive (Local)"
    else:
        # Railway: Supabase
        from app.supabase_storage import supabase_storage
        sync_status = supabase_storage.get_status()
        storage_type = "Supabase Storage (Cloud)"
    
    response = f"""📊 **STATISTIK SIGNAL TRACKING**

━━━━━━━━━━━━━━━━━━━━━━

📝 **DATA TERSIMPAN:**
• Total Prompts: {total_prompts}
• Active Signals: {active_count}
• Completed Signals: {completed_count}
• Log Files: {len(prompt_files)}

━━━━━━━━━━━━━━━━━━━━━━

☁️ **STORAGE:**
• Type: {storage_type}
• Status: {'✅ Enabled' if sync_status['enabled'] else '❌ Disabled'}
"""
    
    if sync_status['enabled']:
        if use_gdrive and os.path.exists('G:/'):
            response += f"""• Path: {sync_status['gdrive_path']}
• Local Files: {sync_status['local_files']}
• GDrive Files: {sync_status['gdrive_files']}
• In Sync: {'✅ Yes' if sync_status['in_sync'] else '⚠️ No'}
"""
        else:
            response += f"""• Bucket: {sync_status.get('bucket', 'N/A')}
• Files: {sync_status.get('files_count', 0)}
• Status: {sync_status.get('status', 'unknown')}
"""
    else:
        response += f"""• Message: {sync_status.get('message', 'Not configured')}
"""
    
    response += """
━━━━━━━━━━━━━━━━━━━━━━

💡 **Commands:**
• `/winrate` - Lihat winrate
• `/weekly_report` - Generate laporan
• `/upload_logs` - Sync ke G: drive
"""
    
    await update.message.reply_text(response, parse_mode='MARKDOWN')
