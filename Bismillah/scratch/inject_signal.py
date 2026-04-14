import asyncio
import httpx

async def send_mock_signal():
    token = "8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4"
    admin_id = "1187119989"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    message = (
        "🚀 <b>Scalping Trade Opened</b>\n\n"
        "<b>User:</b> <code>System Inject</code>\n"
        "<b>Pair:</b> <code>XAUUSDT</code>\n"
        "<b>Side:</b> <code>LONG</code>\n"
        "<b>Entry:</b> <code>2350.50</code>\n"
        "<b>Leverage:</b> <code>50x</code>\n\n"
        "🎯 <b>Targets:</b>\n"
        "• TP1: 2360.00\n"
        "• TP2: 2375.00\n"
        "• TP3: 2390.00\n\n"
        "🛑 <b>Stop Loss:</b> 2335.00\n\n"
        "<i>Admin Notification enabled via Engine Monitor.</i>"
    )
    
    payload = {
        "chat_id": admin_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        print("RESULT_START")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        print("RESULT_END")

if __name__ == "__main__":
    asyncio.run(send_mock_signal())
