# 🧪 TAHAP 3: Test Deposit Flow

## 📍 Status Sekarang

✅ Tahap 1: Code preparation - SELESAI
✅ Tahap 2: Database migration - SELESAI
🔄 **Tahap 3: Test deposit flow - SEDANG BERJALAN**

---

## 🎯 Tujuan Testing

Memastikan bahwa:
1. Menu AI Agent bisa dibuka
2. User yang belum deposit melihat pesan "Deposit Diperlukan"
3. Tombol "Deposit Sekarang" berfungsi
4. Wallet address centralized muncul dengan benar
5. Pending deposit tercatat di database

---

## 📋 Langkah-langkah Test

### 1️⃣ Jalankan Bot Lokal

**Buka Command Prompt/Terminal:**

```bash
cd Bismillah
python bot.py
```

**Yang Harus Anda Lihat:**
```
Bot started successfully!
Listening for updates...
```

⚠️ **Jika ada error:**
- Screenshot error-nya
- Kirim ke saya untuk troubleshooting

---

### 2️⃣ Buka Bot di Telegram

1. **Buka Telegram** di HP/Desktop
2. **Cari bot Anda** (nama bot yang sudah Anda buat)
3. **Klik `/start`** atau **`/menu`**

---

### 3️⃣ Test Menu AI Agent

**Klik menu:** `🤖 AI Agent`

**Yang HARUS muncul (jika belum pernah deposit):**

```
🤖 Selamat Datang di AI Agent!

💡 Apa itu AI Agent?
AI Agent adalah autonomous trading agent yang menggunakan Conway credits sebagai bahan bakar untuk beroperasi.

⚠️ Deposit Diperlukan
Untuk menggunakan fitur AI Agent, Anda perlu melakukan deposit terlebih dahulu.

💰 Cara Deposit:
1. Klik tombol "💰 Deposit Sekarang" di bawah
2. Deposit USDT/USDC ke address yang diberikan
3. Credits akan otomatis ditambahkan setelah 12 konfirmasi
4. Setelah deposit, Anda bisa spawn agent dan mulai trading!

📊 Conversion Rate:
• 1 USDT = 100 Conway Credits
• 1 USDC = 100 Conway Credits

🌐 Supported Networks:
• Polygon (Recommended - Low fees)
• Base
• Arbitrum

💡 Minimum Deposit: 5 USDT/USDC
```

**Tombol yang HARUS ada:**
- `💰 Deposit Sekarang`
- `❓ Cara Deposit`
- `🔙 Kembali`

---

### 4️⃣ Test Tombol "Deposit Sekarang"

**Klik tombol:** `💰 Deposit Sekarang`

**Yang HARUS muncul:**

```
💰 Deposit USDT/USDC

📍 Alamat Deposit (Semua User):
0x63116672bef9f26fd906cd2a57550f7a13925822

📱 QR Code:
[Klik untuk melihat QR Code]

🌐 Network yang Didukung:
• Polygon (Direkomendasikan - Biaya rendah)
• Base
• Arbitrum

💱 Conversion Rate:
• 1 USDT = 100 Conway Credits
• 1 USDC = 100 Conway Credits

📊 Contoh:
• Deposit 5 USDT = 500 Conway Credits
• Deposit 10 USDC = 1,000 Conway Credits
• Deposit 50 USDT = 5,000 Conway Credits

⚠️ Penting:
• Minimum deposit: 5 USDT/USDC
• Hanya kirim USDT atau USDC
• JANGAN kirim token lain
• Credits akan ditambahkan otomatis setelah 12 konfirmasi

🔄 Cara Kerja:
1. Kirim USDT/USDC ke address di atas
2. Conway Dashboard akan detect deposit Anda
3. Credits otomatis masuk ke akun Anda
4. Cek balance di menu "📊 Agent Status"

💡 Tip: Gunakan network Polygon untuk biaya gas terendah!
```

**Tombol yang HARUS ada:**
- `❓ Cara Deposit`
- `🔙 Kembali`

---

### 5️⃣ Verifikasi Wallet Address

**PENTING:** Pastikan wallet address yang muncul adalah:

```
0x63116672bef9f26fd906cd2a57550f7a13925822
```

✅ **Jika address ini muncul** = TEST BERHASIL!
❌ **Jika address berbeda** = Ada masalah, screenshot dan kirim ke saya

---

### 6️⃣ Cek Database (Opsional)

Untuk memastikan pending deposit tercatat:

1. **Buka Supabase Dashboard**
2. **Klik "Table Editor"**
3. **Pilih table `pending_deposits`**
4. **Cari user_id Anda** (Telegram user ID)

**Yang harus ada:**
- `user_id`: ID Telegram Anda
- `status`: `waiting`
- `created_at`: Timestamp saat Anda klik deposit

---

## ✅ Checklist Test

Centang setiap item setelah berhasil:

- [ ] Bot bisa dijalankan tanpa error
- [ ] Menu AI Agent bisa dibuka
- [ ] Muncul pesan "Deposit Diperlukan"
- [ ] Tombol "💰 Deposit Sekarang" ada dan bisa diklik
- [ ] Setelah klik, muncul wallet address
- [ ] Wallet address = `0x63116672bef9f26fd906cd2a57550f7a13925822`
- [ ] QR Code link bisa dibuka
- [ ] Instruksi deposit lengkap muncul
- [ ] Tombol "Kembali" berfungsi

---

## 🐛 Troubleshooting

### Bot tidak bisa jalan

**Error: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Error: Database connection failed**
- Cek file `.env`
- Pastikan `SUPABASE_URL` dan `SUPABASE_SERVICE_KEY` benar

### Menu AI Agent tidak muncul

**Solusi:**
1. Restart bot: `Ctrl+C` lalu `python bot.py`
2. Di Telegram, ketik `/start` lagi

### Wallet address salah

**Solusi:**
1. Cek file `.env`
2. Pastikan ada: `CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822`
3. Restart bot

### Tombol tidak berfungsi

**Solusi:**
1. Cek terminal untuk error messages
2. Screenshot error dan kirim ke saya

---

## 📸 Screenshot yang Perlu Anda Ambil

Untuk dokumentasi, ambil screenshot:

1. **Menu AI Agent** (pesan "Deposit Diperlukan")
2. **Halaman Deposit** (dengan wallet address)
3. **Terminal** (jika ada error)

---

## 🎉 Jika Test Berhasil

Setelah semua checklist ✅, laporkan ke saya:

**"Test berhasil! Wallet address muncul dengan benar."**

Lalu kita akan lanjut ke:
- **Tahap 4:** Webhook Receiver (untuk auto-credit)
- **Tahap 5:** Deploy ke Railway

---

## ❌ Jika Ada Masalah

Kirim ke saya:
1. Screenshot error
2. Pesan error di terminal
3. Langkah mana yang gagal

Saya akan bantu troubleshoot! 😊

---

## 📞 Apa Selanjutnya?

Setelah test berhasil, kita punya 2 opsi:

### Opsi A: Lanjut Webhook (Recommended)
- Buat webhook receiver untuk auto-credit
- Integrasi dengan Conway Dashboard
- Test dengan deposit real

### Opsi B: Deploy Dulu ke Railway
- Deploy bot dengan centralized wallet
- Test di production
- Webhook bisa ditambahkan nanti

**Pilih mana?** Saya recommend Opsi A (webhook dulu) supaya sistem lengkap sebelum deploy.

---

**Status:** Tahap 3 - Ready to Test! 🚀

Silakan mulai test sekarang dan kabari saya hasilnya!
