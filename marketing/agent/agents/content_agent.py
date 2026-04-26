"""
Content Agent — generate batch konten marketing (feed + reels) per siklus kampanye.
marketing/agent/agents/content_agent.py
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import List

from marketing.agent.agents.strategist_agent import CampaignPlan
from marketing.agent.config import Config
from marketing.agent.core.audience_intelligence import AudienceIntelligence, AudiencePersona
from marketing.agent.core.content_engine import ContentEngine, PASContent, SYSTEM_PROMPT
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FeedContent:
    topic: str
    persona: AudiencePersona
    emotion_type: str       # "fear", "greed", "education"
    pas: PASContent
    image_size: str         # "1080x1080" or "1080x1350"
    template: str           # "product" or "education"
    image_path: str | None = None  # diisi oleh DesignerAgent setelah render


@dataclass
class ReelsScript:
    topic: str
    persona: AudiencePersona
    hook_segment: str           # 3-5 detik
    main_content: str           # 10-45 detik
    cta_segment: str            # 3-5 detik
    narration: str              # full narasi untuk voice-over
    visual_description: str     # instruksi visual untuk Kling AI
    caption: str
    hashtags: List[str]
    duration_target: int        # dalam detik, max 60
    video_path: str | None = None  # diisi oleh DesignerAgent setelah generate


@dataclass
class ContentItem:
    id: str
    content_type: str           # "feed" or "reels"
    feed: FeedContent = None
    reels: ReelsScript = None
    hooks: List[str] = field(default_factory=list)
    status: str = "draft"


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_REELS_PROMPT = (
    "Buat skrip Reels Instagram untuk persona {persona} dengan topik: {topic}\n"
    "Struktur skrip (total max 60 detik):\n"
    "- hook_segment: kalimat pembuka yang menarik perhatian (3-5 detik)\n"
    "- main_content: isi utama yang edukatif/persuasif (10-45 detik)\n"
    "- cta_segment: ajakan bertindak yang jelas (3-5 detik), WAJIB sertakan 't.me/cryptomentor_bot'\n"
    "- narration: teks narasi lengkap untuk voice-over (gabungan semua segmen)\n"
    "- visual_description: deskripsi visual yang vivid dan spesifik untuk Kling AI "
    "(deskripsikan scene, warna, gerakan, suasana, elemen visual yang menarik)\n"
    "- caption: caption Instagram 150-300 karakter\n"
    "- hashtags: array 3-5 hashtag relevan\n"
    "- duration_target: estimasi durasi total dalam detik (max 60)\n"
    "Emotion trigger: {emotion_trigger}\n"
    "Output JSON dengan semua field di atas."
)

_DEFAULT_CTA = "Mulai trading otomatis sekarang di t.me/cryptomentor_bot"


# ---------------------------------------------------------------------------
# ContentAgent
# ---------------------------------------------------------------------------

class ContentAgent:
    """
    Agen konten yang menghasilkan batch 10 konten per siklus kampanye:
    3 fear-based, 3 greed-based, 4 edukasi — mix 6 feed + 4 reels.
    """

    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db
        self.content_engine = ContentEngine()
        self.audience_intel = AudienceIntelligence()

    # ------------------------------------------------------------------
    # Batch Generation
    # ------------------------------------------------------------------

    async def generate_batch(self, plan: CampaignPlan) -> List[ContentItem]:
        """
        Generate 10 konten per siklus:
        - 3 fear-based  (persona Fear_Driven)  → feed
        - 3 greed-based (persona Greed_Driven) → feed
        - 4 edukasi     (persona Beginner)     → 2 feed + 4 reels (total 4 reels)

        Mix: 6 feed + 4 reels
        Topik diambil dari plan.market_sentiment.key_topics (rotasi).
        """
        topics = plan.market_sentiment.key_topics or ["AutoTrade", "Risk Management", "Crypto Education"]
        items: List[ContentItem] = []

        # Helper untuk rotasi topik
        def get_topic(index: int) -> str:
            return topics[index % len(topics)]

        # --- 3 fear-based feed ---
        for i in range(3):
            topic = get_topic(i)
            try:
                feed = await self.generate_feed_content(topic, AudiencePersona.FEAR_DRIVEN, "fear")
                hooks = await self.generate_hooks(topic, count=3)
                item = ContentItem(
                    id=str(uuid.uuid4()),
                    content_type="feed",
                    feed=feed,
                    hooks=hooks,
                    status="draft",
                )
                await self._save_content_to_db(item, plan.id)
                items.append(item)
            except Exception as exc:
                logger.error("Gagal generate fear feed #%d: %s", i + 1, exc)

        # --- 3 greed-based feed ---
        for i in range(3):
            topic = get_topic(i + 3)
            try:
                feed = await self.generate_feed_content(topic, AudiencePersona.GREED_DRIVEN, "greed")
                hooks = await self.generate_hooks(topic, count=3)
                item = ContentItem(
                    id=str(uuid.uuid4()),
                    content_type="feed",
                    feed=feed,
                    hooks=hooks,
                    status="draft",
                )
                await self._save_content_to_db(item, plan.id)
                items.append(item)
            except Exception as exc:
                logger.error("Gagal generate greed feed #%d: %s", i + 1, exc)

        # --- 4 edukasi: 2 feed + 2 reels (total 4 reels dari batch) ---
        # Sesuai spec: 6 feed + 4 reels total
        # fear(3 feed) + greed(3 feed) + edu(0 feed + 4 reels) = 6 feed + 4 reels
        for i in range(4):
            topic = get_topic(i + 6)
            try:
                reels = await self.generate_reels_script(topic, AudiencePersona.BEGINNER)
                hooks = await self.generate_hooks(topic, count=3)
                item = ContentItem(
                    id=str(uuid.uuid4()),
                    content_type="reels",
                    reels=reels,
                    hooks=hooks,
                    status="draft",
                )
                await self._save_content_to_db(item, plan.id)
                items.append(item)
            except Exception as exc:
                logger.error("Gagal generate edu reels #%d: %s", i + 1, exc)

        logger.info(
            "Batch selesai: %d konten dihasilkan (target 10) untuk campaign %s",
            len(items),
            plan.id,
        )
        return items

    # ------------------------------------------------------------------
    # Feed Content
    # ------------------------------------------------------------------

    async def generate_feed_content(
        self,
        topic: str,
        persona: AudiencePersona,
        emotion_type: str,
    ) -> FeedContent:
        """
        Generate konten feed Instagram dengan PAS framework.

        Template selection:
        - emotion_type "education" → template "education", size "1080x1350"
        - emotion_type "fear" atau "greed" → template "product", size "1080x1080"
        """
        pas = await self.apply_pas_framework(topic, persona)

        # Pastikan CTA ada
        if not pas.cta or "t.me" not in pas.cta:
            pas = PASContent(
                hook=pas.hook,
                problem=pas.problem,
                agitate=pas.agitate,
                solution=pas.solution,
                cta=_DEFAULT_CTA,
                caption=pas.caption,
                hashtags=pas.hashtags,
                ai_provider=pas.ai_provider,
            )

        if emotion_type == "education":
            template = "education"
            image_size = "1080x1350"
        else:
            template = "product"
            image_size = "1080x1080"

        return FeedContent(
            topic=topic,
            persona=persona,
            emotion_type=emotion_type,
            pas=pas,
            image_size=image_size,
            template=template,
        )

    # ------------------------------------------------------------------
    # Reels Script
    # ------------------------------------------------------------------

    async def generate_reels_script(
        self,
        topic: str,
        persona: AudiencePersona,
    ) -> ReelsScript:
        """
        Generate skrip Reels dengan struktur:
        - hook (3-5 detik)
        - main_content (10-45 detik)
        - cta (3-5 detik, selalu sertakan t.me/cryptomentor_bot)
        Total max 60 detik.
        """
        emotion_trigger = self.audience_intel.get_emotion_trigger(persona)

        user_prompt = _REELS_PROMPT.format(
            persona=persona.value,
            topic=topic,
            emotion_trigger=emotion_trigger.value,
        )

        try:
            raw, _ = await self.content_engine._call_ai_with_fallback(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            data = ContentEngine._parse_json_response(raw)
        except Exception as exc:
            logger.warning("generate_reels_script AI gagal, menggunakan fallback: %s", exc)
            data = {}

        hook_segment = data.get("hook_segment", f"Tau gak? {topic} bisa ubah cara trading kamu!")
        main_content = data.get("main_content", f"Dengan CryptoMentor, kamu bisa manfaatkan {topic} secara otomatis.")
        cta_segment = data.get("cta_segment", _DEFAULT_CTA)

        # Pastikan CTA selalu ada link t.me
        if "t.me/cryptomentor_bot" not in cta_segment:
            cta_segment = f"{cta_segment} Coba di t.me/cryptomentor_bot"

        narration = data.get("narration", f"{hook_segment} {main_content} {cta_segment}")
        visual_description = data.get(
            "visual_description",
            f"Video dinamis dengan grafik kripto, warna biru dan hijau, "
            f"menampilkan dashboard trading CryptoMentor, suasana profesional dan modern.",
        )

        caption = data.get("caption", f"{topic} — trading otomatis dengan AI. {_DEFAULT_CTA}")
        caption = await self.content_engine.validate_caption_length(caption)
        caption = await self.content_engine.add_disclaimer_if_needed(caption)

        hashtags = data.get("hashtags", ["#CryptoMentor", "#TradingKripto", "#AutoTrade"])
        if not isinstance(hashtags, list):
            hashtags = ["#CryptoMentor", "#TradingKripto", "#AutoTrade"]

        duration_target = int(data.get("duration_target", 45))
        duration_target = min(60, max(15, duration_target))

        return ReelsScript(
            topic=topic,
            persona=persona,
            hook_segment=hook_segment,
            main_content=main_content,
            cta_segment=cta_segment,
            narration=narration,
            visual_description=visual_description,
            caption=caption,
            hashtags=hashtags,
            duration_target=duration_target,
        )

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    async def generate_hooks(self, topic: str, count: int = 3) -> List[str]:
        """Generate minimal 3 varian hook untuk A/B testing."""
        return await self.content_engine.generate_hooks(topic, count=count)

    # ------------------------------------------------------------------
    # PAS Framework
    # ------------------------------------------------------------------

    async def apply_pas_framework(self, topic: str, persona: AudiencePersona) -> PASContent:
        """Generate konten berstruktur PAS menggunakan ContentEngine."""
        return await self.content_engine.generate_with_pas(topic, persona)

    # ------------------------------------------------------------------
    # Save to DB
    # ------------------------------------------------------------------

    async def _save_content_to_db(self, item: ContentItem, campaign_id: str) -> str:
        """
        Simpan ContentItem ke tabel marketing_content dengan status "draft".
        Return content_id.
        """
        data: dict = {
            "id": item.id,
            "campaign_id": campaign_id,
            "content_type": item.content_type,
            "status": item.status,
        }

        if item.content_type == "feed" and item.feed:
            feed = item.feed
            data.update({
                "topic_category": "product_highlight" if feed.emotion_type != "education" else "crypto_education",
                "target_persona": feed.persona.value,
                "emotion_trigger": feed.emotion_type if feed.emotion_type in ("fear", "greed") else "security",
                "hook": feed.pas.hook,
                "caption": feed.pas.caption,
                "hashtags": feed.pas.hashtags,
                "pas_problem": feed.pas.problem,
                "pas_agitate": feed.pas.agitate,
                "pas_solution": feed.pas.solution,
                "pas_cta": feed.pas.cta,
                "ai_provider": feed.pas.ai_provider,
            })

        elif item.content_type == "reels" and item.reels:
            reels = item.reels
            emotion_trigger = self.audience_intel.get_emotion_trigger(reels.persona)
            data.update({
                "topic_category": "crypto_education",
                "target_persona": reels.persona.value,
                "emotion_trigger": emotion_trigger.value,
                "hook": reels.hook_segment,
                "caption": reels.caption,
                "hashtags": reels.hashtags,
                "pas_cta": reels.cta_segment,
            })

        try:
            result = await self.db.insert("marketing_content", data)
            saved_id = result.get("id", item.id)
            logger.debug("Konten disimpan: id=%s, type=%s", saved_id, item.content_type)
            return saved_id
        except Exception as exc:
            logger.error("Gagal menyimpan konten %s: %s", item.id, exc)
            return item.id
