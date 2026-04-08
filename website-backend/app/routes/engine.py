"""
Engine control endpoints — start/stop/state the autotrade engine.

The website backend runs on the same VPS as the Telegram bot, so we can
directly call start_engine / stop_engine from the bot's module.
Engine state is persisted in Supabase autotrade_sessions so both the web
and Telegram bot stay in sync.
"""

import os
import sys
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt import decode_token
from app.db.supabase import _client

router = APIRouter(prefix="/dashboard/engine", tags=["engine"])
bearer = HTTPBearer()

# Make Bismillah importable
_BISMILLAH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Bismillah")
)
if _BISMILLAH not in sys.path:
    sys.path.insert(0, _BISMILLAH)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])


def _get_session(tg_id: int) -> dict:
    res = _client().table("autotrade_sessions").select("*").eq(
        "telegram_id", tg_id
    ).limit(1).execute()
    return res.data[0] if res.data else {}


@router.get("/state")
async def engine_state(tg_id: int = Depends(get_current_user)):
    """Return whether the engine is currently running for this user."""
    try:
        from app.autotrade_engine import is_running
        running = is_running(tg_id)
    except Exception:
        # Fallback: read from Supabase
        session = _get_session(tg_id)
        running = session.get("engine_active", False) and session.get("status") == "active"

    session = _get_session(tg_id)
    return {
        "running": running,
        "status": session.get("status", "unknown"),
        "engine_active": session.get("engine_active", False),
        "trading_mode": session.get("trading_mode", "scalping"),
    }


@router.post("/start")
async def engine_start(tg_id: int = Depends(get_current_user)):
    """Start the autotrade engine for this user (mirrors Telegram bot behaviour)."""
    s = _client()

    # Get session
    session = _get_session(tg_id)
    if not session:
        raise HTTPException(status_code=404, detail="No autotrade session found. Set up via Telegram bot first.")

    deposit = float(session.get("initial_deposit") or 0)
    leverage = int(session.get("leverage") or 10)
    if deposit <= 0:
        raise HTTPException(status_code=400, detail="Invalid deposit amount. Update via Telegram bot.")

    # Get API keys
    try:
        from app.services import bitunix as bsvc
        keys = bsvc.get_user_api_keys(tg_id)
    except Exception:
        keys = None

    if not keys:
        raise HTTPException(status_code=409, detail="Bitunix API keys not configured.")

    # Check if already running
    try:
        from app.autotrade_engine import is_running, start_engine
        if is_running(tg_id):
            return {"running": True, "message": "Engine already running."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine module error: {e}")

    # Start engine — we need a bot instance. Use a minimal stub that sends
    # Telegram messages via HTTP (no PTB Application needed).
    try:
        from telegram import Bot
        from config import TELEGRAM_BOT_TOKEN
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        from app.skills_repo import has_skill
        is_premium = has_skill(tg_id, "dual_tp_rr3")

        exchange_id = keys.get("exchange", "bitunix")

        start_engine(
            bot=bot,
            user_id=tg_id,
            api_key=keys["api_key"],
            api_secret=keys["api_secret"],
            amount=deposit,
            leverage=leverage,
            notify_chat_id=tg_id,
            is_premium=is_premium,
            silent=False,
            exchange_id=exchange_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start engine: {e}")

    # Update Supabase
    s.table("autotrade_sessions").update({
        "status": "active",
        "engine_active": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("telegram_id", tg_id).execute()

    return {"running": True, "message": "Engine started."}


@router.post("/stop")
async def engine_stop(tg_id: int = Depends(get_current_user)):
    """Stop the autotrade engine for this user."""
    s = _client()

    try:
        from app.autotrade_engine import stop_engine, is_running
        was_running = is_running(tg_id)
        stop_engine(tg_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine module error: {e}")

    # Update Supabase
    s.table("autotrade_sessions").update({
        "status": "stopped",
        "engine_active": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("telegram_id", tg_id).execute()

    # Notify user on Telegram
    try:
        from telegram import Bot
        from config import TELEGRAM_BOT_TOKEN
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=tg_id,
            text="🛑 <b>AutoTrade stopped via Web Dashboard.</b>\n\nUse /autotrade to restart.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    return {"running": False, "message": "Engine stopped."}
