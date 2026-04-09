"""
Strategist Agent — analisa market sentiment, tentukan campaign angle dan persona target.
marketing/agent/agents/strategist_agent.py
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

from marketing.agent.config import Config
from marketing.agent.core.audience_intelligence import (
    AudienceIntelligence,
    AudiencePersona,
    EmotionTrigger,
)
from marketing.agent.core.content_engine import ContentEngine, SYSTEM_PROMPT
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MarketSentiment:
    trend: str              # "bullish", "bearish", "sideways"
    fear_greed_index: int   # 0-100
    dominant_emotion: str   # "fear", "greed", "neutral"
    key_topics: list[str]


@dataclass
class CampaignPlan:
    id: str
    cycle_number: int
    market_sentiment: MarketSentiment
    campaign_angle: str
    target_persona: AudiencePersona
    emotion_trigger: EmotionTrigger
    strategist_notes: str


@dataclass
class AnalystFeedback:
    best_performing_persona: Optional[str]
    best_performing_hook_type: Optional[str]
    recommended_angle: Optional[str]
    notes: str


# ---------------------------------------------------------------------------
# Default fallback values
# ---------------------------------------------------------------------------

_FALLBACK_SENTIMENT = MarketSentiment(
    trend="sideways",
    fear_greed_index=50,
    dominant_emotion="neutral",
    key_topics=["AutoTrade", "Risk Management", "Crypto Education"],
)

_SENTIMENT_PROMPT = (
    "Analisa kondisi market kripto saat ini. Tentukan: "
    "trend (bullish/bearish/sideways), fear_greed_index (0-100), "
    "dominant_emotion (fear/greed/neutral), dan 3-5 topik kripto yang sedang trending. "
    "Output JSON dengan field: trend, fear_greed_index, dominant_emotion, key_topics (array string)."
)

# Angle mapping berdasarkan dominant_emotion
_EMOTION_ANGLE_MAP: dict[str, str] = {
    "fear": "keamanan dan proteksi modal",
    "greed": "peluang profit dan growth",
    "neutral": "edukasi dan konsistensi",
}

# Persona mapping berdasarkan emotion_trigger
_TRIGGER_PERSONA_MAP: dict[EmotionTrigger, AudiencePersona] = {
    EmotionTrigger.FEAR: AudiencePersona.FEAR_DRIVEN,
    EmotionTrigger.GREED: AudiencePersona.GREED_DRIVEN,
    EmotionTrigger.SECURITY: AudiencePersona.BEGINNER,
}


# ---------------------------------------------------------------------------
# StrategistAgent
# ---------------------------------------------------------------------------

class StrategistAgent:
    """
    Agen strategist yang menganalisa market sentiment, menentukan campaign angle,
    memilih persona target, dan menyimpan campaign plan ke Supabase.
    """

    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db
        self.content_engine = ContentEngine()
        self.audience_intel = AudienceIntelligence()

    # ------------------------------------------------------------------
    # Market Sentiment Analysis
    # ------------------------------------------------------------------

    async def analyze_market_sentiment(self) -> MarketSentiment:
        """
        Analisa kondisi market kripto menggunakan AI.
        Fallback ke default sideways/neutral jika AI gagal.
        """
        try:
            raw, _ = await self.content_engine._call_ai_with_fallback(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=_SENTIMENT_PROMPT,
            )
            data = ContentEngine._parse_json_response(raw)

            trend = str(data.get("trend", "sideways")).lower()
            if trend not in ("bullish", "bearish", "sideways"):
                trend = "sideways"

            fear_greed = int(data.get("fear_greed_index", 50))
            fear_greed = max(0, min(100, fear_greed))

            dominant_emotion = str(data.get("dominant_emotion", "neutral")).lower()
            if dominant_emotion not in ("fear", "greed", "neutral"):
                dominant_emotion = "neutral"

            key_topics = data.get("key_topics", [])
            if not isinstance(key_topics, list) or not key_topics:
                key_topics = _FALLBACK_SENTIMENT.key_topics

            return MarketSentiment(
                trend=trend,
                fear_greed_index=fear_greed,
                dominant_emotion=dominant_emotion,
                key_topics=key_topics,
            )

        except Exception as exc:
            logger.warning("analyze_market_sentiment gagal, menggunakan fallback: %s", exc)
            return _FALLBACK_SENTIMENT

    # ------------------------------------------------------------------
    # Campaign Angle Determination
    # ------------------------------------------------------------------

    async def determine_campaign_angle(
        self,
        sentiment: MarketSentiment,
        feedback: Optional[AnalystFeedback] = None,
    ) -> CampaignPlan:
        """
        Tentukan campaign angle berdasarkan market sentiment dan feedback Analyst.
        Buat CampaignPlan lengkap dengan persona dan emotion trigger.
        """
        # Tentukan angle dasar dari dominant_emotion
        angle = _EMOTION_ANGLE_MAP.get(sentiment.dominant_emotion, "edukasi dan konsistensi")

        # Override dengan rekomendasi Analyst jika tersedia
        if feedback and feedback.recommended_angle:
            angle = feedback.recommended_angle
            logger.info("Campaign angle di-override oleh Analyst: %s", angle)

        # Tentukan emotion trigger dari angle
        if "proteksi" in angle or "keamanan" in angle:
            emotion_trigger = EmotionTrigger.FEAR
        elif "profit" in angle or "growth" in angle:
            emotion_trigger = EmotionTrigger.GREED
        else:
            emotion_trigger = EmotionTrigger.SECURITY

        # Pilih persona berdasarkan emotion trigger
        target_persona = _TRIGGER_PERSONA_MAP.get(emotion_trigger, AudiencePersona.BEGINNER)

        # Buat catatan strategist
        notes_parts = [
            f"Market trend: {sentiment.trend}",
            f"Fear/Greed Index: {sentiment.fear_greed_index}",
            f"Dominant emotion: {sentiment.dominant_emotion}",
            f"Campaign angle: {angle}",
        ]
        if feedback and feedback.notes:
            notes_parts.append(f"Analyst notes: {feedback.notes}")

        cycle_number = await self.get_latest_cycle_number() + 1

        plan = CampaignPlan(
            id=str(uuid.uuid4()),
            cycle_number=cycle_number,
            market_sentiment=sentiment,
            campaign_angle=angle,
            target_persona=target_persona,
            emotion_trigger=emotion_trigger,
            strategist_notes="\n".join(notes_parts),
        )

        return plan

    # ------------------------------------------------------------------
    # Persona Selection
    # ------------------------------------------------------------------

    async def select_target_persona(self, plan: CampaignPlan) -> AudiencePersona:
        """
        Pilih persona target berdasarkan emotion_trigger dari campaign plan.

        - fear  → Fear_Driven
        - greed → Greed_Driven
        - default → Beginner
        """
        return _TRIGGER_PERSONA_MAP.get(plan.emotion_trigger, AudiencePersona.BEGINNER)

    # ------------------------------------------------------------------
    # Save Campaign Plan
    # ------------------------------------------------------------------

    async def save_campaign_plan(self, plan: CampaignPlan) -> str:
        """
        Simpan campaign plan ke tabel marketing_campaigns di Supabase.
        Return plan_id (UUID string).
        """
        sentiment = plan.market_sentiment
        analyst_feedback: dict | None = None

        data = {
            "id": plan.id,
            "cycle_number": plan.cycle_number,
            "market_sentiment": sentiment.trend,
            "campaign_angle": plan.campaign_angle,
            "target_persona": plan.target_persona.value,
            "emotion_trigger": plan.emotion_trigger.value,
            "strategist_notes": plan.strategist_notes,
            "analyst_feedback": json.dumps({
                "fear_greed_index": sentiment.fear_greed_index,
                "dominant_emotion": sentiment.dominant_emotion,
                "key_topics": sentiment.key_topics,
            }),
            "status": "active",
        }

        try:
            result = await self.db.insert("marketing_campaigns", data)
            saved_id = result.get("id", plan.id)
            logger.info("Campaign plan disimpan: id=%s, cycle=%d", saved_id, plan.cycle_number)
            return saved_id
        except Exception as exc:
            logger.error("Gagal menyimpan campaign plan: %s", exc)
            return plan.id

    # ------------------------------------------------------------------
    # Cycle Number
    # ------------------------------------------------------------------

    async def get_latest_cycle_number(self) -> int:
        """
        Ambil cycle_number terbesar dari tabel marketing_campaigns.
        Return 0 jika belum ada data.
        """
        try:
            rows = await self.db.select("marketing_campaigns", limit=1)
            # Supabase tidak support ORDER BY via select helper, ambil semua dan cari max
            all_rows = await self.db.select("marketing_campaigns", limit=1000)
            if not all_rows:
                return 0
            return max(row.get("cycle_number", 0) for row in all_rows)
        except Exception as exc:
            logger.warning("Gagal mengambil cycle number: %s", exc)
            return 0
