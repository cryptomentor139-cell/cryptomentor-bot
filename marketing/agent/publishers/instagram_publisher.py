"""
Instagram Graph API publisher.

Endpoints:
  POST /v18.0/{ig-user-id}/media         → upload container
  POST /v18.0/{ig-user-id}/media_publish → publish
  GET  /v18.0/{media-id}/insights        → metrik
"""
import asyncio
import logging
from typing import List

import httpx

from .base_publisher import BasePublisher, PostMetrics, PublishResult

logger = logging.getLogger(__name__)

# Error codes yang memerlukan retry dengan delay panjang
_RATE_LIMIT_CODES = {4, 32}
_RETRY_DELAY_SECONDS = 15 * 60  # 15 menit
_MAX_RETRIES = 3


class InstagramPublisher(BasePublisher):
    BASE_URL = "https://graph.instagram.com/v18.0"

    def __init__(self, access_token: str, user_id: str) -> None:
        self.access_token = access_token
        self.user_id = user_id

    # ------------------------------------------------------------------
    # Publish feed (image)
    # ------------------------------------------------------------------

    async def publish_feed(
        self, image_path: str, caption: str, hashtags: List[str]
    ) -> PublishResult:
        """
        Upload image container lalu publish ke Instagram feed.
        image_path diperlakukan sebagai URL publik gambar.
        Retry 3x dengan delay 15 menit jika rate limit (error code 4 atau 32).
        """
        full_caption = self._build_caption(caption, hashtags)

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                creation_id = await self._create_image_container(image_path, full_caption)
                media_id = await self._publish_container(creation_id)
                post_url = f"https://www.instagram.com/p/{media_id}/"
                logger.info("Instagram feed published: %s", media_id)
                return PublishResult(
                    success=True,
                    platform="instagram",
                    post_id=media_id,
                    post_url=post_url,
                )
            except _RateLimitError as exc:
                logger.warning(
                    "Instagram rate limit (attempt %d/%d): %s", attempt, _MAX_RETRIES, exc
                )
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY_SECONDS)
                else:
                    msg = f"Instagram rate limit setelah {_MAX_RETRIES}x retry: {exc}"
                    await self._send_admin_notification(msg)
                    return PublishResult(success=False, platform="instagram", error=msg)
            except Exception as exc:
                logger.error("Instagram publish_feed error: %s", exc)
                return PublishResult(success=False, platform="instagram", error=str(exc))

        # Seharusnya tidak sampai sini
        return PublishResult(success=False, platform="instagram", error="Max retries exceeded")

    # ------------------------------------------------------------------
    # Publish reels (video)
    # ------------------------------------------------------------------

    async def publish_reels(self, video_path: str, caption: str) -> PublishResult:
        """
        Upload video sebagai Instagram Reels.
        video_path diperlakukan sebagai URL publik video.
        """
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                creation_id = await self._create_reels_container(video_path, caption)
                media_id = await self._publish_container(creation_id)
                post_url = f"https://www.instagram.com/reel/{media_id}/"
                logger.info("Instagram reels published: %s", media_id)
                return PublishResult(
                    success=True,
                    platform="instagram",
                    post_id=media_id,
                    post_url=post_url,
                )
            except _RateLimitError as exc:
                logger.warning(
                    "Instagram rate limit reels (attempt %d/%d): %s", attempt, _MAX_RETRIES, exc
                )
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY_SECONDS)
                else:
                    msg = f"Instagram reels rate limit setelah {_MAX_RETRIES}x retry: {exc}"
                    await self._send_admin_notification(msg)
                    return PublishResult(success=False, platform="instagram", error=msg)
            except Exception as exc:
                logger.error("Instagram publish_reels error: %s", exc)
                return PublishResult(success=False, platform="instagram", error=str(exc))

        return PublishResult(success=False, platform="instagram", error="Max retries exceeded")

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """Ambil metrik dari Instagram Insights API."""
        metrics = PostMetrics(post_id=post_id, platform="instagram")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/{post_id}/insights",
                    params={
                        "metric": "likes,comments,reach,impressions,saved",
                        "access_token": self.access_token,
                    },
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])
                for item in data:
                    name = item.get("name")
                    value = item.get("values", [{}])[0].get("value", 0)
                    if name == "likes":
                        metrics.likes = value
                    elif name == "comments":
                        metrics.comments = value
                    elif name == "reach":
                        metrics.reach = value
                    elif name == "impressions":
                        metrics.impressions = value
                    elif name == "saved":
                        metrics.saves = value
        except Exception as exc:
            logger.error("Instagram get_post_metrics error (post_id=%s): %s", post_id, exc)
        return metrics

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _create_image_container(self, image_url: str, caption: str) -> str:
        """POST ke /media untuk membuat image container. Return creation_id."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/{self.user_id}/media",
                data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                },
            )
            return self._handle_response(resp, "create_image_container")

    async def _create_reels_container(self, video_url: str, caption: str) -> str:
        """POST ke /media untuk membuat Reels container. Return creation_id."""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.BASE_URL}/{self.user_id}/media",
                data={
                    "video_url": video_url,
                    "media_type": "REELS",
                    "caption": caption,
                    "access_token": self.access_token,
                },
            )
            return self._handle_response(resp, "create_reels_container")

    async def _publish_container(self, creation_id: str) -> str:
        """POST ke /media_publish untuk mempublikasikan container. Return media_id."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/{self.user_id}/media_publish",
                data={
                    "creation_id": creation_id,
                    "access_token": self.access_token,
                },
            )
            return self._handle_response(resp, "publish_container")

    def _handle_response(self, resp: httpx.Response, context: str) -> str:
        """Parse response, raise _RateLimitError jika rate limit, return 'id'."""
        try:
            body = resp.json()
        except Exception:
            resp.raise_for_status()
            raise

        if "error" in body:
            err = body["error"]
            code = err.get("code", 0)
            msg = err.get("message", str(err))
            if code in _RATE_LIMIT_CODES:
                raise _RateLimitError(f"[{context}] code={code}: {msg}")
            raise Exception(f"Instagram API error [{context}] code={code}: {msg}")

        resp.raise_for_status()
        return body["id"]

    @staticmethod
    def _build_caption(caption: str, hashtags: List[str]) -> str:
        if hashtags:
            return f"{caption}\n\n{' '.join(hashtags)}"
        return caption


class _RateLimitError(Exception):
    """Internal: Instagram rate limit error (code 4 atau 32)."""
