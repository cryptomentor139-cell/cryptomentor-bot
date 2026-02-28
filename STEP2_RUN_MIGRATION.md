# 🚀 STEP 2: RUN MIGRATION DI SUPABASE

## ✅ Backup Selesai! Sekarang Run Migration

Backup sudah aman tersimpan di `backup_users_20260220.csv`. Sekarang kita tambahkan kolom `automaton_access` ke database.

---

## 📝 LANGKAH 1: BUKA SQL EDITOR LAGI

Anda masih di Supabase SQL Editor kan? Kalau sudah close, buka lagi:

1. Login ke https://supabase.com
2. Pilih project **CryptoMentor AI**
3. Klik **SQL Editor** di sidebar kiri

---

## 📋 LANGKAH 2: PASTE MIGRATION SQL

**Copy SQL ini** (klik untuk select, lalu Ctrl+C):

```sql
-- Add automaton_access column
ALTER TABLE users ADD COLUMN IF NOT EXISTS automaton_access BOOLEAN DEFAULT FALSE;

-- Grant access to existing lifetime users (subscription_end IS NULL)
UPDATE users 
SET automaton_access = TRUE 
WHERE is_premium = TRUE AND subscription_end IS NULL;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_automaton_access ON users(automaton_access);

-- Verify migration success
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN automaton_access = TRUE THEN 1 ELSE 0 END) as users_with_access,
    SUM(CASE WHEN is_premium = TRUE AND automaton_access = FALSE THEN 1 ELSE 0 END) as premium_need_to_pay
FROM users;
```

**Lalu:**
1. **Klik di SQL Editor** (area besar)
2. **Select all** (Ctrl+A)
3. **Paste SQL di atas** (Ctrl+V)

---

## ▶️ LANGKAH 3: RUN MIGRATION

**Tekan F5** atau klik tombol **"Run"**

**Tunggu 2-5 detik...**

Hasil akan muncul di tab "Results" dengan statistik:
- `total_users`: Total semua users
- `users_with_access`: Lifetime users yang dapat akses gratis
- `premium_need_to_pay`: Premium users yang perlu bayar Rp2,000,000

---

## ✅ VERIFIKASI MIGRATION BERHASIL

**Hasil yang diharapkan:**

```
total_users | users_with_access | premium_need_to_pay
------------|-------------------|--------------------
1200+       | 40-50             | 5-15
```

**Artinya:**
- ✅ Kolom `automaton_access` berhasil ditambahkan
- ✅ Lifetime users (40-50 orang) dapat akses otomatis
- ✅ Regular premium users (5-15 orang) perlu bayar

---

## 🔍 LANGKAH 4: CEK DETAIL (OPTIONAL)

**Ingin lihat detail users yang dapat akses?** Run query ini:

```sql
-- List lifetime users with automatic access
SELECT telegram_id, first_name, username, is_premium, automaton_access
FROM users
WHERE automaton_access = TRUE
ORDER BY telegram_id
LIMIT 20;
```

**Ingin lihat premium users yang perlu bayar?** Run query ini:

```sql
-- List premium users who need to pay
SELECT telegram_id, first_name, username, is_premium, automaton_access
FROM users
WHERE is_premium = TRUE AND automaton_access = FALSE
ORDER BY telegram_id;
```

---

## 🆘 TROUBLESHOOTING

### ❌ Error: Column Already Exists

```
ERROR: column "automaton_access" already exists
```

**Artinya:** Migration sudah pernah dijalankan sebelumnya.

**Solusi:** Skip migration, langsung ke Step 3 (Deploy code).

### ❌ Error: Column "subscription_end" Does Not Exist

**Artinya:** Database Anda tidak punya kolom `subscription_end`.

**Solusi:** Gunakan query alternatif ini:

```sql
-- Add automaton_access column
ALTER TABLE users ADD COLUMN IF NOT EXISTS automaton_access BOOLEAN DEFAULT FALSE;

-- Grant access to ALL premium users (karena tidak ada subscription_end)
UPDATE users 
SET automaton_access = TRUE 
WHERE is_premium = TRUE;

-- Create index
CREATE INDEX IF NOT EXISTS idx_users_automaton_access ON users(automaton_access);

-- Verify
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN automaton_access = TRUE THEN 1 ELSE 0 END) as users_with_access
FROM users;
```

**Note:** Ini akan memberikan akses ke SEMUA premium users. Jika Anda ingin membatasi, edit manual nanti via admin tool.

### ❌ Error: Permission Denied

**Artinya:** Akun Anda tidak punya permission untuk ALTER TABLE.

**Solusi:** 
1. Check apakah Anda login sebagai owner project
2. Atau gunakan Service Role Key (di Settings → API)

### ❌ Migration Berhasil tapi `users_with_access` = 0

**Artinya:** Tidak ada lifetime users, atau kolom `subscription_end` tidak NULL untuk lifetime users.

**Solusi:** 
- Check struktur database Anda
- Atau grant access manual nanti via admin tool

---

## 📊 APA YANG TERJADI?

Migration ini melakukan 3 hal:

1. **Tambah kolom `automaton_access`** (BOOLEAN, default FALSE)
   - FALSE = Belum bayar, tidak bisa akses Automaton
   - TRUE = Sudah bayar atau lifetime user, bisa akses

2. **Grant akses otomatis ke lifetime users**
   - Lifetime users = `is_premium = TRUE` dan `subscription_end IS NULL`
   - Mereka dapat akses GRATIS (tidak perlu bayar Rp2,000,000)

3. **Buat index** untuk query lebih cepat
   - Index pada kolom `automaton_access`

---

## ✅ SETELAH MIGRATION BERHASIL

**Konfirmasi ke saya:**

"Migration selesai, hasil: [total_users] users, [users_with_access] dapat akses"

**Contoh:**
"Migration selesai, hasil: 1234 users, 45 dapat akses"

**Lalu kita lanjut:**
1. ✅ Backup completed
2. ✅ Migration completed
3. ⏳ Deploy code ke Railway (next step)

---

## 🔄 ROLLBACK (Jika Ada Masalah)

**Jika migration gagal atau ada error**, rollback dengan query ini:

```sql
-- Remove automaton_access column
ALTER TABLE users DROP COLUMN IF EXISTS automaton_access;

-- Drop index
DROP INDEX IF EXISTS idx_users_automaton_access;
```

Lalu restore dari backup CSV jika perlu.

---

**MULAI SEKARANG!** Copy SQL migration di atas dan paste di SQL Editor Supabase Anda.

