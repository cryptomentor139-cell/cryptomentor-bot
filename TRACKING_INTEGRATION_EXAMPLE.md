# 🔧 Contoh Integrasi Signal Tracking

## 1. Register Commands di bot.py

Tambahkan di `setup_application()`:

```python
# Register signal tracking handlers
try:
    from app.handlers_signal_tracking import (
        cmd_winrate, 
        cmd_weekly_report, 
        cmd_upload_logs,
        cmd_signal_stats
    )
    self.application.add_handler(CommandHandler("winrate", cmd_winrate))
    self.application.add_handler(CommandHandler("weekly_report", cmd_weekly_report))
    self.application.add_handler(CommandHandler("upload_logs", cmd_upload_logs))
    self.application.add_handler(CommandHandler("signal_stats", cmd_signal_stats))
    print("✅ Signal tracking handlers registered")
except Exception as e:
    print(f"⚠️ Signal tracking handlers failed: {e}")
```

## 2. Start Scheduler di bot.py

Tambahkan di `main()`:

```python
async def main():
    bot = TelegramBot()
    await bot.setup_application()
    
    # Start scheduler untuk auto upload & weekly report
    from app.scheduler import task_scheduler
    import asyncio
    
    # Run scheduler di background
    asyncio.create_task(task_scheduler.start())
    
    # Start bot
    await bot.application.run_polling()
```

## 3. Track Command di analyze_command

```python
async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else "BTC"
    user = update.effective_user
    
    # TAMBAHKAN INI: Track command
    from app.signal_tracker_integration import track_user_command
    track_user_command(
        user_id=user.id,
        username=user.username,
        command="/analyze",
        symbol=symbol,
        timeframe="1h"
    )
    
    # ... rest of code ...
    
    # TAMBAHKAN INI: Track signal setelah generate
    if demand_zones:
        from app.signal_tracker_integration import track_signal_given
        zone = demand_zones[0]
        signal_id = track_signal_given(
            user_id=user.id,
            symbol=symbol,
            timeframe="1h",
            entry_price=zone.midpoint,
            tp1=zone.high * 1.02,
            tp2=zone.high * 1.05,
            sl=zone.low * 0.98,
            signal_type="LONG"
        )
```

## 4. Track Command di futures_command

```python
async def futures_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else "BTC"
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    user = update.effective_user
    
    # Track command
    from app.signal_tracker_integration import track_user_command
    track_user_command(
        user_id=user.id,
        username=user.username,
        command="/futures",
        symbol=symbol,
        timeframe=timeframe
    )
    
    # ... generate signal ...
    
    # Track signal
    from app.signal_tracker_integration import track_signal_given
    signal_id = track_signal_given(
        user_id=user.id,
        symbol=symbol,
        timeframe=timeframe,
        entry_price=entry_price,
        tp1=tp1,
        tp2=tp2,
        sl=sl,
        signal_type=signal_type
    )
```

## 5. Track AI Commands

```python
# Di handlers_deepseek.py

async def handle_ai_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else "BTC"
    user = update.effective_user
    
    # Track AI command
    from app.signal_tracker_integration import track_user_command
    track_user_command(
        user_id=user.id,
        username=user.username,
        command="/ai",
        symbol=symbol,
        timeframe="analysis"
    )
    
    # ... rest of code ...
```

## 6. Update Signal Result (Manual atau Auto)

### Manual Update via Admin Command

```python
# Buat command baru untuk admin update signal result
async def cmd_update_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /update_signal <signal_id> <WIN|LOSS> <pnl_percent>
    Example: /update_signal 123_BTCUSDT_1234567890 WIN 2.5
    """
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /update_signal <signal_id> <WIN|LOSS> <pnl_percent>"
        )
        return
    
    signal_id = context.args[0]
    result = context.args[1].upper()
    pnl = float(context.args[2])
    
    from app.signal_tracker_integration import update_signal_outcome
    hit_tp = (result == "WIN")
    update_signal_outcome(signal_id, hit_tp, pnl)
    
    await update.message.reply_text(
        f"✅ Signal {signal_id} updated: {result} ({pnl:+.2f}%)"
    )
```

### Auto Update (Future Enhancement)

```python
# Bisa dibuat background task yang monitor price
# dan auto update signal result ketika hit TP/SL

async def monitor_active_signals():
    """Background task untuk monitor signal"""
    from app.signal_logger import signal_logger
    from pathlib import Path
    import json
    
    while True:
        signals_file = Path("signal_logs/active_signals.jsonl")
        if signals_file.exists():
            with open(signals_file, "r") as f:
                for line in f:
                    signal = json.loads(line)
                    
                    # Get current price
                    current_price = get_current_price(signal['symbol'])
                    
                    # Check if hit TP or SL
                    if current_price >= signal['tp1']:
                        # Hit TP1
                        pnl = ((signal['tp1'] - signal['entry_price']) / signal['entry_price']) * 100
                        update_signal_outcome(signal['signal_id'], True, pnl)
                    elif current_price <= signal['sl']:
                        # Hit SL
                        pnl = ((signal['sl'] - signal['entry_price']) / signal['entry_price']) * 100
                        update_signal_outcome(signal['signal_id'], False, pnl)
        
        await asyncio.sleep(300)  # Check every 5 minutes
```

## 7. Test Integration

```bash
# Test tracking
python -c "from app.signal_tracker_integration import track_user_command; track_user_command(123, 'testuser', '/analyze', 'BTC', '1h')"

# Test winrate calculation
python -c "from app.signal_tracker_integration import get_current_winrate; print(get_current_winrate())"

# Test weekly report
python -c "import asyncio; from app.weekly_report import weekly_reporter; asyncio.run(weekly_reporter.generate_report())"
```

## 8. Verify Files Created

```bash
# Check log files
ls -la signal_logs/

# View prompt logs
cat signal_logs/prompts_2026-02-16.jsonl

# View active signals
cat signal_logs/active_signals.jsonl

# View completed signals
cat signal_logs/completed_signals.jsonl
```

## ✅ Checklist Integration

- [ ] Register tracking handlers di bot.py
- [ ] Start scheduler di main()
- [ ] Add tracking ke /analyze command
- [ ] Add tracking ke /futures command
- [ ] Add tracking ke /ai commands
- [ ] Create /update_signal command
- [ ] Test manual tracking
- [ ] Test winrate calculation
- [ ] Test weekly report generation
- [ ] Setup Google Drive credentials
- [ ] Test auto upload
- [ ] Verify first weekly report
