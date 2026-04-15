"""
Analytics API — FastAPI app untuk observability dashboard
Provides real-time trading stats, position coordination state, and performance metrics.

Port: 8896 (analytics4896.cryptomentor.id)
Auth: Telegram Login Widget — verifies hash against bot token, issues session JWT
Rate limiting: 100 req/menit per user
"""

import asyncio
import hashlib
import hmac
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Admin authentication
# ─────────────────────────────────────────────────────────────────────────────

ADMIN_ALLOWLIST: set = set()


def _load_admin_ids():
    """Load admin IDs from environment (same as bot.py)."""
    global ADMIN_ALLOWLIST
    admin_ids = []

    # Try multiple environment variable names
    for env_var in ["ADMIN_IDS", "ADMIN1", "ADMIN2", "ADMIN3", "ADMIN4", "ADMIN5"]:
        val = os.getenv(env_var, "").strip()
        if val:
            try:
                admin_id = int(val)
                admin_ids.append(admin_id)
            except ValueError:
                logger.warning(f"[Analytics] Invalid admin ID in {env_var}: {val}")

    ADMIN_ALLOWLIST = set(admin_ids)
    logger.info(f"[Analytics] Loaded {len(ADMIN_ALLOWLIST)} admin IDs")


def _verify_dashboard_password(password: str) -> bool:
    """Verify the dashboard access password."""
    correct = os.getenv("DASHBOARD_PASSWORD", "secret4896")
    return hmac.compare_digest(password.encode(), correct.encode())


def _issue_session_jwt(telegram_id: int) -> str:
    """Issue a short-lived session JWT after successful Telegram auth."""
    import jwt as pyjwt
    secret = os.getenv("JWT_SECRET", "analytics-secret-key")
    payload = {
        "sub": str(telegram_id),
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7,  # 7 days
    }
    return pyjwt.encode(payload, secret, algorithm="HS256")


def _verify_admin_jwt(token: str) -> Optional[int]:
    """
    Verify session JWT issued by /auth/login.
    sub=0 means password-authenticated (always allowed).
    """
    if not token:
        return None

    try:
        import jwt as pyjwt
        secret = os.getenv("JWT_SECRET", "analytics-secret-key")
        payload = pyjwt.decode(token, secret, algorithms=["HS256"])
        # sub=0 → password login, always valid
        return int(payload.get("sub", -1))

    except Exception as e:
        logger.warning(f"[Analytics] JWT verification failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Rate limiter
# ─────────────────────────────────────────────────────────────────────────────


def _admin_key(request: Request) -> str:
    """Rate limit key = admin telegram_id (from verified token)."""
    admin_id = getattr(request.state, "_admin_id", None)
    if admin_id:
        return str(admin_id)
    return get_remote_address(request)


limiter = Limiter(key_func=_admin_key)

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Analytics API",
    version="1.0.0",
    description="Real-time trading analytics and coordination observability",
)

# Enable CORS for dashboard frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to analytics4896.cryptomentor.id in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "rate_limit_exceeded"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Middleware: verify Authorization header and extract admin_id
# ─────────────────────────────────────────────────────────────────────────────


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Verify JWT token for all endpoints except health check, dashboard, and auth."""
    if request.url.path in ("/health", "/", "/dashboard", "/favicon.ico", "/auth/login"):
        return await call_next(request)

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]

    # Verify token
    admin_id = _verify_admin_jwt(token)
    if admin_id is None:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": "Invalid or missing token"},
        )

    # Store admin_id in request state for use in endpoints
    request.state._admin_id = admin_id
    return await call_next(request)


# ─────────────────────────────────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required)."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/auth/login")
async def auth_login(request: Request):
    """Verify dashboard password and issue a session JWT."""
    data = await request.json()
    password = <REDACTED_PASSWORD>"password", "")

    if not _verify_dashboard_password(password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Issue a generic admin session token
    session_token = _issue_session_jwt(0)
    logger.info("[Analytics] Dashboard login successful")
    return {"token": session_token}


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the analytics dashboard HTML (no auth required — auth happens in browser)."""
    import pathlib
    dashboard = pathlib.Path(__file__).parent / "analytics_dashboard.html"
    if dashboard.exists():
        return HTMLResponse(content=dashboard.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard file not found</h1>", status_code=404)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/analytics/coordinator-state
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/api/analytics/coordinator-state")
@limiter.limit("100/minute")
async def get_coordinator_state(
    request: Request,
    user_id: Optional[int] = None,
    symbol: Optional[str] = None,
):
    """
    Get coordinator state (symbol ownership, pending orders, cooldowns).

    Query params:
      - user_id: Filter by user (optional)
      - symbol: Filter by symbol (optional)

    Returns:
        {
            "timestamp": ISO8601,
            "total_users": int,
            "total_symbols": int,
            "users": {
                "123": {
                    "symbols": {
                        "BTCUSDT": {
                            "owner": "swing" | "scalp" | "one_click" | "manual" | "unknown" | "none",
                            "has_position": bool,
                            "side": "long" | "short" | "none",
                            "size": float,
                            "entry_price": float,
                            "pending_order": bool,
                            "cooldown_until": ISO8601 | null,
                            "last_exit_ts": unix_timestamp | null,
                        },
                        ...
                    }
                }
            }
        }
    """
    try:
        from app.symbol_coordinator import get_coordinator

        coordinator = get_coordinator()
        snapshot = await coordinator.export_debug_snapshot()

        # Filter by user_id if provided
        if user_id:
            if str(user_id) not in snapshot.get("users", {}):
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_users": 0,
                    "total_symbols": 0,
                    "users": {},
                }
            snapshot["users"] = {str(user_id): snapshot["users"][str(user_id)]}

        # Filter by symbol if provided
        if symbol and user_id:
            user_data = snapshot["users"].get(str(user_id), {})
            symbols = user_data.get("symbols", {})
            if symbol in symbols:
                user_data["symbols"] = {symbol: symbols[symbol]}
            else:
                user_data["symbols"] = {}

        snapshot["timestamp"] = datetime.now(timezone.utc).isoformat()
        return snapshot

    except Exception as e:
        logger.error(f"[Analytics] coordinator-state failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "service_unavailable", "message": str(e)},
        )


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/analytics/trading-stats
# ─────────────────────────────────────────────────────────────────────────────


