# 🎮 Command Reference - Signal Tracking System

## 📱 Admin Commands

### View Winrate
```bash
/winrate
```
Menampilkan winrate 7 hari terakhir

**Output:**
```
📊 WINRATE SIGNAL (7 HARI TERAKHIR)
• Total Signal: 45
• Win: 32 ✅
• Loss: 13 ❌
• Winrate: 71.11% 🎯
• Avg PnL: +3.25%
```

---

### View Winrate Custom Period
```bash
/winrate 30
```
Menampilkan winrate 30 hari terakhir (bisa diganti angka lain)

---

### Generate Weekly Report
```bash
/weekly_report
```
Generate dan tampilkan laporan mingguan lengkap

**Output:**
```
📊 LAPORAN MINGGUAN SIGNAL
🗓️ Periode: 10/02/2026 - 17/02/2026

📈 PERFORMA SIGNAL:
• Total Signal: 45
• Win: 32 ✅
• Loss: 13 ❌
• Winrate: 71.11% 🎯
• Avg PnL: +3.25%

👥 AKTIVITAS USER:
• Total Prompts: 156
• Rata-rata per hari: 22

📊 ANALISIS:
✅ Performa EXCELLENT!
💰 Profit margin sangat bagus!

🎯 REKOMENDASI:
• Maintain current strategy
```

---

### Upload Logs to Google Drive
```bash
/upload_logs
```
Upload semua logs ke Google Drive secara manual

**Output:**
```
✅ Logs uploaded successfully!
```

---

### View Signal Statistics
```bash
/signal_stats
```
Menampilkan statistik tracking system

**Output:**
```
📊 STATISTIK SIGNAL TRACKING

📝 DATA TERSIMPAN:
• Total Prompts: 156
• Active Signals: 12
• Completed Signals: 45
• Log Files: 7

💡 Commands:
• /winrate - Lihat winrate
• /weekly_report - Generate laporan
• /upload_logs - Upload ke GDrive
```

---

## 💻 Setup Commands

### Install Dependencies
```bash
pip install PyDrive2
```

### Run Setup Script
```bash
python setup_signal_tracking.py
```

### Run Integration Helper
```bash
python integrate_signal_tracking.py
```

---

## 🔧 Python Integration Code

### Track User Command
```python
from app.signal_tracker_integration import track_user_command

track_user_command(
    user_id=user.id,
    username=user.username,
    command="/analyze",
    symbol="BTC",
    timeframe="1h"
)
```

### Track Signal Given
```python
from app.signal_tracker_integration import track_signal_given

signal_id = track_signal_given(
    user_id=user.id,
    symbol="BTCUSDT",
    timeframe="1h",
    entry_price=50000,
    tp1=51000,
    tp2=52000,
    sl=49500,
    signal_type="LONG"
)
```

### Update Signal Result
```python
from app.signal_tracker_integration import update_signal_outcome

update_signal_outcome(
    signal_id="123_BTCUSDT_1234567890",
    hit_tp=True,  # True = WIN, False = LOSS
    pnl_percent=2.5
)
```

### Get Current Winrate
```python
from app.signal_tracker_integration import get_current_winrate

stats = get_current_winrate(days=7)
print(f"Winrate: {stats['winrate']}%")
```

---

## 📁 File Commands

### View Prompt Logs
```bash
# Linux/Mac
cat signal_logs/prompts_2026-02-16.jsonl

# Windows
type signal_logs\prompts_2026-02-16.jsonl
```

### View Active Signals
```bash
# Linux/Mac
cat signal_logs/active_signals.jsonl

# Windows
type signal_logs\active_signals.jsonl
```

### View Completed Signals
```bash
# Linux/Mac
cat signal_logs/completed_signals.jsonl

# Windows
type signal_logs\completed_signals.jsonl
```

### Count Total Prompts
```bash
# Linux/Mac
wc -l signal_logs/prompts_*.jsonl

# Windows
find /c /v "" signal_logs\prompts_*.jsonl
```

---

## 🔍 Debugging Commands

### Check if Tracking Working
```bash
python -c "from app.signal_tracker_integration import track_user_command; track_user_command(123, 'test', '/test', 'BTC', '1h'); print('✅ Tracking works!')"
```

