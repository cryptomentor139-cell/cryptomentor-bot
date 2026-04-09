"""
Content Engine — generate konten marketing CryptoMentor menggunakan PAS framework
dengan rotasi AI provider: Cerebras → DeepSeek → OpenAI.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

import httpx

from marketing.agent.core.audience_intelligence import AudiencePersona, EmotionTrigger

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AIProvider(str, Enum):
    CEREBRAS = "cerebras"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"


class HookType(str, Enum):
    NUMBER = "number"          # "90% trader rugi karena..."
    QUESTION = "question"      # "Kenapa AI lebih profit?"
    CONTRARIAN = "contrarian"  # "Stop belajar chart..."


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class PASContent:
    hook: str
    problem: str
    agitate: str
    solution: str
    cta: str
    caption: str
    hashtags: List[str]
    ai_provider: str


# ---------------------------------------------------------------------------
# Prompt constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "Kamu adalah copywriter marketing CryptoMentor yang ahli dalam konten kripto Indonesia.\n"
    "Brand: CryptoMentor — AI Trading Assistant untuk trader kripto Indonesia.\n"
    "Produk utama: AutoTrade (trading otomatis), StackMentor (manajemen modal 60/30/10),\n"
    "Scalping Mode, multi-exchange (BingX, Binance, Bybit, Bitunix).\n"
    "Target: trader kripto Indonesia, usia 20-35 tahun.\n"
    "Tone: santai, percaya diri, edukatif, tidak hard selling.\n"
    "WAJIB: Setiap konten dengan klaim finansial harus diakhiri dengan disclaimer."
)

_PAS_TEMPLATE = (
    "Buat konten {content_type} untuk persona {persona} dengan topik: {topic}\n"
    "Struktur PAS:\n"
    "- Problem: masalah spesifik {persona}\n"
    "- Agitate: perkuat urgensi dengan data/skenario nyata\n"
    "- Solution: solusi CryptoMentor yang relevan\n"
    "- CTA: ajakan bertindak spesifik, sertakan link t.me/cryptomentor_bot\n"
    "Emotion trigger: {emotion_trigger}\n"
    "Output JSON: {{hook, problem, agitate, solution, cta, caption (150-300 karakter), hashtags (array 3-5)}}"
)

_HOOK_PROMPTS: dict[HookType, str] = {
    HookType.NUMBER: (
        "Buat hook dengan angka spesifik untuk topik: {topic}. "
        "Contoh: '90% trader rugi karena...'. "
        "Kembalikan hanya teks hook saja, tanpa penjelasan tambahan."
    ),
    HookType.QUESTION: (
        "Buat hook berupa pertanyaan provokatif untuk topik: {topic}. "
        "Contoh: 'Kenapa AI lebih profit dari manusia?'. "
        "Kembalikan hanya teks hook saja, tanpa penjelasan tambahan."
    ),
    HookType.CONTRARIAN: (
        "Buat hook pernyataan kontraintuitif untuk topik: {topic}. "
        "Contoh: 'Stop belajar chart, ini yang lebih penting'. "
        "Kembalikan hanya teks hook saja, tanpa penjelasan tambahan."
    ),
}

# ---------------------------------------------------------------------------
# Provider API configs
# ---------------------------------------------------------------------------

_PROVIDER_CONFIGS: dict[str, dict] = {
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "model": "llama-3.3-70b",
        "env_key": "CEREBRAS_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
}


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class ContentEngine:
    """
    Generate konten marketing menggunakan PAS framework dengan rotasi
    AI provider: Cerebras (utama) → DeepSeek → OpenAI (fallback).
    """

    PROVIDER_PRIORITY = [
        {"name": "cerebras", "model": "llama-3.3-70b"},
        {"name": "deepseek", "model": "deepseek-chat"},
        {"name": "openai", "model": "gpt-4o-mini"},
    ]

    FINANCIAL_KEYWORDS = ["profit", "untung", "return", "gain", "cuan", "%", "x lipat"]
    DISCLAIMER = "Bukan saran keuangan. Trading mengandung risiko."

    def __init__(self) -> None:
        self._provider_index: int = 0  # tracks current provider for round-robin

    # ------------------------------------------------------------------
    # Provider selection & rotation
    # ------------------------------------------------------------------

    def select_provider(self) -> AIProvider:
        """
        Pilih provider berdasarkan ketersediaan API key.
        Rotasi: Cerebras → DeepSeek → OpenAI.
        """
        for entry in self.PROVIDER_PRIORITY:
            name = entry["name"]
            cfg = _PROVIDER_CONFIGS[name]
            if os.getenv(cfg["env_key"]):
                return AIProvider(name)
        # Fallback ke OpenAI meskipun key tidak ada (akan error saat call)
        return AIProvider.OPENAI

    # ------------------------------------------------------------------
    # Low-level AI call
    # ------------------------------------------------------------------

    async def _call_ai(
        self,
        provider: AIProvider,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Panggil AI provider menggunakan httpx.AsyncClient (OpenAI-compatible API).
        Raise httpx.HTTPStatusError atau Exception jika gagal.
        """
        cfg = _PROVIDER_CONFIGS[provider.value]
        api_key = os.getenv(cfg["env_key"], "")
        url = f"{cfg['base_url']}/chat/completions"

        payload = {
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.8,
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_ai_with_fallback(
        self,
        system_prompt: str,
        user_prompt: str,
        preferred_provider: Optional[AIProvider] = None,
    ) -> tuple[str, str]:
        """
        Coba provider secara berurutan. Return (content, provider_name).
        """
        # Build ordered list: preferred first, then rest
        order = list(self.PROVIDER_PRIORITY)
        if preferred_provider:
            order = [p for p in order if p["name"] == preferred_provider.value] + \
                    [p for p in order if p["name"] != preferred_provider.value]

        last_error: Exception | None = None
        for entry in order:
            provider = AIProvider(entry["name"])
            cfg = _PROVIDER_CONFIGS[provider.value]
            if not os.getenv(cfg["env_key"]):
                logger.debug("Skipping %s — API key not set", provider.value)
                continue
            try:
                content = await self._call_ai(provider, system_prompt, user_prompt)
                return content, provider.value
            except Exception as exc:
                logger.warning("Provider %s failed: %s", provider.value, exc)
                last_error = exc

        raise RuntimeError(
            f"Semua AI provider gagal. Error terakhir: {last_error}"
        )

    # ------------------------------------------------------------------
    # PAS content generation
    # ------------------------------------------------------------------

    async def generate_with_pas(
        self,
        topic: str,
        persona: AudiencePersona,
        provider: Optional[AIProvider] = None,
    ) -> PASContent:
        """
        Generate konten lengkap menggunakan PAS framework.
        Otomatis fallback ke provider berikutnya jika gagal.
        """
        from marketing.agent.core.audience_intelligence import AudienceIntelligence

        ai = AudienceIntelligence()
        emotion_trigger = ai.get_emotion_trigger(persona)

        user_prompt = _PAS_TEMPLATE.format(
            content_type="feed Instagram",
            persona=persona.value,
            topic=topic,
            emotion_trigger=emotion_trigger.value,
        )

        raw, used_provider = await self._call_ai_with_fallback(
            SYSTEM_PROMPT, user_prompt, preferred_provider=provider
        )

        # Parse JSON dari response
        pas_data = self._parse_json_response(raw)

        caption = pas_data.get("caption", "")
        caption = await self.validate_caption_length(caption)
        caption = await self.add_disclaimer_if_needed(caption)

        return PASContent(
            hook=pas_data.get("hook", ""),
            problem=pas_data.get("problem", ""),
            agitate=pas_data.get("agitate", ""),
            solution=pas_data.get("solution", ""),
            cta=pas_data.get("cta", ""),
            caption=caption,
            hashtags=pas_data.get("hashtags", []),
            ai_provider=used_provider,
        )

    # ------------------------------------------------------------------
    # Hook generation
    # ------------------------------------------------------------------

    async def generate_hook(self, topic: str, hook_type: HookType) -> str:
        """Generate satu hook berdasarkan tipe yang ditentukan."""
        user_prompt = _HOOK_PROMPTS[hook_type].format(topic=topic)
        raw, _ = await self._call_ai_with_fallback(SYSTEM_PROMPT, user_prompt)
        return raw.strip()

    async def generate_hooks(self, topic: str, count: int = 3) -> List[str]:
        """
        Generate hooks — satu per tipe hook (NUMBER, QUESTION, CONTRARIAN).
        `count` dibatasi maksimal 3 (satu per tipe).
        """
        hook_types = list(HookType)[:count]
        hooks: List[str] = []
        for hook_type in hook_types:
            hook = await self.generate_hook(topic, hook_type)
            hooks.append(hook)
        return hooks

    # ------------------------------------------------------------------
    # Caption validation
    # ------------------------------------------------------------------

    async def validate_caption_length(
        self,
        caption: str,
        min_len: int = 150,
        max_len: int = 300,
    ) -> str:
        """
        Pastikan caption berada dalam rentang min_len–max_len karakter.
        - Jika terlalu pendek: minta AI untuk memperpanjang.
        - Jika terlalu panjang: potong di batas kata terdekat sebelum max_len.
        """
        if len(caption) < min_len:
            expand_prompt = (
                f"Panjang caption berikut hanya {len(caption)} karakter, "
                f"terlalu pendek. Panjang minimal adalah {min_len} karakter. "
                f"Perluas caption ini tanpa mengubah maknanya:\n\n{caption}"
            )
            try:
                expanded, _ = await self._call_ai_with_fallback(
                    SYSTEM_PROMPT, expand_prompt
                )
                caption = expanded.strip()
            except Exception:
                # Jika AI gagal, kembalikan caption asli
                pass

        if len(caption) > max_len:
            # Potong di batas kata terdekat
            truncated = caption[:max_len]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
            caption = truncated

        return caption

    # ------------------------------------------------------------------
    # Disclaimer
    # ------------------------------------------------------------------

    async def add_disclaimer_if_needed(self, content: str) -> str:
        """
        Tambahkan disclaimer jika konten mengandung keyword finansial.
        Disclaimer tidak ditambahkan jika sudah ada.
        """
        content_lower = content.lower()

        has_financial = any(kw.lower() in content_lower for kw in self.FINANCIAL_KEYWORDS)
        already_has_disclaimer = self.DISCLAIMER.lower() in content_lower

        if has_financial and not already_has_disclaimer:
            return f"{content}\n\n{self.DISCLAIMER}"

        return content

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json_response(raw: str) -> dict:
        """
        Parse JSON dari response AI. Coba beberapa strategi:
        1. Parse langsung
        2. Ekstrak blok ```json ... ```
        3. Cari kurung kurawal pertama dan terakhir
        """
        raw = raw.strip()

        # Strategi 1: parse langsung
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Strategi 2: ekstrak blok ```json
        if "```json" in raw:
            start = raw.index("```json") + 7
            end = raw.index("```", start)
            try:
                return json.loads(raw[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                pass

        # Strategi 3: cari { ... }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                pass

        # Fallback: kembalikan dict kosong dengan raw sebagai hook
        logger.warning("Tidak dapat parse JSON dari response AI, menggunakan fallback.")
        return {
            "hook": raw[:200] if raw else "",
            "problem": "",
            "agitate": "",
            "solution": "",
            "cta": "Coba sekarang di t.me/cryptomentor_bot",
            "caption": raw[:300] if raw else "",
            "hashtags": ["#CryptoMentor", "#TradingKripto"],
        }
