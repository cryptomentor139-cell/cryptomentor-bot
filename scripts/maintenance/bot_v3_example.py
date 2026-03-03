"""
Contoh Integration Automaton AI ke Bot V3
Copy code ini ke handler bot V3 kamu
"""

# Import Automaton client
from automaton_bot_client import AutomatonBotClient

# Initialize client (sekali saja di awal)
automaton = AutomatonBotClient()

# ===== CONTOH 1: Handler untuk /ai_signal =====

def handle_ai_signal(message):
    """
    Handler untuk command /ai_signal BTCUSDT
    Bisa dipanggil dari bot handler kamu
    """
    # Parse symbol dari message
    try:
        symbol = message.text.split()[1].upper()
    except:
        return "Cara pakai: /ai_signal BTCUSDT"
    
    # Check premium user (sesuaikan dengan sistem bot kamu)
    user_id = message.from_user.id
    if not is_premium_user(user_id):
        return "🔒 Fitur Premium! Upgrade untuk akses AI signals."
    
    # Send "analyzing" message
    bot.send_message(message.chat.id, f"🤖 AI sedang menganalisis {symbol}...")
    
    # Get AI signal
    result = automaton.get_ai_signal(symbol, timeout=90)
    
    if result['success']:
        # Send AI response
        response = f"🤖 AI Analysis: {symbol}\n\n{result['signal']}\n\n⚠️ AI-generated. DYOR!"
        bot.send_message(message.chat.id, response)
    else:
        # Send error
        bot.send_message(message.chat.id, f"❌ {result['error']}")


# ===== CONTOH 2: Handler untuk /ai_ask =====

def handle_ai_ask(message):
    """
    Handler untuk command /ai_ask <pertanyaan>
    """
    # Parse question
    question = message.text.replace('/ai_ask', '').strip()
    if not question:
        return "Cara pakai: /ai_ask <pertanyaan>"
    
    # Check premium
    if not is_premium_user(message.from_user.id):
        return "🔒 Fitur Premium!"
    
    # Send thinking message
    bot.send_message(message.chat.id, "🤖 AI sedang berpikir...")
    
    # Ask AI
    result = automaton.ask_ai(question, timeout=60)
    
    if result['success']:
        bot.send_message(message.chat.id, f"🤖 {result['signal']}")
    else:
        bot.send_message(message.chat.id, f"❌ {result['error']}")


# ===== CONTOH 3: Check Automaton Status =====

def check_ai_status():
    """
    Check apakah Automaton online
    Bisa dipanggil untuk health check
    """
    status = automaton.check_status()
    
    if status['online']:
        return f"✅ AI Online\nTotal analyses: {status['total_turns']}"
    else:
        return "❌ AI Offline"


# ===== CONTOH 4: Integration ke Bot Existing =====

# Jika pakai python-telegram-bot:
from telegram.ext import CommandHandler

def setup_ai_handlers(application):
    """Add AI handlers ke bot"""
    application.add_handler(CommandHandler("ai_signal", handle_ai_signal))
    application.add_handler(CommandHandler("ai_ask", handle_ai_ask))

# Jika pakai telebot:
@bot.message_handler(commands=['ai_signal'])
def ai_signal_command(message):
    handle_ai_signal(message)

@bot.message_handler(commands=['ai_ask'])
def ai_ask_command(message):
    handle_ai_ask(message)


# ===== HELPER FUNCTIONS =====

def is_premium_user(user_id):
    """
    Check premium status
    Sesuaikan dengan database/sistem bot kamu
    """
    # Contoh: hardcoded list
    PREMIUM_USERS = [123456789, 987654321]
    return user_id in PREMIUM_USERS
    
    # Atau dari database:
    # return db.check_premium(user_id)


# ===== USAGE EXAMPLE =====

if __name__ == "__main__":
    print("Contoh cara pakai di bot V3:")
    print("\n1. Import:")
    print("   from automaton_bot_client import AutomatonBotClient")
    print("   automaton = AutomatonBotClient()")
    
    print("\n2. Di handler bot:")
    print("   result = automaton.get_ai_signal('BTCUSDT')")
    print("   if result['success']:")
    print("       bot.send_message(chat_id, result['signal'])")
    
    print("\n3. Test:")
    automaton = AutomatonBotClient()
    status = automaton.check_status()
    print(f"   AI Status: {'Online' if status['online'] else 'Offline'}")
