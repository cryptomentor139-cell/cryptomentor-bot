# 📊 Signal Tracking & Winrate System

Sistem untuk tracking semua prompt user, signal yang diberikan, dan laporan winrate mingguan otomatis.

## 🎯 Fitur

### 1. **Logging Prompt User**
- Semua command user tersimpan dalam file JSONL
- Format: `signal_logs/prompts_YYYY-MM-DD.jsonl`
- Data: timestamp, user_id, username, command, symbol, timeframe

### 2. **Tracking Signal & Winrate**
- Setiap signal yang diberikan di-track
- Update otomatis WIN/LOSS berdasarkan TP/SL
- Hitung winrate dan avg PnL

### 3. **Upload ke Google Drive**
- Otomatis upload logs setiap hari jam 23:00
- Folder: `CryptoBot_Signals`
- Backup semua data untuk dokumentasi

### 4. **Laporan Mingguan ke Admin**
- Otomatis kirim setiap Senin jam 09:00
- Berisi: winrate, total signal, avg PnL, analisis
- Dikirim ke semua admin via Telegram

## 📦 Installation

### 1. Install Dependencies

```bash
pip install PyDrive2
```

Update `requirements.txt`:
```
PyDrive2==1.20.0
```

### 2. Setup Google Drive API

#### A. Buat Project di Google Cloud Console

1. Buka https://console.cloud.google.com/
2. Buat project baru: "CryptoBot Signals"
3. Enable Google Drive API:
   - APIs & Services → Library
   - Cari "Google Drive API"
   - Klik Enable

#### B. Buat OAuth Credentials

1. APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: Desktop app
4. Name: "CryptoBot Desktop"
5. Download JSON → Simpan sebagai `gdrive_credentials.json`

#### C. Setup Credentials

```bash
# Copy credentials ke folder bot
cp gdrive_credentials.json Bismillah/
```

### 3. First Time Authentication

Jalankan script test untuk authenticate:

```python
from app.gdrive_uploader import gdrive_uploader

# Ini akan buka browser untuk login Google
# Setelah login, token akan tersimpan di gdrive_token.json
```

## 🚀 Usage

### Admin Commands

```bash
# Lihat winrate 7 hari terakhir
/winrate

# Lihat winrate 30 hari terakhir
/winrate 30

# Generate laporan mingguan manual
/weekly_report

# Upload logs ke Google Drive manual
/upload_logs

# Lihat statistik tracking
/signal_stats
```

### Automatic Tasks

1. **Daily Upload** (23:00 WIB)
   - Upload semua logs hari ini ke Google Drive
   - Backup otomatis

2. **Weekly Report** (Senin 09:00 WIB)
   - Generate laporan winrate mingguan
   - Kirim ke semua admin
   - Analisis performa

## 📁 File Structure

```
signal_logs/
├── prompts_2026-02-16.jsonl          # Prompt user harian
├── prompts_2026-02-17.jsonl
├── active_signals.jsonl               # Signal yang masih aktif
└── completed_signals.jsonl            # Signal yang sudah closed
```

## 🔧 Integration dengan Bot

### 1. Track User Command

```python
from app.signal_tracker_integration import track_user_command

# Di setiap command handler
track_user_command(
    user_id=user.id,
    username=user.username,
    command="/analyze",
    symbol="BTCUSDT",
    timeframe="1h"
)
```

### 2. Track Signal Given

```python
from app.signal_tracker_integration import track_signal_given

# Setelah generate signal
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

### 3. Update Signal Result

```python
from app.signal_tracker_integration import update_signal_outcome

# Ketika signal hit TP atau SL
update_signal_outcome(
    signal_id="123_BTCUSDT_1234567890",
    hit_tp=True,  # True jika hit TP, False jika hit SL
    pnl_percent=2.5  # Persentase profit/loss
)
```

## 📊 Laporan Mingguan Format

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

━━━━━━━━━━━━━━━━━━━━━━

📅 Laporan dibuat: 17/02/2026 09:00 WIB
🤖 CryptoMentor AI Bot
```

## 🔐 Security Notes

1. **Jangan commit credentials**:
   ```bash
   # Add to .gitignore
   gdrive_credentials.json
   gdrive_token.json
   signal_logs/
   ```

2. **Protect admin commands**:
   - Semua command tracking hanya untuk admin
   - Validasi user_id sebelum execute

3. **Data privacy**:
   - Logs berisi user_id dan username
   - Pastikan Google Drive folder private

## 🐛 Troubleshooting

### Google Drive Upload Gagal

```bash
# Re-authenticate
rm gdrive_token.json
python -c "from app.gdrive_uploader import gdrive_uploader"
```

### Scheduler Tidak Jalan

```bash
# Check logs
tail -f bot.log | grep "Scheduler"

# Manual trigger
/upload_logs
/weekly_report
```

### Winrate Tidak Akurat

```bash
# Check signal files
ls -la signal_logs/
cat signal_logs/completed_signals.jsonl

# Verify tracking integration
/signal_stats
```

## 📈 Next Steps

1. ✅ Setup Google Drive credentials
2. ✅ Test authentication
3. ✅ Integrate tracking di command handlers
4. ✅ Test manual commands
5. ✅ Verify automatic scheduler
6. ✅ Monitor first weekly report

## 💡 Tips

- Gunakan `/signal_stats` untuk monitor data
- Check Google Drive folder setiap hari
- Review laporan mingguan untuk improve strategy
- Backup `signal_logs/` folder secara berkala
