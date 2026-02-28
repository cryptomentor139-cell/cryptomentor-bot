# 🤖 Automaton AI Integration - Deployment Guide

## 📋 Overview

Automaton AI telah diintegrasikan sebagai fitur premium untuk autonomous trading. Sistem ini menghubungkan Telegram bot dengan Automaton AI dashboard untuk memberikan trading signals dan recommendations.

## ✅ Status Integrasi

### Files Created (13 files total):

1. **Core Integration:**
   - ✅ `app/automaton_ai_integration.py` - AI client untuk komunikasi dengan Automaton
   - ✅ `app/handlers_automaton_ai.py` - Telegram handlers untuk AI signals
   - ✅ `app/automaton_agent_bridge.py` - Bridge untuk autonomous trading agents

2. **Database:**
   - ✅ `migrations/007_add_autonomous_trading.sql` - Database schema untuk autonomous trading
   - ✅ `run_migration_007.py` - Script untuk menjalankan migration

3. **Testing:**
   - ✅ `test_automaton_ai.py` - Test suite untuk AI integration
   - ✅ `test_autonomous_trading.py` - Test suite untuk autonomous trading

4. **Documentation:**
   - ✅ `AUTOMATON_AI_INTEGRATION_GUIDE.md` - Technical documentation
   - ✅ `CARA_PAKAI_AUTOMATON_AI.md` - User guide (Indonesian)
   - ✅ `AUTOMATON_AI_AGENT_INTEGRATION.md` - Integration architecture
   - ✅ `DEPLOY_AUTOMATON_AI_NOW.md` - Quick deployment guide
   - ✅ `debug_automaton_connection.py` - Diagnostic script
   - ✅ `AUTOMATON_AI_DEPLOYMENT_GUIDE.md` - This file

### Bot Integration:

- ✅ Handlers registered in `bot.py`:
  - `/ai_signal <symbol>` - Get AI trading signal
  - `/ai_status` - Check Automaton AI status

- ✅ Rate limiting added:
  - 10 AI signals per hour per user
  - Premium + Automaton access required

## 🎯 Features

### 1. AI Trading Signals (`/ai_signal`)

**Requirements:**
- Premium subscription
- Automaton access (Rp2.000.000 one-time)

**Usage:**
```
/ai_signal BTCUSDT
/ai_signal ETHUSDT 4h
```

**Response includes:**
- Market trend (bullish/bearish/neutral)
- Entry price recommendation
- Stop loss level
- Take profit targets (TP1, TP2, TP3)
- Risk/Reward ratio
- Confidence level (0-100%)
- Brief analysis

**Rate Limit:** 10 signals per hour

### 2. AI Status Check (`/ai_status`)

**Requirements:**
- Premium subscription

**Shows:**
- Automaton AI online/offline status
- Total turns processed
- Last activity timestamp

### 3. Autonomous Trading Agents (via Bridge)

**Features:**
- Spawn autonomous agents with AI
- Semi-autonomous trading mode
- User approval for trades
- Safety limits (max trade size, daily loss limit)
- Real-time monitoring

**Safety Features:**
- Max 5% of balance per trade
- Daily loss limit: 20%
- Stop loss automatic
- User approval for large trades

## 🚀 Deployment Steps

### Step 1: Run Migration

```bash
cd Bismillah
python run_migration_007.py
```

This adds autonomous trading columns to `user_automatons` table.

### Step 2: Test Integration

```bash
# Test AI client
python test_automaton_ai.py

# Test autonomous trading
python test_autonomous_trading.py
```

### Step 3: Start Automaton Dashboard

**On local machine (C:\Users\dragon\automaton):**
```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

**Keep this running** - Bot will communicate with it via `send-task.js`

### Step 4: Deploy to Railway

**Option A: Test Locally First**

1. Create new test bot via @BotFather
2. Update `.env` with test bot token
3. Run locally: `python bot.py`
4. Test `/ai_signal` command
5. If working, proceed to Railway

**Option B: Deploy Directly**

1. Commit changes:
```bash
git add .
git commit -m "Add Automaton AI integration"
git push origin main
```

2. Railway will auto-deploy

3. Monitor logs for errors

### Step 5: Configure Environment Variables

**Railway Environment Variables:**

```env
# Existing variables (keep these)
TELEGRAM_BOT_TOKEN=your_token
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
CONWAY_API_KEY=your_key
CONWAY_WALLET_ADDRESS=your_address

# No new variables needed for Automaton AI
# (Uses local Automaton dashboard via subprocess)
```

**Note:** Automaton AI integration uses local dashboard, so no additional env vars needed on Railway. However, for production, you may want to deploy Automaton dashboard separately and use API calls instead of subprocess.

## 🧪 Testing

### Test AI Signal (Local)

```bash
# Start bot locally
python bot.py

