import asyncio
import os
from datetime import datetime, UTC
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1187119989"))

async def main():
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN/BOT_TOKEN env var")
    bot = Bot(TOKEN)

    now_str = datetime.now(UTC).strftime('%d %b %Y %H:%M:%S UTC')
    text = (
        "🤖 <b>Cryptomentor AI Autotrade</b>\n\n"
        "<b>Direction:</b> Long\n"
        "<b>Trading Pair:</b> XAUUSDT\n"
        "<b>Entry:</b> 2350.45\n"
        "<b>TP:</b> 2375.00\n"
        "<b>SL:</b> 2345.10\n"
        "<b>Risk PNL:</b> $10.00\n"
        "<b>Risk % on equity:</b> 1.00%\n"
        "<b>Order ID:</b> <code>ORD-XAU-777</code>\n"
        "<b>Date and time:</b> " + now_str + "\n\n"
        "⚡ <b>Margin Efficiency Optimized</b>\n"
        "• Leverage hiked to <b>125x</b> (Max for XAU)\n"
        "• Dynamic SL adjusted to maintain exact USD risk."
    )
    try:
        await bot.get_me() # verify token
        await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode='HTML')
        print(f"[OK] Mock signal sent to Admin {ADMIN_ID}")
    except Exception as e:
        print(f"[ERR] Failed to send to Admin {ADMIN_ID}: {e}")

if __name__ == '__main__':
    asyncio.run(main())
