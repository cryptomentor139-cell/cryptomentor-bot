"""
Lead Capture Manager — tangkap dan kelola lead dari platform sosial media.
marketing/agent/core/lead_capture.py
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from marketing.agent.core.audience_intelligence import AudienceSegment
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

LOW_CVR_THRESHOLD = 0.02
LOW_CVR_DAYS = 7


@dataclass
class Lead:
    id: str
    source_platform: str
    source_content_id: Optional[str]
    telegram_chat_id: int
    contact_id: str
    persona: Optional[str]
    segment: str = "Cold"
    status: str = "new"


class LeadCaptureManager:
    def __init__(self, db: SupabaseDB) -> None:
        self.db = db

    async def record_lead(self, telegram_chat_id: int, source_platform: str,
                          source_content_id: Optional[str] = None) -> Lead:
        try:
            existing = await self.db.select("marketing_leads",
                                            filters={"telegram_chat_id": telegram_chat_id}, limit=1)
            if existing:
                row = existing[0]
                return Lead(
                    id=row["id"], source_platform=row.get("source_platform", source_platform),
                    source_content_id=row.get("source_content_id"),
                    telegram_chat_id=telegram_chat_id,
                    contact_id=row.get("contact_id", str(telegram_chat_id)),
                    persona=row.get("persona"), segment=row.get("segment", "Cold"),
                    status=row.get("status", "new"),
                )
        except Exception as exc:
            logger.error("Gagal cek lead existing: %s", exc)

        lead_id = str(uuid.uuid4())
        data: dict = {
            "id": lead_id, "source_platform": source_platform,
            "contact_id": str(telegram_chat_id), "contact_type": "telegram",
            "telegram_chat_id": telegram_chat_id, "segment": "Cold", "status": "new",
        }
        if source_content_id:
            data["source_content_id"] = source_content_id

        try:
            result = await self.db.insert("marketing_leads", data)
            saved_id = result.get("id", lead_id)
        except Exception as exc:
            logger.error("Gagal simpan lead baru: %s", exc)
            saved_id = lead_id

        return Lead(id=saved_id, source_platform=source_platform,
                    source_content_id=source_content_id, telegram_chat_id=telegram_chat_id,
                    contact_id=str(telegram_chat_id), persona=None, segment="Cold", status="new")

    async def update_segment(self, lead_id: str, segment: AudienceSegment) -> None:
        try:
            await self.db.update("marketing_leads", lead_id, {"segment": segment.value})
        except Exception as exc:
            logger.error("Gagal update segment lead %s: %s", lead_id, exc)

    async def track_conversion(self, lead_id: str) -> None:
        try:
            await self.db.update("marketing_leads", lead_id, {
                "status": "converted",
                "converted_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            logger.error("Gagal track konversi lead %s: %s", lead_id, exc)

    async def get_conversion_rate(self, platform: str, days: int = 7) -> float:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        try:
            all_leads = await self.db.select("marketing_leads",
                                             filters={"source_platform": platform}, limit=1000)
            recent = [r for r in all_leads if self._parse_dt(r.get("created_at")) >= cutoff]
            if not recent:
                return 0.0
            converted = sum(1 for r in recent if r.get("status") == "converted")
            return converted / len(recent)
        except Exception as exc:
            logger.error("Gagal hitung CVR platform %s: %s", platform, exc)
            return 0.0

    async def check_low_conversion_alert(self, platform: str) -> bool:
        try:
            low_days = 0
            for day_offset in range(LOW_CVR_DAYS):
                end = datetime.now(timezone.utc) - timedelta(days=day_offset)
                start = end - timedelta(days=1)
                all_leads = await self.db.select("marketing_leads",
                                                 filters={"source_platform": platform}, limit=1000)
                day_leads = [r for r in all_leads
                             if start <= self._parse_dt(r.get("created_at")) < end]
                if not day_leads:
                    low_days += 1
                    continue
                converted = sum(1 for r in day_leads if r.get("status") == "converted")
                if converted / len(day_leads) < LOW_CVR_THRESHOLD:
                    low_days += 1
                else:
                    break
            return low_days >= LOW_CVR_DAYS
        except Exception as exc:
            logger.error("Gagal cek low CVR alert %s: %s", platform, exc)
            return False

    @staticmethod
    def _parse_dt(value: object) -> datetime:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        return datetime.min.replace(tzinfo=timezone.utc)
