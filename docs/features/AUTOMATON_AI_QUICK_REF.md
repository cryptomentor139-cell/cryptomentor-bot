# 🤖 Automaton AI - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Start Automaton
```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

### 2. Start Bot
```bash
cd C:\V3-Final-Version\Bismillah
python bot.py
```

### 3. Test
```
/ai_status
/ai_signal BTCUSDT
```

## 📱 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/ai_signal <symbol> [tf]` | Get AI signal | `/ai_signal BTCUSDT 1h` |
| `/ai_status` | Check AI status | `/ai_status` |

## ⏱️ Timeframes

| Code | Timeframe |
|------|-----------|
| `1m` | 1 minute |
| `5m` | 5 minutes |
| `15m` | 15 minutes |
| `1h` | 1 hour (default) |
| `4h` | 4 hours |
| `1d` | 1 day |

## 🔐 Requirements

- ✅ Premium subscription
- ✅ Automaton access (Rp2.000.000)
- ✅ Rate limit: 10/hour

## 📂 Files

```
app/
├── automaton_ai_integration.py  # AI client
├── handlers_automaton_ai.py     # Handlers
└── rate_limiter.py              # Rate limit

bot.py                           # Updated
test_automaton_ai.py             # Tests
```

## 🐛 Quick Fixes

| Error | Fix |
|-------|-----|
| "AI Offline" | Start Automaton dashboard |
| "send-task.js not found" | Check file exists |
| "Timeout" | Increase timeout / check logs |
| "Rate limit" | Wait 1 hour |

## 📊 Response Format

```
🤖 AI Trading Signal

📊 Symbol: BTCUSDT
⏰ Timeframe: 1h

🟢 Trend: BULLISH
💰 Entry: 45,250
🛑 Stop Loss: 44,800
🎯 Take Profit:
   TP1: 45,800
   TP2: 46,200
   TP3: 46,800
📈 Risk/Reward: 1:3.2
🎲 Confidence: 85%
```

## 🧪 Test Commands

```bash
# Run tests
python test_automaton_ai.py

# Check AI status
/ai_status

# Get signal
/ai_signal BTCUSDT

# Test rate limit (send 11x)
/ai_signal BTCUSDT
```

## 📖 Full Docs

- **User Guide:** `CARA_PAKAI_AUTOMATON_AI.md`
- **Tech Docs:** `AUTOMATON_AI_INTEGRATION_GUIDE.md`
- **Deploy:** `DEPLOY_AUTOMATON_AI_NOW.md`
- **Summary:** `AUTOMATON_AI_SUMMARY.md`

## ✅ Checklist

- [ ] Automaton running
- [ ] Bot running
- [ ] Tests pass
- [ ] Commands work
- [ ] Rate limit works

---

**Quick Ref v1.0** | 2026-02-22
