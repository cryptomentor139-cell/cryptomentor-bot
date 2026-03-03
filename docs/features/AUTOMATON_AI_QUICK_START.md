# 🚀 Automaton AI - Quick Start Guide

## ⚡ 3-Step Deployment

### 1️⃣ Run Migration (30 seconds)

```bash
cd Bismillah
python run_migration_007.py
```

**Expected output:**
```
✅ Migration 007 executed successfully!
📊 Changes:
  • Added automaton_ai_task_id column
  • Added trading_enabled column
  • Added strategy column
  ... (10 columns total)
```

### 2️⃣ Test Integration (2 minutes)

```bash
python test_automaton_ai.py
```

**Expected output:**
```
✅ PASSED - Initialize AI Client
✅ PASSED - Check AI Status
✅ PASSED - Get AI Signal (if Automaton running)
```

**If Automaton not running:**
```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

### 3️⃣ Deploy to Railway (5 minutes)

**Option A: Auto-deploy (Recommended)**
```bash
git add .
git commit -m "Add Automaton AI integration"
git push origin main
```

Railway will auto-deploy in ~3-5 minutes.

**Option B: Test locally first**
```bash
# Create test bot via @BotFather
# Update .env with test token
python bot.py

# Test in Telegram:
/ai_signal BTCUSDT
```

## 🎯 User Commands

### For Premium Users with Automaton Access:

```
/ai_signal BTCUSDT          → Get AI trading signal
/ai_signal ETHUSDT 4h       → Get signal for 4h timeframe
/ai_status                  → Check Automaton AI status
```

### Access Requirements:

1. **Premium subscription** (any tier)
2. **Automaton access** (Rp2.000.000 one-time)

### Rate Limits:

- 10 AI signals per hour per user
- Resets every hour

## 💡 Quick Troubleshooting

### "Automaton AI Offline"
```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

### "No response from Automaton AI"
- Wait 60 seconds and retry
- Check Automaton is running
- Verify database: `C:\root\.automaton\state.db`

### "Rate limit exceeded"
- Wait 1 hour for reset
- Or upgrade to higher tier (future feature)

## 📊 Monitoring

### Check System Health:
```bash
python debug_automaton_connection.py
```

### Check Railway Logs:
```bash
railway logs
```

Look for:
```
✅ Automaton AI handlers registered (Premium)
✅ AI signal request from user 123456
✅ AI response received in 45s
```

## 💰 OpenAI Credits

Automaton AI uses OpenAI API (not Conway credits).

**Recommended deposit:** $10-20 for 500-1000 signals

**To add credits:**
1. Go to platform.openai.com
2. Billing → Add credits
3. Deposit $10-20

**Cost per signal:** ~$0.01-0.02

## 🎉 Success Checklist

- [ ] Migration 007 completed
- [ ] Tests passing
- [ ] Automaton dashboard running
- [ ] Bot deployed to Railway
- [ ] `/ai_signal` command working
- [ ] Rate limiting working
- [ ] OpenAI credits added

## 📞 Need Help?

1. Check logs: `railway logs`
2. Run diagnostics: `python debug_automaton_connection.py`
3. Review full guide: `AUTOMATON_AI_DEPLOYMENT_GUIDE.md`
4. Contact admin if persistent issues

---

**Status:** ✅ Ready for deployment

**Time to deploy:** ~10 minutes total

**Next:** Run migration and push to Railway!
