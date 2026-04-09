"""
Approval Queue — antrian persetujuan konten sebelum distribusi.
marketing/agent/core/approval_queue.py
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

import httpx

from marketing.agent.config import Config
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"


class ApprovalQueue:
    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db

    # ------------------------------------------------------------------
    # Queue Management
    # ------------------------------------------------------------------

    async def add_to_queue(self, content_id: str) -> None:
        """
        Update status marketing_content ke "pending_approval" dan kirim
        notifikasi Telegram ke semua admin dengan preview konten dan
        tombol Approve/Reject.
        """
        # Update status ke pending_approval
        try:
            await self.db.update("marketing_content", content_id, {
                "status": "pending_approval",
            })
        except Exception as exc:
            logger.error("Gagal update status pending_approval content %s: %s", content_id, exc)

        # Ambil data konten untuk preview
        content_data: dict = {}
        try:
            rows = await self.db.select("marketing_content", filters={"id": content_id}, limit=1)
            if rows:
                content_data = rows[0]
        except Exception as exc:
            logger.warning("Gagal ambil data konten %s untuk notifikasi: %s", content_id, exc)

        content_type = content_data.get("content_type", "unknown")
        hook = content_data.get("hook", "-")
        short_id = content_id[:8]

        message = (
            f"📋 Konten baru menunggu persetujuan\n"
            f"ID: {short_id}\n"
            f"Tipe: {content_type}\n"
            f"Hook: {hook}\n\n"
            f"/approve_{short_id} | /reject_{short_id}"
        )

        for admin_id in self.config.telegram_admin_ids:
            await self._send_telegram_message(admin_id, message)

    async def approve(self, content_id: str) -> None:
        """Update status konten ke 'approved'."""
        try:
            await self.db.update("marketing_content", content_id, {
                "status": "approved",
                "approved_at": datetime.now(timezone.utc).isoformat(),
            })
            logger.info("Konten %s disetujui.", content_id)
        except Exception as exc:
            logger.error("Gagal approve konten %s: %s", content_id, exc)

    async def reject(self, content_id: str, reason: str = "") -> None:
        """Update status konten ke 'rejected' dan simpan rejection_reason."""
        update_data: dict = {"status": "rejected"}
        if reason:
            update_data["rejection_reason"] = reason
        try:
            await self.db.update("marketing_content", content_id, update_data)
            logger.info("Konten %s ditolak. Alasan: %s", content_id, reason or "-")
        except Exception as exc:
            logger.error("Gagal reject konten %s: %s", content_id, exc)

    # ------------------------------------------------------------------
    # Reminders
    # ------------------------------------------------------------------

    async def check_pending_reminders(self) -> None:
        """
        Cari konten dengan status 'pending_approval' lebih dari 24 jam
        dan kirim reminder ke admin.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        try:
            rows = await self.db.select(
                "marketing_content",
                filters={"status": "pending_approval"},
                limit=100,
            )
        except Exception as exc:
            logger.error("Gagal ambil pending content untuk reminder: %s", exc)
            return

        stale = []
        for row in rows:
            created_raw = row.get("created_at")
            if not created_raw:
                continue
            try:
                created_at = datetime.fromisoformat(
                    str(created_raw).replace("Z", "+00:00")
                )
                if not created_at.tzinfo:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                if created_at < cutoff:
                    stale.append(row)
            except ValueError:
                continue

        if not stale:
            return

        message_lines = [
            f"⏰ <b>Reminder: {len(stale)} konten menunggu persetujuan lebih dari 24 jam</b>\n"
        ]
        for row in stale[:10]:  # batasi 10 item per notifikasi
            short_id = str(row.get("id", ""))[:8]
            content_type = row.get("content_type", "?")
            hook = (row.get("hook") or "-")[:60]
            message_lines.append(f"• [{short_id}] {content_type}: {hook}")
            message_lines.append(f"  /approve_{short_id} | /reject_{short_id}")

        if len(stale) > 10:
            message_lines.append(f"\n...dan {len(stale) - 10} konten lainnya.")

        message = "\n".join(message_lines)
        for admin_id in self.config.telegram_admin_ids:
            await self._send_telegram_message(admin_id, message)

    # ------------------------------------------------------------------
    # Auto-publish
    # ------------------------------------------------------------------

    async def is_auto_publish_enabled(self) -> bool:
        """
        Cek env var ENABLE_AUTO_PUBLISH.
        Return True jika auto-publish aktif.
        """
        val = os.getenv("ENABLE_AUTO_PUBLISH", "false")
        return val.strip().lower() in ("true", "1", "yes", "on")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _send_telegram_message(self, chat_id: int, text: str) -> bool:
        url = TELEGRAM_API_BASE.format(token=self.config.telegram_bot_token)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                })
                response.raise_for_status()
                return response.json().get("ok", False)
        except Exception as exc:
            logger.error("Gagal kirim Telegram ke %d: %s", chat_id, exc)
            return False
