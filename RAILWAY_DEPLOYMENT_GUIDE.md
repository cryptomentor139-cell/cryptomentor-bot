# 🚀 Railway Deployment Guide - CryptoMentor Bot

## ✅ Kenapa Railway?

### Keunggulan Railway:
- ✅ **Network Bagus** - Bisa akses semua crypto APIs (Binance, CoinGecko, dll)
- ✅ **Free Tier** - $5 credit gratis per bulan (cukup untuk bot kecil)
- ✅ **Easy Deploy** - Connect GitHub dan auto-deploy
- ✅ **Environment Variables** - Mudah manage `.env`
- ✅ **Logs & Monitoring** - Real-time logs
- ✅ **Auto Restart** - Jika bot crash, auto restart
- ✅ **Custom Domain** - Bisa pakai domain sendiri (optional)

### Railway vs Alternatives:

| Platform | Network | Free Tier | Ease | Recommended |
|----------|---------|-----------|------|-------------|
| **Railway** | ✅ Excellent | $5/month | ⭐⭐⭐⭐⭐ | ✅ YES |
| Heroku | ✅ Good | ❌ Paid only | ⭐⭐⭐⭐ | ⚠️ Paid |
| Replit | ❌ Blocked | ✅ Free | ⭐⭐⭐ | ❌ NO |
| DigitalOcean | ✅ Excellent | ❌ $4/month | ⭐⭐⭐ | ⚠️ Paid |
| AWS EC2 | ✅ Excellent | ✅ 12 months | ⭐⭐ | ⚠️ Complex |

**Kesimpulan**: Railway adalah pilihan terbaik! 🏆

---

## 📋 Prerequisites

### 1. GitHub Account
- Buat akun di https://github.com jika belum punya
- Install Git di komputer

### 2. Railway Account
- Buat akun di https://railway.app
- Login dengan GitHub (recommended)

### 3. Project Files
- Pastikan semua file bot sudah siap
- `.env` file dengan semua API keys

---

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Project Files

#### A. Create `requirements.txt`
```bash
# Di folder Bismillah
pip freeze > requirements.txt
```

Atau buat manual:
```txt
python-telegram-bot==20.7
requests>=2.31.0
python-dotenv>=1.0.0
supabase>=2.0.0
pytz>=2023.3
aiohttp>=3.9.0
```

#### B. Create `Procfile`
```bash
# Di folder Bismillah, buat file bernama "Procfile" (tanpa extension)
web: python main.py
```

#### C. Create `railway.json` (Optional - untuk config)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### D. Create `.gitignore`
```txt
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
```

### Step 2: Push to GitHub

```bash
# Di folder Bismillah
cd Bismillah

# Initialize git (jika belum)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - CryptoMentor Bot"

# Create repo di GitHub (via web), lalu:
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy ke Railway

#### A. Login ke Railway
1. Buka https://railway.app
2. Login dengan GitHub
3. Klik "New Project"

#### B. Connect GitHub Repo
1. Pilih "Deploy from GitHub repo"
2. Pilih repository `cryptomentor-bot`
3. Klik "Deploy Now"

#### C. Add Environment Variables
1. Klik project yang baru dibuat
2. Klik tab "Variables"
3. Klik "Raw Editor"
4. Copy-paste semua dari `.env` file:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=5888741423:AAEuKYz_wM0eq1j0cyH53xIr-3qRiMLIp-Q
TOKEN=5888741423:AAEuKYz_wM0eq1j0cyH53xIr-3qRiMLIp-Q

# Admin IDs
ADMIN1=1187119989
ADMIN2=7079544380
ADMIN3=Optional

# StepFun AI Configuration
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=stepfun/step-3.5-flash

# Multi-Source Data Providers
HELIUS_API_KEY=3b32e914-4a27-417d-8dab-a70a1a9d1e8c
CRYPTOCOMPARE_API_KEY=44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9

# Supabase Configuration
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Other configs
WELCOME_CREDITS=100
SESSION_SECRET=FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==
USE_LEGACY_FUTURES_SIGNALS=true
```

5. Klik "Save"

#### D. Deploy!
Railway akan otomatis:
1. Detect Python project
2. Install dependencies dari `requirements.txt`
3. Run `python main.py`
4. Bot akan online! 🎉

### Step 4: Verify Deployment

#### A. Check Logs
1. Di Railway dashboard, klik tab "Deployments"
2. Klik deployment yang sedang running
3. Lihat logs real-time

Expected logs:
```
✅ CryptoMentor AI initialized (Provider: OpenRouter, Model: stepfun/step-3.5-flash)
✅ Bot started successfully
✅ Polling started
```

#### B. Test Bot
```
/start
/ai btc
/price eth
```

Semua harus bekerja dengan baik!

---

## 🔧 Railway Configuration

### Auto-Deploy on Push
Railway otomatis deploy setiap kali Anda push ke GitHub:

