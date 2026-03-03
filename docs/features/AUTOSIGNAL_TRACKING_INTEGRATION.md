# 📊 Auto Signal Tracking Integration

## 🎯 Purpose

Track semua auto signals ke database untuk:
1. **Monitor winrate** - Berapa % signal yang WIN vs LOSS
2. **AI Iteration** - CryptoMentor AI belajar dari hasil signal
3. **Performance analysis** - Coin mana yang paling profitable
4. **User feedback** - Data untuk improve signal quality

## ✅ Integration Complete

### What Was Added

**File**: `app/autosignal_fast.py`

**Code Added** (in `_broadcast` function):
```python
# Track signal to database for AI iteration
signal_id = None
try:
    from app.signal_tracker_integration import track_signal_given
    # Track signal for first user (representative)
    if receivers:
        signal_id = track_signal_given(
            user_id=receivers[0],  # Use first user as representative
            symbol=sig.get("symbol", ""),
            timeframe=sig.get("timeframe", TIMEFRAME),
            entry_price=sig.get("entry_price", 0),
            tp1=sig.get("tp1", 0),
            tp2=sig.get("tp2", 0),
            sl=sig.get("sl", 0),
            signal_type=sig.get("side", "LONG")
        )
        print(f"[AutoSignal] Tracked signal: {signal_id}")
except Exception as e:
    print(f"[AutoSignal] Failed to track signal: {e}")
```

## 📊 What Gets Tracked

### Signal Data
```json
{
  "signal_id": "123456_BTCUSDT_1771234567",
  "user_id": 123456,
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "signal_type": "LONG",
  "entry_price": 50000,
  "tp1": 51000,
  "tp2": 52000,
  "sl": 49000,
  "status": "ACTIVE",
  "timestamp": "2026-02-16T10:30:00Z"
}
```

### Storage Locations

**Local**: `signal_logs/active_signals.jsonl`

**G: Drive**: `G:\Drive Saya\CryptoBot_Signals\active_signals.jsonl`

**Supabase**: `cryptobot-signals` bucket (Railway)

## 🔄 Signal Lifecycle

### 1. Signal Generated
```
Auto signal detects opportunity
  ↓
Generate signal (BTCUSDT LONG)
  ↓
Track to database (active_signals.jsonl)
  ↓
Send to lifetime users
```

### 2. Signal Active
```
Signal tracked with:
- Entry price
- TP1, TP2
- Stop loss
- Status: ACTIVE
```

### 3. Signal Completed (Manual Update)
```
Admin checks price later
  ↓
If hit TP → Update as WIN
If hit SL → Update as LOSS
  ↓
Move to completed_signals.jsonl
  ↓
Calculate winrate
```

## 📈 Winrate Tracking

### View Winrate
```
/winrate        # 7-day winrate
/winrate 30     # 30-day winrate
```

### Admin Panel
```
/admin → Signal Tracking → Winrate 7d/30d
```

### Example Output
```
📊 WINRATE SIGNAL (7 HARI)

📈 STATISTIK:
• Total Signal: 45
• Win: 32 ✅
• Loss: 13 ❌
• Winrate: 71.1% 🎯
• Avg PnL: +1.8%
```

## 🤖 AI Iteration Process

### 1. Data Collection
```
Auto signals tracked daily
  ↓
Stored in signal_logs/
  ↓
Synced to G: drive / Supabase
```

### 2. Weekly Analysis
```
Every Monday 09:00 WIB
  ↓
Generate weekly report
  ↓
Analyze WIN/LOSS patterns
  ↓
Send to admin
```

### 3. AI Learning
```
Admin reviews report
  ↓
Identify patterns:
- Which coins perform best?
- Which timeframes work?
- Which indicators are accurate?
  ↓
Adjust signal logic
  ↓
Improve future signals
```

## 📊 Data Analysis

### Questions AI Can Answer

**Performance**:
- Which coins have highest winrate?
- Which timeframe is most accurate?
- What's the average PnL per signal?

**Patterns**:
- Do LONG signals perform better than SHORT?
- Are demand zones more reliable than supply zones?
- Does momentum indicator improve accuracy?

