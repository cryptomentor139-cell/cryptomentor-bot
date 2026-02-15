# ⚡ Railway Quick Start - 15 Menit Deploy!

## 🎯 Goal
Deploy CryptoMentor Bot ke Railway dalam 15 menit!

---

## ✅ Step 1: Prepare Files (2 menit)

### Check Files:
```bash
cd Bismillah

# Harus ada:
ls railway.json      # ✅ Created
ls Procfile          # ✅ Created
ls .gitignore        # ✅ Created
ls requirements.txt  # ⚠️ Need to create
```

### Create `requirements.txt`:
```bash
pip freeze > requirements.txt
```

Atau copy ini:
```txt
python-telegram-bot==20.7
requests>=2.31.0
python-dotenv>=1.0.0
supabase>=2.0.0
pytz>=2023.3
aiohttp>=3.9.0
```

---

## ✅ Step 2: Push to GitHub (5 menit)

### A. Create GitHub Repo
1. Buka https://github.com/new
2. Nama: `cryptomentor-bot`
3. Private atau Public (terserah)
4. Klik "Create repository"

### B. Push Code
```bash
# Di folder Bismillah
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git
git push -u origin main
```

---

## ✅ Step 3: Deploy ke Railway (5 menit)

### A. Login Railway
1. Buka https://railway.app
2. Klik "Login"
3. Login dengan GitHub

### B. Create New Project
1. Klik "New Project"
2. Pilih "Deploy from GitHub repo"
3. Pilih `cryptomentor-bot`
4. Klik "Deploy Now"

### C. Add Environment Variables
1. Klik project yang baru dibuat
2. Klik tab "Variables"
3. Klik "Raw Editor"
4. Copy-paste dari `.env`:

```env
TELEGRAM_BOT_TOKEN=5888741423:AAEuKYz_wM0eq1j0cyH53xIr-3qRiMLIp-Q
TOKEN=5888741423:AAEuKYz_wM0eq1j0cyH53xIr-3qRiMLIp-Q
ADMIN1=1187119989
ADMIN2=7079544380
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=stepfun/step-3.5-flash
HELIUS_API_KEY=3b32e914-4a27-417d-8dab-a70a1a9d1e8c
CRYPTOCOMPARE_API_KEY=44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzMjExOTksImV4cCI6MjA3MDg5NzE5OX0.placeholder
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y
WELCOME_CREDITS=100
SESSION_SECRET=FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==
USE_LEGACY_FUTURES_SIGNALS=true
```

5. Klik "Save"

---

## ✅ Step 4: Verify (3 menit)

### A. Check Logs
1. Klik tab "Deployments"
2. Klik deployment yang running
3. Lihat logs

Expected:
```
✅ CryptoMentor AI initialized
✅ Bot started successfully
✅ Polling started
```

### B. Test Bot
Di Telegram:
```
/start
/ai btc
/price eth
```

Semua harus bekerja! 🎉

---

## 🎊 Done!

**Bot sudah online 24/7 di Railway!**

### What's Next?

#### Auto-Deploy on Update:
```bash
# Make changes
git add .
git commit -m "Update bot"
git push

# Railway auto-deploy! 🚀
```

#### Monitor:
- Railway Dashboard → Metrics
- Railway Dashboard → Logs

#### Upgrade (Optional):
- Railway Dashboard → Settings → Plan
- Upgrade jika perlu more resources

---

## 💰 Cost

### Free Tier:
- $5 credit per bulan (gratis)
- ~500 hours runtime

### Estimated:
- Bot 24/7: ~$14/month
- Dengan $5 free: **~$9/month**

**Worth it untuk bot yang reliable!**

---

## 🐛 Troubleshooting

### Bot tidak start?
```
Railway Dashboard → Deployments → Logs
```

Look for errors dan fix.

### Missing dependency?
```bash
# Add to requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Environment variable missing?
```
Railway Dashboard → Variables → Add
```

---

## 📚 Full Guide

Lihat `RAILWAY_DEPLOYMENT_GUIDE.md` untuk guide lengkap.

---

**Total Time: 15 menit**
**Result: Bot online 24/7! 🚀**

**Happy Deploying!**
