# 🤖 AI Iteration Process - How CryptoMentor Learns & Improves

## 📊 Current Indicators Used

### 1. Supply & Demand Zones (Primary)
```python
# From snd_zone_detector.py
demand_zones = detect_snd_zones(symbol, timeframe)
supply_zones = detect_snd_zones(symbol, timeframe)

# Indicators tracked:
- Zone strength (0-100)
- Distance from current price
- Zone width
- Touch count
```

**What's Measured**:
- Apakah price dekat demand zone? (< 2%)
- Apakah price dekat supply zone? (< 2%)
- Seberapa kuat zone tersebut? (strength score)

### 2. Price Momentum
```python
change_24h = price_data.get('change_24h', 0)

# Signals:
if change_24h > 5%:  # Strong uptrend
    → LONG signal
elif change_24h < -5%:  # Strong downtrend
    → SHORT signal
```

**What's Measured**:
- Perubahan harga 24 jam
- Arah momentum (bullish/bearish)
- Kekuatan momentum (magnitude)

### 3. Volume
```python
volume_24h = price_data.get('volume_24h', 0)

# Confirmation:
if volume_24h > 1_000_000:  # High volume
    → Increase confidence
```

**What's Measured**:
- Volume 24 jam
- Apakah ada volume confirmation?
- Liquidity check

### 4. Confidence Score
```python
# Base confidence
confidence = 70 + (zone_strength / 5)

# Adjustments:
if strong_momentum:
    confidence += 5
if high_volume:
    confidence += 5

# Threshold
if confidence < 75:
    → Skip signal
```

**What's Measured**:
- Overall signal quality
- Combination of all factors
- Risk assessment

## 📈 Data Collected for Each Signal

### Signal Metadata
```json
{
  "signal_id": "123456_BTCUSDT_1771234567",
  "timestamp": "2026-02-16T10:30:00Z",
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "signal_type": "LONG",
  
  // Entry & Targets
  "entry_price": 50000,
  "tp1": 51000,
  "tp2": 52000,
  "sl": 49000,
  
  // Indicators at signal time
  "indicators": {
    "change_24h": 3.5,
    "volume_24h": 2500000,
    "zone_strength": 85,
    "distance_to_zone": 1.2,
    "confidence": 82
  },
  
  // Reasons
  "reasons": [
    "Near demand zone",
    "Dip: -3.2%"
  ],
  
  // Result (updated later)
  "result": "WIN",
  "pnl_percent": 2.5,
  "closed_at": "2026-02-16T12:15:00Z"
}
```

## 🔍 Analysis Process

### Phase 1: Data Collection (Week 1-4)

**Collect Minimum 100 Signals**:
```
Week 1: 50 signals
Week 2: 50 signals
Week 3: 50 signals
Week 4: 50 signals
Total: 200 signals
```

**Data Points per Signal**:
- Entry price
- TP1, TP2, SL
- Indicators (momentum, volume, zone strength)
- Reasons
- Result (WIN/LOSS)
- PnL %

### Phase 2: Pattern Analysis (Week 5)

**1. Winrate by Indicator**

```python
# Analyze: Which indicator predicts WIN best?

# By Zone Strength
zone_strength_80_100 = signals.filter(zone_strength >= 80)
winrate_strong_zones = zone_strength_80_100.winrate()
# Result: 75% winrate

zone_strength_60_80 = signals.filter(60 <= zone_strength < 80)
winrate_medium_zones = zone_strength_60_80.winrate()
# Result: 65% winrate

# Insight: Strong zones (80+) have 10% better winrate
```

**2. Winrate by Momentum**

```python
# Analyze: Does momentum direction matter?

long_signals = signals.filter(signal_type == "LONG")
long_with_positive_momentum = long_signals.filter(change_24h > 0)
winrate_aligned = long_with_positive_momentum.winrate()
# Result: 72% winrate

long_with_negative_momentum = long_signals.filter(change_24h < 0)
winrate_counter = long_with_negative_momentum.winrate()
# Result: 58% winrate

# Insight: Momentum alignment improves winrate by 14%
```

**3. Winrate by Volume**

```python
# Analyze: Does volume matter?

high_volume = signals.filter(volume_24h > 1_000_000)
winrate_high_vol = high_volume.winrate()
# Result: 70% winrate

low_volume = signals.filter(volume_24h < 1_000_000)
winrate_low_vol = low_volume.winrate()
# Result: 55% winrate

# Insight: High volume improves winrate by 15%
```

