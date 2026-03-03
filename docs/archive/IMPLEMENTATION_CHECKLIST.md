# ✅ Implementation Checklist - Signal Tracking System

## 📋 Pre-Implementation

- [ ] Backup bot code saat ini
- [ ] Backup database (jika ada)
- [ ] Read `SIGNAL_TRACKING_README.md`
- [ ] Read `QUICK_START_TRACKING.md`

## 🔧 Setup Phase

### 1. Dependencies
- [ ] Install PyDrive2: `pip install PyDrive2`
- [ ] Verify installation: `python -c "import pydrive2"`
- [ ] Update requirements.txt (sudah done)

### 2. Google Drive Setup
- [ ] Buka Google Cloud Console
- [ ] Buat project baru: "CryptoBot Signals"
- [ ] Enable Google Drive API
- [ ] Create OAuth credentials (Desktop app)
- [ ] Download credentials JSON
- [ ] Rename to `gdrive_credentials.json`
- [ ] Copy ke folder `Bismillah/`
- [ ] Verify file exists: `ls gdrive_credentials.json`

### 3. Initial Setup
- [ ] Run: `python setup_signal_tracking.py`
- [ ] Authenticate Google Drive (browser akan terbuka)
- [ ] Verify `gdrive_token.json` created
- [ ] Check `signal_logs/` directory created

## 🔌 Integration Phase

### 1. Register Admin Commands
Di `bot.py` → method `setup_application()`, tambahkan:

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

- [ ] Code added
- [ ] No syntax errors
- [ ] Saved file

### 2. Start Scheduler
Di `bot.py` → method `main()`, sebelum `run_polling()`:

```python
# Start scheduler untuk auto upload & weekly report
from app.scheduler import task_scheduler
import asyncio

# Run scheduler di background
asyncio.create_task(task_scheduler.start())
print("✅ Scheduler started")
```

- [ ] Code added
- [ ] No syntax errors
- [ ] Saved file

### 3. Add Tracking to Commands

#### A. analyze_command
Di method `analyze_command()`, setelah get user info:

```python
# Track command
from app.signal_tracker_integration import track_user_command
track_user_command(
    user_id=user.id,
    username=user.username,
    command="/analyze",
    symbol=symbol,
    timeframe="1h"
)
```

Setelah generate signal (jika ada demand_zones):

```python
# Track signal
from app.signal_tracker_integration import track_signal_given
if demand_zones:
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

- [ ] Command tracking added
- [ ] Signal tracking added
- [ ] Tested

#### B. futures_command
Di method `futures_command()`:

```python
# Track command
from app.signal_tracker_integration import track_user_command
track_user_command(
    user_id=user.id,
    username=user.username,
    command="/futures",
    symbol=symbol,
    timeframe=timeframe
)

# Track signal (setelah generate)
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

- [ ] Command tracking added
- [ ] Signal tracking added
- [ ] Tested

#### C. AI Commands (handlers_deepseek.py)
Di `handle_ai_analyze()`, `handle_ai_chat()`, dll:

```python
# Track AI command
from app.signal_tracker_integration import track_user_command
track_user_command(
    user_id=user.id,
    username=user.username,
    command="/ai",  # atau /chat, /aimarket
    symbol=symbol if symbol else "general",
    timeframe="analysis"
)
```

- [ ] AI commands tracked
- [ ] Tested

## 🧪 Testing Phase

### 1. Manual Testing
- [ ] Start bot: `python bot.py`
- [ ] Check logs: "Signal tracking handlers registered"
- [ ] Check logs: "Scheduler started"
- [ ] Test command: `/analyze btc`
- [ ] Verify file created: `signal_logs/prompts_YYYY-MM-DD.jsonl`
- [ ] Check file content: `cat signal_logs/prompts_*.jsonl`

### 2. Admin Commands Testing
- [ ] Test: `/signal_stats`
- [ ] Test: `/winrate`
- [ ] Test: `/winrate 30`
- [ ] Test: `/weekly_report`
- [ ] Test: `/upload_logs`
- [ ] Verify all commands work

