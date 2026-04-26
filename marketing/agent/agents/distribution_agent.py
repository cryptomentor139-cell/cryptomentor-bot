"""
Distribution Agent — distribusi konten ke semua platform sosial media.
marketing/agent/agents/distribution_agent.py
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, time, timedelta, timezone
from typing import Optional

from marketing.agent.agents.content_agent import ContentItem
from marketing.agent.config import Config
from marketing.agent.core.ab_testing import ABTestManager
from marketing.agent.db.supabase_client import SupabaseDB
from marketing.agent.publishers import (
    FacebookPublisher, InstagramPublisher, PublishResult, ThreadsPublisher, TikTokPublisher,
)

logger = logging.getLogger(__name__)

OPTIMAL_TIMES_WIB = [time(7, 0), time(12, 0), time(19, 0)]
WIB_UTC_OFFSET = 7
CAPTION_MAX = {"instagram": 2200, "facebook": 63206, "tiktok": 2200, "threads": 500}
AB_TEST_DELAY_HOURS = 2


class DistributionAgent:
    def __init__(self, config: Config, db: SupabaseDB) -> None:
        self.config = config
        self.db = db
        self.ab_manager = ABTestManager(db)
        self.publishers: dict = {}
        if config.enable_instagram:
            self.publishers["instagram"] = InstagramPublisher(config.instagram_access_token, config.instagram_user_id)
        if config.enable_facebook:
            self.publishers["facebook"] = FacebookPublisher(config.facebook_page_access_token, config.facebook_page_id)
        if config.enable_tiktok:
            self.publishers["tiktok"] = TikTokPublisher(config.tiktok_access_token)
        if config.enable_threads:
            self.publishers["threads"] = ThreadsPublisher(config.threads_access_token, config.instagram_user_id)

    async def distribute_content(self, item: ContentItem) -> dict[str, PublishResult]:
        results: dict[str, PublishResult] = {}
        caption_base = self._get_caption(item)
        hashtags = self._get_hashtags(item)
        image_path = self._get_image_path(item)
        video_path = self._get_video_path(item)

        for platform, publisher in self.publishers.items():
            caption = self._adapt_caption(caption_base, platform, hashtags)
            try:
                if item.content_type == "reels" and video_path:
                    result: PublishResult = await publisher.publish_reels(video_path, caption)
                elif image_path:
                    result = await publisher.publish_feed(image_path, caption, hashtags)
                else:
                    result = PublishResult(success=False, platform=platform, error="No media path")

                results[platform] = result
                if result.success:
                    await self._save_publication(item.id, platform, result)
            except Exception as exc:
                logger.error("Error publish %s ke %s: %s", item.id, platform, exc)
                results[platform] = PublishResult(success=False, platform=platform, error=str(exc))

        return results

    async def schedule_post(self, item: ContentItem, platform: str, post_time: datetime) -> str:
        pub_id = str(uuid.uuid4())
        data = {"id": pub_id, "content_id": item.id, "platform": platform,
                "scheduled_at": post_time.isoformat(), "status": "scheduled", "retry_count": 0}
        try:
            result = await self.db.insert("marketing_publications", data)
            return result.get("id", pub_id)
        except Exception as exc:
            logger.error("Gagal jadwalkan post: %s", exc)
            return pub_id

    async def run_ab_test(self, hook_a: ContentItem, hook_b: ContentItem, campaign_id: str) -> str:
        await self.distribute_content(hook_a)
        post_time_b = datetime.now(timezone.utc) + timedelta(hours=AB_TEST_DELAY_HOURS)
        for platform in self.publishers:
            await self.schedule_post(hook_b, platform, post_time_b)
        session = await self.ab_manager.create_test(
            campaign_id=campaign_id, test_variable="hook_type",
            variant_a_id=hook_a.id, variant_b_id=hook_b.id,
        )
        return session.id

    async def retry_failed_post(self, publication_id: str, max_retries: int = 3) -> bool:
        try:
            rows = await self.db.select("marketing_publications", filters={"id": publication_id}, limit=1)
        except Exception:
            return False

        if not rows:
            return False

        pub = rows[0]
        content_id = pub.get("content_id")
        platform = pub.get("platform")
        retry_count = int(pub.get("retry_count") or 0)

        if retry_count >= max_retries:
            return False

        publisher = self.publishers.get(platform)
        if not publisher:
            return False

        try:
            content_rows = await self.db.select("marketing_content", filters={"id": content_id}, limit=1)
        except Exception:
            return False

        if not content_rows:
            return False

        content_data = content_rows[0]
        await self.db.update("marketing_publications", publication_id,
                             {"status": "retrying", "retry_count": retry_count + 1})

        try:
            image_path = content_data.get("image_path")
            video_path = content_data.get("video_path")
            caption = content_data.get("caption", "")
            hashtags = content_data.get("hashtags") or []
            content_type = content_data.get("content_type", "feed")

            if content_type == "reels" and video_path:
                result: PublishResult = await publisher.publish_reels(video_path, caption)
            elif image_path:
                result = await publisher.publish_feed(image_path, caption, hashtags)
            else:
                result = PublishResult(success=False, platform=platform, error="No media path")

            if result.success:
                await self.db.update("marketing_publications", publication_id, {
                    "status": "published", "platform_post_id": result.post_id,
                    "post_url": result.post_url,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                })
                return True
            else:
                raise Exception(result.error or "Unknown error")

        except Exception as exc:
            new_count = retry_count + 1
            if new_count >= max_retries:
                await self.db.update("marketing_publications", publication_id,
                                     {"status": "failed", "error_message": str(exc), "retry_count": new_count})
                logger.error("ADMIN ALERT: Publication %s gagal di %s setelah max retries: %s",
                             publication_id, platform, exc)
            else:
                await self.db.update("marketing_publications", publication_id,
                                     {"retry_count": new_count, "error_message": str(exc)})
            return False

    async def get_next_optimal_time(self) -> datetime:
        now_utc = datetime.now(timezone.utc)
        now_wib_hour = (now_utc.hour + WIB_UTC_OFFSET) % 24
        now_wib_minute = now_utc.minute

        for optimal_wib in sorted(OPTIMAL_TIMES_WIB):
            if (optimal_wib.hour, optimal_wib.minute) > (now_wib_hour, now_wib_minute):
                utc_hour = (optimal_wib.hour - WIB_UTC_OFFSET) % 24
                next_time = now_utc.replace(hour=utc_hour, minute=optimal_wib.minute, second=0, microsecond=0)
                return next_time

        first_wib = sorted(OPTIMAL_TIMES_WIB)[0]
        utc_hour = (first_wib.hour - WIB_UTC_OFFSET) % 24
        return (now_utc + timedelta(days=1)).replace(hour=utc_hour, minute=first_wib.minute, second=0, microsecond=0)

    async def _save_publication(self, content_id: str, platform: str,
                                 result: PublishResult, ab_variant: Optional[str] = None) -> str:
        pub_id = str(uuid.uuid4())
        data: dict = {
            "id": pub_id, "content_id": content_id, "platform": platform,
            "platform_post_id": result.post_id, "post_url": result.post_url,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "status": "published" if result.success else "failed", "retry_count": 0,
        }
        if ab_variant:
            data["ab_test_variant"] = ab_variant
        if not result.success and result.error:
            data["error_message"] = result.error
        try:
            saved = await self.db.insert("marketing_publications", data)
            return saved.get("id", pub_id)
        except Exception as exc:
            logger.error("Gagal simpan publication: %s", exc)
            return pub_id

    def _get_caption(self, item: ContentItem) -> str:
        if item.content_type == "feed" and item.feed:
            return item.feed.pas.caption if item.feed.pas else ""
        if item.content_type == "reels" and item.reels:
            return item.reels.caption
        return ""

    def _get_hashtags(self, item: ContentItem) -> list[str]:
        if item.content_type == "feed" and item.feed:
            return item.feed.pas.hashtags if item.feed.pas else []
        if item.content_type == "reels" and item.reels:
            return item.reels.hashtags
        return []

    def _get_image_path(self, item: ContentItem) -> Optional[str]:
        if item.content_type == "feed" and item.feed:
            return item.feed.image_path
        return None

    def _get_video_path(self, item: ContentItem) -> Optional[str]:
        if item.content_type == "reels" and item.reels:
            return item.reels.video_path
        return None

    def _adapt_caption(self, caption: str, platform: str, hashtags: list[str]) -> str:
        max_len = CAPTION_MAX.get(platform, 2200)
        if platform == "threads":
            short = caption[:400].rstrip()
            if len(caption) > 400:
                short += "..."
            if hashtags:
                short += f"\n{hashtags[0]}"
            return short[:max_len]
        hashtag_str = " ".join(hashtags) if hashtags else ""
        full = f"{caption}\n\n{hashtag_str}".strip() if hashtag_str else caption
        return full[:max_len]
