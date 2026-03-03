# OpenClaw Quick Start Guide

## Setup

### 1. Add API Key to .env
```bash
# Option 1: Use OpenRouter (Recommended - you already have this!)
# OpenClaw will automatically use your existing DEEPSEEK_API_KEY
DEEPSEEK_API_KEY=sk-or-v1-your-openrouter-key
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1

# Option 2: Use Direct Anthropic API (Optional)
# Get API key from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# OpenClaw Configuration (optional, defaults are fine)
OPENCLAW_PLATFORM_FEE=0.20
OPENCLAW_USDC_TO_CREDITS=100
```

**Note:** OpenClaw will automatically detect and use OpenRouter if `DEEPSEEK_API_KEY` is available. No need for separate Anthropic API key!

### 2. Run Database Migration
```bash
cd Bismillah
python3 -c "
from database import Database
db = Database()
with open('migrations/010_openclaw_claude_assistant.sql', 'r') as f:
    sql = f.read()
    db.execute_script(sql)
print('✅ Migration completed')
"
```

### 3. Test OpenClaw Manager
```python
from database import Database
from app.openclaw_manager import get_openclaw_manager

db = Database()
manager = get_openclaw_manager(db)

# Test 1: Create assistant
assistant = manager.create_assistant(
    user_id=123456789,
    name="TestBot",
    personality="friendly"
)
print(f"✅ Assistant created: {assistant['assistant_id']}")

# Test 2: Purchase credits (simulate)
result = manager.purchase_credits(
    user_id=123456789,
    amount_usdc=100.0
)
print(f"✅ Credits purchased: {result['credits']} credits")
print(f"   Platform fee: {result['platform_fee']} USDC")

# Test 3: Check balance
credits = manager.get_user_credits(123456789)
print(f"✅ Balance: {credits} credits")
```

## User Flow Testing

### 1. Create AI Assistant
```
User: /openclaw_create Alex friendly
Bot: ✅ AI Assistant Created!
     🤖 Name: Alex
     🎭 Personality: friendly
     🆔 ID: OCAI-123456789-abc123
     
     💬 Start chatting: /openclaw_start
     💰 Buy credits: /openclaw_buy
```

### 2. Purchase Credits
```
User: /openclaw_buy
Bot: [Shows purchase options with platform fee breakdown]

User: [Clicks "100 USDC (8,000 credits)"]
Bot: 💰 Purchase Summary
     Amount: 100 USDC
     Platform Fee (20%): 20 USDC
     Net Amount: 80 USDC
     Credits: 8,000 credits
     
     📍 Deposit Address: 0x...
     Network: Base (USDC)
```

### 3. Activate OpenClaw Mode
```
User: /openclaw_start
Bot: ✅ OpenClaw Mode Activated
     🤖 Assistant: Alex
     💰 Credits: 8,000
     
     💬 You can now chat freely!
     Just type your message - no commands needed.
```

### 4. Chat Freely (No Commands!)
```
User: Explain quantum computing in simple terms
Bot: [AI Response from Claude Sonnet 4.5]
     
     💬 1,234 tokens • 💰 15 credits • Balance: 7,985
```

```
User: What are the practical applications?
Bot: [AI Response continues conversation with context]
     
     💬 987 tokens • 💰 12 credits • Balance: 7,973
```

### 5. Check Balance
```
User: /openclaw_balance
Bot: 💰 OpenClaw Credit Balance
     👤 User: John
     🆔 ID: 123456789
     
     💳 Credits: 7,973
     🤖 Assistants: 1
     📊 Total Tokens Used: 2,221
     💸 Total Spent: 27 credits
```

### 6. View History
```
User: /openclaw_history
Bot: 📚 Recent Conversations
     
     1. 🤖 Alex
        💬 2 messages • 💰 27 credits
        🕐 2026-03-03 10:30
```

### 7. Exit Mode
```
User: /openclaw_exit
Bot: 👋 OpenClaw Mode Deactivated
     You can now use regular bot commands.
     
     🔄 Reactivate: /openclaw_start
```

## Testing Checklist

