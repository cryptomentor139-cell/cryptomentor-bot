"""
Analyst Agent — evaluasi performa konten dan generate laporan mingguan.
marketing/agent/agents/analyst_agent.py
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx

from marketing.agent.agents.strategist_agent import AnalystFeedback
from marketing.agent.config import Config
from marketing.agent.db.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"
CVR_DROP_THRESHOLD = 0.30


@dataclass
class ContentMetrics:
    content_id: str
    platform: str
    ctr: float
    engagement_rate: float
    conversion_rate: float
    leads_generated: int
    hours_since_publish: float


@dataclass
class WeeklyReport:
    total_content: int
    total_reach: int
    total_leads: int
    avg_ctr: float
    avg_conversion_rate: float
    best_content_id: Optional[str]
    scale_decisions: List[str]
    kill_decisions: List[str]
    recommendations: str


class AnalystAgent:
    SCALE_CTR_THRESHOLD = 0.03
    SCALE_CVR_THRESHOLD = 0.05
    KILL_CTR_THRESHOLD = 0.01
    KILL_ENGAGEMENT_RATIO = 0.80
    KILL_MIN_HOURS = 48

    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db

    async def collect_metrics(self, content_ids: List[str]) -> List[ContentMetrics]:
        results: List[ContentMetrics] = []
        for content_id in content_ids:
            try:
                analytics_rows = await self.db.select("marketing_analytics",
                                                      filters={"content_id": content_id}, limit=20)
                pub_rows = await self.db.select("marketing_publications",
                                               filters={"content_id": content_id}, limit=10)
                if not analytics_rows:
                    continue

                n = len(analytics_rows)
                avg_ctr = sum(float(r.get("ctr") or 0) for r in analytics_rows) / n
                avg_engagement = sum(float(r.get("engagement_rate") or 0) for r in analytics_rows) / n
                avg_cvr = sum(float(r.get("conversion_rate") or 0) for r in analytics_rows) / n
                total_leads = sum(int(r.get("leads_generated") or 0) for r in analytics_rows)
                platform = analytics_rows[0].get("platform", "unknown")

                hours_since = 0.0
                if pub_rows:
                    published_at_raw = pub_rows[0].get("published_at")
                    if published_at_raw:
                        published_at = self._parse_dt(published_at_raw)
                        hours_since = (datetime.now(timezone.utc) - published_at).total_seconds() / 3600

                results.append(ContentMetrics(
                    content_id=content_id, platform=platform, ctr=avg_ctr,
                    engagement_rate=avg_engagement, conversion_rate=avg_cvr,
                    leads_generated=total_leads, hours_since_publish=hours_since,
                ))
            except Exception as exc:
                logger.error("Gagal collect metrics content %s: %s", content_id, exc)
        return results

    async def make_scale_decision(self, metrics: ContentMetrics) -> bool:
        should_scale = (metrics.ctr > self.SCALE_CTR_THRESHOLD or
                        metrics.conversion_rate > self.SCALE_CVR_THRESHOLD)
        if should_scale:
            await self._update_analytics_decision(metrics.content_id, scale_decision=True)
        return should_scale

    async def make_kill_decision(self, metrics: ContentMetrics) -> bool:
        if metrics.hours_since_publish < self.KILL_MIN_HOURS:
            return False
        avg_engagement = await self._get_avg_engagement_rate()
        should_kill = (metrics.ctr < self.KILL_CTR_THRESHOLD and
                       metrics.engagement_rate < avg_engagement * self.KILL_ENGAGEMENT_RATIO and
                       metrics.hours_since_publish >= self.KILL_MIN_HOURS)
        if should_kill:
            await self._update_analytics_decision(metrics.content_id, kill_decision=True)
        return should_kill

    async def generate_weekly_report(self) -> WeeklyReport:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        try:
            all_analytics = await self.db.select("marketing_analytics", limit=1000)
            recent = [r for r in all_analytics if self._parse_dt(r.get("measured_at")) >= cutoff]
            content_ids = list({r.get("content_id") for r in recent if r.get("content_id")})
            total_reach = sum(int(r.get("reach") or 0) for r in recent)
            total_leads = sum(int(r.get("leads_generated") or 0) for r in recent)
            ctrs = [float(r.get("ctr") or 0) for r in recent if r.get("ctr") is not None]
            cvrs = [float(r.get("conversion_rate") or 0) for r in recent if r.get("conversion_rate") is not None]
            avg_ctr = sum(ctrs) / len(ctrs) if ctrs else 0.0
            avg_cvr = sum(cvrs) / len(cvrs) if cvrs else 0.0
            best_content_id = max(recent, key=lambda r: float(r.get("ctr") or 0)).get("content_id") if recent else None
            scale_decisions = list(dict.fromkeys(r.get("content_id") for r in recent if r.get("scale_decision") and r.get("content_id")))
            kill_decisions = list(dict.fromkeys(r.get("content_id") for r in recent if r.get("kill_decision") and r.get("content_id")))
            recommendations = self._generate_recommendations(avg_ctr, avg_cvr, len(scale_decisions), len(kill_decisions), len(content_ids))
            return WeeklyReport(total_content=len(content_ids), total_reach=total_reach, total_leads=total_leads,
                                avg_ctr=avg_ctr, avg_conversion_rate=avg_cvr, best_content_id=best_content_id,
                                scale_decisions=scale_decisions, kill_decisions=kill_decisions, recommendations=recommendations)
        except Exception as exc:
            logger.error("Gagal generate weekly report: %s", exc)
            return WeeklyReport(0, 0, 0, 0.0, 0.0, None, [], [], "Data tidak tersedia.")

    async def generate_feedback(self) -> AnalystFeedback:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        try:
            all_analytics = await self.db.select("marketing_analytics", limit=1000)
            recent = [r for r in all_analytics if self._parse_dt(r.get("measured_at")) >= cutoff]
            if not recent:
                return AnalystFeedback(None, None, None, "Belum ada data analytics minggu ini.")

            best_row = max(recent, key=lambda r: float(r.get("ctr") or 0))
            best_content_id = best_row.get("content_id")
            best_persona: Optional[str] = None
            recommended_angle: Optional[str] = None

            if best_content_id:
                content_rows = await self.db.select("marketing_content", filters={"id": best_content_id}, limit=1)
                if content_rows:
                    best_persona = content_rows[0].get("target_persona")
                    emotion_trigger = content_rows[0].get("emotion_trigger")
                    if emotion_trigger == "fear":
                        recommended_angle = "keamanan dan proteksi modal"
                    elif emotion_trigger == "greed":
                        recommended_angle = "peluang profit dan growth"
                    else:
                        recommended_angle = "edukasi dan konsistensi"

            avg_ctr = sum(float(r.get("ctr") or 0) for r in recent) / len(recent)
            notes = f"Total konten: {len(set(r.get('content_id') for r in recent))}\nRata-rata CTR: {avg_ctr:.2%}"
            if best_persona:
                notes += f"\nPersona terbaik: {best_persona}"

            return AnalystFeedback(best_performing_persona=best_persona, best_performing_hook_type=None,
                                   recommended_angle=recommended_angle, notes=notes)
        except Exception as exc:
            logger.error("Gagal generate feedback: %s", exc)
            return AnalystFeedback(None, None, None, f"Error: {exc}")

    async def send_weekly_report_telegram(self, report: WeeklyReport) -> None:
        message = self._format_weekly_report(report)
        for admin_id in self.config.telegram_admin_ids:
            await self._send_telegram_message(admin_id, message)

    async def check_conversion_drop_alert(self) -> None:
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=7)
        prev_week_start = now - timedelta(days=14)
        try:
            all_analytics = await self.db.select("marketing_analytics", limit=2000)
            this_week = [r for r in all_analytics if week_start <= self._parse_dt(r.get("measured_at")) <= now]
            prev_week = [r for r in all_analytics if prev_week_start <= self._parse_dt(r.get("measured_at")) < week_start]
            cvr_this = self._avg_cvr(this_week)
            cvr_prev = self._avg_cvr(prev_week)
            if cvr_prev > 0:
                drop_ratio = (cvr_prev - cvr_this) / cvr_prev
                if drop_ratio > CVR_DROP_THRESHOLD:
                    alert_msg = (f"⚠️ <b>ALERT: Penurunan Conversion Rate</b>\n\n"
                                 f"CVR minggu ini: {cvr_this:.2%}\nCVR minggu lalu: {cvr_prev:.2%}\n"
                                 f"Penurunan: {drop_ratio:.1%}\n\nSegera review strategi konten.")
                    for admin_id in self.config.telegram_admin_ids:
                        await self._send_telegram_message(admin_id, alert_msg)
        except Exception as exc:
            logger.error("Gagal cek CVR drop alert: %s", exc)

    async def _get_avg_engagement_rate(self) -> float:
        try:
            rows = await self.db.select("marketing_analytics", limit=500)
            rates = [float(r.get("engagement_rate") or 0) for r in rows if r.get("engagement_rate")]
            return sum(rates) / len(rates) if rates else 0.01
        except Exception:
            return 0.01

    async def _update_analytics_decision(self, content_id: str, scale_decision: bool = False, kill_decision: bool = False) -> None:
        try:
            rows = await self.db.select("marketing_analytics", filters={"content_id": content_id}, limit=10)
            for row in rows:
                row_id = row.get("id")
                if row_id:
                    update_data: dict = {}
                    if scale_decision:
                        update_data["scale_decision"] = True
                    if kill_decision:
                        update_data["kill_decision"] = True
                    if update_data:
                        await self.db.update("marketing_analytics", row_id, update_data)
        except Exception as exc:
            logger.error("Gagal update analytics decision content %s: %s", content_id, exc)

    async def _send_telegram_message(self, chat_id: int, text: str) -> bool:
        url = TELEGRAM_API_BASE.format(token=self.config.telegram_bot_token)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json={"chat_id": chat_id, "text": text,
                                                         "parse_mode": "HTML", "disable_web_page_preview": True})
                response.raise_for_status()
                return response.json().get("ok", False)
        except Exception as exc:
            logger.error("Gagal kirim Telegram ke %d: %s", chat_id, exc)
            return False

    def _format_weekly_report(self, report: WeeklyReport) -> str:
        lines = ["📊 <b>Laporan Mingguan Marketing CryptoMentor</b>", "",
                 f"📝 Total Konten: {report.total_content}", f"👥 Total Reach: {report.total_reach:,}",
                 f"🎯 Total Lead: {report.total_leads}", f"📈 Rata-rata CTR: {report.avg_ctr:.2%}",
                 f"💰 Rata-rata CVR: {report.avg_conversion_rate:.2%}"]
        if report.best_content_id:
            lines.append(f"🏆 Konten Terbaik: {report.best_content_id[:8]}...")
        if report.scale_decisions:
            lines.append(f"\n✅ Scale Decisions: {len(report.scale_decisions)} konten")
        if report.kill_decisions:
            lines.append(f"❌ Kill Decisions: {len(report.kill_decisions)} konten")
        lines.extend(["", "💡 <b>Rekomendasi:</b>", report.recommendations])
        return "\n".join(lines)

    def _generate_recommendations(self, avg_ctr: float, avg_cvr: float, scale_count: int, kill_count: int, total_content: int) -> str:
        recs = []
        if avg_ctr < self.KILL_CTR_THRESHOLD:
            recs.append("CTR di bawah 1% — pertimbangkan untuk mengubah hook dan format konten.")
        elif avg_ctr > self.SCALE_CTR_THRESHOLD:
            recs.append("CTR di atas 3% — pertahankan format konten yang sedang berjalan.")
        if avg_cvr < 0.02:
            recs.append("CVR rendah — review sales funnel dan pesan closing di Telegram.")
        elif avg_cvr > self.SCALE_CVR_THRESHOLD:
            recs.append("CVR tinggi — tingkatkan volume konten untuk memaksimalkan konversi.")
        if kill_count > scale_count:
            recs.append("Lebih banyak kill daripada scale — eksperimen dengan angle konten baru.")
        if not recs:
            recs.append("Performa stabil. Lanjutkan strategi saat ini dan monitor tren mingguan.")
        return " ".join(recs)

    def _avg_cvr(self, rows: list) -> float:
        cvrs = [float(r.get("conversion_rate") or 0) for r in rows if r.get("conversion_rate")]
        return sum(cvrs) / len(cvrs) if cvrs else 0.0

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
