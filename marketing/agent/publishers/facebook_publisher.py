"""
Facebook Graph API publisher.

Endpoints:
  POST /v18.0/{page-id}/photos   → upload foto ke Page
  POST /v18.0/{page-id}/videos   → upload video Reels
  GET  /v18.0/{post-id}/insights → metrik
"""
import logging
from typing import List

import httpx

from .base_publisher import BasePublisher, PostMetrics, PublishResult

logger = logging.getLogger(__name__)

# OAuthException code 190 = token expired
_OAUTH_EXPIRED_CODE = 190


class FacebookPublisher(BasePublisher):
    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self, page_access_token: str, page_id: str) -> None:
        self.page_access_token = page_access_token
        self.page_id = page_id

    # ------------------------------------------------------------------
    # Publish feed (photo)
    # ------------------------------------------------------------------

    async def publish_feed(
        self, image_path: str, caption: str, hashtags: List[str]
    ) -> PublishResult:
        """
        POST ke /{page-id}/photos dengan url dan message.
        Deteksi OAuthException code 190 (token expired) → log error khusus.
        image_path diperlakukan sebagai URL publik gambar.
        """
        message = self._build_message(caption, hashtags)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/{self.page_id}/photos",
                    data={
                        "url": image_path,
                        "message": message,
                        "access_token": self.page_access_token,
                    },
                )
                post_id = self._handle_response(resp, "publish_feed")
                post_url = f"https://www.facebook.com/{post_id}"
                logger.info("Facebook feed published: %s", post_id)
                return PublishResult(
                    success=True,
                    platform="facebook",
                    post_id=post_id,
                    post_url=post_url,
                )
        except _TokenExpiredError as exc:
            msg = f"Facebook token expired — perlu refresh Page Access Token: {exc}"
            logger.error(msg)
            await self._send_admin_notification(msg)
            return PublishResult(success=False, platform="facebook", error=msg)
        except Exception as exc:
            logger.error("Facebook publish_feed error: %s", exc)
            return PublishResult(success=False, platform="facebook", error=str(exc))

    # ------------------------------------------------------------------
    # Publish reels (video)
    # ------------------------------------------------------------------

    async def publish_reels(self, video_path: str, caption: str) -> PublishResult:
        """
        POST ke /{page-id}/videos untuk upload video Reels.
        video_path diperlakukan sebagai URL publik video.
        """
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/{self.page_id}/videos",
                    data={
                        "file_url": video_path,
                        "description": caption,
                        "access_token": self.page_access_token,
                    },
                )
                post_id = self._handle_response(resp, "publish_reels")
                post_url = f"https://www.facebook.com/{post_id}"
                logger.info("Facebook reels published: %s", post_id)
                return PublishResult(
                    success=True,
                    platform="facebook",
                    post_id=post_id,
                    post_url=post_url,
                )
        except _TokenExpiredError as exc:
            msg = f"Facebook token expired (reels) — perlu refresh Page Access Token: {exc}"
            logger.error(msg)
            await self._send_admin_notification(msg)
            return PublishResult(success=False, platform="facebook", error=msg)
        except Exception as exc:
            logger.error("Facebook publish_reels error: %s", exc)
            return PublishResult(success=False, platform="facebook", error=str(exc))

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """Ambil metrik dari Facebook Insights API."""
        metrics = PostMetrics(post_id=post_id, platform="facebook")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/{post_id}/insights",
                    params={
                        "metric": "post_impressions,post_reach,post_reactions_by_type_total,"
                                  "post_clicks,post_video_views",
                        "access_token": self.page_access_token,
                    },
                )
                resp.raise_for_status()
                data = resp.json().get("data", [])
                for item in data:
                    name = item.get("name")
                    value = item.get("values", [{}])[0].get("value", 0)
                    if name == "post_impressions":
                        metrics.impressions = value if isinstance(value, int) else 0
                    elif name == "post_reach":
                        metrics.reach = value if isinstance(value, int) else 0
                    elif name == "post_clicks":
                        metrics.clicks = value if isinstance(value, int) else 0
                    elif name == "post_reactions_by_type_total":
                        # value adalah dict {LIKE: n, LOVE: n, ...}
                        if isinstance(value, dict):
                            metrics.likes = sum(value.values())
        except Exception as exc:
            logger.error("Facebook get_post_metrics error (post_id=%s): %s", post_id, exc)
        return metrics

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_response(self, resp: httpx.Response, context: str) -> str:
        """Parse response, raise _TokenExpiredError jika OAuthException 190, return 'id'."""
        try:
            body = resp.json()
        except Exception:
            resp.raise_for_status()
            raise

        if "error" in body:
            err = body["error"]
            code = err.get("code", 0)
            msg = err.get("message", str(err))
            if code == _OAUTH_EXPIRED_CODE:
                raise _TokenExpiredError(f"[{context}] OAuthException code=190: {msg}")
            raise Exception(f"Facebook API error [{context}] code={code}: {msg}")

        resp.raise_for_status()
        return body.get("id", body.get("post_id", ""))

    @staticmethod
    def _build_message(caption: str, hashtags: List[str]) -> str:
        if hashtags:
            return f"{caption}\n\n{' '.join(hashtags)}"
        return caption


class _TokenExpiredError(Exception):
    """Internal: Facebook OAuthException code 190 — token expired."""
