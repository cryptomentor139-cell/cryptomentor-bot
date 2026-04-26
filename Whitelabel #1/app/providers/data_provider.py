"""
WL#1 Data Provider — wrapper yang memastikan API key
diambil dari config WL#1, bukan dari environment global.
"""
import os
import sys

# Pastikan config WL#1 yang dipakai, bukan Bismillah
_wl_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if _wl_root not in sys.path:
    sys.path.insert(0, _wl_root)

import config as wl_config


def get_provider_env() -> dict:
    """
    Return dict env vars untuk crypto providers khusus WL#1.
    Dipakai saat inisialisasi provider agar tidak bocor ke instance lain.
    """
    return {
        "CRYPTOCOMPARE_API_KEY": wl_config.CRYPTOCOMPARE_API_KEY,
        "HELIUS_API_KEY":        wl_config.HELIUS_API_KEY,
        "COINGECKO_API_KEY":     wl_config.COINGECKO_API_KEY,
        "CRYPTONEWS_API_KEY":    wl_config.CRYPTONEWS_API_KEY,
    }


def inject_provider_env():
    """
    Inject API keys WL#1 ke os.environ sebelum provider diinisialisasi.
    Panggil ini di awal bot.py sebelum import provider lain.
    """
    for key, val in get_provider_env().items():
        if val:
            os.environ[key] = val
