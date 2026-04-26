"""
Video Generator — pipeline ElevenLabs (TTS) + Kling AI (text-to-video) untuk Reels.
marketing/agent/core/video_generator.py
"""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

_REELS_OUTPUT_DIR = Path("marketing/output/reels")
_REELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class VideoGenerationError(Exception):
    """Raised saat pipeline video gagal setelah semua retry."""


class ElevenLabsClient:
    BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    def __init__(self, api_key: str, voice_id: str) -> None:
        self.api_key = api_key
        self.voice_id = voice_id

    async def synthesize(self, text: str) -> bytes:
        url = self.BASE_URL.format(voice_id=self.voice_id)
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.content
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    logger.warning("ElevenLabs retry %d/3: %s", attempt + 1, exc)

        raise VideoGenerationError(f"ElevenLabs gagal setelah 3 percobaan: {last_exc}") from last_exc


class KlingAIClient:
    BASE_URL = "https://api.klingai.com/v1/videos/text2video"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def generate(self, prompt: str, audio_url: str, duration: int = 15) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "kling-v1",
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, text overlay",
            "duration": duration,
            "aspect_ratio": "9:16",
            "audio_url": audio_url,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        task_id = data.get("task_id") or data.get("id") or data.get("data", {}).get("task_id")
        if not task_id:
            raise VideoGenerationError(f"Kling AI tidak mengembalikan task_id. Response: {data}")
        return task_id

    async def poll_status(self, task_id: str, timeout_seconds: int = 300) -> dict:
        url = f"https://api.klingai.com/v1/videos/text2video/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        elapsed = 0

        while elapsed < timeout_seconds:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

            result = data.get("data", data)
            status = result.get("status", "")

            if status == "completed":
                return result
            if status in ("failed", "error"):
                raise VideoGenerationError(f"Kling AI task {task_id} gagal: {status}")

            await asyncio.sleep(10)
            elapsed += 10

        raise VideoGenerationError(f"Kling AI task {task_id} timeout setelah {timeout_seconds}s")

    async def download_video(self, video_url: str, output_path: str) -> str:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            response = await client.get(video_url)
            response.raise_for_status()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path


class VideoGenerator:
    def __init__(self, config) -> None:
        self.elevenlabs = ElevenLabsClient(config.elevenlabs_api_key, config.elevenlabs_voice_id)
        self.kling = KlingAIClient(config.kling_ai_api_key)
        self.config = config

    async def generate_voiceover(self, narration: str, content_id: str) -> str:
        audio_bytes = await self.elevenlabs.synthesize(narration)
        mp3_path = f"/tmp/voiceover_{content_id}.mp3"
        with open(mp3_path, "wb") as f:
            f.write(audio_bytes)
        return mp3_path

    async def generate_video(self, prompt: str, audio_path: str, content_id: str, duration: int = 45) -> str:
        audio_url = f"file://{os.path.abspath(audio_path)}"
        task_id = await self.kling.generate(prompt=prompt, audio_url=audio_url, duration=min(duration, 15))
        result = await self.kling.poll_status(task_id)

        video_url = (
            result.get("video_url")
            or result.get("result", {}).get("video_url")
            or result.get("videos", [{}])[0].get("url", "")
        )
        if not video_url:
            raise VideoGenerationError(f"Tidak ada video_url dari Kling AI task {task_id}")

        output_path = str(_REELS_OUTPUT_DIR / f"{content_id}.mp4")
        return await self.kling.download_video(video_url, output_path)

    async def create_reels_video(self, script, content_id: str) -> str:
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                mp3_path = await self.generate_voiceover(script.narration, content_id)
                mp4_path = await self.generate_video(
                    prompt=script.visual_description,
                    audio_path=mp3_path,
                    content_id=content_id,
                    duration=script.duration_target,
                )
                return mp4_path
            except Exception as exc:
                last_exc = VideoGenerationError(str(exc))
                if attempt < 1:
                    await asyncio.sleep(5)

        raise VideoGenerationError(
            f"create_reels_video gagal setelah 2 percobaan untuk {content_id}: {last_exc}"
        ) from last_exc
