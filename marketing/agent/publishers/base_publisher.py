"""
Base class untuk semua publisher platform sosial media.
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PublishResult:
    success: bool
    platform: str
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PostMetrics:
    post_id: str
    platform: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0
    clicks: int = 0


class BasePublisher(ABC):
    @abstractmethod
    async def publish_feed(self, image_path: str, caption: str, hashtags: List[str]) -> PublishResult:
        ...

    @abstractmethod
    async def publish_reels(self, video_path: str, caption: str) -> PublishResult:
        ...

    @abstractmethod
    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        ...

    async def _send_admin_notification(self, message: str) -> None:
        # Log saja untuk sekarang, notifikasi Telegram dihandle oleh Orchestrator
        logging.getLogger(__name__).error("Publisher error: %s", message)
