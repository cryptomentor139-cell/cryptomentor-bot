"""
Designer Agent — render feed image via Puppeteer dan generate Reels video.
marketing/agent/agents/designer_agent.py
"""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from datetime import date
from pathlib import Path

from marketing.agent.core.video_generator import VideoGenerationError, VideoGenerator

logger = logging.getLogger(__name__)


class DesignerAgent:
    TEMPLATES_DIR = Path("marketing/templates")
    OUTPUT_FEEDS_DIR = Path("marketing/output/feeds")
    OUTPUT_REELS_DIR = Path("marketing/output/reels")
    GENERATE_JS = Path("marketing/generate.js")

    def __init__(self, config) -> None:
        self.config = config
        self.video_generator = VideoGenerator(config)
        self.OUTPUT_FEEDS_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_REELS_DIR.mkdir(parents=True, exist_ok=True)

    def select_template(self, content_type: str, emotion_type: str) -> str:
        if emotion_type == "education" or content_type == "education":
            return "education.html"
        return "product.html"

    async def render_feed_image(self, content, content_id: str) -> str:
        template = self.select_template(content.template, content.emotion_type)
        today = date.today().isoformat()
        tema = content.topic.lower().replace(" ", "_")[:30]
        output_path = str(self.OUTPUT_FEEDS_DIR / f"{today}_{tema}_instagram.png")

        data = {
            "id": content_id,
            "type": content.template,
            "theme": tema,
            "eyebrow": (content.pas.hook or "")[:60],
            "headline": (content.pas.problem or "")[:80],
            "subtext": (content.pas.solution or "")[:120],
            "cta": (content.pas.cta or "")[:60],
            "output_path": output_path,
        }
        return await self.render_via_puppeteer(template, data, content_id)

    async def render_via_puppeteer(self, template: str, data: dict, content_id: str) -> str:
        tmp_json = f"/tmp/post_{content_id}.json"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        cmd = ["node", str(self.GENERATE_JS), f"--data={tmp_json}", "--no-send"]
        last_exc: Exception | None = None

        for attempt in range(3):
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=30),
                )
                if result.returncode != 0:
                    raise RuntimeError(f"generate.js error: {result.stderr.strip()}")

                # Parse output path dari stdout
                for line in result.stdout.splitlines():
                    if "→" in line:
                        return line.split("→")[-1].strip()
                    if line.strip().endswith(".png"):
                        return line.strip()

                return data.get("output_path", "")
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    logger.warning("Puppeteer retry %d/3: %s", attempt + 1, exc)

        raise RuntimeError(f"render_via_puppeteer gagal setelah 3 percobaan: {last_exc}") from last_exc

    async def generate_reels_video(self, script, content_id: str) -> str | None:
        if not self.config.enable_video_generation:
            logger.info("Video generation dinonaktifkan, skip content_id=%s", content_id)
            return None
        try:
            mp4_path = await self.video_generator.create_reels_video(script, content_id)
            return mp4_path
        except VideoGenerationError as exc:
            logger.warning("generate_reels_video gagal content_id=%s: %s", content_id, exc)
            return None

    async def process_content_item(self, item) -> object:
        if item.content_type == "feed" and item.feed:
            try:
                image_path = await self.render_feed_image(item.feed, item.id)
                item.feed.image_path = image_path
            except Exception as exc:
                logger.error("Gagal render feed image content_id=%s: %s", item.id, exc)
        elif item.content_type == "reels" and item.reels:
            video_path = await self.generate_reels_video(item.reels, item.id)
            item.reels.video_path = video_path
        return item
