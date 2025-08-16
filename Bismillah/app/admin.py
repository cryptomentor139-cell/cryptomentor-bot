
from .stats import build_system_status

# Global state - update sesuai kebutuhan
AUTO_SIGNALS_RUNNING = True
LEGACY_JSON_PATH = "Bismillah/data/users_local.json"  # Path ke JSON lokal

def get_admin_panel_text() -> str:
    """Generate admin panel text with system status"""
    return build_system_status(
        auto_signals_running=AUTO_SIGNALS_RUNNING,
        legacy_json_path=LEGACY_JSON_PATH
    )
