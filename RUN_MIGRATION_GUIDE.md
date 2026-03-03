# 🔧 Cara Run Migration Database - Step by Step

## 📋 Pilihan 1: Via Railway Dashboard (RECOMMENDED)

### Step 1: Buka Railway Dashboard
1. Buka browser
2. Go to: https://railway.app
3. Login dengan akun Anda
4. Pilih project: **industrious-dream**

### Step 2: Buka Service Shell
1. Click pada service **web**
2. Klik tab **"Shell"** di bagian atas
3. Tunggu shell terbuka (akan muncul terminal)

### Step 3: Run Migration
Ketik command ini di shell:

```bash
python run_openclaw_skills_migration.py
```

Tekan Enter.

### Step 4: Lihat Output
Anda akan melihat:

```
🔄 Connecting to database...
✅ Connected to database
🔄 Running migration 011_openclaw_skills.sql...
✅ Migration completed successfully!

📊 Verifying tables...
✅ Created 3 tables:
   • openclaw_skills_catalog
   • openclaw_assistant_skills
   • openclaw_skill_usage

✅ Loaded 10 default skills

📦 Skills by category:
   • trading: 3 skills
   • crypto: 3 skills
   • analysis: 1 skills
   • automation: 1 skills
   • research: 1 skills
   • general: 1 skills

💰 Skills by type:
   • Free: 4 skills
   • Premium: 6 skills

============================================================
✅ OpenClaw Skills System Ready!
============================================================
```

### Step 5: Restart Bot
Setelah migration selesai, restart bot:

1. Kembali ke service overview
2. Klik tombol **"Restart"** (icon refresh)
3. Tunggu bot restart (~30 detik)

### Step 6: Test
Kirim message ke bot Telegram Anda:

```
/openclaw_start
```

Atau sebagai admin, langsung chat:
```
Show bot statistics
```

---

## 📋 Pilihan 2: Via Railway CLI

### Step 1: Install Railway CLI (jika belum)
```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Mac/Linux
curl -fsSL https://railway.app/install.sh | sh
```

### Step 2: Login
```bash
railway login
```

### Step 3: Link Project
```bash
cd Bismillah
railway link
```
Pilih project: **industrious-dream**

### Step 4: Open Shell
```bash
railway shell
```

Ini akan membuka shell di Railway server.

### Step 5: Run Migration
Di dalam Railway shell, ketik:

```bash
python run_openclaw_skills_migration.py
```

### Step 6: Exit Shell
```bash
exit
```

### Step 7: Restart Bot
```bash
railway restart
```

---

## 📋 Pilihan 3: Via Direct Database Connection

Jika Anda punya database URL, bisa run migration dari local:

### Step 1: Get Database URL
```bash
railway variables
```

Copy value dari `DATABASE_URL`

### Step 2: Set Environment Variable
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://..."

# Mac/Linux
export DATABASE_URL="postgresql://..."
```

### Step 3: Install Dependencies (jika belum)
```bash
pip install psycopg2-binary python-dotenv
```

### Step 4: Run Migration
```bash
python run_openclaw_skills_migration.py
```

---

## ✅ Verification Checklist

Setelah migration, verify:

- [ ] No error "no such column: credits"
- [ ] Bot responds to /openclaw_start
- [ ] Admin auto-activation works
- [ ] Loading indicators show
- [ ] Cost displayed after responses

---

## 🐛 Troubleshooting

### Error: "No module named 'psycopg2'"
**Solution:** Run di Railway server, bukan local machine

### Error: "DATABASE_URL not found"
**Solution:** Make sure running di Railway environment

### Error: "Table already exists"
**Solution:** Migration sudah pernah dirun, skip step ini

### Error: "Connection refused"
**Solution:** Check DATABASE_URL valid

---

## 📞 Quick Commands

### Check if migration needed:
```bash
railway run python -c "from services import get_database; db = get_database(); print('DB Connected')"
```

### Check tables exist:
```bash
railway run python -c "from services import get_database; db = get_database(); db.cursor.execute('SELECT COUNT(*) FROM openclaw_skills_catalog'); print(f'Skills: {db.cursor.fetchone()[0]}')"
```

### Restart bot:
```bash
railway restart
```

### Check logs:
```bash
railway logs --tail 50
```

---

## 🎯 Recommended Method

**EASIEST:** Use Railway Dashboard Shell (Pilihan 1)

1. Open https://railway.app
2. Go to project → service → Shell tab
3. Run: `python run_openclaw_skills_migration.py`
4. Click Restart button
5. Done! ✅

---

## 📊 Expected Timeline

- Open Railway Dashboard: 30 seconds
- Run migration: 10 seconds
- Restart bot: 30 seconds
- **Total: ~1 minute**

---

## 🎉 After Migration

Your bot will have:
- ✅ OpenClaw Admin Mode active
- ✅ Pay-per-use model working
- ✅ Loading indicators showing
- ✅ All features functional

**Enjoy your upgraded bot!** 🚀
