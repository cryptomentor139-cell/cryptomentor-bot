# OpenClaw - OpenRouter Integration ✅

## Update Summary

OpenClaw sekarang **otomatis menggunakan OpenRouter** untuk Claude Sonnet 4! Tidak perlu API key terpisah dari Anthropic.

## ✨ Keuntungan

### 1. **Reuse Existing API Key**
- OpenClaw otomatis pakai `DEEPSEEK_API_KEY` yang sudah ada
- Tidak perlu beli API key Anthropic terpisah
- Satu API key untuk semua AI models

### 2. **Automatic Detection**
```python
# OpenClaw akan otomatis detect:
if DEEPSEEK_API_KEY exists:
    → Use OpenRouter (Claude via OpenRouter)
elif ANTHROPIC_API_KEY exists:
    → Use Direct Anthropic API
else:
    → Error: No API key found
```

### 3. **Same Features**
- Seamless chat mode ✅
- Self-aware AI ✅
- Platform fee 20% ✅
- Token tracking ✅
- Semua fitur sama persis!

## 🚀 Setup (Super Simple!)

### Anda TIDAK Perlu Apa-apa!

Karena Anda sudah punya `DEEPSEEK_API_KEY` di `.env`, OpenClaw akan otomatis pakai itu untuk Claude.

```bash
# .env Anda saat ini:
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1

# OpenClaw akan otomatis pakai ini! ✅
```

### Langkah Setup:

1. **Run Migration** (one-time)
```bash
cd Bismillah
python3 -c "
from database import Database
db = Database()
with open('migrations/010_openclaw_claude_assistant.sql', 'r') as f:
    sql = f.read()
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        try:
            db.execute(stmt)
        except Exception as e:
            if 'already exists' not in str(e):
                print(f'Error: {e}')
    db.commit()
print('✅ Migration completed')
"
```

2. **Restart Bot**
```bash
python3 bot.py
```

3. **Test!**
```
/openclaw_create MyBot friendly
/openclaw_start
Hello, can you help me?
```

## 🔧 Technical Changes

### Modified Files:

**Bismillah/app/openclaw_manager.py**
```python
# Before: Only Anthropic direct API
self.client = anthropic.Anthropic(api_key=api_key)

# After: Auto-detect OpenRouter or Anthropic
if openrouter_key:
    self.use_openrouter = True
    self.api_key = openrouter_key
    self.base_url = 'https://openrouter.ai/api/v1'
elif anthropic_key:
    self.use_openrouter = False
    self.client = anthropic.Anthropic(api_key=anthropic_key)
```

**API Call:**
```python
# OpenRouter API
if self.use_openrouter:
    response = requests.post(
        f"{self.base_url}/chat/completions",
        headers={'Authorization': f'Bearer {self.api_key}'},
        json={
            'model': 'anthropic/claude-sonnet-4',
            'messages': messages,
            'max_tokens': 8192
        }
    )
    
# Direct Anthropic API
else:
    response = self.client.messages.create(
        model='claude-sonnet-4-20250514',
        messages=messages
    )
```

## 💰 Pricing via OpenRouter

### Claude Sonnet 4 via OpenRouter:
- Input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens
- Same as direct Anthropic!

### Your Platform Fee Model:
```
100 USDC Purchase:
├─ 20 USDC (20%) → Your Profit
└─ 80 USDC (80%) → Claude API + Server
    ├─ ~60 USDC → Claude via OpenRouter
    └─ ~20 USDC → Railway server
```

## ✅ Benefits of OpenRouter

1. **Single API Key** - Satu key untuk semua models
2. **Fallback Options** - Bisa switch model kalau Claude down
3. **Cost Tracking** - OpenRouter dashboard untuk monitoring
4. **Rate Limits** - Lebih generous dari direct API
5. **No Separate Billing** - Semua dalam satu invoice

## 🧪 Testing

### Test OpenRouter Connection:
```python
import requests

headers = {
    'Authorization': 'Bearer sk-or-v1-your-key',
    'Content-Type': 'application/json'
}

response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    json={
        'model': 'anthropic/claude-sonnet-4',
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'max_tokens': 100
    }
)

print(response.json())
```

### Test OpenClaw Manager:
```python
from database import Database
from app.openclaw_manager import get_openclaw_manager

db = Database()
manager = get_openclaw_manager(db)

print(f"Using OpenRouter: {manager.use_openrouter}")
print(f"Model: {manager.MODEL}")

# Should print:
# Using OpenRouter: True
# Model: anthropic/claude-sonnet-4
```

## 📊 Comparison

### Before (Direct Anthropic):
```
❌ Need separate ANTHROPIC_API_KEY
❌ Separate billing
❌ Separate rate limits
❌ Only Claude models
```

### After (OpenRouter):
```
✅ Use existing DEEPSEEK_API_KEY
✅ Single billing
✅ Combined rate limits
✅ Access to all models (Claude, GPT, Gemini, etc)
✅ Fallback options
```

## 🎯 Next Steps

1. ✅ OpenRouter integration complete
2. 🔄 Run database migration
3. 🔄 Restart bot
4. 🔄 Test with `/openclaw_start`
5. 🔄 Monitor OpenRouter dashboard

## 💡 Pro Tips

### 1. Monitor Usage
Check OpenRouter dashboard:
- https://openrouter.ai/activity

### 2. Set Budget Limits
Prevent overspending:
- https://openrouter.ai/settings

### 3. Track Costs
```sql
-- Check platform revenue
SELECT SUM(amount_usdc) FROM platform_revenue WHERE source = 'openclaw_fee';

-- Check user spending
SELECT SUM(total_credits_spent) FROM openclaw_assistants;
```

## 🎉 Summary

OpenClaw sekarang **100% compatible dengan OpenRouter**!

✅ Tidak perlu API key terpisah
✅ Otomatis pakai DEEPSEEK_API_KEY yang ada
✅ Semua fitur tetap sama
✅ Setup super simple
✅ Ready to use!

**Tinggal run migration dan restart bot, langsung bisa pakai!** 🚀