```bash
# Make changes
git add .
git commit -m "Update bot"
git push

# Railway will auto-deploy! 🚀
```

### Custom Start Command
Jika perlu custom command:
1. Klik "Settings"
2. Scroll ke "Deploy"
3. Edit "Start Command": `python main.py`

### Resource Limits
Free tier Railway:
- **Memory**: 512MB - 1GB
- **CPU**: Shared
- **Network**: Unlimited
- **Storage**: 1GB

Cukup untuk bot Telegram!

---

## 💰 Railway Pricing

### Free Tier
- **$5 credit per bulan** (gratis)
- Cukup untuk bot kecil-menengah
- ~500 hours runtime per bulan

### Estimasi Usage
Bot Telegram 24/7:
- **CPU**: ~$0.01/hour = ~$7/month
- **Memory**: ~$0.01/hour = ~$7/month
- **Total**: ~$14/month

**Dengan $5 free credit**: Bayar ~$9/month

### Tips Hemat:
1. Optimize code untuk reduce CPU usage
2. Use caching untuk reduce API calls
3. Monitor usage di Railway dashboard

---

## 🐛 Troubleshooting

### Bot Tidak Start?

#### Check 1: Logs
```
Railway Dashboard → Deployments → View Logs
```

Look for errors:
- `ModuleNotFoundError` → Missing dependency
- `KeyError` → Missing environment variable
- `ConnectionError` → Network issue (rare on Railway)

#### Check 2: Environment Variables
```
Railway Dashboard → Variables
```

Pastikan semua API keys ada dan benar.

#### Check 3: Start Command
```
Railway Dashboard → Settings → Deploy → Start Command
```

Harus: `python main.py`

### Bot Crash Terus?

#### Enable Auto-Restart
Railway sudah auto-restart by default, tapi bisa di-configure:

```json
// railway.json
{
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Check Memory Usage
Jika bot crash karena memory:
1. Optimize code
2. Reduce cache size
3. Upgrade Railway plan

### Network Issue?

Railway **TIDAK** memblokir crypto APIs, tapi jika ada issue:

```bash
# Test dari Railway logs
curl https://api.binance.com/api/v3/ping
curl https://api.coingecko.com/api/v3/ping
```

Jika timeout, contact Railway support (rare).

---

## 📊 Monitoring

### Railway Dashboard
- **Deployments**: History & status
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time logs
- **Variables**: Environment variables

### Custom Monitoring
Add logging di bot:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info("Bot started")
logger.info(f"User {user_id} used /ai command")
logger.error(f"Error: {e}")
```

Logs akan muncul di Railway dashboard.

---

## 🔐 Security Best Practices

### 1. Never Commit `.env`
```bash
# .gitignore
.env
.env.local
```

### 2. Use Railway Variables
Jangan hardcode API keys di code!

### 3. Rotate API Keys
Ganti API keys secara berkala:
1. Generate new key
2. Update di Railway Variables
3. Redeploy

### 4. Monitor Logs
Check logs untuk suspicious activity.

---

## 🚀 Advanced: Custom Domain

### Add Custom Domain (Optional)
1. Railway Dashboard → Settings → Domains
2. Klik "Add Domain"
3. Enter domain: `bot.yourdomain.com`
4. Add CNAME record di DNS provider:
   ```
   CNAME bot.yourdomain.com → your-app.railway.app
   ```

Bot akan accessible via custom domain!

---

## 📝 Deployment Checklist

### Pre-Deployment:
- [ ] `requirements.txt` created
- [ ] `Procfile` created
- [ ] `.gitignore` configured
- [ ] All API keys ready
- [ ] Code tested locally

### Deployment:
- [ ] GitHub repo created
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] GitHub repo connected
- [ ] Environment variables added
- [ ] Deployment successful

### Post-Deployment:
- [ ] Bot responds to `/start`
- [ ] `/ai btc` works
- [ ] `/price eth` works
- [ ] Logs look good
- [ ] No errors in Railway dashboard

---

## 🎉 Summary

**Railway adalah pilihan TERBAIK untuk deploy bot crypto!**

### Keunggulan:
- ✅ Network bagus (bisa akses semua crypto APIs)
- ✅ Easy deployment (connect GitHub & done)
- ✅ Free tier ($5/month credit)
- ✅ Auto-deploy on push
- ✅ Real-time logs & monitoring
- ✅ Auto-restart on failure

### Expected Results:
- ⚡ Bot online 24/7
- ✅ Semua fitur bekerja (AI, SnD, Price, dll)
- 📊 Real-time monitoring
- 🔄 Auto-deploy on updates

**Total setup time: ~15 menit**
**Monthly cost: ~$9 (setelah $5 free credit)**

---

**Date**: 2026-02-15
**Status**: ✅ READY TO DEPLOY
**Recommended**: Railway.app 🏆

**Happy Deploying! 🚀**
