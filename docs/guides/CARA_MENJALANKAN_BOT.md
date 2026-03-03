# 🚀 Cara Menjalankan CryptoMentor AI Bot

## 📋 Persyaratan

- Python 3.8 atau lebih baru
- pip (Python package manager)
- File `.env` dengan konfigurasi yang benar

---

## 🔧 Instalasi Dependencies

### Windows (CMD/PowerShell):
```bash
cd Bismillah
pip install -r requirements.txt
```

### Linux/Mac:
```bash
cd Bismillah
pip3 install -r requirements.txt
```

---

## ▶️ Cara Menjalankan Bot

### 1️⃣ Metode Standar (Foreground)

Bot akan berjalan di terminal dan menampilkan log secara real-time.

**Windows:**
```bash
cd Bismillah
python main.py
```

**Linux/Mac:**
```bash
cd Bismillah
python3 main.py
```

**Untuk Stop:**
- Tekan `Ctrl + C`

---

### 2️⃣ Metode Background (Recommended untuk Server)

Bot akan berjalan di background dan tetap jalan meskipun terminal ditutup.

**Windows (PowerShell):**
```powershell
cd Bismillah
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

**Linux/Mac (dengan nohup):**
```bash
cd Bismillah
nohup python3 main.py > bot.log 2>&1 &
```

**Untuk Stop (Linux/Mac):**
```bash
# Cari process ID
ps aux | grep main.py

# Stop dengan PID
kill <PID>
```

**Untuk Stop (Windows):**
```powershell
# Cari process
Get-Process python

# Stop dengan nama
Stop-Process -Name python
```

---

### 3️⃣ Metode dengan Screen (Linux/Mac - Recommended)

Screen memungkinkan bot tetap jalan meskipun SSH terputus.

**Install screen (jika belum ada):**
```bash
# Ubuntu/Debian
sudo apt-get install screen

# CentOS/RHEL
sudo yum install screen
```

**Jalankan bot:**
```bash
cd Bismillah

# Buat session baru bernama "cryptobot"
screen -S cryptobot

# Jalankan bot
python3 main.py

# Detach dari screen (bot tetap jalan)
# Tekan: Ctrl + A, lalu D
```

**Kembali ke session:**
```bash
# Lihat semua session
screen -ls

# Attach ke session
screen -r cryptobot
```

**Stop bot:**
```bash
# Attach ke session
screen -r cryptobot

# Stop bot dengan Ctrl + C

# Keluar dari screen
exit
```

---

### 4️⃣ Metode dengan PM2 (Node.js Process Manager)

PM2 adalah process manager yang powerful untuk production.

**Install PM2:**
```bash
npm install -g pm2
```

**Jalankan bot:**
```bash
cd Bismillah
pm2 start main.py --name cryptobot --interpreter python3
```

**Perintah PM2:**
```bash
# Lihat status
pm2 status

# Lihat logs
pm2 logs cryptobot

# Restart bot
pm2 restart cryptobot

# Stop bot
pm2 stop cryptobot

# Delete dari PM2
pm2 delete cryptobot

# Auto-start saat server reboot
pm2 startup
pm2 save
```

---

## 📊 Monitoring Bot

### Cek Status Bot:
```bash
cd Bismillah
python verify_bot_running.py
```

### Cek Logs (jika menggunakan nohup):
```bash
cd Bismillah
tail -f bot.log
```

### Cek Logs (jika menggunakan PM2):
```bash
pm2 logs cryptobot
```

---

## ⚠️ PENTING: Hanya 1 Instance!

**JANGAN menjalankan 2 bot dengan token yang sama secara bersamaan!**

Jika bot sudah jalan di server, STOP dulu sebelum menjalankan di local:

1. Stop bot di server
2. Jalankan bot di local untuk testing
3. Stop bot di local
4. Start lagi bot di server

---

## 🔍 Troubleshooting

### Bot tidak merespon:
1. Cek apakah ada bot lain yang jalan dengan token sama
2. Cek file `.env` sudah benar
3. Cek koneksi internet
4. Lihat logs untuk error

### Error "Module not found":
```bash
pip install -r requirements.txt
```

### Error "Permission denied":
```bash
# Linux/Mac
chmod +x main.py
```

### Bot crash terus:
```bash
# Lihat error di logs
# Pastikan semua dependencies terinstall
# Cek file .env lengkap
```

---

## 📝 File Penting

- `main.py` - Entry point bot (GUNAKAN INI)
- `bot.py` - Class utama bot (JANGAN jalankan langsung)
- `.env` - Konfigurasi (TOKEN, API keys, dll)
- `requirements.txt` - List dependencies

---

## 🎯 Quick Start

**Untuk testing cepat:**
```bash
cd Bismillah
python main.py
```

**Untuk production (Linux/Mac):**
```bash
cd Bismillah
screen -S cryptobot
python3 main.py
# Tekan Ctrl+A lalu D untuk detach
```

**Untuk production (dengan PM2):**
```bash
cd Bismillah
pm2 start main.py --name cryptobot --interpreter python3
pm2 save
```

---

## 📞 Support

Jika ada masalah:
1. Cek logs untuk error message
2. Pastikan `.env` sudah benar
3. Pastikan tidak ada bot lain yang jalan dengan token sama
4. Jalankan `python verify_bot_running.py` untuk diagnostik
