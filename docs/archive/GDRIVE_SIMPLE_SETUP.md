# 🚀 Google Drive Setup - Versi Simple (Tanpa OAuth API)

## 💡 Konsep

Menggunakan **Google Drive for Desktop** yang sudah ter-mount di `G:\` - tidak perlu ribet dengan OAuth API!

## ✅ Keuntungan Metode Ini

1. **Super Simple** - Tidak perlu setup OAuth credentials
2. **No API Limits** - Tidak ada quota limit
3. **Real-time Sync** - Google Drive for Desktop auto-sync
4. **Easy Access** - Bisa akses langsung dari File Explorer
5. **No Authentication** - Sekali setup, jalan terus

## 📋 Setup (5 Menit)

### 1. Install Google Drive for Desktop

**Download:**
- Windows: https://www.google.com/drive/download/
- Mac: https://www.google.com/drive/download/

**Install:**
1. Download installer
2. Run installer
3. Login dengan Google account
4. Pilih "Stream files" atau "Mirror files"
5. Done!

### 2. Verify G: Drive Mounted

**Windows:**
```cmd
dir G:\
```

**Jika berhasil**, kamu akan lihat folder Google Drive kamu.

**Jika G: tidak ada**, cek di File Explorer - mungkin di drive letter lain (H:, I:, dll)

### 3. Set Environment Variable (Optional)

Jika Google Drive ter-mount di drive letter lain, set di `.env`:

```bash
# Jika di H: drive
GDRIVE_PATH=H:/CryptoBot_Signals

# Jika di I: drive
GDRIVE_PATH=I:/CryptoBot_Signals

# Default: G:/CryptoBot_Signals
```

### 4. Test

```bash
python -c "import os; print('✅ G: drive available' if os.path.exists('G:/') else '❌ G: drive not found')"
```

## 🎯 Cara Kerja

### Automatic Mode

Bot akan **otomatis detect** G: drive:

```python
# Di signal_logger.py
if os.path.exists('G:/'):
    # Langsung save ke G:/CryptoBot_Signals
    self.log_dir = Path('G:/CryptoBot_Signals')
else:
    # Fallback ke local
    self.log_dir = Path('signal_logs')
```

### File Structure

```
G:/CryptoBot_Signals/
├── prompts_2026-02-16.jsonl      # User prompts
├── prompts_2026-02-17.jsonl
├── active_signals.jsonl           # Active signals
└── completed_signals.jsonl        # Closed signals
```

### Sync Schedule

**Otomatis:**
- Setiap file baru langsung ke G: drive
- Google Drive for Desktop auto-sync ke cloud
- Real-time backup

**Manual:**
- `/upload_logs` - Force sync semua files

## 🔧 Commands

### Check Status
```bash
/signal_stats
```

Output:
```
📊 STATISTIK SIGNAL TRACKING

☁️ GOOGLE DRIVE SYNC:
• Status: ✅ Enabled
• Path: G:/CryptoBot_Signals
• Local Files: 15
• GDrive Files: 15
• In Sync: ✅ Yes
```

### Force Sync
```bash
/upload_logs
```

Output:
```
✅ Sync complete!

📊 Synced: 15 files
❌ Failed: 0 files
```

## 🎨 Advantages vs OAuth API

| Aspek | OAuth API | G: Drive Mount | Winner |
|-------|-----------|----------------|---------|
| Setup Time | 15-30 min | 5 min | 🟢 Mount |
| Complexity | High | Low | 🟢 Mount |
| API Limits | Yes (quota) | No | 🟢 Mount |
| Authentication | Need refresh | Once | 🟢 Mount |
| Real-time | No | Yes | 🟢 Mount |
| Access | API only | File Explorer | 🟢 Mount |
| Reliability | Depends on API | Very high | 🟢 Mount |

## 🐛 Troubleshooting

### G: Drive Not Found

**Check:**
```cmd
# Windows
wmic logicaldisk get name

# PowerShell
Get-PSDrive -PSProvider FileSystem
```

**Solution:**
1. Pastikan Google Drive for Desktop running
2. Check system tray icon
3. Restart Google Drive for Desktop
4. Set `GDRIVE_PATH` di .env jika di drive lain

### Sync Not Working

**Check:**
```bash
/signal_stats
```

**Solution:**
1. Verify G: drive accessible
2. Check folder permissions
3. Restart bot
4. Manual sync: `/upload_logs`

### Files Not Syncing to Cloud

**Check:**
- Google Drive for Desktop status
- Internet connection
- Google Drive storage quota

**Solution:**
1. Open Google Drive for Desktop
2. Check sync status
3. Pause & resume sync
4. Check error messages

## 💡 Tips

### 1. Monitor Sync Status
```bash
# Check regularly
/signal_stats
```

### 2. Backup Strategy
```
Primary: G:/CryptoBot_Signals (auto-sync to cloud)
Fallback: signal_logs/ (local backup)
```

### 3. Access from Anywhere
- Open Google Drive web
- Navigate to CryptoBot_Signals folder
- Download files as needed

### 4. Share with Team
- Right-click folder in G: drive
- Share → Add people
- Set permissions

## 🎯 Migration from OAuth API

Jika sebelumnya pakai OAuth API:

1. **Uninstall PyDrive2**
   ```bash
   pip uninstall PyDrive2
   ```

2. **Remove credentials**
   ```bash
   rm gdrive_credentials.json
   rm gdrive_token.json
   ```

3. **Update .env**
   ```bash
   # Remove these (not needed anymore)
   # GDRIVE_CREDENTIALS_FILE=...
   # GDRIVE_FOLDER_NAME=...
   
   # Add this (optional)
   GDRIVE_PATH=G:/CryptoBot_Signals
   ```

4. **Restart bot**
   ```bash
   python bot.py
   ```

## ✅ Verification Checklist

- [ ] Google Drive for Desktop installed
- [ ] G: drive visible in File Explorer
- [ ] Bot started successfully
- [ ] `/signal_stats` shows "✅ Enabled"
- [ ] Files created in G:/CryptoBot_Signals
- [ ] Files syncing to cloud (check web)

## 🎉 Done!

Sistem tracking sekarang:
- ✅ Langsung save ke G: drive
- ✅ Auto-sync ke cloud
- ✅ No API complexity
- ✅ Real-time backup
- ✅ Easy access

**Jauh lebih simple dari OAuth API!** 🚀

---

**Version**: 2.0.0 (Simplified)  
**Last Updated**: 2026-02-16  
**Setup Time**: 5 menit
