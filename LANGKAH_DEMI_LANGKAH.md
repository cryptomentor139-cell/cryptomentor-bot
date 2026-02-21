# 🎯 Panduan Langkah Demi Langkah - Centralized Wallet

## 📍 Anda Sekarang Di Sini: TAHAP 1 SELESAI ✅

Saya sudah mempersiapkan semuanya. Sekarang kita tinggal jalankan migration ke database.

---

## 🚀 LANGKAH 1: Buka Supabase Dashboard

### Apa yang harus dilakukan:

1. **Buka browser** (Chrome, Firefox, Edge, apapun)

2. **Ketik URL ini:**
   ```
   https://supabase.com/dashboard
   ```

3. **Login** dengan akun Supabase Anda

4. **Pilih project** Anda yang bernama: `xrbqnocovfymdikngaza`

### Screenshot yang akan Anda lihat:
```
┌─────────────────────────────────────┐
│  Supabase Dashboard                 │
├─────────────────────────────────────┤
│  Projects:                          │
│  ▶ xrbqnocovfymdikngaza  ← KLIK INI│
│                                     │
└─────────────────────────────────────┘
```

---

## 🚀 LANGKAH 2: Buka SQL Editor

### Apa yang harus dilakukan:

1. **Di sidebar kiri**, cari menu **"SQL Editor"**

2. **Klik "SQL Editor"**

3. **Klik tombol "+ New Query"** (tombol hijau di pojok kanan atas)

### Screenshot yang akan Anda lihat:
```
┌─────────────────────────────────────┐
│ ☰ Menu                              │
├─────────────────────────────────────┤
│ 🏠 Home                             │
│ 📊 Table Editor                     │
│ 📝 SQL Editor      ← KLIK INI       │
│ 🔐 Authentication                   │
│ 📦 Storage                          │
└─────────────────────────────────────┘
```

Setelah klik SQL Editor, Anda akan lihat:
```
┌─────────────────────────────────────┐
│ SQL Editor                          │
│                                     │
│ [+ New Query]  ← KLIK INI           │
└─────────────────────────────────────┘
```

---

## 🚀 LANGKAH 3: Copy Migration SQL

### Apa yang harus dilakukan:

1. **Buka file ini di editor Anda:**
   ```
   Bismillah/migrations/006_centralized_wallet_system.sql
   ```

2. **Select semua isi file:**
   - Tekan `Ctrl + A` (Windows/Linux)
   - Atau `Cmd + A` (Mac)

3. **Copy:**
   - Tekan `Ctrl + C` (Windows/Linux)
   - Atau `Cmd + C` (Mac)

### Tips:
- File ini panjang (sekitar 400 baris)
- Pastikan Anda copy SEMUA dari awal sampai akhir
- Jangan copy sebagian saja

---

## 🚀 LANGKAH 4: Paste ke SQL Editor

### Apa yang harus dilakukan:

1. **Klik di area SQL Editor** (kotak putih besar)

2. **Paste:**
   - Tekan `Ctrl + V` (Windows/Linux)
   - Atau `Cmd + V` (Mac)

3. **Anda akan lihat** banyak kode SQL muncul

### Screenshot yang akan Anda lihat:
```
┌─────────────────────────────────────┐
│ SQL Editor                          │
├─────────────────────────────────────┤
│ -- Migration 006: Centralized...   │
│ CREATE TABLE IF NOT EXISTS...      │
│ ...                                 │
│ (banyak kode SQL)                   │
│                                     │
│                    [Run] ← TOMBOL   │
└─────────────────────────────────────┘
```

---

## 🚀 LANGKAH 5: Jalankan Migration

### Apa yang harus dilakukan:

1. **Klik tombol "Run"** (pojok kanan bawah)
   - Atau tekan `Ctrl + Enter`

2. **Tunggu 5-10 detik**

3. **Anda akan lihat pesan:**
   ```
   ✅ Success. No rows returned
   ```

### Jika ada error:
- Jangan panik!
- Screenshot error-nya
- Kirim ke saya, saya akan bantu

---

## 🚀 LANGKAH 6: Verifikasi Table Sudah Dibuat

### Apa yang harus dilakukan:

1. **Klik "Table Editor"** di sidebar kiri

2. **Scroll ke bawah**, Anda harus lihat 5 table baru:
   - ✅ `pending_deposits`
   - ✅ `deposit_transactions`
   - ✅ `user_credits_balance`
   - ✅ `webhook_logs`
   - ✅ `credit_transactions`

### Screenshot yang akan Anda lihat:
```
┌─────────────────────────────────────┐
│ Tables                              │
├─────────────────────────────────────┤
│ ▶ users                             │
│ ▶ custodial_wallets                 │
│ ▶ pending_deposits      ← BARU!     │
│ ▶ deposit_transactions  ← BARU!     │
│ ▶ user_credits_balance  ← BARU!     │
│ ▶ webhook_logs          ← BARU!     │
│ ▶ credit_transactions   ← BARU!     │
└─────────────────────────────────────┘
```

---

## ✅ SELESAI! TAHAP 2 COMPLETE!

Jika Anda sudah lihat 5 table baru di atas, berarti **BERHASIL!** 🎉

---

## 📞 Apa Selanjutnya?

Setelah migration berhasil, kita akan lanjut ke:

### TAHAP 3: Test Deposit Flow
- Test klik menu AI Agent
- Test klik Deposit Now
- Lihat apakah muncul wallet address yang benar

### TAHAP 4: Buat Webhook Receiver
- Terima notifikasi dari Conway Dashboard
- Credit user otomatis

### TAHAP 5: Deploy ke Railway
- Update bot di Railway
- Test dengan deposit real

---

## 🆘 Butuh Bantuan?

**Jika stuck di langkah manapun:**
1. Screenshot layar Anda
2. Kirim ke saya
3. Saya akan bantu troubleshoot

**Jika berhasil:**
1. Bilang "sudah selesai"
2. Kita lanjut ke tahap berikutnya

---

## 📋 Checklist Progress

- [x] Tahap 1: Persiapan code ✅
- [ ] Tahap 2: Apply migration (Anda sedang di sini)
- [ ] Tahap 3: Test deposit flow
- [ ] Tahap 4: Webhook receiver
- [ ] Tahap 5: Deploy to Railway

---

**Sekarang:** Silakan ikuti Langkah 1-6 di atas.

**Setelah selesai:** Bilang ke saya "migration sudah jalan" atau "ada error"

Saya tunggu kabar Anda! 😊