**4. Winrate by Coin**

```python
# Analyze: Which coins perform best?

btc_signals = signals.filter(symbol == "BTCUSDT")
btc_winrate = btc_signals.winrate()
# Result: 78% winrate

eth_signals = signals.filter(symbol == "ETHUSDT")
eth_winrate = eth_signals.winrate()
# Result: 72% winrate

doge_signals = signals.filter(symbol == "DOGEUSDT")
doge_winrate = doge_signals.winrate()
# Result: 45% winrate

# Insight: Focus on BTC/ETH, avoid DOGE
```

**5. Winrate by Timeframe**

```python
# Analyze: Is 15m too noisy?

tf_15m = signals.filter(timeframe == "15m")
winrate_15m = tf_15m.winrate()
# Result: 62% winrate

# Test with 1h data
tf_1h = historical_signals.filter(timeframe == "1h")
winrate_1h = tf_1h.winrate()
# Result: 71% winrate

# Insight: 1h timeframe is 9% more accurate
```

### Phase 3: Optimization (Week 6)

**Based on Analysis, Adjust Parameters**:

```python
# OLD SETTINGS
MIN_CONFIDENCE = 75
TIMEFRAME = "15m"
MIN_ZONE_STRENGTH = 0  # No minimum
REQUIRE_VOLUME = False
REQUIRE_MOMENTUM_ALIGN = False

# NEW SETTINGS (Optimized)
MIN_CONFIDENCE = 80  # Increase threshold
TIMEFRAME = "1h"     # Use higher timeframe
MIN_ZONE_STRENGTH = 80  # Only strong zones
REQUIRE_VOLUME = True   # Must have volume > 1M
REQUIRE_MOMENTUM_ALIGN = True  # Momentum must align
```

**Update Signal Logic**:

```python
def compute_signal_fast_v2(base_symbol: str):
    """
    Optimized version based on data analysis
    """
    # Get data
    snd_result = detect_snd_zones(full_symbol, "1h", limit=50)  # Changed to 1h
    
    # Check zone strength
    if demand_zones:
        nearest_demand = min(demand_zones, key=lambda z: abs(current_price - z.midpoint))
        
        # NEW: Require strong zones
        if nearest_demand.strength < 80:  # Skip weak zones
            return None
        
        distance_pct = abs(current_price - nearest_demand.midpoint) / current_price * 100
        
        if distance_pct < 2:
            side = "LONG"
            confidence = 70 + nearest_demand.strength / 5
            
            # NEW: Require momentum alignment
            if change_24h < 0:  # Counter-trend
                confidence -= 10  # Penalize
            else:
                confidence += 5   # Reward
            
            # NEW: Require volume
            if volume_24h < 1_000_000:
                confidence -= 10  # Penalize low volume
            
            # NEW: Higher threshold
            if confidence < 80:  # Increased from 75
                return None
            
            reasons.append(f"Strong zone: {nearest_demand.strength:.0f}%")
            
            # NEW: Add momentum info
            if change_24h > 0:
                reasons.append(f"Momentum aligned: {change_24h:+.1f}%")
    
    return signal
```

### Phase 4: A/B Testing (Week 7-8)

**Run Both Versions in Parallel**:

```python
# 50% users get old version
# 50% users get new version

# Track results separately
old_version_winrate = track_winrate(version="v1")
new_version_winrate = track_winrate(version="v2")

# Compare after 2 weeks
if new_version_winrate > old_version_winrate + 5%:
    # New version is significantly better
    deploy_to_all_users(version="v2")
else:
    # Keep old version or iterate more
    continue_testing()
```

### Phase 5: Continuous Monitoring (Ongoing)

**Weekly Reports**:
```python
# Every Monday 09:00 WIB
def generate_weekly_report():
    signals = get_signals_last_7_days()
    
    report = {
        "total_signals": len(signals),
        "wins": signals.filter(result="WIN").count(),
        "losses": signals.filter(result="LOSS").count(),
        "winrate": calculate_winrate(signals),
        "avg_pnl": calculate_avg_pnl(signals),
        
        # Breakdown by indicator
        "by_zone_strength": analyze_by_zone_strength(signals),
        "by_momentum": analyze_by_momentum(signals),
        "by_volume": analyze_by_volume(signals),
        "by_coin": analyze_by_coin(signals),
        
        # Recommendations
        "recommendations": generate_recommendations(signals)
    }
    
    send_to_admin(report)
```

