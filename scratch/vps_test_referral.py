import os
import asyncio
import httpx
from supabase import create_client

# VPS paths
ENV_PATH = "/root/cryptomentor-bot/website-backend/.env"

def load_vps_env():
    if not os.path.exists(ENV_PATH):
        print(f"File {ENV_PATH} not found!")
        return
    with open(ENV_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

async def test_notification():
    load_vps_env()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    sb_url = os.getenv("SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not bot_token or not sb_url or not sb_key:
        print("Missing env vars!")
        return

    supabase = create_client(sb_url, sb_key)
    
    # 1. Get an active partner
    res = supabase.table("community_partners").select("*").eq("status", "active").limit(1).execute()
    if not res.data:
        print("No active community partners found in DB!")
        # Fallback to test with cryptotradersid if it exists
        res = supabase.table("community_partners").select("*").eq("community_code", "cryptotradersid").execute()
        
    if not res.data:
        print("No partners found to test with.")
        return
        
    partner = res.data[0]
    p_name = partner['community_name']
    p_code = partner['community_code']
    p_id = partner['telegram_id']
    
    print(f"Testing with Partner: {p_name} ({p_code}) -> TG ID: {p_id}")
    
    # 2. Simulate UID submission notification
    test_uid = "999888777"
    user_id = 12345  # Fake user
    
    msg = (
        f"🔔 <b>New UID Verification Request</b>\n\n"
        f"Community: <b>{p_name}</b> (<code>{p_code}</code>)\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Bitunix UID: <code>{test_uid}</code>\n\n"
        f"Please approve or reject this user."
    )
    
    # Standard buttons
    from json import dumps
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Approve", "callback_data": f"uid_acc_{user_id}"},
            {"text": "❌ Reject", "callback_data": f"uid_reject_{user_id}"}
        ]]
    }
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": p_id,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": dumps(keyboard)
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        if resp.status_code == 200:
            print(f"SUCCESS: Notification sent to {p_name} (ID: {p_id})")
        else:
            print(f"FAILED: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_notification())
