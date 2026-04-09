"""
Konfigurasi Marketing AI Agent.
Membaca semua env vars dari .env dan memvalidasi saat startup.
"""
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env dari direktori marketing/agent/ atau root proyek
_ENV_PATH = Path(__file__).parent / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    load_dotenv()

# Path ke brand_context.json
_BRAND_CONTEXT_PATH = Path(__file__).parent / "brand_context.json"

# Env vars yang wajib ada saat startup
_REQUIRED_VARS: list[str] = [
    # AI Providers
    "OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "CEREBRAS_API_KEY",
    # Social Media
    "INSTAGRAM_ACCESS_TOKEN",
    "INSTAGRAM_USER_ID",
    "FACEBOOK_PAGE_ACCESS_TOKEN",
    "FACEBOOK_PAGE_ID",
    "TIKTOK_ACCESS_TOKEN",
    "THREADS_ACCESS_TOKEN",
    # Video Generation
    "KLING_AI_API_KEY",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    # Database
    "SUPABASE_URL",
    "SUPABASE_KEY",
    # Telegram
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_ADMIN_IDS",
]

# Toggle vars — opsional, default True
_TOGGLE_VARS: list[str] = [
    "ENABLE_INSTAGRAM",
    "ENABLE_FACEBOOK",
    "ENABLE_TIKTOK",
    "ENABLE_THREADS",
    "ENABLE_VIDEO_GENERATION",
]


class ConfigError(Exception):
    """Raised saat env vars yang diperlukan tidak ditemukan."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            f"Konfigurasi tidak lengkap. Env vars yang hilang: {', '.join(missing)}"
        )


def _parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in ("false", "0", "no", "off")


class Config:
    """
    Singleton konfigurasi Marketing AI Agent.

    Contoh penggunaan:
        cfg = Config()
        cfg.validate()          # raise ConfigError jika ada yang hilang
        ctx = cfg.get_brand_context()
        cfg.reload()            # reload brand_context.json tanpa restart
    """

    def __init__(self) -> None:
        # AI Providers
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.cerebras_api_key: str = os.getenv("CEREBRAS_API_KEY", "")

        # Social Media
        self.instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.instagram_user_id: str = os.getenv("INSTAGRAM_USER_ID", "")
        self.facebook_page_access_token: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        self.facebook_page_id: str = os.getenv("FACEBOOK_PAGE_ID", "")
        self.tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
        self.threads_access_token: str = os.getenv("THREADS_ACCESS_TOKEN", "")

        # Video Generation
        self.kling_ai_api_key: str = os.getenv("KLING_AI_API_KEY", "")
        self.elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
        self.elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "")

        # Database
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_key: str = os.getenv("SUPABASE_KEY", "")

        # Telegram
        self.telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_admin_ids: list[int] = self._parse_admin_ids(
            os.getenv("TELEGRAM_ADMIN_IDS", "")
        )

        # Toggles (default True)
        self.enable_instagram: bool = _parse_bool(os.getenv("ENABLE_INSTAGRAM"))
        self.enable_facebook: bool = _parse_bool(os.getenv("ENABLE_FACEBOOK"))
        self.enable_tiktok: bool = _parse_bool(os.getenv("ENABLE_TIKTOK"))
        self.enable_threads: bool = _parse_bool(os.getenv("ENABLE_THREADS"))
        self.enable_video_generation: bool = _parse_bool(os.getenv("ENABLE_VIDEO_GENERATION"))

        # Brand context cache
        self._brand_context: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_admin_ids(raw: str) -> list[int]:
        """Parse comma-separated Telegram admin IDs menjadi list[int]."""
        ids: list[int] = []
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        return ids

    # ------------------------------------------------------------------
    # Validasi
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validasi semua env vars yang wajib ada.
        Raise ConfigError dengan daftar lengkap yang hilang.
        """
        missing = [var for var in _REQUIRED_VARS if not os.getenv(var)]
        if missing:
            raise ConfigError(missing)

    # ------------------------------------------------------------------
    # Brand Context
    # ------------------------------------------------------------------

    def get_brand_context(self) -> dict[str, Any]:
        """
        Return brand context dari brand_context.json.
        Raise FileNotFoundError / ValueError jika file tidak ada atau tidak valid.
        """
        if self._brand_context is None:
            self._load_brand_context()
        return self._brand_context  # type: ignore[return-value]

    def reload(self) -> None:
        """Reload brand_context.json tanpa restart sistem."""
        self._brand_context = None
        self._load_brand_context()

    def _load_brand_context(self) -> None:
        if not _BRAND_CONTEXT_PATH.exists():
            raise FileNotFoundError(
                f"brand_context.json tidak ditemukan di {_BRAND_CONTEXT_PATH}. "
                "Proses pembuatan konten dihentikan."
            )
        try:
            with open(_BRAND_CONTEXT_PATH, encoding="utf-8") as f:
                self._brand_context = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"brand_context.json tidak dapat dibaca (JSON tidak valid): {exc}"
            ) from exc
