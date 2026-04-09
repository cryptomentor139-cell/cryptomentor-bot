"""
Marketing Orchestrator — entry point utama Marketing AI Agent.
Menjalankan loop 7 langkah secara berkelanjutan.
marketing/agent/main.py
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

import httpx

from marketing.agent.agents.analyst_agent import AnalystAgent
from marketing.agent.agents.content_agent import ContentAgent, ContentItem
from marketing.agent.agents.designer_agent import DesignerAgent
from marketing.agent.agents.distribution_agent import DistributionAgent
from marketing.agent.agents.sales_agent import SalesAgent
from marketing.agent.agents.strategist_agent import AnalystFeedback, CampaignPlan, StrategistAgent
from marketing.agent.config import Config
from marketing.agent.core.approval_queue import ApprovalQueue
from marketing.agent.core.brand_context_watcher import BrandContextWatcher
from marketing.agent.core.content_calendar import ContentCalendarManager
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class CycleResult:
    success: bool
    cycle_number: int
    content_count: int
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class MarketingOrchestrator:
    """
    Orchestrator utama yang menjalankan loop 7 langkah:
    1. Strategist: analisa market, tentukan angle & persona
    2. Content Agent: generate 10 konten
    3. Designer Agent: render image/video
    4. Approval Queue: kirim ke admin atau auto-publish
    5. Distribution Agent: posting ke semua platform
    6. Analyst Agent: evaluasi performa
    7. Feedback ke Strategist untuk siklus berikutnya
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.db = SupabaseDB(config)

        # Inisialisasi semua agen
        self.strategist = StrategistAgent(config, self.db)
        self.content_agent = ContentAgent(config, self.db)
        self.designer = DesignerAgent(config)
        self.distribution = DistributionAgent(config, self.db)
        self.sales = SalesAgent(config, self.db)
        self.analyst = AnalystAgent(config, self.db)
        self.approval_queue = ApprovalQueue(config, self.db)
        self.calendar_manager = ContentCalendarManager(config, self.db)
        self.brand_watcher = BrandContextWatcher(config)

        # State antar siklus
        self._analyst_feedback: Optional[AnalystFeedback] = None
        self._last_campaign_plan: Optional[CampaignPlan] = None

    # ------------------------------------------------------------------
    # Main cycle
    # ------------------------------------------------------------------

    async def run_cycle(self) -> CycleResult:
        """
        Jalankan 7 langkah loop satu siklus penuh.
        Graceful degradation: error per agen tidak menghentikan siklus.
        """
        cycle_number = 0
        content_items: List[ContentItem] = []

        # ----------------------------------------------------------------
        # Langkah 1: Strategist — analisa market & tentukan campaign plan
        # ----------------------------------------------------------------
        plan: Optional[CampaignPlan] = None
        try:
            sentiment = await self.strategist.analyze_market_sentiment()
            plan = await self.strategist.determine_campaign_angle(
                sentiment, self._analyst_feedback
            )
            await self.strategist.save_campaign_plan(plan)
            self._last_campaign_plan = plan
            cycle_number = plan.cycle_number
            logger.info(
                "[Siklus %d] Strategist selesai: angle=%s, persona=%s",
                cycle_number,
                plan.campaign_angle,
                plan.target_persona.value,
            )
        except Exception as exc:
            await self.handle_agent_error("Strategist", exc)
            # Graceful degradation: gunakan plan dari siklus sebelumnya
            if self._last_campaign_plan:
                plan = self._last_campaign_plan
                cycle_number = plan.cycle_number + 1
                logger.warning(
                    "[Siklus %d] Menggunakan campaign plan dari siklus sebelumnya.",
                    cycle_number,
                )
            else:
                # Tidak ada plan sama sekali — skip siklus
                return CycleResult(
                    success=False,
                    cycle_number=0,
                    content_count=0,
                    error=f"Strategist gagal dan tidak ada plan sebelumnya: {exc}",
                )

        # ----------------------------------------------------------------
        # Langkah 2: Content Agent — generate 10 konten
        # ----------------------------------------------------------------
        try:
            content_items = await self.content_agent.generate_batch(plan)
            logger.info(
                "[Siklus %d] Content Agent selesai: %d konten dihasilkan.",
                cycle_number,
                len(content_items),
            )
        except Exception as exc:
            await self.handle_agent_error("Content", exc)
            # Graceful degradation: skip siklus, coba lagi 1 jam kemudian
            return CycleResult(
                success=False,
                cycle_number=cycle_number,
                content_count=0,
                error=f"Content Agent gagal: {exc}",
            )

        # ----------------------------------------------------------------
        # Langkah 3: Designer Agent — render image/video
        # ----------------------------------------------------------------
        processed_items: List[ContentItem] = []
        for item in content_items:
            try:
                processed = await self.designer.process_content_item(item)
                processed_items.append(processed)
            except Exception as exc:
                await self.handle_agent_error("Designer", exc)
                # Graceful degradation: lanjutkan dengan konten tanpa media
                logger.warning(
                    "[Siklus %d] Designer gagal untuk item %s, lanjutkan tanpa media.",
                    cycle_number,
                    item.id,
                )
                processed_items.append(item)

        logger.info(
            "[Siklus %d] Designer Agent selesai: %d item diproses.",
            cycle_number,
            len(processed_items),
        )

        # ----------------------------------------------------------------
        # Langkah 4: Approval Queue
        # ----------------------------------------------------------------
        auto_publish = await self.approval_queue.is_auto_publish_enabled()
        approved_items: List[ContentItem] = []

        if auto_publish:
            # Auto-publish: langsung ke distribusi
            approved_items = processed_items
            logger.info(
                "[Siklus %d] Auto-publish aktif: %d konten langsung ke distribusi.",
                cycle_number,
                len(approved_items),
            )
        else:
            # Manual approval: kirim ke queue dan tunggu
            for item in processed_items:
                try:
                    await self.approval_queue.add_to_queue(item.id)
                except Exception as exc:
                    logger.error(
                        "[Siklus %d] Gagal add to queue item %s: %s",
                        cycle_number,
                        item.id,
                        exc,
                    )

            # Tunggu approval (polling dengan timeout 1 jam)
            approved_items = await self._wait_for_approvals(
                [item.id for item in processed_items],
                timeout_seconds=3600,
            )
            logger.info(
                "[Siklus %d] Approval selesai: %d/%d konten disetujui.",
                cycle_number,
                len(approved_items),
                len(processed_items),
            )

        # ----------------------------------------------------------------
        # Langkah 5: Distribution Agent — posting ke semua platform
        # ----------------------------------------------------------------
        distributed_ids: List[str] = []
        for item in approved_items:
            try:
                results = await self.distribution.distribute_content(item)
                success_count = sum(1 for r in results.values() if r.success)
                if success_count > 0:
                    distributed_ids.append(item.id)
                    logger.info(
                        "[Siklus %d] Konten %s didistribusikan ke %d platform.",
                        cycle_number,
                        item.id[:8],
                        success_count,
                    )
                else:
                    # Semua platform gagal
                    await self.handle_agent_error(
                        "Distribution",
                        Exception(f"Semua platform gagal untuk konten {item.id[:8]}"),
                    )
            except Exception as exc:
                await self.handle_agent_error("Distribution", exc)
                # Graceful degradation: tandai failed, notifikasi admin, lanjutkan

        logger.info(
            "[Siklus %d] Distribution selesai: %d konten berhasil didistribusikan.",
            cycle_number,
            len(distributed_ids),
        )

        # ----------------------------------------------------------------
        # Langkah 6: Analyst Agent — evaluasi performa
        # ----------------------------------------------------------------
        try:
            # Kumpulkan metrik dari siklus sebelumnya (bukan siklus ini)
            all_content_rows = await self.db.select(
                "marketing_content",
                filters={"status": "published"},
                limit=50,
            )
            prev_content_ids = [r.get("id") for r in all_content_rows if r.get("id")]

            if prev_content_ids:
                metrics_list = await self.analyst.collect_metrics(prev_content_ids)
                for metrics in metrics_list:
                    await self.analyst.make_scale_decision(metrics)
                    await self.analyst.make_kill_decision(metrics)

            # Laporan mingguan setiap hari Senin
            now_utc = datetime.now(timezone.utc)
            if now_utc.weekday() == 0:  # Senin
                report = await self.analyst.generate_weekly_report()
                await self.analyst.send_weekly_report_telegram(report)

            # Cek penurunan conversion rate
            await self.analyst.check_conversion_drop_alert()

            logger.info("[Siklus %d] Analyst Agent selesai.", cycle_number)
        except Exception as exc:
            await self.handle_agent_error("Analyst", exc)
            # Graceful degradation: skip laporan, lanjutkan ke siklus berikutnya

        # ----------------------------------------------------------------
        # Langkah 7: Feedback ke Strategist
        # ----------------------------------------------------------------
        try:
            self._analyst_feedback = await self.analyst.generate_feedback()
            logger.info(
                "[Siklus %d] Feedback Analyst: persona=%s, angle=%s",
                cycle_number,
                self._analyst_feedback.best_performing_persona,
                self._analyst_feedback.recommended_angle,
            )
        except Exception as exc:
            await self.handle_agent_error("Analyst (feedback)", exc)
            # Graceful degradation: gunakan feedback kosong
            self._analyst_feedback = AnalystFeedback(None, None, None, "")

        return CycleResult(
            success=True,
            cycle_number=cycle_number,
            content_count=len(distributed_ids),
        )

    # ------------------------------------------------------------------
    # Continuous loop
    # ------------------------------------------------------------------

    async def run_continuous(self, interval_hours: int = 24) -> None:
        """
        Loop terus dengan interval yang dapat dikonfigurasi.
        Jalankan run_cycle() setiap interval_hours jam.
        """
        # Start brand context watcher
        self.brand_watcher.start()

        logger.info(
            "Marketing Orchestrator dimulai. Interval: %d jam.", interval_hours
        )
        await self.send_admin_notification(
            f"🚀 Marketing AI Agent dimulai.\nInterval siklus: {interval_hours} jam."
        )

        try:
            while True:
                logger.info("Memulai siklus baru...")
                try:
                    result = await self.run_cycle()
                    if result.success:
                        logger.info(
                            "Siklus %d selesai: %d konten didistribusikan.",
                            result.cycle_number,
                            result.content_count,
                        )
                    else:
                        logger.warning(
                            "Siklus %d gagal: %s",
                            result.cycle_number,
                            result.error,
                        )
                        # Jika Content Agent gagal, coba lagi 1 jam kemudian
                        if result.error and "Content Agent gagal" in result.error:
                            logger.info("Retry dalam 1 jam karena Content Agent gagal.")
                            await asyncio.sleep(3600)
                            continue
                except Exception as exc:
                    logger.exception("Error tidak terduga dalam run_cycle: %s", exc)
                    await self.handle_agent_error("Orchestrator", exc)

                # Tunggu interval sebelum siklus berikutnya
                logger.info("Menunggu %d jam sebelum siklus berikutnya...", interval_hours)
                await asyncio.sleep(interval_hours * 3600)
        finally:
            self.brand_watcher.stop()
            logger.info("Marketing Orchestrator dihentikan.")

    # ------------------------------------------------------------------
    # Error handling & notifications
    # ------------------------------------------------------------------

    async def handle_agent_error(self, agent: str, error: Exception) -> None:
        """Log error dan kirim notifikasi Telegram ke admin."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.error("Agent error [%s]: %s", agent, error)

        message = (
            f"🚨 Marketing Agent Error\n"
            f"Agen: {agent}\n"
            f"Error: {error}\n"
            f"Waktu: {timestamp}"
        )
        await self.send_admin_notification(message)

    async def send_admin_notification(self, message: str) -> None:
        """Kirim pesan ke semua admin via Telegram."""
        url = TELEGRAM_API_BASE.format(token=self.config.telegram_bot_token)
        for admin_id in self.config.telegram_admin_ids:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json={
                        "chat_id": admin_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    })
                    response.raise_for_status()
            except Exception as exc:
                logger.error("Gagal kirim notifikasi ke admin %d: %s", admin_id, exc)

    # ------------------------------------------------------------------
    # Telegram message handler
    # ------------------------------------------------------------------

    async def handle_telegram_message(self, telegram_chat_id: int, text: str) -> str:
        """Delegasikan pesan Telegram ke Sales Agent."""
        return await self.sales.handle_telegram_message(telegram_chat_id, text)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _wait_for_approvals(
        self,
        content_ids: List[str],
        timeout_seconds: int = 3600,
        poll_interval: int = 60,
    ) -> List[ContentItem]:
        """
        Poll Supabase hingga semua konten di-approve/reject atau timeout.
        Return list ContentItem yang statusnya 'approved'.
        """
        approved: List[ContentItem] = []
        pending = set(content_ids)
        elapsed = 0

        while pending and elapsed < timeout_seconds:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            still_pending = set()
            for content_id in pending:
                try:
                    rows = await self.db.select(
                        "marketing_content",
                        filters={"id": content_id},
                        limit=1,
                    )
                    if not rows:
                        still_pending.add(content_id)
                        continue

                    status = rows[0].get("status", "pending_approval")
                    if status == "approved":
                        # Rekonstruksi ContentItem minimal dari DB
                        item = _build_content_item_from_row(rows[0])
                        approved.append(item)
                    elif status == "rejected":
                        logger.info("Konten %s ditolak.", content_id[:8])
                    else:
                        still_pending.add(content_id)
                except Exception as exc:
                    logger.warning("Gagal cek status konten %s: %s", content_id[:8], exc)
                    still_pending.add(content_id)

            pending = still_pending

        if pending:
            logger.warning(
                "Timeout approval: %d konten masih pending setelah %d detik.",
                len(pending),
                timeout_seconds,
            )

        return approved


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_content_item_from_row(row: dict) -> ContentItem:
    """Rekonstruksi ContentItem minimal dari baris DB."""
    from marketing.agent.agents.content_agent import ContentItem as CI
    item = CI(
        id=row.get("id", ""),
        content_type=row.get("content_type", "feed"),
        status=row.get("status", "approved"),
    )
    return item


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = Config()
    try:
        config.validate()
    except Exception as exc:
        logger.error("Konfigurasi tidak valid: %s", exc)
        return

    orchestrator = MarketingOrchestrator(config)
    await orchestrator.run_continuous(interval_hours=24)


if __name__ == "__main__":
    asyncio.run(main())
