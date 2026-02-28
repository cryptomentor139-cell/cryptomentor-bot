"""
Integration untuk tracking signal di command handlers
"""
from app.signal_logger import signal_logger
import logging

logger = logging.getLogger(__name__)

def track_user_command(user_id: int, username: str, command: str, symbol: str = None, timeframe: str = None):
    """Track command user untuk dokumentasi"""
    try:
        signal_logger.log_user_prompt(user_id, username, command, symbol, timeframe)
        logger.debug(f"Tracked command: {command} from user {user_id}")
    except Exception as e:
        logger.error(f"Failed to track command: {e}")

def track_signal_given(user_id: int, symbol: str, timeframe: str, 
                      entry_price: float, tp1: float, tp2: float, sl: float,
                      signal_type: str = "LONG"):
    """Track signal yang diberikan ke user"""
    try:
        signal_id = signal_logger.log_signal_result(
            user_id, symbol, timeframe, entry_price, tp1, tp2, sl, signal_type
        )
        logger.info(f"Signal tracked: {signal_id}")
        return signal_id
    except Exception as e:
        logger.error(f"Failed to track signal: {e}")
        return None

def update_signal_outcome(signal_id: str, hit_tp: bool, pnl_percent: float):
    """Update hasil signal (WIN jika hit TP, LOSS jika hit SL)"""
    try:
        result = "WIN" if hit_tp else "LOSS"
        signal_logger.update_signal_result(signal_id, result, pnl_percent)
        logger.info(f"Signal {signal_id} updated: {result} ({pnl_percent:+.2f}%)")
    except Exception as e:
        logger.error(f"Failed to update signal: {e}")

def get_current_winrate(days: int = 7):
    """Dapatkan winrate saat ini"""
    try:
        stats = signal_logger.calculate_winrate(days)
        return stats
    except Exception as e:
        logger.error(f"Failed to get winrate: {e}")
        return None
