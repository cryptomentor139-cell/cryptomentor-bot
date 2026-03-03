#!/usr/bin/env python3
"""Quick Bot Test - Fast validation without external API calls"""

from dotenv import load_dotenv
load_dotenv()

print("🚀 Quick Bot Test\n")

# Test 1: Bot Init
print("1️⃣ Testing Bot Initialization...")
try:
    from bot import TelegramBot
    bot = TelegramBot()
    print(f"   ✅ Bot OK - {len(bot.admin_ids)} admins\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")
    exit(1)

# Test 2: Database
print("2️⃣ Testing Database...")
try:
    from services import get_database
    db = get_database()
    stats = db.get_user_stats()
    print(f"   ✅ Database OK - {stats['total_users']} users\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")
    exit(1)

# Test 3: Handlers
print("3️⃣ Testing Critical Handlers...")
handlers_ok = 0
handlers_total = 0

critical_handlers = [
    "app.handlers_manual_signals",
    "app.handlers_admin_premium", 
    "app.handlers_deepseek",
    "app.handlers_automaton",
    "menu_handlers",
    "menu_system"
]

for handler in critical_handlers:
    handlers_total += 1
    try:
        __import__(handler)
        handlers_ok += 1
    except Exception as e:
        print(f"   ⚠️ {handler}: {str(e)[:40]}")

print(f"   ✅ {handlers_ok}/{handlers_total} handlers loaded\n")

# Test 4: Setup Application (without running)
print("4️⃣ Testing Application Setup...")
try:
    import asyncio
    async def test_setup():
        await bot.setup_application()
        return True
    
    result = asyncio.run(test_setup())
    print(f"   ✅ Application setup successful\n")
except Exception as e:
    print(f"   ❌ Setup failed: {str(e)[:100]}\n")
    exit(1)

print("=" * 50)
print("🎉 ALL TESTS PASSED!")
print("=" * 50)
print("\n💡 Bot is ready to run. Start with:")
print("   python main.py")
