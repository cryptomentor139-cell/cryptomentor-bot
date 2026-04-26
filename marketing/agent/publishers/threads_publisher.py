"""
Threads API publisher (Meta ecosystem — sama dengan Instagram credentials).

Endpoints:
  POST /v1.0/{user-id}/threads         → buat container
  POST /v1.0/{user-id}/threads_publish → publish
  GET  /v1.0/{threads-media-id}/insights → metrik
"""
import logging
from typing import List

import httpx

from .base_publisher import BasePublisher, PostMetrics, PublishResult

logger = logging.getLogger(__name__)


class ThreadsPublisher(BasePublisher):
    BASE_URL = "https://graph.threads.net/v1.0"

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
        Buat container lalu publish ke Threads.
        image_path diperlakukan sebagai URL publik gambar.
        """
        text = self._build_text(caption, hashtags)
        try:
            container_id = await self._create_image_container(image_path, text)
            media_id = await self._publish_container(container_id)
            post_url = f"https://www.threads.net/@{self.user_id}/post/{media_id}"
            logger.info("Threads feed published: %s", media_id)
            return PublishResult(
                success=True,
                platform="threads",
                post_id=media_id,
                post_url=post_url,
            )
        except Exception as exc:
            logger.error("Threads publish_feed error: %s", exc)
            return PublishResult(success=False, platform="threads", error=str(exc))

    # ------------------------------------------------------------------
    # Publish reels (video)
    # ------------------------------------------------------------------

    async def publish_reels(self, video_path: str, caption: str) -> PublishResult:
        """
        Video post di Threads.
        video_path diperlakukan sebagai URL publik video.
        """
        try:
            container_id = await self._create_video_container(video_path, caption)
            media_id = await self._publish_container(container_id)
            post_url = f"https://www.threads.net/@{self.user_id}/post/{media_id}"
            logger.info("Threads video published: %s", media_id)
            return PublishResult(
                success=True,
                platform="threads",
                post_id=media_id,
                post_url=post_url,
            )
        except Exception as exc:
            logger.error("Threads publish_reels error: %s", exc)
            return PublishResult(success=False, platform="threads", error=str(exc))

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """Ambil metrik dari Threads Insights API."""
        metrics = PostMetrics(post_id=post_id, platform="threads")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/{post_id}/insights",
                    params={
                        "metric": "likes,replies,reposts,quotes,views",
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
                    elif name == "replies":
                        metrics.comments = value
                    elif name == "reposts":
                        metrics.shares = value
                    elif name == "views":
                        metrics.impressions = value
        except Exception as exc:
            logger.error("Threads get_post_metrics error (post_id=%s): %s", post_id, exc)
        return metrics

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _create_image_container(self, image_url: str, text: str) -> str:
        """POST ke /{user-id}/threads untuk membuat image container. Return container_id."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/{self.user_id}/threads",
                data={
                    "media_type": "IMAGE",
                    "image_url": image_url,
                    "text": text,
                    "access_token": self.access_token,
                },
            )
            return self._handle_response(resp, "create_image_container")

    async def _create_video_container(self, video_url: str, text: str) -> str:
        """POST ke /{user-id}/threads untuk membuat video container. Return container_id."""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.BASE_URL}/{self.user_id}/threads",
                data={
                    "media_type": "VIDEO",
                    "video_url": video_url,
                    "text": text,
                    "access_token": self.access_token,
                },
            )
            return self._handle_response(resp, "create_video_container")

    async def _publish_container(self, container_id: str) -> str:
        """POST ke /{user-id}/threads_publish untuk mempublikasikan container. Return media_id."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/{self.user_id}/threads_publish",
                data={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )
            return self._handle_response(resp, "publish_container")

    def _handle_response(self, resp: httpx.Response, context: str) -> str:
        """Parse response, raise Exception jika ada error, return 'id'."""
        try:
            body = resp.json()
        except Exception:
            resp.raise_for_status()
            raise

        if "error" in body:
            err = body["error"]
            code = err.get("code", 0)
            msg = err.get("message", str(err))
            raise Exception(f"Threads API error [{context}] code={code}: {msg}")

        resp.raise_for_status()
        return body["id"]

    @staticmethod
    def _build_text(caption: str, hashtags: List[str]) -> str:
        if hashtags:
            return f"{caption}\n\n{' '.join(hashtags)}"
        return caption
