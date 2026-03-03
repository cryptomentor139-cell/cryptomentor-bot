# 📝 Summary: Cara Running Bot

## 🎯 Cara Paling Mudah

### Windows:
```bash
cd Bismillah
python main.py
```

### Linux/Mac:
```bash
cd Bismillah
python3 main.py
```

**Stop:** Tekan `Ctrl + C`

---

## 🚀 Cara dengan Script Helper

### Windows:
```bash
# Double-click atau:
start_bot.bat
```

### Linux/Mac:
```bash
chmod +x start_bot.sh
./start_bot.sh
```

---

## 🔧 Cara untuk Production (Server)

### Metode 1: Screen (Recommended)
```bash
cd Bismillah
screen -S cryptobot
python3 main.py
# Tekan Ctrl+A lalu D untuk detach

# Kembali ke session:
screen -r cryptobot
```

### Metode 2: PM2 (Advanced)
```bash
cd Bismillah
pm2 start main.py --name cryptobot --interpreter python3
pm2 save

# Monitoring:
pm2 status
pm2 logs cryptobot
```

### Metode 3: Nohup (Simple)
```bash
cd Bismillah
nohup python3 main.py > bot.log 2>&1 &

# Stop:
ps aux | grep main.py
kill <PID>
```

---

## ⚠️ PENTING!

**HANYA 1 BOT BOLEH JALAN DENGAN TOKEN YANG SAMA!**

Jika bot sudah jalan di server:
1. Stop bot di server dulu
2. Baru jalankan di local untuk testing
3. Setelah selesai, stop local dan start lagi di server

---

## 📊 Cek Status Bot

```bash
python verify_bot_running.py
```

---

## 📚 File Dokumentasi

1. **README_QUICK_START.md** - Panduan singkat
2. **CARA_MENJALANKAN_BOT.md** - Panduan lengkap
3. **start_bot.bat** - Script Windows
4. **start_bot.sh** - Script Linux/Mac
5. **stop_bot.sh** - Stop bot di Linux/Mac

---

## 🎓 Yang Perlu Diingat

1. File yang dijalankan: **main.py** (BUKAN bot.py)
2. Konfigurasi ada di: **.env**
3. Dependencies: **requirements.txt**
4. Hanya 1 instance per token
5. Bot di server Anda sudah jalan dengan baik!

---

## ✅ Status Saat Ini

- ✅ Bot sudah di-deploy di server
- ✅ Bot merespon dengan baik
- ✅ Semua fitur berfungsi
- ✅ DeepSeek AI terintegrasi
- ✅ Broadcast system sudah diperbaiki
- ✅ Database (Local + Supabase) terhubung

**Bot Anda sudah production-ready!** 🎉
