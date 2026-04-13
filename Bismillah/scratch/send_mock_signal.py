import asyncio
import os
import random
import sys
from datetime import UTC, datetime
from pathlib import Path

from telegram import Bot


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def _fmt(v: float, d: int = 2) -> str:
    return f"{float(v):,.{d}f}"


async def main():
    repo_root = Path(__file__).resolve().parents[2]
    _load_env_file(repo_root / "Bismillah" / ".env")

    bismillah_root = repo_root / "Bismillah"
    if str(bismillah_root) not in sys.path:
        sys.path.insert(0, str(bismillah_root))

    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN", "")
    admin_id = int(os.getenv("ADMIN_TELEGRAM_ID", "1187119989"))

    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN/BOT_TOKEN env var")

    from app.handlers_autotrade import get_user_api_keys
    from app.supabase_repo import get_autotrade_session
    from app.exchange_registry import get_client
    from app.position_sizing import calculate_position_size_pro

    keys = get_user_api_keys(admin_id)
    if not keys:
        raise RuntimeError(f"No API keys found for admin {admin_id}")

    exchange_id = str(keys.get("exchange") or "bitunix").lower()
    client = get_client(exchange_id, keys["api_key"], keys["api_secret"])

    account = await asyncio.to_thread(client.get_account_info)
    if not account.get("success"):
        raise RuntimeError(f"Account fetch failed: {account.get('error') or account.get('message')}")

    available = float(account.get("available", 0) or 0)
    frozen = float(account.get("frozen", 0) or 0)
    upnl = float(account.get("total_unrealized_pnl", 0) or 0)
    equity = available + frozen + upnl

    symbol = "ETHUSDT"
    ticker = await asyncio.to_thread(client.get_ticker, symbol)
    if ticker.get("success"):
        entry = float(ticker.get("mark_price") or ticker.get("price") or ticker.get("last") or 0)
    else:
        entry = 0.0
    if entry <= 0:
        entry = 3000.0

    sess = get_autotrade_session(admin_id) or {}
    risk_pct = float(sess.get("risk_per_trade") or 1.0)
    baseline_leverage = int(sess.get("leverage") or 20)

    sl_dist_pct = 0.005  # 0.5%
    sl = entry * (1.0 - sl_dist_pct)
    tp1 = entry * (1.0 + sl_dist_pct * 1.5)
    tp2 = entry * (1.0 + sl_dist_pct * 2.5)
    tp3 = entry * (1.0 + sl_dist_pct * 3.5)

    max_leverage_allowed = baseline_leverage
    if hasattr(client, "get_max_leverage"):
        try:
            max_leverage_allowed = int(await asyncio.to_thread(client.get_max_leverage, symbol))
        except Exception:
            max_leverage_allowed = baseline_leverage

    sizing = calculate_position_size_pro(
        balance=equity,
        risk_pct=risk_pct,
        entry_price=entry,
        sl_price=sl,
        leverage=baseline_leverage,
        symbol=symbol,
        max_leverage=max_leverage_allowed,
        min_sl_dist_pct=0.002,
    )
    if not sizing.get("valid"):
        raise RuntimeError(f"Sizing failed: {sizing.get('error')}")

    leverage = int(sizing.get("leverage", baseline_leverage) or baseline_leverage)
    qty = float(sizing.get("qty") or 0.0)
    sl_effective = float(sizing.get("sl_price") or sl)
    risk_amount = float(sizing.get("risk_amount") or (equity * (risk_pct / 100.0)))
    margin_used = float(sizing.get("margin_required") or 0.0)
    risk_pct_effective = float(sizing.get("risk_pct") or risk_pct)

    now_str = datetime.now(UTC).strftime("%d %b %Y %H:%M:%S UTC")
    order_id = f"MOCK-ETH-{random.randint(1000, 9999)}"
    text = (
        "🤖 <b>Cryptomentor AI Autotrade (Mock Injection)</b>\n\n"
        "<b>Direction:</b> Long\n"
        "<b>Trading Pair:</b> ETHUSDT\n"
        f"<b>Entry:</b> {_fmt(entry, 2)}\n"
        f"<b>TP1:</b> {_fmt(tp1, 2)}\n"
        f"<b>TP2:</b> {_fmt(tp2, 2)}\n"
        f"<b>TP3:</b> {_fmt(tp3, 2)}\n"
        f"<b>SL:</b> {_fmt(sl_effective, 2)}\n"
        f"<b>Qty:</b> {_fmt(qty, 4)} ETH | <b>Leverage:</b> {leverage}x\n"
        f"<b>Margin used:</b> ${_fmt(margin_used, 2)}\n"
        f"<b>Risk PNL:</b> ${_fmt(risk_amount, 2)}\n"
        f"<b>Risk % on equity:</b> {risk_pct_effective:.2f}%\n"
        f"<b>Account equity:</b> ${_fmt(equity, 2)}\n"
        f"<b>Order ID:</b> <code>{order_id}</code>\n"
        f"<b>Date and time:</b> {now_str}\n\n"
        "⚡ <b>Sample Trade Alert</b>\n"
        f"• Exchange: <b>{exchange_id.upper()}</b>\n"
        f"• Leverage profile: <b>{leverage}x</b> (max-safe optimized)\n"
        "• This is a mock signal preview for admin validation."
    )

    bot = Bot(token)
    await bot.get_me()
    await bot.send_message(chat_id=admin_id, text=text, parse_mode="HTML")
    print(f"[OK] ETH mock signal sent to admin {admin_id} using live balance ${_fmt(equity, 2)}")


if __name__ == "__main__":
    asyncio.run(main())
