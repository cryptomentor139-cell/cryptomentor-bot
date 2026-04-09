"""
A/B Testing Manager — kelola sesi A/B test konten marketing.
marketing/agent/core/ab_testing.py
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

VALID_TEST_VARIABLES = {"hook_type", "content_format", "post_time", "caption_length"}
KILL_CTR_THRESHOLD = 0.01
KILL_HOURS = 48
EVAL_HOURS = 24


@dataclass
class ABTestSession:
    id: str
    campaign_id: str
    test_variable: str
    variant_a_content_id: str
    variant_b_content_id: str
    started_at: datetime
    evaluation_at: datetime


class ABTestManager:
    def __init__(self, db: SupabaseDB) -> None:
        self.db = db

    async def create_test(self, campaign_id: str, test_variable: str,
                          variant_a_id: str, variant_b_id: str) -> ABTestSession:
        if test_variable not in VALID_TEST_VARIABLES:
            test_variable = "hook_type"

        now = datetime.now(timezone.utc)
        evaluation_at = now + timedelta(hours=EVAL_HOURS)
        test_id = str(uuid.uuid4())

        data = {
            "id": test_id,
            "campaign_id": campaign_id,
            "test_variable": test_variable,
            "variant_a_content_id": variant_a_id,
            "variant_b_content_id": variant_b_id,
            "started_at": now.isoformat(),
            "evaluation_at": evaluation_at.isoformat(),
            "status": "running",
        }

        try:
            result = await self.db.insert("marketing_ab_tests", data)
            saved_id = result.get("id", test_id)
        except Exception as exc:
            logger.error("Gagal menyimpan A/B test: %s", exc)
            saved_id = test_id

        return ABTestSession(
            id=saved_id, campaign_id=campaign_id, test_variable=test_variable,
            variant_a_content_id=variant_a_id, variant_b_content_id=variant_b_id,
            started_at=now, evaluation_at=evaluation_at,
        )

    async def evaluate_winner(self, test_id: str) -> Optional[str]:
        try:
            rows = await self.db.select("marketing_ab_tests", filters={"id": test_id})
        except Exception as exc:
            logger.error("Gagal ambil A/B test %s: %s", test_id, exc)
            return None

        if not rows:
            return None

        test = rows[0]
        started_at_raw = test.get("started_at")
        if not started_at_raw:
            return None

        started_at = datetime.fromisoformat(str(started_at_raw).replace("Z", "+00:00"))
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)

        hours_elapsed = (datetime.now(timezone.utc) - started_at).total_seconds() / 3600

        if hours_elapsed < EVAL_HOURS:
            return None

        ctr_a = await self._get_content_ctr(test.get("variant_a_content_id"))
        ctr_b = await self._get_content_ctr(test.get("variant_b_content_id"))

        if hours_elapsed >= KILL_HOURS and ctr_a < KILL_CTR_THRESHOLD and ctr_b < KILL_CTR_THRESHOLD:
            await self._update_test_status(test_id, "killed", None, ctr_a, ctr_b)
            return "kill"

        winner = "A" if ctr_a >= ctr_b else "B"
        return winner

    async def record_pattern(self, test_id: str, winner: str) -> None:
        winner_variant = winner if winner in ("A", "B") else None
        status = "completed" if winner in ("A", "B") else "killed"
        try:
            rows = await self.db.select("marketing_ab_tests", filters={"id": test_id})
            if rows:
                test = rows[0]
                ctr_a = await self._get_content_ctr(test.get("variant_a_content_id"))
                ctr_b = await self._get_content_ctr(test.get("variant_b_content_id"))
            else:
                ctr_a, ctr_b = 0.0, 0.0
        except Exception:
            ctr_a, ctr_b = 0.0, 0.0

        await self._update_test_status(test_id, status, winner_variant, ctr_a, ctr_b)

    async def _get_content_ctr(self, content_id: Optional[str]) -> float:
        if not content_id:
            return 0.0
        try:
            rows = await self.db.select("marketing_analytics", filters={"content_id": content_id}, limit=10)
            ctrs = [float(r.get("ctr") or 0) for r in rows]
            return sum(ctrs) / len(ctrs) if ctrs else 0.0
        except Exception:
            return 0.0

    async def _update_test_status(self, test_id: str, status: str,
                                   winner: Optional[str], ctr_a: float, ctr_b: float) -> None:
        try:
            await self.db.update("marketing_ab_tests", test_id, {
                "status": status, "winner_variant": winner,
                "variant_a_ctr": round(ctr_a, 4), "variant_b_ctr": round(ctr_b, 4),
            })
        except Exception as exc:
            logger.error("Gagal update A/B test %s: %s", test_id, exc)
