# 🚀 Cerebras AI Setup - Ultra Fast LLM

## Mengapa Cerebras?

### ⚡ Kecepatan Luar Biasa
- **Cerebras**: < 1 detik response ✅
- **DeepSeek**: 10-30 detik response ❌
- **Improvement**: 10-30x lebih cepat!

### 💰 Pricing
- **Free Tier**: Tersedia untuk testing
- **Pay-as-you-go**: Sangat affordable
- **No monthly fee**: Bayar per request saja

### 🎯 Model Quality
- **Llama 3.1 70B**: Model powerful & accurate
- **OpenAI-compatible**: Mudah integrasi
- **Reliable**: Production-ready

## 📝 Step-by-Step Setup

### Step 1: Dapatkan API Key

1. **Buka Website Cerebras**
   ```
   https://cloud.cerebras.ai/
   ```

2. **Sign Up / Login**
   - Klik "Sign Up" atau "Get Started"
   - Daftar dengan email Anda
   - Verifikasi email

3. **Dapatkan API Key**
   - Login ke dashboard
   - Cari menu "API Keys" atau "Settings"
   - Klik "Create New API Key"
   - **COPY API KEY** (simpan baik-baik!)

### Step 2: Tambahkan ke .env File

Edit file `.env` di folder `Bismillah/`:

```bash
# Cerebras AI (Ultra Fast LLM)
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

**PENTING**: Ganti `your_cerebras_api_key_here` dengan API key Anda!

### Step 3: Install Dependencies

```bash
cd Bismillah
pip install openai python-dotenv
```

**Note**: Cerebras menggunakan OpenAI-compatible API, jadi kita pakai library `openai`.

### Step 4: Test API Key

```bash
python test_cerebras.py
```

**Expected Output**:
```
🧪 Testing Cerebras API...
============================================================

📊 Test 1: Simple Chat
------------------------------------------------------------
⏱️ Response time: 0.85 seconds
📝 Answer: Bitcoin is a decentralized digital currency...
✅ Status: FAST

📊 Test 2: Crypto Market Analysis
------------------------------------------------------------
⏱️ Response time: 0.92 seconds
📝 Analysis: Based on the data, BTC shows neutral momentum...
✅ Status: FAST

📊 Test 3: Speed Test (5 requests)
------------------------------------------------------------
Request 1: 0.78s
Request 2: 0.81s
Request 3: 0.85s
Request 4: 0.79s
Request 5: 0.83s

⏱️ Average response time: 0.81 seconds
✅ Status: EXCELLENT

============================================================
📊 SUMMARY
============================================================
✅ API Key: Valid
✅ Model: llama3.1-70b
✅ Average Speed: 0.81s
✅ Quality: Good (Llama 3.1 70B)

🎉 EXCELLENT! Cerebras is MUCH faster than DeepSeek!
💡 Recommended for production use
```

### Step 5: Integrate ke Bot

Setelah test berhasil, kita bisa integrate ke bot dengan 2 cara:

#### Option A: Replace DeepSeek dengan Cerebras

Edit `bot.py`:
```python
# BEFORE:
from deepseek_ai import DeepSeekAI
deepseek = DeepSeekAI()

# AFTER:
from cerebras_ai import CerebrasAI
cerebras = CerebrasAI()
```

#### Option B: Gunakan Cerebras untuk Futures Signals

Edit `futures_signal_generator.py`:
```python
# BEFORE:
self.ai = None  # AI DISABLED

# AFTER:
from cerebras_ai import CerebrasAI
self.ai = CerebrasAI()
```

## 🎯 Usage Examples

### Example 1: Market Analysis

```python
from cerebras_ai import cerebras_ai

# Analyze BTC
market_data = {
    'price': 68000,
    'change_24h': 2.5,
    'volume_24h': 25000000000
}

analysis = await cerebras_ai.analyze_market_simple(
    symbol='BTC',
    market_data=market_data,
    language='id'
)

print(analysis)
```

**Output** (< 1 second):
```
🤖 **AI Analysis: BTC**

📊 Kondisi Market:
Bitcoin saat ini berada di $68,000 dengan kenaikan 2.5% dalam 24 jam. 
Volume trading yang tinggi ($25B) menunjukkan aktivitas market yang sehat.

