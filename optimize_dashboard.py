import sys
import os

file_path = r'd:\cryptomentorAI\website-backend\app\routes\dashboard.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Parallel Portfolio Fetch replacement
old_portfolio = """    s = _client()

    # User data
    user_res = s.table("users").select(
        "telegram_id, username, first_name, credits, is_premium, premium_until, is_lifetime"
    ).eq("telegram_id", tg_id).limit(1).execute()
    user = user_res.data[0] if user_res.data else {}

    # Autotrade session
    session_res = s.table("autotrade_sessions").select(
        "trading_mode, engine_active, auto_mode_enabled, risk_mode, risk_per_trade, status, current_balance, total_profit"
    ).eq("telegram_id", tg_id).limit(1).execute()
    session = session_res.data[0] if session_res.data else {}

    # Open positions (trades yang belum closed)
    positions_res = s.table("autotrade_trades").select(
        "id, symbol, side, entry_price, qty, leverage, pnl_usdt, tp1_price, tp2_price, tp3_price, tp1_hit, tp2_hit, tp3_hit, opened_at"
    ).eq("telegram_id", tg_id).eq("status", "open").execute()
    positions = positions_res.data or []

    # PnL 30 hari terakhir
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    pnl_res = s.table("autotrade_trades").select("pnl_usdt").eq(
        "telegram_id", tg_id
    ).in_("status", CLOSED_STATUSES).gte("closed_at", since).execute()
    pnl_30d = sum(float(t.get("pnl_usdt") or 0) for t in (pnl_res.data or []))

    # Live Bitunix data (sync with Telegram bot). Best-effort: if keys are
    # missing or exchange call fails, fall back to Supabase-only values.
    live_account = None
    live_positions = None
    bitunix_error = None
    if bsvc.get_user_api_keys(tg_id):
        try:
            acc = await bsvc.fetch_account(tg_id)
            if acc.get("success"):
                live_account = {
                    "balance": acc.get("available", 0),
                    "available": acc.get("available", 0),
                    "frozen": acc.get("frozen", 0),
                    "margin": acc.get("margin", 0),
                    "cross_unrealized_pnl": acc.get("cross_unrealized_pnl", 0),
                    "isolation_unrealized_pnl": acc.get("isolation_unrealized_pnl", 0),
                    "total_unrealized_pnl": acc.get("total_unrealized_pnl", 0),
                }
            else:
                bitunix_error = acc.get("message") or acc.get("error") or "Account fetch returned failure"
            pos = await bsvc.fetch_positions(tg_id)
            if pos.get("success"):
                live_positions = pos.get("positions", [])
            elif not bitunix_error:
                bitunix_error = pos.get("message") or pos.get("error") or "Positions fetch returned failure"
        except Exception as e:
            bitunix_error = str(e)
    else:
        bitunix_error = "API keys not found or could not be decrypted\""""

new_portfolio = """    s = _client()
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    # Parallel Fetch for Portfolio
    try:
        # Check if keys exist first (sync check to decide whether to fetch Bitunix data)
        has_keys = bsvc.get_user_api_keys(tg_id) is not None
        
        tasks = [
            asyncio.to_thread(lambda: s.table("users").select(
                "telegram_id, username, first_name, credits, is_premium, premium_until, is_lifetime"
            ).eq("telegram_id", tg_id).limit(1).execute()),
            asyncio.to_thread(lambda: s.table("autotrade_sessions").select(
                "trading_mode, engine_active, auto_mode_enabled, risk_mode, risk_per_trade, status, current_balance, total_profit"
            ).eq("telegram_id", tg_id).limit(1).execute()),
            asyncio.to_thread(lambda: s.table("autotrade_trades").select(
                "id, symbol, side, entry_price, qty, leverage, pnl_usdt, tp1_price, tp2_price, tp3_price, tp1_hit, tp2_hit, tp3_hit, opened_at"
            ).eq("telegram_id", tg_id).eq("status", "open").execute()),
            asyncio.to_thread(lambda: s.table("autotrade_trades").select("pnl_usdt").eq(
                "telegram_id", tg_id
            ).in_("status", CLOSED_STATUSES).gte("closed_at", since).execute()),
        ]
        
        if has_keys:
            tasks.append(bsvc.fetch_account(tg_id))
            tasks.append(bsvc.fetch_positions(tg_id))
        
        results = await asyncio.gather(*tasks)
        
        user_res = results[0]
        session_res = results[1]
        positions_res = results[2]
        pnl_res = results[3]
        
        acc = results[4] if has_keys else {"success": False, "error": "No keys"}
        pos = results[5] if has_keys else {"success": False, "error": "No keys"}
        
    except Exception as e:
        logger.error(f"[Portfolio:{tg_id}] Parallel fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio data")

    user = user_res.data[0] if user_res.data else {}
    session = session_res.data[0] if session_res.data else {}
    positions = positions_res.data or []
    pnl_30d = sum(float(t.get("pnl_usdt") or 0) for t in (pnl_res.data or []))

    live_account = None
    live_positions = None
    bitunix_error = None

    if has_keys:
        if acc.get("success"):
            live_account = {
                "balance": acc.get("available", 0),
                "available": acc.get("available", 0),
                "frozen": acc.get("frozen", 0),
                "margin": acc.get("margin", 0),
                "cross_unrealized_pnl": acc.get("cross_unrealized_pnl", 0),
                "isolation_unrealized_pnl": acc.get("isolation_unrealized_pnl", 0),
                "total_unrealized_pnl": acc.get("total_unrealized_pnl", 0),
            }
        else:
            bitunix_error = acc.get("message") or acc.get("error") or "Account fetch failed"

        if pos.get("success"):
            live_positions = pos.get("positions", [])
        elif not bitunix_error:
            bitunix_error = pos.get("message") or pos.get("error") or "Positions fetch failed"
    else:
        bitunix_error = "API keys not found or could not be decrypted\""""

