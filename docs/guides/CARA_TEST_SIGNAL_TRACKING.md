# 🧪 Cara Test Signal Tracking Commands

## 🚀 Quick Start (3 Langkah)

### 1️⃣ Restart Bot
```bash
cd Bismillah
python main.py
```

**Expected output**:
```
✅ Signal tracking admin commands registered
✅ Signal tracking scheduler started
```

### 2️⃣ Test Commands di Telegram
Buka bot Anda di Telegram, lalu coba commands ini:

#### Command 1: `/signal_stats`
```
/signal_stats
```

**Expected response**:
```
📊 STATISTIK SIGNAL TRACKING

━━━━━━━━━━━━━━━━━━━━━━

📝 DATA TERSIMPAN:
• Total Prompts: 148
• Active Signals: 0
• Completed Signals: 2
• Log Files: 1

☁️ STORAGE:
• Type: G: Drive (Local)
• Status: ✅ Enabled
• Path: G:/Drive Saya/CryptoBot_Signals
```

#### Command 2: `/winrate`
```
/winrate
```

**Expected response**:
```
📊 WINRATE SIGNAL (7 HARI TERAKHIR)

📈 STATISTIK:
• Total Signal: 2
• Win: 2 ✅
• Loss: 0 ❌
• Winrate: 100.0% 🎯
• Avg PnL: +2.25%
```

#### Command 3: `/winrate 30`
```
/winrate 30
```

**Expected response**: Winrate untuk 30 hari terakhir

#### Command 4: `/upload_logs`
```
/upload_logs
```

**Expected response**:
```
✅ G: Drive Sync complete!

📊 Synced: 3 files
❌ Failed: 0 files
```

### 3️⃣ Verify Files
Check files di G: drive:

**Path**: `G:\Drive Saya\CryptoBot_Signals\`

**Files**:
- `prompts_2026-02-16.jsonl` - User commands
- `active_signals.jsonl` - Ongoing signals
- `completed_signals.jsonl` - Finished signals

## 🔍 Troubleshooting

### ❌ Command tidak berfungsi?

#### Check 1: Apakah Anda admin?
Commands ini hanya untuk admin. Check `.env`:
```bash
ADMIN1=your_telegram_id
ADMIN2=another_admin_id
```

#### Check 2: Apakah bot sudah restart?
```bash
# Stop bot (Ctrl+C)
# Start again
python main.py
```

#### Check 3: Apakah handlers registered?
Look for this in bot startup logs:
```
✅ Signal tracking admin commands registered
```

### ⚠️ G: drive not found?

#### Check 1: Apakah Google Drive for Desktop running?
- Open Task Manager
- Look for "GoogleDriveFS.exe"
- If not running, start Google Drive for Desktop

#### Check 2: Apakah G: drive mounted?
```bash
# Check if G: drive exists
dir G:\
```

#### Check 3: Check .env configuration
```bash
GDRIVE_PATH=G:/Drive Saya/CryptoBot_Signals
USE_GDRIVE=true
```

### 📊 No winrate data?

Ini normal jika:
- Belum ada signal yang di-track
- Belum ada signal yang completed (WIN/LOSS)

**Solution**: Track beberapa signal dulu:
```python
from app.signal_tracker_integration import track_signal_given, update_signal_outcome

# Track signal
signal_id = track_signal_given(
    user_id=123456,
    symbol="BTCUSDT",
    timeframe="1h",
    entry_price=50000,
    tp1=51000,
    tp2=52000,
    sl=49500,
    signal_type="LONG"
)

# Update result (WIN)
update_signal_outcome(signal_id, hit_tp=True, pnl_percent=2.5)
```

## 🧪 Integration Test

Run test script untuk verify semua components:

```bash
cd Bismillah
python test_signal_tracking_integration.py
```

**Expected output**:
```
✅ All handlers imported successfully
✅ All integration helpers imported
✅ Scheduler imported successfully
✅ Signal logger initialized
✅ G: drive sync enabled
✅ Command tracking works
✅ Signal tracking works
✅ Signal update works
✅ Winrate calculation works
✅ Signal tracking handlers registered in bot.py
✅ /signal_stats command registered
✅ Scheduler startup added to main.py
```

## 📱 Test Flow

### Complete Test Scenario

1. **Start bot**
   ```bash
   python main.py
   ```

2. **Send test command** (as admin in Telegram)
   ```
   /signal_stats
   ```

3. **Check response**
   - Should show statistics
   - Should show G: drive status
   - Should show file counts

4. **Check winrate**
   ```
   /winrate
   ```

5. **Force sync**
   ```
   /upload_logs
   ```

6. **Verify files in G: drive**
   - Open File Explorer
   - Navigate to `G:\Drive Saya\CryptoBot_Signals\`
   - Check files exist and have recent timestamps

7. **Check Google Drive web**
   - Open https://drive.google.com
   - Look for `CryptoBot_Signals` folder
   - Verify files are synced to cloud

## ✅ Success Indicators

### Bot Startup
```
✅ Bot module imported successfully
✅ Bot initialized successfully
✅ Signal tracking admin commands registered
✅ Signal tracking scheduler started
✅ Application handlers registered successfully
```

### Command Response
- Commands respond immediately
- No error messages
- Data shows correctly
- Files sync to G: drive

### File System
- Files created in `signal_logs/`
- Files synced to `G:\Drive Saya\CryptoBot_Signals\`
- Files appear in Google Drive web interface

## 🎯 What's Next?

### 1. Add Tracking to Commands
Integrate tracking into existing commands:
- `/analyze` - Track analysis requests
- `/futures` - Track futures signals
- `/ai` - Track AI analysis requests

### 2. Monitor Winrate
- Check `/winrate` weekly
- Review patterns in WIN/LOSS
- Iterate based on data

### 3. Deploy to Railway
- System will auto-switch to Supabase Storage
- Weekly reports sent to admin automatically
- Continuous improvement based on data

## 💡 Tips

1. **Test locally first** before deploying to Railway
2. **Check G: drive sync** regularly to ensure data backup
3. **Review weekly reports** for improvement insights
4. **Track all signals** for accurate winrate calculation
5. **Use `/signal_stats`** to monitor system health

---

**Status**: ✅ Ready to test!  
**Commands**: `/signal_stats`, `/winrate`, `/upload_logs`, `/weekly_report`  
**Next**: Restart bot dan test commands di Telegram!