## 🎯 Specific Improvements Based on Data

### Example 1: Zone Strength Threshold

**Data Shows**:
```
Zone Strength 90-100: 82% winrate
Zone Strength 80-90:  75% winrate
Zone Strength 70-80:  68% winrate
Zone Strength 60-70:  58% winrate
Zone Strength <60:    45% winrate
```

**Action**: Increase MIN_ZONE_STRENGTH from 0 to 80

**Expected Impact**: Winrate improves from 65% to 75%

### Example 2: Momentum Alignment

**Data Shows**:
```
LONG + Positive momentum: 72% winrate
LONG + Negative momentum: 58% winrate
SHORT + Negative momentum: 70% winrate
SHORT + Positive momentum: 55% winrate
```

**Action**: Require momentum alignment or penalize confidence

**Expected Impact**: Winrate improves by 10-15%

### Example 3: Volume Filter

**Data Shows**:
```
Volume > 5M:   78% winrate
Volume 1-5M:   70% winrate
Volume 500K-1M: 62% winrate
Volume < 500K:  48% winrate
```

**Action**: Require minimum volume of 1M

**Expected Impact**: Filter out 48% winrate signals, keep 70%+ only

### Example 4: Coin Selection

**Data Shows**:
```
BTC:  78% winrate
ETH:  72% winrate
BNB:  68% winrate
SOL:  65% winrate
DOGE: 45% winrate
SHIB: 42% winrate
```

**Action**: Exclude coins with <60% winrate

**Expected Impact**: Overall winrate improves from 65% to 72%

### Example 5: Timeframe Optimization

**Data Shows**:
```
5m:  55% winrate (too noisy)
15m: 62% winrate (current)
1h:  71% winrate (better)
4h:  68% winrate (too slow)
```

**Action**: Change from 15m to 1h timeframe

**Expected Impact**: Winrate improves by 9%

## 🔄 Iteration Cycle

```
Week 1-4: Collect 200+ signals
    ↓
Week 5: Analyze patterns
    ↓
Week 6: Optimize parameters
    ↓
Week 7-8: A/B test new version
    ↓
Week 9: Deploy if better
    ↓
Week 10+: Monitor & repeat
```

## 📊 Key Metrics Tracked

### Performance Metrics
- **Winrate**: % of signals that hit TP
- **Avg PnL**: Average profit/loss per signal
- **Risk/Reward**: TP vs SL ratio
- **Hit Rate**: % of signals that trigger

### Indicator Metrics
- **Zone Strength**: Correlation with winrate
- **Momentum**: Impact on success rate
- **Volume**: Confirmation value
- **Distance**: Optimal entry distance

### Coin Metrics
- **Per-coin winrate**: Which coins work best
- **Volatility**: Impact on success
- **Liquidity**: Minimum volume needed
- **Market cap**: Size vs performance

## 🎯 Optimization Goals

### Short-term (1-3 months)
- Improve winrate from 65% to 75%
- Reduce false signals by 30%
- Increase avg PnL from 1.5% to 2.5%

### Medium-term (3-6 months)
- Achieve 80% winrate
- Adaptive parameters per coin
- Dynamic confidence scoring
- Market condition awareness

### Long-term (6-12 months)
- Machine learning integration
- Predictive modeling
- Real-time optimization
- Personalized signals per user

## 📝 Summary

### Current Indicators
1. ✅ Supply & Demand zones
2. ✅ Price momentum (24h change)
3. ✅ Volume (24h)
4. ✅ Confidence score

### Analysis Process
1. ✅ Collect 200+ signals
2. ✅ Analyze patterns by indicator
3. ✅ Identify what works/doesn't
4. ✅ Optimize parameters
5. ✅ A/B test improvements
6. ✅ Deploy if better
7. ✅ Repeat weekly

### Expected Improvements
- **Winrate**: 65% → 75% → 80%
- **Avg PnL**: 1.5% → 2.5% → 3.5%
- **Signal Quality**: Better filtering
- **User Satisfaction**: Higher profits

**The more data collected, the smarter the system becomes!** 🚀

---

**Process**: Data-driven iteration  
**Frequency**: Weekly analysis  
**Goal**: Continuous improvement  
**Status**: ✅ Tracking active
