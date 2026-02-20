# Backup Database Supabase (Free Plan) - TANPA PREMIUM

## ⚠️ Supabase Free Plan Tidak Ada Auto Backup

Jangan khawatir! Kita bisa backup manual via SQL export. Ini GRATIS dan AMAN.

## Cara Backup Manual (5 Menit) ✅

### Step 1: Login ke Supabase ✅
1. Buka https://supabase.com
2. Login dengan akun Anda
3. Pilih project **CryptoMentor AI**

### Step 2: Buka SQL Editor ✅
1. Klik **SQL Editor** di sidebar kiri
2. Klik tombol **New** (pojok kanan atas, warna hijau)
3. Akan muncul editor kosong dengan text "Hit CTRL+K to generate query or just start typing"

### Step 3: Paste SQL Export Query
**Copy-paste SQL ini ke editor** (replace semua text yang ada):

```sql
SELECT 
    telegram_id,
    first_name,
    last_name,
    username,
    language_code,
    is_premium,
    credits,
    subscription_end,
    referred_by,
    referral_code,
    premium_referral_code,
    premium_earnings,
    created_at,
    banned
FROM users
ORDER BY telegram_id;
```

### Step 4: Run Query
1. Klik tombol **Run** (pojok kanan bawah, warna hijau) atau tekan **F5**
2. Tunggu hasil muncul di tab "Results" (1-5 detik)
3. Anda akan lihat tabel dengan semua data users

### Step 5: Download Results
1. Di tab "Results", cari tombol **Download** atau icon download
2. Pilih format **CSV**
3. Save file dengan nama: `backup_users_20260220.csv`
4. Simpan di tempat aman (Desktop, Google Drive, dll)

### Step 6: Verifikasi Backup
1. Buka file CSV yang di-download
2. Check jumlah rows (harus ada 1200+ users)
3. Check ada kolom: telegram_id, first_name, is_premium, dll

## Screenshot Lokasi

```
Supabase Dashboard
└── SQL Editor (sidebar kiri)
    └── New query (tombol hijau)
        └── Paste SQL
        └── Run (F5)
        └── Download CSV (pojok kanan atas)
```

## Backup Tambahan (Optional tapi Recommended)

### Backup Premium Users Only
```sql
-- Export premium users only
SELECT 
    telegram_id,
    first_name,
    username,
    is_premium,
    subscription_end,
    credits
FROM users
WHERE is_premium = TRUE
ORDER BY subscription_end NULLS FIRST;
```

Download sebagai: `backup_premium_users_20260220.csv`

### Backup Lifetime Users Only
```sql
-- Export lifetime users only
SELECT 
    telegram_id,
    first_name,
    username,
    is_premium,
    subscription_end,
    credits
FROM users
WHERE is_premium = TRUE AND subscription_end IS NULL
ORDER BY telegram_id;
```

Download sebagai: `backup_lifetime_users_20260220.csv`

## Verifikasi Backup Berhasil

### Check File Size
- `backup_users_20260220.csv` harus > 50 KB
- Jika < 10 KB, ada yang salah

### Check Jumlah Rows
1. Buka file CSV di Excel/Notepad
2. Count jumlah baris (exclude header)
3. Harus ada 1200+ rows

### Check Sample Data
Pastikan ada data seperti:
```
telegram_id,first_name,is_premium,subscription_end
1187119989,Bil,true,2025-09-08T12:23:45
6478958291,Zeed,true,null
```

## Restore dari Backup (Jika Diperlukan)

### Jika Migration Gagal:

#### Step 1: Hapus Column Baru
```sql
-- Remove automaton_access column
ALTER TABLE users DROP COLUMN IF EXISTS automaton_access;
```

#### Step 2: Verify Data Masih Utuh
```sql
-- Check users still exist
SELECT COUNT(*) FROM users;

-- Check premium users
SELECT COUNT(*) FROM users WHERE is_premium = TRUE;
```

Jika data hilang, lanjut ke Step 3.

#### Step 3: Restore dari CSV (Manual)
1. Buka Supabase Dashboard
2. Table Editor → users
3. Import CSV yang di-backup
4. Map columns dengan benar
5. Click Import

## Checklist Backup

- [ ] ✅ Login ke Supabase
- [ ] ✅ Buka SQL Editor
- [ ] ✅ Run export query
- [ ] ✅ Download CSV (> 50 KB)
- [ ] ✅ Save di tempat aman
- [ ] ✅ Verifikasi jumlah rows (1200+)
- [ ] ✅ (Optional) Backup premium users
- [ ] ✅ (Optional) Backup lifetime users

## Setelah Backup Selesai

Lanjut ke deployment:
1. ✅ Backup completed (CSV downloaded)
2. ⏳ Run Supabase migration (next step)
3. ⏳ Deploy code to Railway
4. ⏳ Test in production

## Troubleshooting

### Query Timeout
- Database terlalu besar
- Coba export per batch:
```sql
-- Export first 500 users
SELECT * FROM users LIMIT 500 OFFSET 0;

-- Export next 500 users
SELECT * FROM users LIMIT 500 OFFSET 500;
```

### Download Button Tidak Muncul
- Scroll ke kanan di hasil query
- Atau copy-paste manual dari hasil

### File CSV Corrupt
- Try export lagi
- Atau gunakan format JSON:
```sql
-- Export as JSON (copy hasil manual)
SELECT json_agg(users) FROM users;
```

## Alternative: Backup via Python (Jika Ada Credentials)

Jika Anda punya `SUPABASE_URL` dan `SUPABASE_SERVICE_KEY`:

```bash
python backup_supabase_users.py
```

Tapi cara SQL export di atas lebih mudah dan tidak perlu credentials!

## Important Notes

✅ **CSV Export = Backup Valid**: File CSV bisa digunakan untuk restore

⚠️ **Simpan di 2 Tempat**: 
- Local (Desktop/Documents)
- Cloud (Google Drive/Dropbox)

🔒 **Jangan Share**: File berisi data sensitif users

⏰ **Backup Sebelum Migration**: WAJIB!

## Next Steps

**SEKARANG**: Export users table ke CSV

**SETELAH BACKUP**: Baca `AUTOMATON_ACCESS_DEPLOYMENT.md` untuk migration

---

**MULAI SEKARANG**: 
1. Login ke Supabase
2. SQL Editor → New query
3. Copy-paste SQL export
4. Run → Download CSV
5. Save file aman

✅ Selesai? Lanjut deployment!