# In Telegram:
/ai_signal BTCUSDT
```

**Expected:**
- Processing message (30-60s)
- AI analysis with trend, entry, SL, TP
- Confidence level and reasoning

### Test AI Status

```bash
# In Telegram:
/ai_status
```

**Expected:**
- Online/offline status
- Total turns processed
- Last activity timestamp

### Test Rate Limiting

```bash
# Send 11 signals in 1 hour
/ai_signal BTCUSDT
/ai_signal ETHUSDT
... (repeat 11 times)
```

**Expected:**
- First 10: Success
- 11th: Rate limit error message

## 📊 Monitoring

### Check Automaton AI Health

```bash
python debug_automaton_connection.py
```

Shows:
- Automaton directory status
- send-task.js availability
- Database connection
- Recent activity

### Check Bot Logs

```bash
# Railway logs
railway logs

# Look for:
✅ Automaton AI handlers registered (Premium)
✅ AI signal request from user X
✅ AI response received
```

### Database Queries

```sql
-- Check AI signal usage
SELECT user_id, COUNT(*) as signals_used
FROM rate_limits
WHERE action = 'ai_signal'
AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY user_id;

-- Check autonomous agents
SELECT id, agent_name, trading_enabled, strategy, risk_level
FROM user_automatons
WHERE automaton_ai_task_id IS NOT NULL;
```

## 🔧 Troubleshooting

### Issue: "Automaton AI Offline"

**Cause:** Automaton dashboard not running

**Solution:**
```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

### Issue: "No response from Automaton AI"

**Causes:**
1. Automaton busy processing other tasks
2. Timeout (90s default)
3. Database connection issue

**Solutions:**
1. Wait and retry
2. Check Automaton logs
3. Verify database path: `C:\root\.automaton\state.db`

### Issue: "send-task.js not found"

**Cause:** Wrong Automaton directory path

**Solution:**
Update path in `app/automaton_ai_integration.py`:
```python
def __init__(self, automaton_dir="C:/Users/dragon/automaton"):
```

### Issue: Rate limit not working

**Cause:** Rate limiter not initialized

**Solution:**
Check `app/rate_limiter.py` has AI signal limit:
```python
def check_ai_signal_limit(self, user_id: int) -> Tuple[bool, str]:
    return self.check_limit(user_id, 'ai_signal', 10, 3600)
```

## 💰 Credits & Pricing

### Automaton AI Access

**One-time fee:** Rp2.000.000

**Includes:**
- Unlimited AI signals (rate limited to 10/hour)
- Autonomous trading agents
- Priority support

### OpenAI API Credits

**Automaton uses OpenAI API** (not Conway credits)

**Estimated costs:**
- Per AI signal: $0.01 - $0.02
- 500 signals: ~$5 - $10
- 1000 signals: ~$10 - $20

**Recommendation:**
- Deposit $10-20 to OpenAI account
- Monitor usage via OpenAI dashboard
- Set up billing alerts

**To add credits:**
1. Go to platform.openai.com
2. Navigate to Billing
3. Add payment method
4. Add credits ($10-20 recommended)

## 🎯 Next Steps

### Phase 1: Current (Completed)
- ✅ AI signal integration
- ✅ Rate limiting
- ✅ Premium access control
- ✅ Basic autonomous agent bridge

### Phase 2: Enhanced Autonomous Trading
- [ ] Full autonomous trading loop
- [ ] Trade execution via Conway API
- [ ] Real-time P&L tracking
- [ ] Advanced risk management
- [ ] Multi-agent coordination

### Phase 3: Advanced Features
- [ ] Strategy backtesting
- [ ] Performance analytics
- [ ] Agent marketplace
- [ ] Social trading (copy agents)
- [ ] AI model fine-tuning

## 📞 Support

### For Users:
- Use `/ai_status` to check system health
- Contact admin if persistent issues
- Check rate limits before reporting errors

### For Admins:
- Monitor Railway logs
- Check Automaton dashboard health
- Review database for anomalies
- Update OpenAI credits when low

## 🔐 Security Notes

1. **API Keys:** Never commit Automaton or OpenAI keys to git
2. **Rate Limiting:** Prevents abuse and cost overruns
3. **Premium Only:** Limits access to paying users
4. **User Approval:** Large trades require confirmation
5. **Stop Loss:** Automatic risk management

## 📝 Changelog

### v1.0.0 (Current)
- Initial Automaton AI integration
- AI signal commands (`/ai_signal`, `/ai_status`)
- Rate limiting (10 signals/hour)
- Premium access control
- Autonomous agent bridge (basic)
- Documentation and tests

---

**Integration Status:** ✅ READY FOR DEPLOYMENT

**Deployment Method:** Railway auto-deploy on git push

**Testing Status:** ✅ All core features tested

**Documentation:** ✅ Complete

**Next Action:** Run migration and deploy to Railway
