# 🚀 Quick Start - CryptoMentor AI Bot

## ⚡ Cara Tercepat Menjalankan Bot

### Windows:
```bash
# Double-click file ini:
start_bot.bat

# Atau di terminal:
cd Bismillah
python main.py
```

### Linux/Mac:
```bash
cd Bismillah

# Beri permission (hanya sekali)
chmod +x start_bot.sh stop_bot.sh

# Jalankan bot
./start_bot.sh

# Atau langsung:
python3 main.py
```

---

## 🛑 Cara Stop Bot

### Windows:
- Tekan `Ctrl + C` di terminal

### Linux/Mac:
```bash
# Jika jalan di foreground
Ctrl + C

# Jika jalan di background
./stop_bot.sh
```

---

## 📋 Checklist Sebelum Menjalankan

- [ ] Python 3.8+ sudah terinstall
- [ ] File `.env` sudah ada dan terisi lengkap
- [ ] Dependencies sudah terinstall (`pip install -r requirements.txt`)
- [ ] **PENTING:** Tidak ada bot lain yang jalan dengan token yang sama

---

## ⚠️ PENTING!

**Hanya boleh ada 1 bot yang jalan dengan token yang sama!**

Jika bot sudah jalan di server, STOP dulu sebelum menjalankan di local.

---

## 🔍 Cek Status Bot

```bash
python verify_bot_running.py
```

---

## 📚 Dokumentasi Lengkap

Lihat file `CARA_MENJALANKAN_BOT.md` untuk panduan lengkap.

---

## 🎯 Struktur File

```
Bismillah/
├── main.py              ← JALANKAN FILE INI
├── bot.py               ← Jangan jalankan langsung
├── .env                 ← Konfigurasi (TOKEN, API keys)
├── requirements.txt     ← Dependencies
├── start_bot.bat        ← Starter untuk Windows
├── start_bot.sh         ← Starter untuk Linux/Mac
└── stop_bot.sh          ← Stopper untuk Linux/Mac
```

---

## 💡 Tips

1. **Testing di Local**: Stop bot di server dulu
2. **Production**: Gunakan PM2 atau screen
3. **Monitoring**: Cek logs secara berkala
4. **Update**: Stop bot → Update code → Start bot

---

## 🆘 Troubleshooting

### Bot tidak merespon?
→ Cek apakah ada bot lain yang jalan dengan token sama

### Error "Module not found"?
→ Jalankan: `pip install -r requirements.txt`

### Bot crash?
→ Lihat error di terminal, cek file `.env`

---

## 📞 Need Help?

1. Baca `CARA_MENJALANKAN_BOT.md`
2. Jalankan `python verify_bot_running.py`
3. Cek logs untuk error message
