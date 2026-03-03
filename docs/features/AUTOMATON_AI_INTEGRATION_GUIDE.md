# 🤖 Automaton AI Integration Guide

## Overview

Automaton AI adalah fitur premium yang mengintegrasikan bot Telegram dengan Automaton AI dashboard untuk memberikan trading signals yang dianalisis oleh AI.

## ✅ Status Integration

- ✅ `automaton_ai_integration.py` - Client untuk komunikasi dengan Automaton
- ✅ `handlers_automaton_ai.py` - Telegram bot handlers
- ✅ Rate limiter untuk AI signals (10 requests/hour)
- ✅ Premium & Automaton access check
- ✅ Integration dengan bot.py
- ✅ Test suite

## 📋 Prerequisites

### 1. Automaton Dashboard Running

Automaton dashboard harus running di terminal terpisah:

```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

### 2. File Requirements

- `C:\Users\dragon\automaton\send-task.js` - Script untuk send task
- `C:\root\.automaton\state.db` - Automaton database

### 3. User Requirements

User harus memiliki:
- ✅ Premium subscription
- ✅ Automaton access (Rp2.000.000 one-time fee)

## 🎯 Features

### 1. AI Signal Command

**Command:** `/ai_signal <symbol> [timeframe]`

**Examples:**
```
/ai_signal BTCUSDT
/ai_signal ETHUSDT 4h
/ai_signal BNBUSDT 1d
```

**Response includes:**
- 📊 Market trend (bullish/bearish/neutral)
- 💰 Entry price recommendation
- 🛑 Stop loss level
- 🎯 Take profit targets (3 levels)
- 📈 Risk/reward ratio
- 🎲 Confidence level (0-100%)
- 📝 Technical analysis

**Rate Limit:** 10 signals per hour per user

### 2. AI Status Command

**Command:** `/ai_status`

**Shows:**
- AI online/offline status
- Total turns processed
- Last activity timestamp

## 🔧 Technical Architecture

### File Structure

```
Bismillah/
├── app/
│   ├── automaton_ai_integration.py  # AI client
│   ├── handlers_automaton_ai.py     # Bot handlers
│   └── rate_limiter.py              # Rate limiting (updated)
├── bot.py                           # Main bot (updated)
└── test_automaton_ai.py             # Test suite
```

### Integration Flow

```
User sends /ai_signal BTCUSDT
    ↓
Premium & Automaton access check
    ↓
Rate limit check (10/hour)
    ↓
AutomatonAIClient.get_ai_signal()
    ↓
subprocess.run(['node', 'send-task.js', task])
    ↓
Wait for response from Automaton DB
    ↓
Parse AI response
    ↓
Format & send to user
```

### Communication Method

Uses `send-task.js` via subprocess (proven working):

```python
subprocess.run(
    ['node', 'send-task.js', task_content],
    cwd=automaton_dir,
    capture_output=True,
    text=True,
    timeout=10
)
```

Response polling from SQLite database:

```python
# Check inbox_messages for processed_at
# Get response from turns table
SELECT thinking FROM turns 
WHERE timestamp > (SELECT received_at FROM inbox_messages WHERE id = ?)
ORDER BY timestamp DESC LIMIT 1
```

## 🚀 Deployment Steps

### Step 1: Verify Files

```bash
# Check if files exist
ls Bismillah/app/automaton_ai_integration.py
ls Bismillah/app/handlers_automaton_ai.py
ls Bismillah/test_automaton_ai.py
```

### Step 2: Start Automaton Dashboard

```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

Keep this terminal running!

### Step 3: Test Integration

```bash
cd Bismillah
python test_automaton_ai.py
```

Expected output:
```
✅ AI client initialized successfully
✅ AI status check successful
✅ AI signal received successfully
```

### Step 4: Start Bot

```bash
cd Bismillah
python bot.py
```

### Step 5: Test Commands

In Telegram:

1. Check AI status:
   ```
   /ai_status
   ```

2. Get AI signal:
   ```
   /ai_signal BTCUSDT
   ```

## 🧪 Testing

### Run Test Suite

```bash
cd Bismillah
python test_automaton_ai.py
```

### Manual Testing

1. **Test AI Status:**
   ```
   /ai_status
   ```
   Expected: Shows online status with turn count

2. **Test AI Signal (Premium User):**
   ```
   /ai_signal BTCUSDT
   ```
   Expected: Returns AI analysis with entry/SL/TP

3. **Test Rate Limit:**
   Send 11 `/ai_signal` commands in 1 hour
   Expected: 11th request shows rate limit error

4. **Test Non-Premium User:**
   Use non-premium account
   Expected: "Premium Required" message

