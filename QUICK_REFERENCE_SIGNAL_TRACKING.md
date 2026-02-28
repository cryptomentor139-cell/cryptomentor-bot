# 🚀 Quick Reference - Signal Tracking Commands

## ⚡ Quick Start (Copy-Paste)

### 1. Restart Bot
```bash
cd Bismillah
python main.py
```

### 2. Test Commands (di Telegram)
```
/signal_stats
/winrate
/winrate 30
/upload_logs
/weekly_report
```

## 📋 Command Reference

| Command | What It Does | Example |
|---------|--------------|---------|
| `/signal_stats` | Show tracking statistics | `/signal_stats` |
| `/winrate` | Show 7-day winrate | `/winrate` |
| `/winrate 30` | Show 30-day winrate | `/winrate 30` |
| `/upload_logs` | Force sync to G: drive | `/upload_logs` |
| `/weekly_report` | Generate weekly report | `/weekly_report` |

## 🔧 Integration Code

### Track Command
```python
from app.signal_tracker_integration import track_user_command
track_user_command(user.id, user.username, "/analyze", "BTC", "1h")
```

### Track Signal
```python
from app.signal_tracker_integration import track_signal_given
signal_id = track_signal_given(
    user.id, "BTCUSDT", "1h", 50000, 51000, 52000, 49500, "LONG"
)
```

### Update Result
```python
from app.signal_tracker_integration import update_signal_outcome
update_signal_outcome(signal_id, hit_tp=True, pnl_percent=2.5)
```

## 📁 File Locations

**Local**: `Bismillah/signal_logs/`  
**G: Drive**: `G:\Drive Saya\CryptoBot_Signals\`  
**Cloud**: Google Drive (auto-sync)

## ⏰ Automatic Schedule

- **Daily Backup**: 23:00 WIB (11 PM)
- **Weekly Report**: Monday 09:00 WIB (9 AM)

## ✅ Success Indicators

**Bot Startup**:
```
✅ Signal tracking admin commands registered
✅ Signal tracking scheduler started
```

**Command Response**: Immediate response with data

**Files**: Created in both local and G: drive

## 🔍 Troubleshooting

**Command not working?**
1. Check you're admin (ADMIN1/ADMIN2 in .env)
2. Restart bot
3. Check startup logs

**G: drive not found?**
1. Start Google Drive for Desktop
2. Check `dir G:\`
3. Check .env GDRIVE_PATH

## 📚 Full Documentation

- `MASALAH_SOLVED.md` - Problem & solution (Indonesian)
- `SIGNAL_TRACKING_FIXED.md` - Technical details (English)
- `CARA_TEST_SIGNAL_TRACKING.md` - Testing guide (Indonesian)

## 🎯 Status

✅ Handlers registered  
✅ Scheduler started  
✅ G: drive working  
✅ Commands tested  
✅ Ready to use  

**Restart bot dan test sekarang!** 🚀
