"""
Content Calendar Manager — pembuatan dan penjadwalan kalender konten mingguan.
marketing/agent/core/content_calendar.py
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from marketing.agent.config import Config
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

CONTENT_CALENDAR_PATH = Path("marketing/content_calendar.json")

# Distribusi konten: 40% edukasi, 30% produk, 30% komunitas+psikologi
CONTENT_DISTRIBUTION = {
    "education": 0.40,
    "product": 0.30,
    "community_psychology": 0.30,
}

# Waktu optimal posting dalam WIB (jam)
OPTIMAL_HOURS_WIB = [7, 12, 19]

# Kategori konten
CATEGORY_EDUCATION = "crypto_education"
CATEGORY_PRODUCT = "product_highlight"
CATEGORY_COMMUNITY = "community"
CATEGORY_PSYCHOLOGY = "trading_psychology"


class ContentCalendarManager:
    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db

    # ------------------------------------------------------------------
    # Calendar Generation
    # ------------------------------------------------------------------

    async def generate_weekly_calendar(
        self,
        campaign_id: str,
        topics: List[str],
    ) -> dict:
        """
        Generate kalender konten untuk 7 hari ke depan.
        Minimal 7 konten per minggu (1 per hari), distribusi:
          - 40% edukasi
          - 30% produk
          - 30% komunitas + psikologi
        Jadwalkan pada waktu optimal: 07:00, 12:00, 19:00 WIB.
        Hindari duplikasi topik dalam 7 hari terakhir.
        """
        # Ambil topik yang sudah digunakan agar tidak duplikat
        used_topics: set[str] = set()
        for platform in ("instagram", "facebook", "tiktok", "threads"):
            used = await self.get_used_topics_last_7_days(platform)
            used_topics.update(t.lower() for t in used)

        # Filter topik yang belum digunakan
        available_topics = [t for t in topics if t.lower() not in used_topics]
        if not available_topics:
            # Jika semua sudah digunakan, gunakan semua topik (rotasi)
            available_topics = topics or ["AutoTrade", "Risk Management", "Crypto Education"]

        # Tentukan jumlah konten per kategori (minimal 7 total)
        total = max(7, len(available_topics))
        edu_count = max(1, round(total * CONTENT_DISTRIBUTION["education"]))
        prod_count = max(1, round(total * CONTENT_DISTRIBUTION["product"]))
        comm_count = total - edu_count - prod_count

        # Buat slot konten
        slots: list[dict] = []
        topic_idx = 0

        def next_topic() -> str:
            nonlocal topic_idx
            t = available_topics[topic_idx % len(available_topics)]
            topic_idx += 1
            return t

        for _ in range(edu_count):
            slots.append({"category": CATEGORY_EDUCATION, "topic": next_topic()})
        for _ in range(prod_count):
            slots.append({"category": CATEGORY_PRODUCT, "topic": next_topic()})
        for i in range(comm_count):
            cat = CATEGORY_COMMUNITY if i % 2 == 0 else CATEGORY_PSYCHOLOGY
            slots.append({"category": cat, "topic": next_topic()})

        # Distribusikan ke 7 hari dengan waktu optimal
        now_utc = datetime.now(timezone.utc)
        # Mulai dari besok pagi 07:00 WIB (00:00 UTC)
        start_date = (now_utc + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        calendar_entries: list[dict] = []
        for idx, slot in enumerate(slots):
            day_offset = idx // len(OPTIMAL_HOURS_WIB)
            hour_idx = idx % len(OPTIMAL_HOURS_WIB)
            wib_hour = OPTIMAL_HOURS_WIB[hour_idx]
            utc_hour = (wib_hour - 7) % 24

            scheduled_dt = (start_date + timedelta(days=day_offset)).replace(
                hour=utc_hour, minute=0, second=0
            )

            entry = {
                "id": str(uuid.uuid4()),
                "campaign_id": campaign_id,
                "topic": slot["topic"],
                "category": slot["category"],
                "scheduled_at_utc": scheduled_dt.isoformat(),
                "scheduled_at_wib": (
                    scheduled_dt + timedelta(hours=7)
                ).strftime("%Y-%m-%d %H:%M WIB"),
                "status": "scheduled",
            }
            calendar_entries.append(entry)

        calendar = {
            "campaign_id": campaign_id,
            "generated_at": now_utc.isoformat(),
            "total_content": len(calendar_entries),
            "distribution": {
                "education": edu_count,
                "product": prod_count,
                "community_psychology": comm_count,
            },
            "entries": calendar_entries,
        }

        logger.info(
            "Kalender mingguan dibuat: %d konten untuk campaign %s",
            len(calendar_entries),
            campaign_id,
        )
        return calendar

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    async def save_calendar(self, calendar: dict) -> None:
        """
        Simpan kalender ke marketing/content_calendar.json dan ke Supabase
        (tabel marketing_campaigns sebagai JSONB di kolom analyst_feedback,
        atau tabel marketing_content untuk setiap entry).
        """
        # Simpan ke file JSON
        try:
            CONTENT_CALENDAR_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONTENT_CALENDAR_PATH, "w", encoding="utf-8") as f:
                json.dump(calendar, f, ensure_ascii=False, indent=2)
            logger.info("Kalender disimpan ke %s", CONTENT_CALENDAR_PATH)
        except Exception as exc:
            logger.error("Gagal simpan kalender ke file: %s", exc)

        # Simpan setiap entry ke Supabase sebagai marketing_content draft
        campaign_id = calendar.get("campaign_id", "")
        for entry in calendar.get("entries", []):
            data = {
                "id": entry["id"],
                "campaign_id": campaign_id,
                "content_type": "feed",
                "topic_category": entry.get("category", CATEGORY_EDUCATION),
                "hook": entry.get("topic", ""),
                "caption": "",
                "status": "draft",
            }
            try:
                await self.db.insert("marketing_content", data)
            except Exception as exc:
                logger.warning(
                    "Gagal simpan calendar entry %s ke Supabase: %s",
                    entry.get("id", "?"),
                    exc,
                )

    # ------------------------------------------------------------------
    # Topic Deduplication
    # ------------------------------------------------------------------

    async def get_used_topics_last_7_days(self, platform: str) -> List[str]:
        """
        Ambil topik yang sudah digunakan dalam 7 hari terakhir dari DB
        untuk platform tertentu.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        topics: list[str] = []
        try:
            # Ambil publikasi 7 hari terakhir untuk platform ini
            pub_rows = await self.db.select(
                "marketing_publications",
                filters={"platform": platform},
                limit=500,
            )
            # Filter berdasarkan published_at >= cutoff
            recent_content_ids = []
            for row in pub_rows:
                pub_at = row.get("published_at") or row.get("scheduled_at") or ""
                if pub_at >= cutoff:
                    cid = row.get("content_id")
                    if cid:
                        recent_content_ids.append(cid)

            # Ambil topik dari marketing_content
            for content_id in recent_content_ids:
                rows = await self.db.select(
                    "marketing_content",
                    filters={"id": content_id},
                    limit=1,
                )
                if rows:
                    hook = rows[0].get("hook") or ""
                    if hook:
                        topics.append(hook)
        except Exception as exc:
            logger.warning("Gagal ambil used topics untuk %s: %s", platform, exc)

        return topics

    # ------------------------------------------------------------------
    # Weekly Report Scheduling
    # ------------------------------------------------------------------

    async def schedule_weekly_report(self) -> None:
        """
        Jadwalkan laporan mingguan setiap Senin 08:00 WIB menggunakan APScheduler.
        """
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger
        except ImportError:
            logger.warning(
                "APScheduler tidak tersedia. Install dengan: pip install apscheduler"
            )
            return

        scheduler = AsyncIOScheduler()
        # Senin (day_of_week=0) jam 08:00 WIB = 01:00 UTC
        scheduler.add_job(
            self._send_weekly_report_notification,
            CronTrigger(day_of_week="mon", hour=1, minute=0),
            id="weekly_report",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Jadwal laporan mingguan aktif: Senin 08:00 WIB")

    async def _send_weekly_report_notification(self) -> None:
        """Kirim notifikasi laporan mingguan ke admin via Telegram."""
        import httpx as _httpx

        message = (
            "📅 <b>Laporan Mingguan Marketing</b>\n\n"
            "Laporan performa konten minggu ini sedang diproses oleh Analyst Agent.\n"
            "Hasil akan dikirim dalam beberapa menit."
        )
        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        for admin_id in self.config.telegram_admin_ids:
            try:
                async with _httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(url, json={
                        "chat_id": admin_id,
                        "text": message,
                        "parse_mode": "HTML",
                    })
            except Exception as exc:
                logger.error("Gagal kirim weekly report notif ke %d: %s", admin_id, exc)