### Test Winrate Calculation
```bash
python -c "from app.signal_tracker_integration import get_current_winrate; print(get_current_winrate())"
```

### Test Google Drive Connection
```bash
python -c "from app.gdrive_uploader import gdrive_uploader; print('✅ Connected' if gdrive_uploader.enabled else '❌ Not connected')"
```

### Test Weekly Report Generation
```bash
python -c "import asyncio; from app.weekly_report import weekly_reporter; print(asyncio.run(weekly_reporter.generate_report()))"
```

---

## 🗂️ Directory Commands

### Create Log Directory
```bash
mkdir signal_logs
```

### List All Log Files
```bash
# Linux/Mac
ls -la signal_logs/

# Windows
dir signal_logs\
```

### Check File Sizes
```bash
# Linux/Mac
du -sh signal_logs/*

# Windows
dir signal_logs\ /s
```

### Backup Logs
```bash
# Linux/Mac
tar -czf signal_logs_backup.tar.gz signal_logs/

# Windows
powershell Compress-Archive -Path signal_logs -DestinationPath signal_logs_backup.zip
```

---

## 🔐 Git Commands

### Add to .gitignore
```bash
echo "gdrive_credentials.json" >> .gitignore
echo "gdrive_token.json" >> .gitignore
echo "signal_logs/" >> .gitignore
```

### Check Ignored Files
```bash
git status --ignored
```

---

## 📊 Analysis Commands

### Count Wins vs Losses
```bash
# Linux/Mac
grep -c '"result": "WIN"' signal_logs/completed_signals.jsonl
grep -c '"result": "LOSS"' signal_logs/completed_signals.jsonl

# Windows (PowerShell)
(Select-String -Path signal_logs\completed_signals.jsonl -Pattern '"result": "WIN"').Count
(Select-String -Path signal_logs\completed_signals.jsonl -Pattern '"result": "LOSS"').Count
```

### Find Signals for Specific Symbol
```bash
# Linux/Mac
grep "BTCUSDT" signal_logs/active_signals.jsonl

# Windows (PowerShell)
Select-String -Path signal_logs\active_signals.jsonl -Pattern "BTCUSDT"
```

### Count Prompts by Command
```bash
# Linux/Mac
grep -o '"command": "[^"]*"' signal_logs/prompts_*.jsonl | sort | uniq -c

# Windows (PowerShell)
Select-String -Path signal_logs\prompts_*.jsonl -Pattern '"command": "([^"]*)"' | 
  ForEach-Object { $_.Matches.Groups[1].Value } | 
  Group-Object | 
  Select-Object Count, Name
```

---

## 🚀 Bot Management Commands

### Start Bot with Tracking
```bash
python bot.py
```

### Check Bot Logs for Tracking
```bash
# Linux/Mac
tail -f bot.log | grep -i "tracking\|scheduler"

# Windows (PowerShell)
Get-Content bot.log -Wait | Select-String -Pattern "tracking|scheduler"
```

### Restart Bot
```bash
# Linux/Mac
pkill -f bot.py && python bot.py

# Windows
taskkill /F /IM python.exe && python bot.py
```

---

## 📅 Scheduled Task Info

### Daily Upload
- **Time**: 23:00 WIB
- **Action**: Upload logs to Google Drive
- **Files**: prompts_*.jsonl, active_signals.jsonl, completed_signals.jsonl

### Weekly Report
- **Time**: Senin 09:00 WIB
- **Action**: Generate and send report to admins
- **Recipients**: All admin IDs in .env

---

## 💡 Quick Tips

### Check if System Running
```bash
/signal_stats
```

### Force Upload Now
```bash
/upload_logs
```

### Get Latest Winrate
```bash
/winrate
```

### Generate Report Anytime
```bash
/weekly_report
```

---

## 🆘 Emergency Commands

### Clear All Logs (DANGER!)
```bash
# Backup first!
rm -rf signal_logs/*
```

### Reset Google Drive Auth
```bash
rm gdrive_token.json
python setup_signal_tracking.py
```

### Verify All Systems
```bash
python setup_signal_tracking.py
```

---

**Quick Reference Card**  
**Version**: 1.0.0  
**Last Updated**: 2026-02-16
