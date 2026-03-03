# 🔧 FIX ERROR: Column "subscription_end" Tidak Ada

## Error yang Terjadi

```
ERROR: 42703: column "subscription_end" does not exist
```

Artinya: Kolom `subscription_end` tidak ada di tabel `users` Anda.

---

## ✅ SOLUSI: Cek Kolom Dulu, Lalu Backup

### LANGKAH 1: Cek Kolom yang Ada

**Paste query ini di SQL Editor** (replace query sebelumnya):

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;
```

**Lalu:**
1. Tekan **F5** atau klik **Run**
2. Lihat hasil di tab Results
3. **Screenshot hasil** dan kirim ke saya

Hasil akan menunjukkan semua kolom yang ada di tabel users.

---

### LANGKAH 2: Backup dengan Query yang Benar

**Setelah tahu kolom apa saja yang ada**, gunakan query ini:

#### Option A: Backup Semua Kolom (Paling Aman)

```sql
SELECT * FROM users ORDER BY telegram_id;
```

**Ini akan export SEMUA kolom yang ada**, jadi tidak akan error.

#### Option B: Backup Kolom Penting Saja

Jika kolom `subscription_end` tidak ada, mungkin namanya berbeda. Coba query ini:

```sql
SELECT 
    telegram_id,
    first_name,
    last_name,
    username,
    is_premium,
    credits,
    created_at
FROM users
ORDER BY telegram_id;
```

**Jika masih error**, berarti ada kolom lain yang tidak ada. Gunakan Option A (`SELECT *`).

---

## 🎯 LANGKAH CEPAT (Recommended)

**Langsung gunakan query ini** (paling aman, tidak akan error):

```sql
SELECT * FROM users ORDER BY telegram_id;
```

**Cara:**
1. **Paste query di atas** di SQL Editor (Ctrl+A, Ctrl+V)
2. **Run** (F5)
3. **Download CSV** dari hasil
4. **Save** sebagai: `backup_users_20260220.csv`

Query `SELECT *` akan export semua kolom yang ada, jadi dijamin tidak error!

---

## 📊 Kenapa Error Terjadi?

Kemungkinan:
1. Database Anda menggunakan nama kolom berbeda (misal: `subscription_expires`, `premium_until`, dll)
2. Kolom `subscription_end` belum dibuat
3. Struktur database berbeda dari dokumentasi

**Solusi:** Gunakan `SELECT *` untuk backup semua data tanpa perlu tahu nama kolom.

---

## ✅ SETELAH BACKUP BERHASIL

**Verifikasi file CSV:**
- File size > 50 KB
- Ada banyak rows (1000+)
- Data terlihat lengkap

**Lalu konfirmasi ke saya:**
"Backup selesai, file CSV sudah tersimpan"

**Next step:**
- Run migration di Supabase
- Deploy code ke Railway

---

## 🆘 Jika Masih Error

**Screenshot dan kirim:**
1. Query yang Anda gunakan
2. Error message lengkap
3. Hasil dari query LANGKAH 1 (list kolom)

Saya akan buatkan query backup yang sesuai dengan struktur database Anda!

---

**COBA SEKARANG:** Paste query `SELECT * FROM users ORDER BY telegram_id;` dan run!

