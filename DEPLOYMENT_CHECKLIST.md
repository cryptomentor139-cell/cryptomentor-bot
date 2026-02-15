# ✅ Railway Deployment Checklist

## 📋 Pre-Deployment Checklist

### 1. Files Ready
- [x] `requirements.txt` - Dependencies list
- [x] `runtime.txt` - Python version (3.11.9)
- [x] `Procfile` - Start command
- [x] `railway.json` - Railway configuration
- [x] `.gitignore` - Git ignore rules
- [x] `README.md` - Project documentation
- [x] `.env.example` - Environment variables template

### 2. API Keys Ready
- [ ] Telegram Bot Token (dari @BotFather)
- [ ] OpenRouter API Key (untuk StepFun AI)
- [ ] Supabase URL & Keys
- [ ] CryptoCompare API Key (optional)
- [ ] Helius API Key (optional)

### 3. Admin IDs Ready
- [ ] ADMIN1 (your Telegram user ID)
- [ ] ADMIN2 (optional)

### 4. Code Tested Locally
- [ ] Bot starts without errors
- [ ] `/start` command works
- [ ] `/ai btc` command works
- [ ] Database connection works

---

## 🚀 Deployment Steps

### Step 1: Prepare Repository

```bash
# Navigate to project folder
cd Bismillah

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Railway deployment"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `cryptomentor-bot`
3. Private or Public (your choice)
4. Click "Create repository"

### Step 3: Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/cryptomentor-bot.git

# Push
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Railway

1. **Login to Railway**
   - Go to https://railway.app
   - Click "Login"
   - Login with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `cryptomentor-bot`
   - Click "Deploy Now"

3. **Add Environment Variables**
   - Click on your project
   - Click "Variables" tab
   - Click "Raw Editor"
   - Copy-paste from your `.env` file:

```env
TELEGRAM_BOT_TOKEN=5888741423:AAEuKYz_wM0eq1j0cyH53xIr-3qRiMLIp-Q
TOKEN=5888741423:AAEuKYz_wM0eq1j0cyH53xIr-3qRiMLIp-Q
ADMIN1=1187119989
ADMIN2=7079544380
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=stepfun/step-3.5-flash
CRYPTOCOMPARE_API_KEY=44d575a1b1df76144a11214917bd37649345ffc2f8a88aee907671850dd662a9
HELIUS_API_KEY=3b32e914-4a27-417d-8dab-a70a1a9d1e8c
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzMjExOTksImV4cCI6MjA3MDg5NzE5OX0.placeholder
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyYnFub2NvdmZ5bWRpa25nYXphIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTMyMTE5OSwiZXhwIjoyMDcwODk3MTk5fQ.QGIlCWKqy8fe0bKJbx6CAqeSr7fq17NBXqNeC8nUu5Y
WELCOME_CREDITS=100
SESSION_SECRET=FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==
USE_LEGACY_FUTURES_SIGNALS=true
PGHOST=ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=npg_PXo7pTdgJ4ny
PGPORT=5432
CRYPTONEWS_API_KEY=2iqmgpfhhlcvrq9sqxhppabo8pxppg5pv1ue37x8
```

   - Click "Save"

4. **Wait for Deployment**
   - Railway will automatically:
     - Detect Python project
     - Install dependencies
     - Start bot with `python main.py`
   - Wait 2-3 minutes

---

## ✅ Post-Deployment Verification

### Step 1: Check Logs

1. Go to Railway Dashboard
2. Click "Deployments" tab
3. Click on the running deployment
4. Check logs for:

```
✅ CryptoMentor AI initialized (Provider: OpenRouter, Model: stepfun/step-3.5-flash)
✅ Bot started successfully
✅ Polling started
```

### Step 2: Test Bot Commands

Open Telegram and test:

```
/start
Expected: Welcome message with menu

/ai btc
Expected: AI analysis in 9-12 seconds

/price eth
Expected: Current ETH price

