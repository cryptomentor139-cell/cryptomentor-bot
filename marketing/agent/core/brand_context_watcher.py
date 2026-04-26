"""
Brand Context Watcher — file watcher untuk reload brand_context.json secara otomatis.
marketing/agent/core/brand_context_watcher.py
"""
from __future__ import annotations

import logging
from pathlib import Path

from marketing.agent.config import Config

logger = logging.getLogger(__name__)

_BRAND_CONTEXT_FILE = Path(__file__).parent.parent / "brand_context.json"


class BrandContextWatcher:
    """
    Memantau perubahan pada brand_context.json menggunakan watchdog.
    Saat file berubah, memanggil config.reload() secara otomatis.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self._observer = None

    def start(self) -> None:
        """Start watchdog observer untuk marketing/agent/brand_context.json."""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            logger.warning(
                "watchdog tidak tersedia. Install dengan: pip install watchdog. "
                "Brand context watcher tidak aktif."
            )
            return

        config = self.config

        class _Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if Path(event.src_path).resolve() == _BRAND_CONTEXT_FILE.resolve():
                    logger.info(
                        "brand_context.json berubah, reload konfigurasi..."
                    )
                    try:
                        config.reload()
                        logger.info("Brand context berhasil di-reload.")
                    except Exception as exc:
                        logger.error("Gagal reload brand context: %s", exc)

            def on_created(self, event):
                self.on_modified(event)

        self._observer = Observer()
        self._observer.schedule(
            _Handler(),
            path=str(_BRAND_CONTEXT_FILE.parent),
            recursive=False,
        )
        self._observer.start()
        logger.info(
            "Brand context watcher aktif: memantau %s", _BRAND_CONTEXT_FILE
        )

    def stop(self) -> None:
        """Stop watchdog observer."""
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join(timeout=5)
                logger.info("Brand context watcher dihentikan.")
            except Exception as exc:
                logger.warning("Error saat menghentikan watcher: %s", exc)
            finally:
                self._observer = None
