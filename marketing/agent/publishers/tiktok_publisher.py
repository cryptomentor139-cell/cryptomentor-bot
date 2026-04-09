"""
TikTok Content Posting API publisher.

Endpoints:
  POST /v2/post/publish/video/init/     → inisialisasi upload video
  POST /v2/post/publish/video/upload/   → upload chunk video
  POST /v2/post/publish/video/complete/ → finalisasi publikasi
  POST /v2/post/publish/content/init/   → photo post
  GET  /v2/research/video/query/        → metrik
"""
import asyncio
import logging
import os
from typing import List

import httpx

from .base_publisher import BasePublisher, PostMetrics, PublishResult

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 10 * 60  # 10 menit
_CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB per chunk


class TikTokPublisher(BasePublisher):
    BASE_URL = "https://open.tiktokapis.com/v2"

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    @property
    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    # ------------------------------------------------------------------
    # Publish feed (photo post)
    # ------------------------------------------------------------------

    async def publish_feed(
        self, image_path: str, caption: str, hashtags: List[str]
    ) -> PublishResult:
        """
        TikTok photo post via /post/publish/content/init/.
        image_path diperlakukan sebagai URL publik gambar.
        """
        title = self._build_title(caption, hashtags)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/post/publish/content/init/",
                    headers={**self._auth_headers, "Content-Type": "application/json"},
                    json={
                        "post_info": {
                            "title": title,
                            "privacy_level": "PUBLIC_TO_EVERYONE",
                            "disable_duet": False,
                            "disable_comment": False,
                            "disable_stitch": False,
                        },
                        "source_info": {
                            "source": "PULL_FROM_URL",
                            "photo_cover_index": 0,
                            "photo_images": [image_path],
                        },
                        "post_mode": "DIRECT_POST",
                        "media_type": "PHOTO",
                    },
                )
                resp.raise_for_status()
                body = resp.json()
                self._check_tiktok_error(body, "publish_feed")
                publish_id = body.get("data", {}).get("publish_id", "")
                logger.info("TikTok photo post initiated: %s", publish_id)
                return PublishResult(
                    success=True,
                    platform="tiktok",
                    post_id=publish_id,
                )
        except Exception as exc:
            logger.error("TikTok publish_feed error: %s", exc)
            return PublishResult(success=False, platform="tiktok", error=str(exc))

    # ------------------------------------------------------------------
    # Publish reels (video — chunked upload)
    # ------------------------------------------------------------------

    async def publish_reels(self, video_path: str, caption: str) -> PublishResult:
        """
        Chunked upload: init → upload chunks → complete.
        Retry 3x dengan interval 10 menit jika gagal.
        video_path adalah path file lokal.
        """
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                result = await self._upload_video(video_path, caption)
                return result
            except Exception as exc:
                logger.warning(
                    "TikTok publish_reels attempt %d/%d failed: %s", attempt, _MAX_RETRIES, exc
                )
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY_SECONDS)
                else:
                    msg = f"TikTok video upload gagal setelah {_MAX_RETRIES}x retry: {exc}"
                    await self._send_admin_notification(msg)
                    return PublishResult(success=False, platform="tiktok", error=msg)

        return PublishResult(success=False, platform="tiktok", error="Max retries exceeded")

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """Ambil metrik via /research/video/query/."""
        metrics = PostMetrics(post_id=post_id, platform="tiktok")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/research/video/query/",
                    headers={**self._auth_headers, "Content-Type": "application/json"},
                    json={
                        "filters": {"video_ids": [post_id]},
                        "fields": "like_count,comment_count,share_count,view_count",
                    },
                )
                resp.raise_for_status()
                body = resp.json()
                self._check_tiktok_error(body, "get_post_metrics")
                videos = body.get("data", {}).get("videos", [])
                if videos:
                    v = videos[0]
                    metrics.likes = v.get("like_count", 0)
                    metrics.comments = v.get("comment_count", 0)
                    metrics.shares = v.get("share_count", 0)
                    metrics.impressions = v.get("view_count", 0)
        except Exception as exc:
            logger.error("TikTok get_post_metrics error (post_id=%s): %s", post_id, exc)
        return metrics

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _upload_video(self, video_path: str, caption: str) -> PublishResult:
        """Jalankan full chunked upload flow: init → upload → complete."""
        file_size = os.path.getsize(video_path)
        chunk_count = max(1, (file_size + _CHUNK_SIZE - 1) // _CHUNK_SIZE)

        # Step 1: Init
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/post/publish/video/init/",
                headers={**self._auth_headers, "Content-Type": "application/json"},
                json={
                    "post_info": {
                        "title": caption[:150],
                        "privacy_level": "PUBLIC_TO_EVERYONE",
                        "disable_duet": False,
                        "disable_comment": False,
                        "disable_stitch": False,
                    },
                    "source_info": {
                        "source": "FILE_UPLOAD",
                        "video_size": file_size,
                        "chunk_size": _CHUNK_SIZE,
                        "total_chunk_count": chunk_count,
                    },
                    "post_mode": "DIRECT_POST",
                    "media_type": "VIDEO",
                },
            )
            resp.raise_for_status()
            body = resp.json()
            self._check_tiktok_error(body, "video_init")
            upload_url = body["data"]["upload_url"]
            publish_id = body["data"]["publish_id"]

        # Step 2: Upload chunks
        with open(video_path, "rb") as f:
            for chunk_idx in range(chunk_count):
                chunk_data = f.read(_CHUNK_SIZE)
                start = chunk_idx * _CHUNK_SIZE
                end = start + len(chunk_data) - 1
                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.put(
                        upload_url,
                        content=chunk_data,
                        headers={
                            "Content-Type": "video/mp4",
                            "Content-Range": f"bytes {start}-{end}/{file_size}",
                            "Content-Length": str(len(chunk_data)),
                        },
                    )
                    resp.raise_for_status()
                logger.debug("TikTok chunk %d/%d uploaded", chunk_idx + 1, chunk_count)

        # Step 3: Complete
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.BASE_URL}/post/publish/video/complete/",
                headers={**self._auth_headers, "Content-Type": "application/json"},
                json={"publish_id": publish_id},
            )
            resp.raise_for_status()
            body = resp.json()
            self._check_tiktok_error(body, "video_complete")

        logger.info("TikTok video published: %s", publish_id)
        return PublishResult(success=True, platform="tiktok", post_id=publish_id)

    @staticmethod
    def _check_tiktok_error(body: dict, context: str) -> None:
        """Raise Exception jika TikTok API mengembalikan error."""
        error = body.get("error", {})
        code = error.get("code", "ok")
        if code not in ("ok", "success", ""):
            msg = error.get("message", str(error))
            raise Exception(f"TikTok API error [{context}] code={code}: {msg}")

    @staticmethod
    def _build_title(caption: str, hashtags: List[str]) -> str:
        # TikTok title max 150 karakter
        base = caption[:100]
        if hashtags:
            tags = " ".join(hashtags)
            return f"{base} {tags}"[:150]
        return base[:150]