# Parallel Settings Fetch replacement
old_settings = """    s = _client()
    row = {}
    one_click_column_available = True
    try:
        res = s.table("autotrade_sessions").select(
            "risk_per_trade, one_click_risk_per_trade, leverage, trading_mode, risk_mode"
        ).eq("telegram_id", tg_id).limit(1).execute()
        row = (res.data or [{}])[0]
    except Exception as e:
        one_click_column_available = False
        logger.warning(f"[Settings:{tg_id}] one_click_risk_per_trade column unavailable, fallback select: {e}")
        res = s.table("autotrade_sessions").select(
            "risk_per_trade, leverage, trading_mode, risk_mode"
        ).eq("telegram_id", tg_id).limit(1).execute()
        row = (res.data or [{}])[0]

    # Fetch LIVE equity from Bitunix (critical for accurate risk calculations)
    # Equity = available + frozen + unrealized_pnl
    equity = 0.0
    available = 0.0
    frozen = 0.0
    unrealized_pnl = 0.0
    try:
        acc = await bsvc.fetch_account(tg_id)
        if acc.get("success"):
            available = float(acc.get("available", 0) or 0)   # free/usable balance
            frozen = float(acc.get("frozen", 0) or 0)         # locked in open positions
            unrealized_pnl = float(acc.get("total_unrealized_pnl", 0) or 0)

            # Equity = available + frozen (total wallet) + unrealized PnL
            equity = available + frozen + unrealized_pnl

            logger.info(
                f"[Equity:{tg_id}] available=${available:.2f} frozen=${frozen:.2f} "
                f"unrealized=${unrealized_pnl:.2f} => equity=${equity:.2f}"
            )
    except Exception as e:
        logger.warning(f"Failed to fetch live equity for {tg_id}: {e}\")"""

new_settings = """    s = _client()
    # Parallel Fetch for Settings
    try:
        results = await asyncio.gather(
            asyncio.to_thread(lambda: s.table("autotrade_sessions").select(
                "risk_per_trade, one_click_risk_per_trade, leverage, trading_mode, risk_mode"
            ).eq("telegram_id", tg_id).limit(1).execute()),
            bsvc.fetch_account(tg_id)
        )
        sess_res, acc = results
        row = (sess_res.data or [{}])[0]
    except Exception as e:
        logger.warning(f"[Settings:{tg_id}] Parallel fetch failed: {e}")
        # Partial fallback logic if parallel gather fails
        return {"success": False, "error": str(e)}

    # Equity = available + frozen (total wallet) + unrealized PnL
    equity = 0.0
    available = 0.0
    frozen = 0.0
    unrealized_pnl = 0.0
    if acc.get("success"):
        available = float(acc.get("available", 0) or 0)
        frozen = float(acc.get("frozen", 0) or 0)
        unrealized_pnl = float(acc.get("total_unrealized_pnl", 0) or 0)
        equity = available + frozen + unrealized_pnl"""

content = content.replace(old_portfolio, new_portfolio)
content = content.replace(old_settings, new_settings)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Applied optimizations.")
