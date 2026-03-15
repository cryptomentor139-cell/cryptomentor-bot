"""

Scheduler - Jadwal otomatis untuk sync logs dan kirim laporan mingguan

Menggunakan local G: drive sync (lebih simple dari API)

"""

import asyncio

from datetime import datetime, time

import logging



logger = logging.getLogger(__name__)



class TaskScheduler:

    """Scheduler untuk task otomatis"""

    

    def __init__(self):

        self.running = False

    

    async def daily_sync_task(self):

        """Task sync harian ke G: drive atau Supabase (setiap jam 23:00)"""

        import os

        from datetime import timedelta

        

        while self.running:

            now = datetime.now()

            

            # Hitung waktu sampai jam 23:00

            target_time = now.replace(hour=23, minute=0, second=0, microsecond=0)

            if now >= target_time:

                # Jika sudah lewat jam 23:00, jadwalkan untuk besok

                target_time = target_time + timedelta(days=1)

            

            wait_seconds = (target_time - now).total_seconds()

            

            logger.info(f"Next daily sync in {wait_seconds/3600:.1f} hours")

            await asyncio.sleep(wait_seconds)

            

            # Sync logs - auto-detect environment

            try:

                use_gdrive = os.getenv('USE_GDRIVE', 'true').lower() == 'true'

                

                if use_gdrive and os.path.exists('G:/'):

                    # Local: Sync to G: drive

                    from app.local_gdrive_sync import local_gdrive_sync

                    synced, failed = local_gdrive_sync.sync_all_logs()

                    logger.info(f"[OK] G: drive sync: {synced} files synced, {failed} failed")

                else:

                    # Railway: Upload to Supabase

                    from app.supabase_storage import supabase_storage

                    uploaded, failed = supabase_storage.upload_all_logs()

                    logger.info(f"[OK] Supabase upload: {uploaded} files uploaded, {failed} failed")

                    

            except Exception as e:

                logger.error(f"Daily sync failed: {e}")

    

    async def weekly_report_task(self):

        """Task laporan mingguan (setiap Senin jam 09:00)"""

        from app.weekly_report import weekly_reporter

        from datetime import timedelta

        

        while self.running:

            now = datetime.now()

            

            # Hitung hari sampai Senin berikutnya

            days_until_monday = (7 - now.weekday()) % 7

            if days_until_monday == 0 and now.hour >= 9:

                days_until_monday = 7

            

            target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

            target_time = target_time + timedelta(days=days_until_monday)

            

            wait_seconds = (target_time - now).total_seconds()

            

            logger.info(f"Next weekly report in {wait_seconds/3600:.1f} hours")

            await asyncio.sleep(wait_seconds)

            

            # Generate dan kirim laporan

            try:

                await weekly_reporter.generate_and_send()

                logger.info("[OK] Weekly report sent to admins")

            except Exception as e:

                logger.error(f"Weekly report failed: {e}")

    

    async def start(self):

        """Start semua scheduled tasks"""

        self.running = True

        logger.info("[ROCKET] Scheduler started")

        

        # Jalankan tasks secara parallel

        await asyncio.gather(

            self.daily_sync_task(),

            self.weekly_report_task()

        )

    

    def stop(self):

        """Stop scheduler"""

        self.running = False

        logger.info("[STOP] Scheduler stopped")



# Global instance

task_scheduler = TaskScheduler()


def start_scheduler(application):
    """Start scheduler dan auto-restart autotrade engines."""
    import asyncio

    async def _start():
        # Auto-restart autotrade engines untuk semua active sessions
        try:
            from app.supabase_repo import _client
            from app.handlers_autotrade import get_user_api_keys
            from app.autotrade_engine import start_engine, is_running

            res = _client().table("autotrade_sessions").select("*").eq("status", "active").execute()
            sessions = res.data or []
            logger.info(f"[AutoTrade] Found {len(sessions)} active sessions to restore")

            for session in sessions:
                user_id = session.get("telegram_id")
                if not user_id:
                    continue
                if is_running(user_id):
                    continue
                keys = get_user_api_keys(user_id)
                if not keys:
                    logger.warning(f"[AutoTrade] No API keys for user {user_id}, skipping")
                    continue
                amount = float(session.get("initial_deposit", 10))
                leverage = int(session.get("leverage", 10))
                try:
                    start_engine(
                        bot=application.bot,
                        user_id=user_id,
                        api_key=keys["api_key"],
                        api_secret=keys["api_secret"],
                        amount=amount,
                        leverage=leverage,
                        notify_chat_id=user_id,
                    )
                    logger.info(f"[AutoTrade] Engine restored for user {user_id}")
                except Exception as e:
                    logger.error(f"[AutoTrade] Failed to restore engine for user {user_id}: {e}")
        except Exception as e:
            logger.error(f"[AutoTrade] Auto-restore failed: {e}")

        # Start scheduler tasks
        task_scheduler.running = True
        logger.info("[ROCKET] Scheduler started")

    asyncio.create_task(_start())

