# 🚀 Run Migration Via Railway CLI - Cara Mudah

## ⚡ Cara Tercepat (30 Detik)

Karena tab Shell tidak tersedia di Railway dashboard Anda, kita akan gunakan Railway CLI dengan cara yang berbeda.

### Step 1: Buka PowerShell/Terminal

Buka PowerShell atau Command Prompt di Windows Anda.

### Step 2: Masuk ke Folder Bismillah

```powershell
cd C:\V3-Final-Version\Bismillah
```

### Step 3: Run Migration via Railway

Gunakan command ini yang akan execute di Railway server (bukan local):

```powershell
railway run --service web python run_openclaw_skills_migration.py
```

**ATAU** jika itu tidak work, gunakan ini:

```powershell
railway run python run_openclaw_skills_migration.py
```

### Step 4: Tunggu Output

Anda akan melihat:
```
🔄 Connecting to database...
✅ Connected to database
✅ Migration completed successfully!
✅ Created 3 tables
✅ Loaded 10 default skills
```

### Step 5: Restart Bot

```powershell
railway restart
```

### Step 6: Check Logs

```powershell
railway logs --tail 50
```

Seharusnya tidak ada error "no such column: credits"

---

## 🔧 Alternative: Run SQL Directly

Jika cara di atas tidak work, kita bisa run SQL file langsung:

### Step 1: Get Database Connection String

```powershell
railway variables | Select-String "PGHOST|PGUSER|PGPASSWORD|PGDATABASE"
```

### Step 2: Install psql (jika belum)

Download PostgreSQL client dari:
https://www.postgresql.org/download/windows/

### Step 3: Run Migration SQL

```powershell
# Set environment variables
$env:PGHOST="ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech"
$env:PGUSER="neondb_owner"
$env:PGDATABASE="neondb"
$env:PGPASSWORD="your_password"

# Run SQL file
psql -f migrations/011_openclaw_skills.sql
```

---

## 🎯 Cara Paling Mudah: Manual SQL

Jika semua cara di atas tidak work, kita bisa copy-paste SQL manual:

### Step 1: Connect ke Database

Gunakan tool seperti:
- **pgAdmin** (https://www.pgadmin.org/)
- **DBeaver** (https://dbeaver.io/)
- **TablePlus** (https://tableplus.com/)

### Step 2: Connection Info

```
Host: ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech
Port: 5432
Database: neondb
User: neondb_owner
Password: (dari Railway variables PGPASSWORD)
SSL: Required
```

### Step 3: Open SQL Editor

Buka SQL editor di tool yang Anda pilih.

### Step 4: Copy-Paste SQL

Buka file `migrations/011_openclaw_skills.sql` dan copy semua isinya.

Paste ke SQL editor dan execute.

### Step 5: Verify

Run query ini untuk verify:

```sql
SELECT COUNT(*) FROM openclaw_skills_catalog;
```

Seharusnya return 10 (10 default skills).

---

## ✅ Verification

Setelah migration, check dengan:

```powershell
railway logs --tail 50
```

Seharusnya tidak ada error:
- ❌ ~~"no such column: credits"~~
- ✅ Bot running normally

---

## 🆘 Jika Masih Error

Jika semua cara di atas tidak work, kita bisa skip migration dan fix error dengan cara lain:

### Option 1: Update Code to Handle Missing Column

Kita bisa update code untuk create column jika tidak ada.

### Option 2: Use Alternative Database Tool

Install pgAdmin atau DBeaver dan run SQL manual.

### Option 3: Contact Railway Support

Minta akses ke Shell tab atau bantuan run migration.

---

## 📞 Need Help?

Jika stuck, mari kita coba cara lain. Beritahu saya error message yang muncul dan kita akan find solution!

---

## 🎉 Success!

Setelah migration berhasil:
- ✅ No database errors
- ✅ OpenClaw working
- ✅ Admin mode active
- ✅ All features functional

**Your bot is ready!** 🚀