/menu
Expected: Interactive menu
```

### Step 3: Test Network Access

Bot should be able to access:
- ✅ Binance API (for price data)
- ✅ CoinGecko API (for market data)
- ✅ OpenRouter API (for AI)
- ✅ Supabase (for database)

Check logs for any connection errors.

### Step 4: Monitor Performance

Railway Dashboard → Metrics:
- CPU usage: Should be low (~5-10%)
- Memory usage: Should be ~100-200MB
- Network: Should show activity

---

## 🐛 Troubleshooting

### Bot Not Starting?

**Check Logs**:
```
Railway Dashboard → Deployments → Logs
```

**Common Issues**:

1. **ModuleNotFoundError**
   - Missing dependency in `requirements.txt`
   - Fix: Add missing package and redeploy

2. **KeyError: 'TELEGRAM_BOT_TOKEN'**
   - Missing environment variable
   - Fix: Add in Railway Variables

3. **Connection Error**
   - Network issue (rare on Railway)
   - Fix: Check API keys are correct

### Bot Crashes Repeatedly?

**Check Memory Usage**:
- Railway Dashboard → Metrics
- If memory > 512MB, optimize code

**Check Error Logs**:
- Look for Python exceptions
- Fix the error and redeploy

### Commands Not Working?

**Test Individually**:
```
/start - Should always work
/ai btc - Tests AI + network
/price eth - Tests crypto API
```

**Check Logs** for specific errors.

---

## 🔄 Update & Redeploy

### Make Changes Locally

```bash
# Edit files
nano bot.py

# Test locally
python main.py

# Commit changes
git add .
git commit -m "Update: description of changes"

# Push to GitHub
git push
```

### Auto-Deploy

Railway will automatically:
1. Detect push to GitHub
2. Pull latest code
3. Rebuild & redeploy
4. Restart bot

**No manual action needed!** 🎉

---

## 📊 Monitoring

### Daily Checks

- [ ] Bot is online (test with `/start`)
- [ ] No errors in logs
- [ ] Memory usage < 512MB
- [ ] CPU usage < 20%

### Weekly Checks

- [ ] Check Railway credit usage
- [ ] Review error logs
- [ ] Test all major commands
- [ ] Check database size

### Monthly Checks

- [ ] Review Railway bill
- [ ] Update dependencies if needed
- [ ] Backup database
- [ ] Review user feedback

---

## 💰 Cost Monitoring

### Railway Free Tier

- **$5 credit per month** (free)
- **Usage**: ~$14/month for 24/7 bot
- **You pay**: ~$9/month (after free credit)

### Check Usage

Railway Dashboard → Usage:
- Current month usage
- Estimated cost
- Credit remaining

### Optimize Costs

1. **Reduce CPU usage**:
   - Optimize code
   - Use caching
   - Reduce API calls

2. **Reduce memory usage**:
   - Clear unused variables
   - Optimize data structures
   - Use generators

3. **Monitor logs**:
   - Fix errors quickly
   - Reduce unnecessary logging

---

## ✅ Final Checklist

### Deployment Complete When:

- [x] Bot is online 24/7
- [x] All commands work
- [x] No errors in logs
- [x] Network access works
- [x] Database connected
- [x] AI responses work
- [x] Monitoring setup

### Success Criteria:

- ✅ Bot responds to `/start` instantly
- ✅ `/ai btc` works in 9-12 seconds
- ✅ `/price eth` shows current price
- ✅ No timeout errors
- ✅ Logs show no errors
- ✅ Memory usage stable
- ✅ CPU usage low

---

## 🎉 Deployment Complete!

**Your CryptoMentor Bot is now live on Railway!**

### What's Next?

1. **Share bot** dengan users
2. **Monitor** performance daily
3. **Update** features as needed
4. **Scale** jika perlu more resources

### Support

- Railway Docs: https://docs.railway.app
- Telegram: @BillFarr
- GitHub Issues: Create issue di repo

---

**Happy Deploying! 🚀**

**Date**: 2026-02-15
**Status**: ✅ READY FOR PRODUCTION