### Basic Functionality
- [ ] Create AI Assistant
- [ ] Purchase credits (simulate)
- [ ] Activate OpenClaw mode
- [ ] Send message (seamless chat)
- [ ] Receive AI response
- [ ] Credits deducted correctly
- [ ] Check balance
- [ ] View history
- [ ] Exit mode

### Credit System
- [ ] Platform fee calculated correctly (20%)
- [ ] Net credits calculated correctly (80%)
- [ ] Credits deducted per message
- [ ] Token usage tracked
- [ ] Balance updated in real-time
- [ ] Insufficient credits handled

### AI Assistant
- [ ] Claude API responds
- [ ] Self-aware system prompt works
- [ ] Context maintained across messages
- [ ] Personality reflected in responses
- [ ] Token counting accurate

### Database
- [ ] Assistants table populated
- [ ] Conversations table populated
- [ ] Messages table populated
- [ ] Credit transactions recorded
- [ ] Platform revenue tracked
- [ ] User credits balance updated

### Security
- [ ] Rate limiting works
- [ ] Content filtering active
- [ ] Data isolation verified
- [ ] Audit logging working

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"
```bash
# Option 1: Use OpenRouter (you already have this!)
# OpenClaw will use your existing DEEPSEEK_API_KEY
# No action needed if DEEPSEEK_API_KEY is already in .env

# Option 2: Add direct Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Error: "Insufficient credits"
```python
# Manually add credits for testing
from database import Database
db = Database()
db.execute("SELECT add_openclaw_credits(?, ?)", (user_id, 100.0))
```

### Error: "Assistant not found"
```python
# Check assistants
from database import Database
from app.openclaw_manager import get_openclaw_manager

db = Database()
manager = get_openclaw_manager(db)
assistants = manager.get_user_assistants(user_id)
print(assistants)
```

### Error: "Claude API timeout"
```python
# Test OpenRouter connection
import requests

headers = {
    'Authorization': f'Bearer {your_openrouter_key}',
    'Content-Type': 'application/json'
}

payload = {
    'model': 'anthropic/claude-sonnet-4',
    'messages': [{'role': 'user', 'content': 'Hello'}],
    'max_tokens': 100
}

response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    json=payload
)
print(response.json())
```

## Admin Testing

### Check Platform Revenue
```sql
SELECT * FROM platform_revenue WHERE source = 'openclaw_fee';
```

### Check User Credits
```sql
SELECT * FROM openclaw_user_credits;
```

### Check Transactions
```sql
SELECT * FROM openclaw_credit_transactions ORDER BY created_at DESC LIMIT 10;
```

### Check Usage Stats
```sql
SELECT * FROM openclaw_usage_stats ORDER BY date DESC LIMIT 7;
```

## Performance Testing

### Test Response Time
```python
import time
from database import Database
from app.openclaw_manager import get_openclaw_manager

db = Database()
manager = get_openclaw_manager(db)

start = time.time()
response, input_tokens, output_tokens, credits = manager.chat(
    user_id=123456789,
    assistant_id="OCAI-123456789-abc123",
    message="Hello, how are you?",
    conversation_id=None
)
elapsed = time.time() - start

print(f"Response time: {elapsed:.2f}s")
print(f"Tokens: {input_tokens + output_tokens}")
print(f"Credits: {credits}")
```

### Test Concurrent Users
```python
import asyncio
from database import Database
from app.openclaw_manager import get_openclaw_manager

async def test_user(user_id):
    db = Database()
    manager = get_openclaw_manager(db)
    
    # Create assistant
    assistant = manager.create_assistant(user_id, f"Bot{user_id}", "friendly")
    
    # Purchase credits
    manager.purchase_credits(user_id, 10.0)
    
    # Chat
    response, _, _, _ = manager.chat(
        user_id, assistant['assistant_id'], "Hello", None
    )
    
    print(f"User {user_id}: OK")

async def main():
    tasks = [test_user(i) for i in range(1, 11)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## Next Steps

1. ✅ Setup complete
2. ✅ Database migrated
3. ✅ Basic testing done
4. 🔄 Deploy to Railway
5. 🔄 Monitor production
6. 🔄 Gather user feedback
7. 🔄 Optimize performance

## Support

For issues or questions:
- Check logs: `tail -f bot.log`
- Check database: `sqlite3 cryptomentor.db`
- Contact admin: @your_admin_username
