# 📊 Signal Tracking & Winrate System

Sistem lengkap untuk tracking prompt user, signal, dan laporan winrate mingguan otomatis ke admin.

## 🎯 Fitur Utama

1. **📝 Logging Semua Prompt User**
   - Setiap command tersimpan dalam file JSONL
   - Format: `signal_logs/prompts_YYYY-MM-DD.jsonl`

2. **📈 Tracking Signal & Winrate**
   - Track setiap signal yang diberikan
   - Update WIN/LOSS otomatis
   - Hitung winrate dan avg PnL

3. **☁️ Auto Upload ke Google Drive**
   - Upload logs setiap hari jam 23:00 WIB
   - Backup otomatis untuk dokumentasi

4. **📊 Laporan Mingguan ke Admin**
   - Kirim setiap Senin jam 09:00 WIB
   - Berisi winrate, analisis, rekomendasi
   - Dikirim via Telegram ke semua admin

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd Bismillah
pip install -r requirements.txt
```

### 2. Setup Google Drive

1. Buat project di Google Cloud Console
2. Enable Google Drive API
3. Download OAuth credentials → `gdrive_credentials.json`
4. Copy ke folder Bismillah

**Detail lengkap**: Lihat `SIGNAL_TRACKING_SETUP.md`

### 3. Run Setup Script

```bash
python setup_signal_tracking.py
```

### 4. Integrate ke Bot

Lihat contoh lengkap di `TRACKING_INTEGRATION_EXAMPLE.md`

**Minimal integration**:

```python
# Di bot.py setup_application()
from app.handlers_signal_tracking import cmd_winrate, cmd_weekly_report
self.application.add_handler(CommandHandler("winrate", cmd_winrate))
self.application.add_handler(CommandHandler("weekly_report", cmd_weekly_report))

# Di bot.py main()
from app.scheduler import task_scheduler
asyncio.create_task(task_scheduler.start())

# Di setiap command handler
from app.signal_tracker_integration import track_user_command
track_user_command(user.id, user.username, "/analyze", "BTC", "1h")
```

## 📱 Admin Commands

```bash
/winrate              # Lihat winrate 7 hari terakhir
/winrate 30           # Lihat winrate 30 hari
/weekly_report        # Generate laporan manual
/upload_logs          # Upload logs manual
/signal_stats         # Statistik tracking
```

## 📊 Contoh Laporan Mingguan

```
📊 LAPORAN MINGGUAN SIGNAL
🗓️ Periode: 10/02/2026 - 17/02/2026

━━━━━━━━━━━━━━━━━━━━━━

📈 PERFORMA SIGNAL:
• Total Signal: 45
• Win: 32 ✅
• Loss: 13 ❌
• Winrate: 71.11% 🎯
• Avg PnL: +3.25%

━━━━━━━━━━━━━━━━━━━━━━

👥 AKTIVITAS USER:
• Total Prompts: 156
• Rata-rata per hari: 22

━━━━━━━━━━━━━━━━━━━━━━

📊 ANALISIS:
✅ Performa EXCELLENT! Signal sangat akurat.
💰 Profit margin sangat bagus!

━━━━━━━━━━━━━━━━━━━━━━

🎯 REKOMENDASI:
• Maintain current strategy
• Consider increasing signal frequency
```

## 📁 File Structure

```
Bismillah/
├── app/
│   ├── signal_logger.py              # Core logging
│   ├── gdrive_uploader.py            # Google Drive integration
│   ├── weekly_report.py              # Report generator
│   ├── scheduler.py                  # Auto tasks
│   ├── signal_tracker_integration.py # Helper functions
│   └── handlers_signal_tracking.py   # Admin commands
├── signal_logs/
│   ├── prompts_2026-02-16.jsonl      # Daily prompts
│   ├── active_signals.jsonl          # Active signals
│   └── completed_signals.jsonl       # Closed signals
├── gdrive_credentials.json           # Google OAuth (gitignored)
├── gdrive_token.json                 # Auth token (gitignored)
└── SIGNAL_TRACKING_SETUP.md          # Full documentation
```

## 🔧 Troubleshooting

### Google Drive tidak connect

```bash
rm gdrive_token.json
python setup_signal_tracking.py
```

### Scheduler tidak jalan

```bash
# Check di bot logs
tail -f bot.log | grep "Scheduler"
```

### Winrate tidak akurat

```bash
# Verify files
ls -la signal_logs/
cat signal_logs/completed_signals.jsonl
```

## 📚 Documentation

- `SIGNAL_TRACKING_SETUP.md` - Setup lengkap Google Drive
- `TRACKING_INTEGRATION_EXAMPLE.md` - Contoh integrasi code
- `setup_signal_tracking.py` - Quick setup script

## ✅ Checklist

- [ ] Install PyDrive2
- [ ] Setup Google Drive credentials
- [ ] Run setup script
- [ ] Integrate tracking di commands
- [ ] Register admin commands
- [ ] Start scheduler
- [ ] Test manual commands
- [ ] Verify auto upload (23:00)
- [ ] Verify weekly report (Senin 09:00)

## 💡 Tips

- Gunakan `/signal_stats` untuk monitor data
- Check Google Drive folder setiap hari
- Review laporan mingguan untuk improve strategy
- Backup `signal_logs/` folder berkala

## 🎯 Benefits

1. **Dokumentasi Lengkap** - Semua prompt user tersimpan
2. **Iterasi Signal** - Analisis winrate untuk improve
3. **Backup Otomatis** - Data aman di Google Drive
4. **Laporan Terstruktur** - Admin dapat monitor performa
5. **Data-Driven** - Keputusan berdasarkan data real

---

**Created by**: CryptoMentor AI Team
**Version**: 1.0.0
**Last Updated**: 2026-02-16