5. **Test Without Automaton Access:**
   Use premium user without Automaton access
   Expected: "Automaton Access Required" message

## 📊 Rate Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| AI Signal | 10 requests | 1 hour |
| Agent Spawn | 1 request | 1 hour |
| Withdrawal | 3 requests | 24 hours |

## 🔐 Security

### Access Control

1. **Premium Check:**
   ```python
   if not db.is_user_premium(user_id):
       return "Premium Required"
   ```

2. **Automaton Access Check:**
   ```python
   if not db.has_automaton_access(user_id):
       return "Automaton Access Required"
   ```

3. **Rate Limiting:**
   ```python
   allowed, error_msg = rate_limiter.check_ai_signal_limit(user_id)
   if not allowed:
       return error_msg
   ```

### Activity Logging

All AI signal requests are logged:

```python
db.log_user_activity(
    user_id,
    'ai_signal_requested',
    f'AI signal for {symbol} ({timeframe})'
)
```

## 🐛 Troubleshooting

### Issue 1: "Automaton AI Offline"

**Cause:** Automaton dashboard not running

**Solution:**
```bash
cd C:\Users\dragon\automaton
node dist/index.js --run
```

### Issue 2: "send-task.js not found"

**Cause:** Missing send-task.js file

**Solution:**
```bash
# Check if file exists
ls C:\Users\dragon\automaton\send-task.js

# If missing, create it or check path
```

### Issue 3: "No response from Automaton AI"

**Cause:** Timeout or database issue

**Solutions:**
1. Check Automaton dashboard logs
2. Verify database at `C:/root/.automaton/state.db`
3. Increase timeout in code (default: 90s)

### Issue 4: Rate Limit Errors

**Cause:** User exceeded 10 signals/hour

**Solution:** Wait for rate limit window to reset

### Issue 5: Premium/Access Denied

**Cause:** User not premium or no Automaton access

**Solution:**
```
# Grant premium
/set_premium <user_id> 30

# Grant Automaton access (admin)
python grant_automaton_access.py <user_id>
```

## 📈 Monitoring

### Check AI Usage

```sql
-- Query user activity logs
SELECT * FROM user_activity 
WHERE action = 'ai_signal_requested' 
ORDER BY timestamp DESC 
LIMIT 100;
```

### Check Rate Limits

Rate limits are stored in-memory. To persist, consider:
- Redis integration
- Database storage
- File-based cache

## 🔄 Updates & Maintenance

### Update AI Client

Edit `app/automaton_ai_integration.py`:
- Adjust timeout values
- Modify response parsing
- Add new AI features

### Update Handlers

Edit `app/handlers_automaton_ai.py`:
- Add new commands
- Modify response formatting
- Update error messages

### Update Rate Limits

Edit `app/rate_limiter.py`:
```python
'ai_signal': {
    'max_requests': 20,  # Increase limit
    'window_seconds': 3600,
    'description': 'AI signal requests'
}
```

## 📝 Future Enhancements

### Planned Features

1. **AI Portfolio Analysis**
   - Command: `/ai_portfolio`
   - Analyze user's portfolio with AI

2. **AI Market Summary**
   - Command: `/ai_market`
   - Daily market overview by AI

3. **AI Risk Assessment**
   - Command: `/ai_risk <symbol>`
   - Risk analysis for specific trades

4. **AI Backtesting**
   - Command: `/ai_backtest <strategy>`
   - Backtest strategies with AI

### Integration Ideas

1. **Webhook Integration**
   - Real-time AI signals via webhook
   - Push notifications for high-confidence signals

2. **Multi-Model Support**
   - Support multiple AI models
   - User can choose preferred model

3. **Historical Analysis**
   - Store AI signal history
   - Track AI accuracy over time

## 📞 Support

### Contact

- Developer: [Your Name]
- Telegram: @yourusername
- Email: your.email@example.com

### Resources

- Automaton Dashboard: `C:\Users\dragon\automaton`
- Bot Directory: `C:\V3-Final-Version\Bismillah`
- Documentation: This file

## ✅ Checklist

Before going live:

- [ ] Automaton dashboard running
- [ ] Test suite passes
- [ ] Premium users can access
- [ ] Rate limits working
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Documentation complete
- [ ] Admin notified

## 🎉 Success Criteria

Integration is successful when:

1. ✅ Premium users can get AI signals
2. ✅ Non-premium users see upgrade message
3. ✅ Rate limits prevent abuse
4. ✅ AI responses are formatted correctly
5. ✅ Error handling works properly
6. ✅ Activity is logged
7. ✅ Bot remains stable

---

**Last Updated:** 2026-02-22
**Version:** 1.0.0
**Status:** ✅ Ready for Testing