### 3. Google Drive Testing
- [ ] Run: `/upload_logs`
- [ ] Check Google Drive folder: "CryptoBot_Signals"
- [ ] Verify files uploaded
- [ ] Check file content di GDrive

### 4. Tracking Verification
- [ ] Run several commands: `/analyze btc`, `/futures eth 1h`
- [ ] Check `signal_logs/prompts_*.jsonl` has entries
- [ ] Check `signal_logs/active_signals.jsonl` has signals
- [ ] Verify data format correct

## 📊 Monitoring Phase

### Day 1
- [ ] Bot running stable
- [ ] Commands tracked correctly
- [ ] No errors in logs
- [ ] Files created properly

### Day 1 - 23:00 WIB
- [ ] Wait for auto upload
- [ ] Check logs: "Daily logs uploaded"
- [ ] Verify files in Google Drive
- [ ] Check for errors

### Week 1 - Senin 09:00 WIB
- [ ] Wait for weekly report
- [ ] Check admin received report
- [ ] Verify report format correct
- [ ] Check winrate calculation accurate

## 🔍 Troubleshooting Checklist

### If Google Drive fails:
- [ ] Check `gdrive_credentials.json` exists
- [ ] Check `gdrive_token.json` exists
- [ ] Re-authenticate: `rm gdrive_token.json && python setup_signal_tracking.py`
- [ ] Check Google Cloud Console: API enabled
- [ ] Check OAuth consent screen configured

### If tracking not working:
- [ ] Check `signal_logs/` directory exists
- [ ] Check file permissions
- [ ] Check imports in bot.py
- [ ] Check for Python errors in logs
- [ ] Verify integration code added correctly

### If scheduler not running:
- [ ] Check logs: "Scheduler started"
- [ ] Check asyncio.create_task() called
- [ ] Check no exceptions in scheduler.py
- [ ] Verify bot running continuously

### If winrate incorrect:
- [ ] Check `completed_signals.jsonl` has data
- [ ] Verify signal update calls working
- [ ] Check date filtering in calculate_winrate()
- [ ] Manually verify calculation

## 📈 Post-Implementation

### Week 1
- [ ] Monitor daily uploads
- [ ] Check weekly report received
- [ ] Verify data accuracy
- [ ] Review winrate stats

### Week 2
- [ ] Compare 2 weekly reports
- [ ] Analyze trends
- [ ] Adjust strategy if needed
- [ ] Document findings

### Month 1
- [ ] Review all data
- [ ] Calculate monthly winrate
- [ ] Identify patterns
- [ ] Optimize signal parameters

## 🎯 Success Criteria

- [ ] ✅ All commands tracked automatically
- [ ] ✅ Files created daily in `signal_logs/`
- [ ] ✅ Daily upload to Google Drive working
- [ ] ✅ Weekly report sent to admins
- [ ] ✅ Winrate calculation accurate
- [ ] ✅ No errors in bot logs
- [ ] ✅ Admin commands working
- [ ] ✅ Data backed up safely

## 📝 Notes

### Important Files
- `signal_logs/` - Local log storage
- `gdrive_credentials.json` - OAuth credentials (gitignored)
- `gdrive_token.json` - Auth token (gitignored)
- `bot.py` - Main integration points

### Key Times
- 23:00 WIB - Daily upload
- Senin 09:00 WIB - Weekly report

### Admin Commands
- `/winrate` - View winrate
- `/weekly_report` - Generate report
- `/upload_logs` - Manual upload
- `/signal_stats` - View statistics

## 🚀 Ready to Deploy

- [ ] All checklist items completed
- [ ] Testing passed
- [ ] Documentation reviewed
- [ ] Backup created
- [ ] Ready for production

---

**Status**: ⏳ Pending Implementation
**Last Updated**: 2026-02-16
**Version**: 1.0.0
