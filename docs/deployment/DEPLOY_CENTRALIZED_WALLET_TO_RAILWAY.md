# 🚀 Deploy Centralized Wallet ke Railway

## 📍 Status

✅ Tahap 1: Code preparation - SELESAI
✅ Tahap 2: Database migration - SELESAI
🔄 **Tahap 3: Deploy ke Railway - SEDANG BERJALAN**

---

## 🎯 Yang Akan Di-Deploy

### File yang Sudah Diupdate:
1. ✅ `menu_handlers.py` - Deposit flow dengan centralized wallet
2. ✅ `.env` - Tambah `CENTRALIZED_WALLET_ADDRESS`
3. ✅ Database Supabase - 5 table baru sudah dibuat

### Yang Perlu Dilakukan:
1. Push code ke GitHub
2. Railway auto-deploy
3. Update environment variable di Railway
4. Test di Telegram

---

## 📋 Langkah Deploy

### 1️⃣ Push Code ke GitHub

**Buka Command Prompt/Terminal di folder Bismillah:**

```bash
cd Bismillah

# Add semua perubahan
git add .

# Commit dengan pesan jelas
git commit -m "feat: implement centralized wallet system for AI Agent deposits"

# Push ke GitHub
git push origin main
```

⚠️ **Jika ada conflict:**
```bash
git pull origin main
# Resolve conflict jika ada
git push origin main
```

---

### 2️⃣ Update Environment Variable di Railway

Railway perlu tahu tentang centralized wallet address.

**Langkah:**

1. **Buka Railway Dashboard**
   - https://railway.app/dashboard

2. **Pilih Project Bot Anda**

3. **Klik Tab "Variables"**

4. **Tambah Variable Baru:**
   - **Variable Name:** `CENTRALIZED_WALLET_ADDRESS`
   - **Value:** `0x63116672bef9f26fd906cd2a57550f7a13925822`
   - Klik **"Add"**

5. **Verify Variable Lain (Pastikan Ada):**
   - ✅ `SUPABASE_URL`
   - ✅ `SUPABASE_SERVICE_KEY`
   - ✅ `TELEGRAM_BOT_TOKEN`
   - ✅ `CONWAY_API_KEY`

---

### 3️⃣ Tunggu Auto-Deploy

Setelah push ke GitHub, Railway akan otomatis:

1. **Detect perubahan** di GitHub
2. **Build** bot dengan code terbaru
3. **Deploy** bot baru
4. **Restart** bot

**Cara Cek Deploy:**

1. Di Railway Dashboard, klik tab **"Deployments"**
2. Lihat status deployment terbaru:
   - 🟡 **Building** = Sedang build
   - 🟢 **Success** = Deploy berhasil
   - 🔴 **Failed** = Ada error

**Waktu Deploy:** Biasanya 2-5 menit

---

### 4️⃣ Cek Logs (Opsional)

Untuk memastikan bot running dengan benar:

1. **Klik tab "Logs"** di Railway
2. **Cari pesan:**
   ```
   Bot started successfully!
   ```

⚠️ **Jika ada error:**
- Screenshot logs
- Kirim ke saya untuk troubleshoot

---

### 5️⃣ Test di Telegram

Setelah deploy berhasil, test deposit flow:

1. **Buka bot di Telegram**
2. **Ketik `/start` atau `/menu`**
3. **Klik "🤖 AI Agent"**
4. **Klik "💰 Deposit Sekarang"**

**Yang HARUS muncul:**
```
💰 Deposit USDT/USDC

📍 Alamat Deposit (Semua User):
0x63116672bef9f26fd906cd2a57550f7a13925822

[QR Code]

🌐 Network yang Didukung:
• Polygon (Direkomendasikan - Biaya rendah)
• Base
• Arbitrum
```

✅ **Jika wallet address `0x6311...5822` muncul** = DEPLOY BERHASIL!

---

## ✅ Checklist Deploy

- [ ] Code di-push ke GitHub
- [ ] Railway auto-deploy triggered
- [ ] Environment variable `CENTRALIZED_WALLET_ADDRESS` ditambahkan
- [ ] Deploy status = Success (hijau)
- [ ] Bot logs menunjukkan "Bot started successfully"
- [ ] Test di Telegram - wallet address muncul dengan benar

---

## 🐛 Troubleshooting

### Deploy Failed (Red)

**Solusi:**
1. Cek logs di Railway untuk error message
2. Biasanya karena:
   - Syntax error di code
   - Missing dependency
   - Environment variable salah

### Bot Tidak Respond di Telegram

**Solusi:**
1. Cek logs di Railway
2. Pastikan bot running (ada log "Bot started")
3. Restart deployment:
   - Klik "..." di deployment
   - Pilih "Restart"

### Wallet Address Tidak Muncul

**Solusi:**
1. Cek environment variable di Railway
2. Pastikan `CENTRALIZED_WALLET_ADDRESS` ada dan benar
3. Restart bot

### Error "Database unavailable"

**Solusi:**
1. Cek `SUPABASE_URL` dan `SUPABASE_SERVICE_KEY`
2. Pastikan migration 006 sudah di-apply di Supabase
3. Test koneksi Supabase

---

## 📸 Screenshot yang Perlu

Untuk dokumentasi:

1. **Railway Deployment Status** (Success/hijau)
2. **Railway Variables** (list semua env vars)
3. **Telegram - Halaman Deposit** (dengan wallet address)
4. **Railway Logs** (jika ada error)

---

## 🎉 Setelah Deploy Berhasil

Laporkan ke saya:

**"Deploy berhasil! Wallet address muncul di Telegram."**

Lalu kita bisa:
- ✅ Mark Tahap 3 sebagai complete
- 🚀 Lanjut ke Tahap 4: Webhook Receiver (opsional)
- 🎯 Atau langsung test dengan deposit real

---

## 📞 Apa Selanjutnya?

### Opsi A: Webhook Receiver (Recommended)
- Buat webhook endpoint untuk terima notifikasi dari Conway
- Auto-credit user setelah deposit
- Fully automated system

### Opsi B: Manual Credit (Temporary)
- User deposit ke wallet
- Admin manually credit user via Supabase
- Webhook bisa ditambahkan nanti

**Pilih mana?** Saya recommend Opsi A untuk sistem yang fully automated.

---

## 🔗 Quick Links

- **Railway Dashboard:** https://railway.app/dashboard
- **GitHub Repo:** (link repo Anda)
- **Supabase Dashboard:** https://supabase.com/dashboard
- **Conway Dashboard:** https://dashboard.conway.tech

---

**Status:** Ready to Deploy! 🚀

Silakan mulai deploy sekarang dengan langkah-langkah di atas!
