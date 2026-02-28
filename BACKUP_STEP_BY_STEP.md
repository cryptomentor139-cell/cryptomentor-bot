# Backup Database - Step by Step dengan Screenshot

## 🎯 Anda Sudah di SQL Editor! Tinggal 3 Langkah Lagi

### ⚠️ TIDAK ADA TOMBOL "NEW QUERY"? TIDAK MASALAH!

Interface Supabase sudah berubah. Editor sudah terbuka di depan Anda. Langsung paste query saja!

### Langkah 1: Paste SQL Query ✅

**Di editor yang sekarang terbuka** (area besar dengan text "Hit CTRL+K to generate query..."):

1. **Klik di area editor** (area putih/hitam besar)
2. **Select all** (Ctrl+A) untuk hapus text yang ada
3. **Paste SQL ini** (Ctrl+V):

```sql
SELECT telegram_id, first_name, last_name, username, is_premium, subscription_end, credits FROM users ORDER BY telegram_id;
```

**Tips:**
- Jika ada text di editor, select all (Ctrl+A) dulu
- Paste query di atas (Ctrl+V)
- Query akan muncul di editor

### Langkah 2: Run Query ✅

**Ada 2 cara run query:**

**Cara 1:** Klik tombol **"Run"** (biasanya pojok kanan bawah, warna hijau/biru)

**Cara 2:** Tekan **F5** di keyboard (lebih cepat!)

**Tunggu 1-5 detik**, hasil akan muncul di bawah editor (tab "Results" atau "Output")

**Jika tidak ada tombol Run:**
- Coba tekan F5
- Atau cari icon ▶️ (play button)
- Atau klik kanan di editor → Run Query

### Langkah 3: Download CSV ✅

**Setelah hasil muncul di bawah editor:**

1. **Lihat hasil query** (tabel dengan data users)
2. **Cari tombol Download:**
   - Biasanya di pojok kanan atas hasil
   - Icon download (⬇️) atau text "Download" atau "Export"
   - Atau icon titik tiga (⋮) → Export → CSV
3. **Klik Download/Export**
4. **Pilih format CSV** (jika ada pilihan)
5. **Save file** dengan nama: `backup_users_20260220.csv`

**Lokasi tombol download bisa di:**
- Toolbar di atas hasil query (pojok kanan)
- Menu titik tiga (⋮) di hasil
- Klik kanan di hasil → Export
- Tombol "Download" atau icon ⬇️

**Jika tidak ketemu tombol download:**
- Screenshot hasil query dan kirim ke saya
- Atau coba cara manual (lihat Troubleshooting)

### Verifikasi Backup Berhasil ✅

**Buka file CSV yang di-download:**

1. Double-click file `backup_users_20260220.csv`
2. Akan terbuka di Excel atau Notepad
3. **Check:**
   - Ada banyak rows (1200+ users)
   - Ada kolom: telegram_id, first_name, is_premium
   - Data terlihat lengkap

**Contoh data yang benar:**
```
telegram_id,first_name,is_premium,subscription_end,credits
1187119989,Bil,true,2025-09-08T12:23:45,0
6478958291,Zeed,true,null,0
5460058203,Muhammad,true,null,0
```

### Troubleshooting

#### Tidak Ada Tombol Download?
**Solusi 1:** Scroll ke kanan di tab Results

**Solusi 2:** Copy manual:
1. Select all hasil (Ctrl+A)
2. Copy (Ctrl+C)
3. Paste ke Excel
4. Save as CSV

**Solusi 3:** Gunakan query yang lebih kecil:
```sql
-- Export first 100 users untuk test
SELECT * FROM users LIMIT 100;
```

#### Query Error?
**Check:**
- Pastikan tidak ada typo
- Pastikan semicolon (;) di akhir
- Try query sederhana dulu:
```sql
SELECT COUNT(*) FROM users;
```

#### File CSV Kosong?
- Query mungkin tidak return data
- Check di tab Results ada data atau tidak
- Try query lagi

### Setelah Backup Selesai

✅ **File CSV tersimpan aman?** 

Lanjut ke deployment:
1. Baca `START_HERE_AUTOMATON_DEPLOY.md`
2. Step 2: Run migration di Supabase
3. Step 3: Deploy ke Railway

---

## Quick Reference

**SQL Query untuk Backup:**
```sql
SELECT * FROM users ORDER BY telegram_id;
```

**Lokasi Save File:**
- Desktop: `C:\Users\YourName\Desktop\backup_users_20260220.csv`
- Documents: `C:\Users\YourName\Documents\backup_users_20260220.csv`

**File Size Expected:**
- 1000 users ≈ 100 KB
- 1200 users ≈ 120 KB
- Jika < 10 KB, ada yang salah

**Next Step:**
Setelah backup selesai, baca `START_HERE_AUTOMATON_DEPLOY.md` untuk deployment!