📈 Analisis Teknikal:
Momentum bullish terlihat dari price action positif. Volume tinggi 
mengkonfirmasi strength dari pergerakan ini.

💡 Rekomendasi:
Watch untuk breakout di atas resistance. Gunakan proper risk management 
dengan stop loss yang ketat.

━━━━━━━━━━━━━━━━━━━━━━
⚡ Powered by Cerebras AI (Llama 3.1 70B)
```

### Example 2: Chat with AI

```python
response = await cerebras_ai.chat_about_market(
    user_message="Apa itu support dan resistance?",
    language='id'
)

print(response)
```

**Output** (< 1 second):
```
📚 Support dan Resistance adalah konsep fundamental dalam trading:

🔵 **Support**: Level harga di mana buying pressure cukup kuat untuk 
mencegah harga turun lebih jauh. Seperti "lantai" yang menahan harga.

🔴 **Resistance**: Level harga di mana selling pressure cukup kuat untuk 
mencegah harga naik lebih tinggi. Seperti "langit-langit" yang membatasi harga.

💡 **Cara Gunakan**:
• Buy near support (risk lebih rendah)
• Sell near resistance (profit taking)
• Breakout = signal kuat untuk trend baru

⚠️ **Catatan**: Support bisa jadi resistance (dan sebaliknya) setelah breakout!

━━━━━━━━━━━━━━━━━━━━━━
⚡ Powered by Cerebras AI
```

## 📊 Performance Comparison

| Feature | DeepSeek | Cerebras | Improvement |
|---------|----------|----------|-------------|
| Response Time | 10-30s | < 1s | **10-30x faster** ✅ |
| Model Quality | Good | Excellent | Better ✅ |
| Reliability | Medium | High | More stable ✅ |
| Cost | Free | Free tier + paid | Affordable ✅ |
| User Experience | Poor (slow) | Excellent (fast) | Much better ✅ |

## 🔧 Troubleshooting

### Error: "API key not found"
**Solution**:
1. Check `.env` file has `CEREBRAS_API_KEY=...`
2. Restart bot after adding API key
3. Make sure no typos in API key

### Error: "Connection timeout"
**Solution**:
1. Check internet connection
2. Check Cerebras service status
3. Try again in a few minutes

### Error: "Rate limit exceeded"
**Solution**:
1. You're making too many requests
2. Wait a few minutes
3. Consider upgrading to paid tier

### Slow Response (> 2 seconds)
**Possible Causes**:
1. Network latency
2. Server load (peak hours)
3. Large prompt (reduce token count)

**Solution**:
- Reduce `max_tokens` in API call
- Optimize prompt length
- Check network speed

## 💡 Best Practices

### 1. Keep Prompts Concise
```python
# BAD (too long):
prompt = "Please analyze this market in great detail with all possible indicators..."

# GOOD (concise):
prompt = "Analyze BTC: Price $68k, RSI 55, Volume high. Market bias?"
```

### 2. Use Appropriate max_tokens
```python
# For quick analysis:
max_tokens=200  # Fast, concise

# For detailed explanation:
max_tokens=400  # More detailed

# Avoid:
max_tokens=2000  # Too slow, unnecessary
```

### 3. Handle Errors Gracefully
```python
try:
    response = await cerebras_ai.analyze_market_simple(...)
except Exception as e:
    # Fallback to technical analysis only
    response = generate_technical_analysis_only(...)
```

### 4. Cache Responses (Optional)
```python
# Cache for 5 minutes to reduce API calls
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_analysis(symbol, timestamp_5min):
    # timestamp_5min = int(time.time() / 300)
    return cerebras_ai.analyze_market_simple(symbol, ...)
```

## 🚀 Next Steps

1. ✅ Get Cerebras API key
2. ✅ Add to `.env` file
3. ✅ Test with `test_cerebras.py`
4. ✅ Integrate to bot
5. ✅ Deploy to Railway
6. ✅ Monitor performance

## 📞 Support

**Cerebras Documentation**:
- https://docs.cerebras.ai/

**API Reference**:
- https://docs.cerebras.ai/api-reference

**Community**:
- Discord: https://discord.gg/cerebras

---

**Status**: ✅ READY TO USE  
**Recommended**: YES (10-30x faster than DeepSeek)  
**Cost**: Free tier available, very affordable paid tier
