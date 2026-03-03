# 🚀 Run Migration - 3 Langkah Mudah

## ⚡ Cara Tercepat (1 Menit)

### 1️⃣ Buka Railway Dashboard

```
🌐 https://railway.app
```

- Login dengan akun Anda
- Pilih project: **industrious-dream**
- Klik service: **web**

### 2️⃣ Buka Shell Tab

- Klik tab **"Shell"** di bagian atas
- Tunggu terminal muncul (loading ~5 detik)

### 3️⃣ Run Command Ini

Copy-paste command ini ke shell:

```bash
python run_openclaw_skills_migration.py
```

Tekan **Enter**

### ✅ Selesai!

Anda akan lihat output seperti ini:

```
✅ Connected to database
✅ Migration completed successfully!
✅ Created 3 tables
✅ Loaded 10 default skills
```

### 4️⃣ Restart Bot

- Kembali ke service overview
- Klik tombol **"Restart"** (icon ↻)
- Tunggu ~30 detik

### 🎉 Done!

Test bot Anda:
```
/openclaw_start
```

Atau sebagai admin:
```
Show bot statistics
```

---

## 📸 Visual Guide

### Step 1: Railway Dashboard
```
┌─────────────────────────────────────┐
│  Railway Dashboard                  │
│                                     │
│  Projects:                          │
│  ┌─────────────────────────────┐   │
│  │ industrious-dream           │   │ ← Click ini
│  │ Status: Running             │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Step 2: Service View
```
┌─────────────────────────────────────┐
│  Service: web                       │
│                                     │
│  [Deployments] [Metrics] [Shell]   │ ← Click Shell
│                           ↑         │
└─────────────────────────────────────┘
```

### Step 3: Shell Terminal
```
┌─────────────────────────────────────┐
│  Shell                              │
│                                     │
│  $ _                                │ ← Ketik command di sini
│                                     │
│                                     │
└─────────────────────────────────────┘
```

### Step 4: Run Migration
```
┌─────────────────────────────────────┐
│  Shell                              │
│                                     │
│  $ python run_openclaw_skills_mi... │
│  🔄 Connecting to database...       │
│  ✅ Connected to database           │
│  ✅ Migration completed!            │
└─────────────────────────────────────┘
```

---

## ⚠️ Jika Ada Masalah

### Problem: Shell tidak muncul
**Solution:** Refresh page, tunggu 10 detik

### Problem: Command not found
**Solution:** Pastikan Anda di Railway shell, bukan local terminal

### Problem: Permission denied
**Solution:** Anda sudah login sebagai owner project

### Problem: Table already exists
**Solution:** Migration sudah pernah dirun, skip!

---

## 🎯 Alternative: Via Railway CLI

Jika Anda prefer command line:

```bash
# 1. Open Railway shell
railway shell

# 2. Run migration
python run_openclaw_skills_migration.py

# 3. Exit
exit

# 4. Restart
railway restart
```

---

## ✅ Verification

Setelah migration, check Railway logs:

```bash
railway logs --tail 20
```

Seharusnya tidak ada error:
- ❌ ~~"no such column: credits"~~
- ✅ Bot running normally

---

## 📞 Need Help?

Jika stuck, check:
1. Railway dashboard: https://railway.app
2. Project logs: `railway logs`
3. Service status: `railway status`

---

## 🎊 Success!

Setelah migration berhasil:
- ✅ OpenClaw Admin Mode active
- ✅ Pay-per-use working
- ✅ Loading indicators showing
- ✅ No database errors

**Your bot is fully upgraded!** 🚀
