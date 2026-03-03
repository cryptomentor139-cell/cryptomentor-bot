# 📦 Cara Create Bucket di Supabase - Step by Step

## 🎯 Langkah-Langkah (2 Menit)

### Step 1: Buka Storage Menu

Dari dashboard yang kamu lihat sekarang:

1. **Lihat sidebar kiri** (menu vertikal)
2. **Cari icon yang mirip folder/storage** 📁
3. **Klik "Storage"**

Atau scroll ke bawah di sidebar sampai ketemu menu "Storage"

### Step 2: Klik "New Bucket"

Setelah masuk ke Storage page:

1. Kamu akan lihat halaman kosong (karena belum ada bucket)
2. **Cari tombol hijau "New Bucket"** atau **"Create a new bucket"**
3. **Klik tombol tersebut**

### Step 3: Isi Form Bucket

Popup/form akan muncul dengan fields:

#### Field 1: Name
```
cryptobot-signals
```
**Penting**: Nama harus **persis** seperti ini (lowercase, pakai dash)

#### Field 2: Public bucket
```
☐ Public bucket (JANGAN CENTANG!)
```
**Penting**: Biarkan **TIDAK dicentang** - bucket harus private!

#### Field 3: File size limit (optional)
```
50 MB
```
Atau biarkan default

#### Field 4: Allowed MIME types (optional)
```
(kosongkan - allow all)
```

### Step 4: Create Bucket

1. **Review settings**:
   - Name: `cryptobot-signals` ✅
   - Public: ❌ (not checked)
   
2. **Klik tombol "Create bucket"** atau **"Save"**

3. **Wait** - Bucket akan dibuat (1-2 detik)

### Step 5: Verify

Setelah create:

1. Kamu akan kembali ke Storage page
2. Sekarang ada bucket baru: **cryptobot-signals**
3. Klik bucket tersebut - akan kosong (normal, belum ada file)

## ✅ Done!

Bucket sudah siap digunakan!

## 🎨 Visual Guide

### Sidebar Menu:
```
🏠 Home
📊 Table Editor
🔐 Authentication
📁 Storage          ← KLIK INI!
📡 Database
⚙️ Settings
```

### Storage Page (Empty):
```
┌─────────────────────────────────────┐
│  Storage                            │
│                                     │
│  No buckets yet                     │
│                                     │
│  [+ New Bucket]  ← KLIK INI!       │
└─────────────────────────────────────┘
```

### Create Bucket Form:
```
┌─────────────────────────────────────┐
│  Create a new bucket                │
│                                     │
│  Name *                             │
│  [cryptobot-signals]                │
│                                     │
│  ☐ Public bucket                    │
│  (JANGAN CENTANG!)                  │
│                                     │
│  File size limit                    │
│  [50] MB                            │
│                                     │
│  [Cancel]  [Create bucket]          │
└─────────────────────────────────────┘
```

### After Create:
```
┌─────────────────────────────────────┐
│  Storage                            │
│                                     │
│  📦 cryptobot-signals               │
│     Private • 0 objects • 0 B       │
│                                     │
└─────────────────────────────────────┘
```

## 🔍 Troubleshooting

### Tidak Ketemu Menu Storage?

**Coba:**
1. Scroll sidebar ke bawah
2. Atau klik icon "☰" (hamburger menu) di kiri atas
3. Atau ketik "Storage" di search box

### Tombol "New Bucket" Tidak Ada?

**Kemungkinan:**
1. Sudah ada bucket dengan nama sama
2. Refresh page (F5)
3. Atau klik "Create bucket" / "Add bucket"

### Error "Bucket name already exists"?

**Solusi:**
1. Bucket sudah dibuat sebelumnya! ✅
2. Cek list buckets - mungkin sudah ada
3. Kalau ada, langsung pakai aja

### Error "Invalid bucket name"?

**Check:**
- Nama harus lowercase: `cryptobot-signals` ✅
- Tidak boleh: `CryptobotSignals` ❌
- Tidak boleh: `cryptobot_signals` ❌
- Harus pakai dash: `-` bukan underscore `_`

## 🎯 Quick Checklist

Sebelum klik "Create bucket", pastikan:

- [ ] Name: `cryptobot-signals` (lowercase, pakai dash)
- [ ] Public bucket: ❌ NOT checked (private)
- [ ] File size limit: 50 MB (atau default)
- [ ] MIME types: kosong (allow all)

## 📸 Screenshot Reference

Kalau bingung, cari di sidebar kiri:
- Icon yang mirip folder 📁
- Text "Storage"
- Biasanya di bawah "Authentication" atau "Database"

## ✅ Verification

Setelah create, test dengan:

1. **Klik bucket** `cryptobot-signals`
2. **Lihat detail**:
   - Name: cryptobot-signals ✅
   - Public: No ✅
   - Objects: 0 ✅
   - Size: 0 B ✅

3. **Try upload** (optional):
   - Klik "Upload file"
   - Pilih file test
   - Upload berhasil = bucket working! ✅

## 🚀 Next Steps

Setelah bucket created:

1. ✅ Bucket ready to use
2. ✅ No need to update `.env`
3. ✅ Ready to deploy to Railway
4. ✅ Bot will auto-upload logs

## 💡 Tips

- **Nama bucket tidak bisa diubah** setelah dibuat
- **Pastikan private** - jangan public!
- **Bucket kosong** adalah normal - akan terisi setelah bot jalan

---

**Setup Time**: 2 menit  
**Difficulty**: Easy  
**Cost**: $0 (Free tier)