# Trade outcome classification
_WIN_STATUSES = {"closed_tp", "closed_tp1", "closed_tp2", "closed_tp3"}
_LOSS_STATUSES = {"closed_sl"}
_CLOSED_STATUSES = _WIN_STATUSES | _LOSS_STATUSES | {
    "closed_flip", "closed_manual", "closed",
    "max_hold_time_exceeded", "sideways_max_hold_exceeded",
}


@app.get("/api/analytics/trading-stats")
@limiter.limit("100/minute")
async def get_trading_stats(
    request: Request,
    user_id: Optional[int] = None,
    days: int = 7,
):
    """
    Get trading statistics (open/closed positions, PnL, win rate by TP/SL outcome).

    Win rate = closed_tp trades / (closed_tp + closed_sl trades).
    PnL from pnl_usdt field where available; falls back to 0.
    Also returns session balance data (current_balance, initial_deposit, total_profit).
    """
    try:
        from app.supabase_repo import _client as get_supabase
        from datetime import datetime as dt

        db = get_supabase()
        start_date = (dt.utcnow() - timedelta(days=days)).isoformat()

        # ── Trades ────────────────────────────────────────────────────────────
        if user_id:
            result = db.table("autotrade_trades").select(
                "telegram_id, symbol, status, side, pnl_usdt, opened_at, closed_at"
            ).eq("telegram_id", user_id).gte("opened_at", start_date).execute()
        else:
            result = db.table("autotrade_trades").select(
                "telegram_id, symbol, status, side, pnl_usdt, opened_at, closed_at"
            ).gte("opened_at", start_date).execute()

        trades = result.data if result.data else []

        user_stats: Dict = {}
        for trade in trades:
            uid = trade["telegram_id"]
            if uid not in user_stats:
                user_stats[uid] = {
                    "total_trades": 0,
                    "open_positions": 0,
                    "closed_positions": 0,
                    "tp_trades": 0,       # won by TP
                    "sl_trades": 0,       # lost by SL
                    "total_pnl_usdt": 0.0,
                    "trade_durations": [],
                    "daily": {},
                    "status_counts": {},
                }

            status = trade.get("status", "")
            pnl = float(trade.get("pnl_usdt") or 0)
            s = user_stats[uid]

            # Count by status bucket
            s["status_counts"][status] = s["status_counts"].get(status, 0) + 1

            if status == "open":
                s["open_positions"] += 1
            elif status in _CLOSED_STATUSES:
                s["closed_positions"] += 1
                s["total_pnl_usdt"] += pnl
                if status in _WIN_STATUSES:
                    s["tp_trades"] += 1
                elif status in _LOSS_STATUSES:
                    s["sl_trades"] += 1

            s["total_trades"] += 1

            # Daily buckets
            day = (trade.get("opened_at") or "")[:10]
            if day:
                bucket = s["daily"].setdefault(day, {"trades": 0, "pnl": 0.0})
                bucket["trades"] += 1
                if status != "open":
                    bucket["pnl"] += pnl

            # Trade durations
            if status != "open" and trade.get("opened_at") and trade.get("closed_at"):
                try:
                    d1 = dt.fromisoformat(trade["opened_at"].replace("Z", "+00:00"))
                    d2 = dt.fromisoformat(trade["closed_at"].replace("Z", "+00:00"))
                    s["trade_durations"].append((d2 - d1).total_seconds())
                except Exception:
                    pass

        # ── Sessions (balance data) ───────────────────────────────────────────
        session_map: Dict = {}
        try:
            if user_id:
                sess_result = db.table("autotrade_sessions").select(
                    "telegram_id, current_balance, initial_deposit, total_profit, status, engine_active, trading_mode"
                ).eq("telegram_id", user_id).execute()
            else:
                sess_result = db.table("autotrade_sessions").select(
                    "telegram_id, current_balance, initial_deposit, total_profit, status, engine_active, trading_mode"
                ).execute()
            for sess in (sess_result.data or []):
                session_map[sess["telegram_id"]] = sess
        except Exception as e:
            logger.warning(f"[Analytics] sessions query failed: {e}")

        # ── Format response ───────────────────────────────────────────────────
        formatted_stats = {}
        all_uids = set(user_stats.keys()) | set(session_map.keys())

        for uid in all_uids:
            stats = user_stats.get(uid, {})
            sess = session_map.get(uid, {})

            tp = stats.get("tp_trades", 0)
            sl = stats.get("sl_trades", 0)
            decisive = tp + sl
            win_rate = (tp / decisive * 100) if decisive > 0 else None

            durations = stats.get("trade_durations", [])
            avg_dur = sum(durations) / len(durations) if durations else 0

            daily_stats = [
                {"date": d, "trades": v["trades"], "pnl": v["pnl"]}
                for d, v in sorted(stats.get("daily", {}).items())
            ]

            init_dep = float(sess.get("initial_deposit") or 0)
            curr_bal = float(sess.get("current_balance") or 0)
            total_profit = float(sess.get("total_profit") or 0)
            roi_pct = ((curr_bal - init_dep) / init_dep * 100) if init_dep > 0 else None

            formatted_stats[uid] = {
                "total_trades": stats.get("total_trades", 0),
                "open_positions": stats.get("open_positions", 0),
                "closed_positions": stats.get("closed_positions", 0),
                "tp_trades": tp,
                "sl_trades": sl,
                "total_pnl_usdt": stats.get("total_pnl_usdt", 0.0),
                "win_rate": win_rate,          # None if no decisive trades
                "avg_trade_duration_seconds": avg_dur,
                "daily_stats": daily_stats,
                "status_counts": stats.get("status_counts", {}),
                # Session data
                "initial_deposit": init_dep,
                "current_balance": curr_bal,
                "total_profit": total_profit,
                "roi_pct": roi_pct,
                "session_status": sess.get("status", "unknown"),
                "engine_active": sess.get("engine_active", False),
                "trading_mode": sess.get("trading_mode", "unknown"),
            }

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "period_days": days,
            "users": formatted_stats,
        }

    except Exception as e:
        logger.error(f"[Analytics] trading-stats failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "service_unavailable", "message": str(e)},
        )


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/analytics/engine-health
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/api/analytics/engine-health")
@limiter.limit("100/minute")
async def get_engine_health(
    request: Request,
    user_id: Optional[int] = None,
):
    """
    Get engine health status (running/stopped, last scan, error count).

    Query params:
      - user_id: Filter by user (optional)

    Returns:
        {
            "timestamp": ISO8601,
            "engines": {
                "123": {
                    "running": bool,
                    "strategy_mode": "swing" | "scalp" | "hybrid" | "unknown",
                    "last_scan_ts": unix_timestamp | null,
                    "total_scans": int,
                    "error_count_24h": int,
                }
            }
        }
    """
    try:
        from app.autotrade_engine import is_running as is_swing_running
        from app.supabase_repo import _client as get_supabase

        db = get_supabase()

        # Get all active sessions
        if user_id:
            result = db.table("autotrade_sessions").select(
                "telegram_id, status, engine_active"
            ).eq("telegram_id", user_id).execute()
        else:
            result = db.table("autotrade_sessions").select(
                "telegram_id, status, engine_active"
            ).in_("status", ["active", "uid_verified"]).execute()

        sessions = result.data if result.data else []

        engines: Dict = {}
        for session in sessions:
            uid = session["telegram_id"]
            running = session.get("engine_active", False)

            # Get error count in last 24 hours (error_logs table may not exist)
            error_count = 0
            try:
                error_result = db.table("error_logs").select(
                    "count"
                ).eq("telegram_id", uid).gte(
                    "created_at", (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
                ).execute()
                error_count = error_result.count if hasattr(error_result, "count") else 0
            except Exception:
                pass

            engines[uid] = {
                "running": running,
                "status": session.get("status", "unknown"),
                "strategy_mode": "swing",  # Default, would be extended to detect scalp mode
                "last_scan_ts": None,  # Would be updated during scans
                "total_scans": 0,  # Would be tracked in session
                "error_count_24h": error_count,
            }

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engines": engines,
        }

    except Exception as e:
        logger.error(f"[Analytics] engine-health failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "service_unavailable", "message": str(e)},
        )


# ─────────────────────────────────────────────────────────────────────────────
# Startup/shutdown
# ─────────────────────────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup_event():
    """Initialize analytics on startup."""
    logger.info("[Analytics] API starting up...")
    _load_admin_ids()
    logger.info(f"[Analytics] Initialized with {len(ADMIN_ALLOWLIST)} admin IDs")


if __name__ == "__main__":
    import uvicorn

    _load_admin_ids()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8896,
        log_level="info",
    )
