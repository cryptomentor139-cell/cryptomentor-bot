"""
Audience Intelligence — klasifikasi persona dan segmen audiens CryptoMentor.
Data pain points dan emotion trigger diambil dari brand_context.json.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AudiencePersona(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE_TRADER = "Intermediate_Trader"
    FEAR_DRIVEN = "Fear_Driven"
    GREED_DRIVEN = "Greed_Driven"


class AudienceSegment(str, Enum):
    COLD = "Cold"
    WARM = "Warm"
    HOT = "Hot"


class EmotionTrigger(str, Enum):
    FEAR = "fear"
    GREED = "greed"
    SECURITY = "security"


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class PersonaProfile:
    persona: AudiencePersona
    pain_points: List[str]
    emotion_trigger: EmotionTrigger
    message: str


# ---------------------------------------------------------------------------
# Keyword maps
# ---------------------------------------------------------------------------

_PERSONA_KEYWORDS: dict[AudiencePersona, list[str]] = {
    AudiencePersona.BEGINNER: [
        "pemula", "baru", "belajar", "tidak tahu", "newbie",
    ],
    AudiencePersona.INTERMEDIATE_TRADER: [
        "sudah trading", "sering loss", "tidak konsisten",
    ],
    AudiencePersona.FEAR_DRIVEN: [
        "takut", "rugi", "scam", "risiko", "bahaya",
    ],
    AudiencePersona.GREED_DRIVEN: [
        "cepat kaya", "profit besar", "fomo", "pump",
    ],
}

# Keywords that indicate a HOT segment (ready to buy / high intent)
_HOT_KEYWORDS: list[str] = ["daftar", "harga", "cara", "berapa", "mau coba"]


# ---------------------------------------------------------------------------
# Helper — load brand_context.json once
# ---------------------------------------------------------------------------

_BRAND_CONTEXT_PATH = Path(__file__).parent.parent / "brand_context.json"
_brand_context_cache: dict[str, Any] | None = None


def _get_brand_context() -> dict[str, Any]:
    global _brand_context_cache
    if _brand_context_cache is None:
        with open(_BRAND_CONTEXT_PATH, encoding="utf-8") as f:
            _brand_context_cache = json.load(f)
    return _brand_context_cache


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class AudienceIntelligence:
    """
    Mengklasifikasikan persona dan segmen audiens berdasarkan profil dan
    riwayat interaksi. Data referensi diambil dari brand_context.json.
    """

    # ------------------------------------------------------------------
    # Persona classification
    # ------------------------------------------------------------------

    def classify_persona(self, profile: dict) -> AudiencePersona:
        """
        Klasifikasi persona berdasarkan keywords di nilai-nilai profile dict.

        Urutan prioritas: Fear_Driven > Greed_Driven > Intermediate_Trader > Beginner.
        Default jika tidak ada match: Beginner.
        """
        # Gabungkan semua nilai string dari profile menjadi satu teks lowercase
        combined = " ".join(
            str(v).lower() for v in profile.values() if v is not None
        )

        # Cek setiap persona sesuai urutan prioritas
        priority_order = [
            AudiencePersona.FEAR_DRIVEN,
            AudiencePersona.GREED_DRIVEN,
            AudiencePersona.INTERMEDIATE_TRADER,
            AudiencePersona.BEGINNER,
        ]

        for persona in priority_order:
            for keyword in _PERSONA_KEYWORDS[persona]:
                if keyword.lower() in combined:
                    return persona

        return AudiencePersona.BEGINNER

    # ------------------------------------------------------------------
    # Segment classification
    # ------------------------------------------------------------------

    def classify_segment(self, interactions: list) -> AudienceSegment:
        """
        Klasifikasi segmen berdasarkan jumlah dan konten interaksi.

        - Cold  : 0 interaksi
        - Warm  : 1–3 interaksi atau ada pertanyaan umum
        - Hot   : ada keyword high-intent ("daftar", "harga", "cara", "berapa", "mau coba")
        """
        if not interactions:
            return AudienceSegment.COLD

        # Gabungkan semua teks interaksi
        combined = " ".join(
            str(item).lower() if isinstance(item, str)
            else " ".join(str(v).lower() for v in item.values() if v is not None)
            if isinstance(item, dict)
            else str(item).lower()
            for item in interactions
        )

        # Cek keyword HOT terlebih dahulu
        for keyword in _HOT_KEYWORDS:
            if keyword.lower() in combined:
                return AudienceSegment.HOT

        # 1–3 interaksi → Warm; lebih dari 3 tanpa keyword HOT → tetap Warm
        return AudienceSegment.WARM

    # ------------------------------------------------------------------
    # Pain points & emotion trigger
    # ------------------------------------------------------------------

    def get_pain_points(self, persona: AudiencePersona) -> List[str]:
        """Return daftar pain points untuk persona dari brand_context.json."""
        ctx = _get_brand_context()
        persona_data = ctx.get("personas", {}).get(persona.value, {})
        return persona_data.get("pain_points", [])

    def get_emotion_trigger(self, persona: AudiencePersona) -> EmotionTrigger:
        """Return emotion trigger untuk persona dari brand_context.json."""
        ctx = _get_brand_context()
        persona_data = ctx.get("personas", {}).get(persona.value, {})
        trigger_str = persona_data.get("emotion_trigger", "security")
        return EmotionTrigger(trigger_str)

    # ------------------------------------------------------------------
    # Full persona profile
    # ------------------------------------------------------------------

    def get_persona_profile(self, persona: AudiencePersona) -> PersonaProfile:
        """Return PersonaProfile lengkap untuk persona yang diberikan."""
        ctx = _get_brand_context()
        persona_data = ctx.get("personas", {}).get(persona.value, {})

        return PersonaProfile(
            persona=persona,
            pain_points=persona_data.get("pain_points", []),
            emotion_trigger=EmotionTrigger(persona_data.get("emotion_trigger", "security")),
            message=persona_data.get("message", ""),
        )
