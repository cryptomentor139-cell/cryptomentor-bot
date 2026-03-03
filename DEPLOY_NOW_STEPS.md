# 🚀 Deploy Bot ke Railway - LANGKAH DEMI LANGKAH

## Status Saat Ini
✅ Code sudah diperbaiki (main.py)
✅ Code sudah di-push ke GitHub
❌ Railway belum deploy otomatis
⏳ Perlu manual trigger deploy

## LANGKAH 1: Buka Railway Dashboard

1. Buka browser, ke: https://railway.app
2. Login dengan akun Anda
3. Pilih project: **industrious-dream**
4. Pilih service: **web** atau **production**

## LANGKAH 2: Connect GitHub (WAJIB - agar Railway pull code terbaru)

**⚠️ PENTING:** Jangan pakai "Redeploy" - itu akan deploy code lama yang error!

### Cara yang BENAR:

1. Klik tab **"Settings"**
2. Scroll ke bagian **"Source"**
3. Lihat status:
   - **Jika belum connected:** Klik **"Connect GitHub"**
   - **Jika sudah connected tapi ke repo lain:** Klik **"Disconnect"** dulu, lalu **"Connect GitHub"**
4. Pilih repository: **cryptomentor139-cell/cryptomentor-bot**
5. Pilih branch: **main**
6. Klik **"Connect"**
7. Railway akan otomatis trigger deploy dengan code terbaru
8. Tunggu 1-2 menit

### Alternatif (jika sudah connected ke repo yang benar):

1. Klik tab **"Deployments"**
2. Klik tombol **"Deploy"** di kanan atas (warna ungu/biru)
3. Railway akan pull code terbaru dari GitHub
4. Tunggu 1-2 menit

## LANGKAH 3: Cek Deploy Logs

1. Setelah deploy mulai, klik deployment yang baru
2. Klik tab **"Deploy Logs"**
3. Tunggu sampai muncul output seperti ini:

```
🚀 Starting CryptoMentor AI Bot...
✅ Bot initialized with 2 admin(s)
✅ Manual signal handlers registered
✅ Admin premium handlers registered
✅ Menu system handlers registered
✅ Application handlers registered successfully
🚀 CryptoMentor AI Bot is running...
🤖 Bot username: @CryptoMentorAI_bot
🔄 Polling for updates...
```

## LANGKAH 4: Test Bot di Telegram

1. Buka Telegram
2. Cari bot: **@CryptoMentorAI_bot** (atau nama bot Anda)
3. Kirim command:
   ```
   /start
   ```
4. Bot harus merespon dengan menu welcome

## LANGKAH 5: Test Fitur Lain

```
/menu       - Tampilkan menu utama
/help       - Panduan command
/price btc  - Cek harga Bitcoin
/credits    - Cek saldo kredit
```

## Troubleshooting

### ❌ Deploy Logs Kosong
**Solusi:**
1. Cek tab **"Build Logs"** (bukan Deploy Logs)
2. Lihat apakah ada error saat install dependencies
3. Jika ada error, screenshot dan tunjukkan ke saya

### ❌ Bot Tidak Merespon
**Solusi:**
1. Cek Deploy Logs untuk error messages
2. Pastikan logs menunjukkan "Polling for updates..."
3. Cek Environment Variables (langkah 6)

### ❌ Error: "TELEGRAM_BOT_TOKEN not found"
**Solusi:**
1. Klik tab **"Variables"**
2. Cek apakah `TELEGRAM_BOT_TOKEN` ada
3. Jika tidak ada, tambahkan (lihat langkah 6)

## LANGKAH 6: Cek Environment Variables (Jika Bot Error)

1. Klik tab **"Variables"**
2. Pastikan ada variable ini (MINIMAL):

```
TELEGRAM_BOT_TOKEN = 8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
ADMIN1 = 1187119989
ADMIN2 = 7079544380
```

3. Jika tidak ada, klik **"New Variable"**
4. Masukkan name dan value
5. Klik **"Add"**
6. Deploy ulang (langkah 2)

## LANGKAH 7: Setup Auto-Deploy (Optional - untuk masa depan)

Agar Railway auto-deploy setiap kali push ke GitHub:

1. Klik tab **"Settings"**
2. Scroll ke bagian **"Source"**
3. Klik **"Connect GitHub"**
4. Pilih repository: **cryptomentor139-cell/cryptomentor-bot**
5. Pilih branch: **main**
6. Klik **"Connect"**
7. Selesai! Sekarang setiap push ke GitHub akan auto-deploy

## Estimasi Waktu
- Deploy: 1-2 menit
- Bot ready: 2-3 menit total
- Test: 30 detik

## Jika Masih Bermasalah

Screenshot dan tunjukkan:
1. Deploy Logs (tab Deploy Logs)
2. Build Logs (tab Build Logs)
3. Variables (tab Variables)
4. Error message di Telegram (jika ada)

Saya akan bantu troubleshoot lebih lanjut.