**Optimization**:
- Should we increase/decrease confidence threshold?
- Should we adjust TP/SL ratios?
- Which coins should we exclude?

## 🔧 Manual Signal Update

### Update Signal Result

**When TP Hit**:
```python
from app.signal_tracker_integration import update_signal_outcome
update_signal_outcome(signal_id, hit_tp=True, pnl_percent=2.5)
```

**When SL Hit**:
```python
update_signal_outcome(signal_id, hit_tp=False, pnl_percent=-2.0)
```

### Via Admin Commands
```
# Future feature: Auto-update via price monitoring
# For now: Manual update by admin
```

## 📈 Iteration Workflow

### Week 1: Collect Data
```
Monday-Sunday: Auto signals running
  ↓
~50-125 signals sent
  ↓
All tracked to database
```

### Week 2: Analyze
```
Monday morning: Weekly report generated
  ↓
Admin reviews:
- Winrate: 65%
- Best coin: BTC (80% winrate)
- Worst coin: DOGE (40% winrate)
  ↓
Insights:
- Demand zones work better than supply
- 15m timeframe too noisy
- Need higher confidence threshold
```

### Week 3: Improve
```
Adjust signal logic:
- Increase confidence from 75% to 80%
- Focus on demand zones
- Use 1h timeframe instead of 15m
  ↓
Deploy changes
  ↓
Monitor new winrate
```

### Week 4: Verify
```
Compare results:
- Old winrate: 65%
- New winrate: 72%
- Improvement: +7%
  ↓
Keep changes if better
  ↓
Continue iteration
```

## 🎯 Benefits

### For Users
- ✅ Better signal quality over time
- ✅ Higher winrate
- ✅ More profitable signals
- ✅ Continuous improvement

### For Admin
- ✅ Data-driven decisions
- ✅ Clear performance metrics
- ✅ Easy to identify issues
- ✅ Track improvement over time

### For AI
- ✅ Learn from real results
- ✅ Adapt to market conditions
- ✅ Improve accuracy
- ✅ Optimize parameters

## 📊 Monitoring

### Daily Check
```
/signal_stats  # Check how many signals sent today
```

### Weekly Review
```
/weekly_report  # Full analysis of past week
```

### Monthly Analysis
```
/winrate 30  # 30-day performance
```

## 🔄 Automatic Features

### Daily Backup (23:00 WIB)
```
All signal data backed up to:
- G: drive (local)
- Supabase (Railway)
```

### Weekly Report (Monday 09:00 WIB)
```
Automatic report sent to admin:
- Total signals
- Winrate
- Best/worst performers
- Recommendations
```

## 📝 Data Format

### Active Signal
```json
{
  "signal_id": "123456_BTCUSDT_1771234567",
  "user_id": 123456,
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "signal_type": "LONG",
  "entry_price": 50000,
  "tp1": 51000,
  "tp2": 52000,
  "sl": 49000,
  "status": "ACTIVE",
  "created_at": "2026-02-16T10:30:00Z"
}
```

### Completed Signal
```json
{
  "signal_id": "123456_BTCUSDT_1771234567",
  "user_id": 123456,
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "signal_type": "LONG",
  "entry_price": 50000,
  "tp1": 51000,
  "tp2": 52000,
  "sl": 49000,
  "status": "CLOSED",
  "result": "WIN",
  "pnl_percent": 2.5,
  "created_at": "2026-02-16T10:30:00Z",
  "closed_at": "2026-02-16T12:15:00Z"
}
```

## 🎯 Summary

### What's Tracked
- ✅ Every auto signal sent
- ✅ Entry, TP, SL prices
- ✅ Signal type (LONG/SHORT)
- ✅ Timestamp

### Where It's Stored
- ✅ Local: `signal_logs/`
- ✅ G: Drive (local dev)
- ✅ Supabase (Railway)

### How It's Used
- ✅ Calculate winrate
- ✅ Generate reports
- ✅ AI iteration
- ✅ Performance analysis

### Benefits
- ✅ Continuous improvement
- ✅ Data-driven decisions
- ✅ Better signals over time
- ✅ Higher user satisfaction

---

**Status**: ✅ Integrated  
**Tracking**: Automatic  
**Reports**: Weekly  
**Iteration**: Continuous
