# ⏰ Auto Signal Cooldown & Anti-Spam System

## 📊 Current Configuration

### Scan Interval
```bash
AUTOSIGNAL_INTERVAL_SEC=1800  # 30 minutes
```
**Artinya**: Bot scan top 25 coins setiap 30 menit

### Cooldown Per Signal
```bash
AUTOSIGNAL_COOLDOWN_MIN=60  # 60 minutes (1 hour)
```
**Artinya**: Setelah kirim signal untuk coin tertentu (misal BTCUSDT LONG), tidak akan kirim signal yang sama lagi selama 60 menit

## 🔄 How It Works

### Example Timeline

**00:00** - Scan #1
- BTC near demand zone → Send LONG signal
- ETH near supply zone → Send SHORT signal
- SOL neutral → Skip

**00:30** - Scan #2
- BTC still near demand → **SKIP** (cooldown 60 min)
- ETH still near supply → **SKIP** (cooldown 60 min)
- SOL now bullish → Send LONG signal

**01:00** - Scan #3
- BTC still near demand → **SKIP** (cooldown not expired)
- ETH moved away → No signal
- SOL still bullish → **SKIP** (cooldown 60 min)

**01:30** - Scan #4
- BTC now near supply → Send SHORT signal ✅ (different side)
- ETH neutral → Skip
- SOL hit TP → **Can send new signal** ✅

## 🎯 Anti-Spam Logic

### Cooldown Key Format
```python
key = f"{symbol}:{side}"
# Examples:
# "BTCUSDT:LONG"
# "ETHUSDT:SHORT"
# "SOLUSDT:LONG"
```

### Cooldown Rules

**Rule 1**: Same coin + same side = Cooldown
```
BTCUSDT LONG → Wait 60 min before BTCUSDT LONG again
```

**Rule 2**: Same coin + different side = OK
```
BTCUSDT LONG → Can send BTCUSDT SHORT immediately
```

**Rule 3**: Different coin = OK
```
BTCUSDT LONG → Can send ETHUSDT LONG immediately
```

## 📊 Recommended Settings

### Conservative (Less Spam)
```bash
AUTOSIGNAL_INTERVAL_SEC=3600   # 1 hour scan
AUTOSIGNAL_COOLDOWN_MIN=180    # 3 hours cooldown
```
**Result**: ~8 scans/day, max 1 signal per coin per 3 hours

### Balanced (Current)
```bash
AUTOSIGNAL_INTERVAL_SEC=1800   # 30 min scan
AUTOSIGNAL_COOLDOWN_MIN=60     # 1 hour cooldown
```
**Result**: ~48 scans/day, max 1 signal per coin per hour

### Aggressive (More Signals)
```bash
AUTOSIGNAL_INTERVAL_SEC=900    # 15 min scan
AUTOSIGNAL_COOLDOWN_MIN=30     # 30 min cooldown
```
**Result**: ~96 scans/day, max 2 signals per coin per hour

## 🎯 Why These Settings?

### Scan Interval (30 min)
- ✅ Fast enough to catch opportunities
- ✅ Not too frequent (avoid spam)
- ✅ Gives market time to move
- ✅ Reasonable server load

### Cooldown (60 min)
- ✅ Prevents duplicate signals
- ✅ Gives time for TP/SL to hit
- ✅ Reduces noise for users
- ✅ Better signal quality

## 📈 Signal Flow

```
Scan #1 (00:00)
  ↓
Check 25 coins
  ↓
BTC: Near demand zone
  ↓
Check cooldown: OK (no recent signal)
  ↓
Generate signal: BTCUSDT LONG
  ↓
Send to lifetime users
  ↓
Mark sent: "BTCUSDT:LONG" @ 00:00
  ↓
Cooldown active until 01:00

Scan #2 (00:30)
  ↓
Check 25 coins
  ↓
BTC: Still near demand zone
  ↓
Check cooldown: SKIP (sent at 00:00, wait until 01:00)
  ↓
No signal sent

Scan #3 (01:00)
  ↓
Check 25 coins
  ↓
BTC: Now near supply zone (different!)
  ↓
Check cooldown: OK (different side: SHORT vs LONG)
  ↓
Generate signal: BTCUSDT SHORT
  ↓
Send to lifetime users
```

## 🔧 Customization

### Change Scan Interval
```bash
# In .env file
AUTOSIGNAL_INTERVAL_SEC=1800  # Change to your preference
```

**Options**:
- `900` = 15 minutes (aggressive)
- `1800` = 30 minutes (balanced)
- `3600` = 1 hour (conservative)
- `7200` = 2 hours (very conservative)

### Change Cooldown
```bash
# In .env file
AUTOSIGNAL_COOLDOWN_MIN=60  # Change to your preference
```

**Options**:
- `30` = 30 minutes (aggressive)
- `60` = 1 hour (balanced)
- `120` = 2 hours (conservative)
- `180` = 3 hours (very conservative)

## 📊 Expected Signal Volume

### With Current Settings (30min scan, 60min cooldown)

**Per Day**:
- Scans: 48 times
- Max signals per coin: 24 (if always meets criteria)
- Realistic signals per coin: 2-5
- Total signals (25 coins): 50-125 per day

**Per User**:
- Lifetime users receive all signals
- ~2-5 signals per hour during active market
- ~50-125 signals per day total

## 🎯 Best Practices

### For Low Spam
```bash
AUTOSIGNAL_INTERVAL_SEC=3600   # 1 hour
AUTOSIGNAL_COOLDOWN_MIN=180    # 3 hours
```
**Result**: ~2-3 signals per coin per day

### For Active Trading
```bash
AUTOSIGNAL_INTERVAL_SEC=1800   # 30 min
AUTOSIGNAL_COOLDOWN_MIN=60     # 1 hour
```
**Result**: ~4-8 signals per coin per day

### For High Frequency
```bash
AUTOSIGNAL_INTERVAL_SEC=900    # 15 min
AUTOSIGNAL_COOLDOWN_MIN=30     # 30 min
```
**Result**: ~8-16 signals per coin per day

## 🚨 Important Notes

### Cooldown is Per Side
- BTCUSDT LONG and BTCUSDT SHORT have separate cooldowns
- This allows reversal signals

### Cooldown Persists Across Restarts
- Saved in `data/autosignal_state.json`
- Bot remembers last sent signals
- Prevents spam after restart

### Manual Trigger Bypasses Cooldown
- `/signal_tick` command ignores cooldown
- Useful for testing
- Use with caution

## 📝 Summary

**Current Settings**:
- ✅ Scan every 30 minutes
- ✅ Cooldown 60 minutes per signal
- ✅ Prevents spam effectively
- ✅ Allows reversal signals
- ✅ Good balance for lifetime users

**Recommendation**: Keep current settings unless users complain about too many/few signals.

---

**Configuration**: Balanced (30min/60min)  
**Status**: ✅ Anti-spam working  
**Adjustable**: Yes, via .env variables
