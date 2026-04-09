"""
Sales Agent — menangani lead dan closing via Telegram bot Bismillah.
Sales Agent HANYA berjalan di Telegram.
marketing/agent/agents/sales_agent.py
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import httpx

from marketing.agent.config import Config
from marketing.agent.core.audience_intelligence import AudienceIntelligence, AudienceSegment
from marketing.agent.core.lead_capture import Lead, LeadCaptureManager
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"
REGISTER_LINK = "https://t.me/cryptomentor_bot"


class ObjectionType(str, Enum):
    TAKUT_SCAM = "takut_scam"
    BISA_RUGI = "bisa_rugi"
    WORTH_IT = "worth_it"
    RIBET_SETUP = "ribet_setup"
    GRATIS_BENERAN = "gratis_beneran"


OBJECTION_KEYWORDS: dict[ObjectionType, list[str]] = {
    ObjectionType.TAKUT_SCAM: ["scam", "penipuan", "bohong", "tipu"],
    ObjectionType.BISA_RUGI: ["rugi", "loss", "risiko", "bahaya"],
    ObjectionType.WORTH_IT: ["worth", "manfaat", "hasil", "profit"],
    ObjectionType.RIBET_SETUP: ["ribet", "susah", "bingung", "cara"],
    ObjectionType.GRATIS_BENERAN: ["gratis", "bayar", "biaya", "fee"],
}

OBJECTION_RESPONSES: dict[ObjectionType, str] = {
    ObjectionType.TAKUT_SCAM: "Kami transparan 100%! CryptoMentor sudah dipercaya 500+ trader. Cek komunitas kami dan lihat sendiri hasil nyata dari pengguna aktif. Tidak ada biaya tersembunyi.",
    ObjectionType.BISA_RUGI: "Trading memang ada risikonya, tapi CryptoMentor punya stop loss otomatis yang melindungi modal kamu 24/7. Sistem kami dirancang untuk meminimalkan loss, bukan menghilangkannya.",
    ObjectionType.WORTH_IT: "Bayangkan tidak perlu pantau chart 24 jam, AI yang entry dan exit untuk kamu. Ratusan trader sudah merasakan manfaatnya. Coba dulu gratis, lihat sendiri hasilnya.",
    ObjectionType.RIBET_SETUP: "Setup cuma 5 menit! Tinggal connect exchange, set risk level, dan biarkan AI yang kerja. Ada panduan lengkap dan support tim kami siap bantu.",
    ObjectionType.GRATIS_BENERAN: "Ya, ada free trial! Kamu bisa coba fitur dasar tanpa bayar. Kalau cocok, baru upgrade ke premium. Tidak ada kartu kredit yang dibutuhkan.",
}

HOT_KEYWORDS = ["daftar", "harga", "cara", "berapa", "mau coba", "mulai", "register"]
OPTED_OUT_KEYWORDS = ["stop", "berhenti", "tidak mau", "unsubscribe", "hapus", "keluar"]

FOLLOWUP_MESSAGES = {
    "initial": f"Halo! 👋 Terima kasih sudah tertarik dengan CryptoMentor.\n\nKami hadir untuk membantu kamu trading kripto lebih cerdas dengan AI. Ada yang ingin kamu tanyakan?\n\nAtau langsung coba gratis di: {REGISTER_LINK}",
    "reengagement": f"Hei, sudah lama tidak ada kabar! 😊\n\nKami punya update terbaru — fitur AutoTrade sekarang support 4 exchange sekaligus. Mau tau lebih lanjut?\n\nCoba gratis: {REGISTER_LINK}",
    "warm": "Terima kasih sudah mau ngobrol! 🙏\n\nBanyak trader seperti kamu yang awalnya ragu, tapi setelah coba CryptoMentor mereka tidak mau balik ke cara manual lagi. Ada pertanyaan spesifik?",
}

CLOSING_MESSAGE = f"Kamu sudah siap untuk mulai trading lebih cerdas! 🚀\n\nDaftar sekarang dan dapatkan akses free trial:\n👉 {REGISTER_LINK}\n\nSetup hanya 5 menit, dan tim kami siap bantu jika ada kendala."


class SalesAgent:
    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db
        self.lead_manager = LeadCaptureManager(db)
        self.audience_intel = AudienceIntelligence()

    async def process_new_lead(self, lead: Lead) -> None:
        await self.send_followup(lead, message_type="initial")
        try:
            await self.db.update("marketing_leads", lead.id, {
                "status": "contacted", "followup_count": 1,
                "last_interaction_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            logger.error("Gagal update status lead %s: %s", lead.id, exc)

    async def send_followup(self, lead: Lead, message_type: str = "initial") -> bool:
        message = FOLLOWUP_MESSAGES.get(message_type, FOLLOWUP_MESSAGES["initial"])
        success = await self._send_telegram_message(lead.telegram_chat_id, message)
        await self._record_interaction(lead.id, "outbound", message_type, message)
        return success

    async def handle_objection(self, lead: Lead, text: str) -> str:
        objection = await self._detect_objection(text)
        if objection:
            response = OBJECTION_RESPONSES[objection]
            await self._record_interaction(lead.id, "outbound", "objection_handling", response, objection.value)
            return response
        return f"Terima kasih atas pertanyaannya! 😊 Ada hal spesifik yang ingin kamu ketahui tentang CryptoMentor? Atau langsung coba di {REGISTER_LINK}"

    async def classify_lead_segment(self, lead: Lead, interactions: list) -> AudienceSegment:
        segment = self.audience_intel.classify_segment(interactions)
        await self.lead_manager.update_segment(lead.id, segment)
        return segment

    async def attempt_closing(self, lead: Lead) -> bool:
        success = await self._send_telegram_message(lead.telegram_chat_id, CLOSING_MESSAGE)
        await self._record_interaction(lead.id, "outbound", "closing", CLOSING_MESSAGE)
        return success

    async def handle_telegram_message(self, telegram_chat_id: int, text: str) -> str:
        text_lower = text.lower().strip()
        lead = await self.lead_manager.record_lead(telegram_chat_id=telegram_chat_id, source_platform="telegram")

        await self._record_interaction(lead.id, "inbound", "general", text)
        try:
            await self.db.update("marketing_leads", lead.id,
                                 {"last_interaction_at": datetime.now(timezone.utc).isoformat()})
        except Exception:
            pass

        if any(kw in text_lower for kw in OPTED_OUT_KEYWORDS):
            await self._handle_opted_out(lead)
            return "Baik, kami menghormati keputusan kamu. Semoga sukses! 🙏"

        interactions = await self._get_lead_interactions(lead.id)
        await self.classify_lead_segment(lead, [text] + [i.get("message_content", "") for i in interactions])

        if await self._is_hot_intent(text_lower):
            await self.attempt_closing(lead)
            return CLOSING_MESSAGE

        objection = await self._detect_objection(text_lower)
        if objection:
            return await self.handle_objection(lead, text_lower)

        if lead.status == "new":
            await self.process_new_lead(lead)
            return FOLLOWUP_MESSAGES["initial"]

        return f"Terima kasih sudah menghubungi CryptoMentor! 😊\n\nKami siap membantu kamu memulai trading otomatis dengan AI. Ada pertanyaan? Atau langsung coba gratis di {REGISTER_LINK}"

    async def _send_telegram_message(self, chat_id: int, text: str) -> bool:
        url = TELEGRAM_API_BASE.format(token=self.config.telegram_bot_token)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json={
                    "chat_id": chat_id, "text": text,
                    "parse_mode": "HTML", "disable_web_page_preview": True,
                })
                response.raise_for_status()
                return response.json().get("ok", False)
        except Exception as exc:
            logger.error("Gagal kirim Telegram ke %d: %s", chat_id, exc)
            return False

    async def _detect_objection(self, text: str) -> Optional[ObjectionType]:
        for objection_type, keywords in OBJECTION_KEYWORDS.items():
            if any(kw in text.lower() for kw in keywords):
                return objection_type
        return None

    async def _is_hot_intent(self, text: str) -> bool:
        return any(kw in text.lower() for kw in HOT_KEYWORDS)

    async def _handle_opted_out(self, lead: Lead) -> None:
        try:
            await self.db.update("marketing_leads", lead.id, {"status": "opted_out"})
        except Exception as exc:
            logger.error("Gagal update opted_out lead %s: %s", lead.id, exc)

    async def _record_interaction(self, lead_id: str, direction: str, message_type: str,
                                   message_content: str, objection_type: Optional[str] = None) -> None:
        import uuid as _uuid
        data: dict = {
            "id": str(_uuid.uuid4()), "lead_id": lead_id, "direction": direction,
            "message_type": message_type, "message_content": message_content[:2000],
        }
        if objection_type:
            data["objection_type"] = objection_type
        try:
            await self.db.insert("marketing_lead_interactions", data)
        except Exception as exc:
            logger.error("Gagal catat interaksi lead %s: %s", lead_id, exc)

    async def _get_lead_interactions(self, lead_id: str) -> list[dict]:
        try:
            return await self.db.select("marketing_lead_interactions",
                                        filters={"lead_id": lead_id}, limit=50)
        except Exception:
            return []
