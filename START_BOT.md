# 🚀 Quick Start Guide - CryptoMentor Bot

## ✅ Pre-Flight Check

Bot sudah ditest dan **SIAP DIJALANKAN**! ✨

---

## 🎯 Cara Menjalankan Bot

### Option 1: Direct Run (Recommended)
```bash
cd Bismillah
python main.py
```

### Option 2: Test First, Then Run
```bash
# Test dulu (5 detik)
python start_bot_test.py

# Kalau test OK, jalankan bot
python main.py
```

---

## 📱 Setelah Bot Running

1. **Buka Telegram** dan cari bot Anda
2. **Kirim `/start`** untuk memulai
3. **Test commands:**
   - `/menu` - Lihat menu utama
   - `/price btc` - Cek harga Bitcoin
   - `/help` - Lihat semua command

---

## 🛑 Cara Stop Bot

Tekan `Ctrl + C` di terminal

---

## 🔍 Monitoring Bot

### Check Status
```bash
# Lihat log di terminal
# Bot akan print setiap aktivitas
```

### Common Messages
- `✅ Bot initialized` - Bot siap
- `✅ Application handlers registered` - Handlers OK
- `Received message from user` - Ada user kirim pesan
- `⚠️ Supabase integration failed` - Normal (optional feature)

---

## ⚡ Quick Commands Reference

### User Commands
```
/start          - Mulai bot & registrasi
/menu           - Menu utama
/help           - Bantuan
/price <coin>   - Cek harga
/market         - Overview market
/credits        - Cek saldo kredit
```

### Signal Commands (Premium/Credits)
```
/analyze BTC           - Analisis Bitcoin
/futures ETH 4h        - Signal futures Ethereum
/futures_signals       - Multi-coin signals
```

### AI Commands (Ultra Fast)
```
/ai BTC                - AI analisis Bitcoin
/chat <pesan>          - Chat dengan AI
/aimarket              - Market summary AI
```

### Admin Commands
```
/admin                           - Panel admin
/set_premium <user_id>           - Kasih premium
/grant_credits <user_id> <amt>   - Kasih credits
/signal_on                       - Aktifkan auto signal
/signal_status                   - Status signal
```

---

## 🐛 Troubleshooting

### Bot tidak start?
```bash
# Check environment
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Token:', 'OK' if os.getenv('TELEGRAM_BOT_TOKEN') else 'MISSING')"
```

### Database error?
```bash
# Test database
python -c "from dotenv import load_dotenv; load_dotenv(); from services import get_database; db = get_database(); print('DB OK')"
```

### Import error?
```bash
# Check dependencies
pip install -r requirements.txt
```

---

## 📊 Bot Statistics

Saat ini bot memiliki:
- **1,063 users** terdaftar
- **49 premium users**
- **2 admins** aktif
- **Semua fitur** berfungsi ✅

---

## 💡 Tips

1. **Jangan close terminal** saat bot running
2. **Monitor log** untuk melihat aktivitas
3. **Test dengan akun sendiri** dulu sebelum announce
4. **Backup database** secara berkala

---

## 🎉 Ready to Go!

Bot sudah 100% siap. Tinggal jalankan:

```bash
python main.py
```

**Good luck!** 🚀
