# 🚀 START HERE: Deploy Automaton

## TL;DR - Quick Deploy

```bash
# 1. Commit config files
cd Bismillah
git add automaton/
git commit -m "feat: automaton railway config"
git push

# 2. Railway Dashboard
# - New Project → GitHub repo
# - Root: Bismillah/automaton
# - Set env vars (see below)

# 3. Get Automaton URL, add to bot:
# CONWAY_API_URL=https://automaton-xxx.railway.app
```

---

## Status

✅ Bot deployed and running
✅ Automaton config files created
⏳ Ready to deploy Automaton

## Files Created

1. ✅ `automaton/.railwayignore` - Ignore unnecessary files
2. ✅ `automaton/Procfile` - Railway start command
3. ✅ `automaton/railway.json` - Railway config
4. ✅ `AUTOMATON_ENV_VARS.md` - Environment variables guide
5. ✅ `DEPLOY_AUTOMATON_RAILWAY_NOW.md` - Detailed deploy guide
6. ✅ `AUTOMATON_DEPLOY_CHECKLIST.md` - Step-by-step checklist

## Quick Start

### 1. Commit Files (2 min)

```bash
cd Bismillah
git add .
git commit -m "feat: automaton railway deployment"
git push origin main
```

### 2. Get CONWAY_API_KEY

Visit: https://conway.tech
- Sign up / Login
- Dashboard → API Keys
- Create New Key
- Copy key

### 3. Deploy to Railway (10 min)

1. Railway Dashboard → New Project
2. Deploy from GitHub → Select repo
3. Root directory: `Bismillah/automaton`
4. Set environment variables:
   ```
   CONWAY_API_KEY=your_key
   CONWAY_WALLET_ADDRESS=your_wallet
   TELEGRAM_BOT_TOKEN=same_as_bot
   NODE_ENV=production
   ```
5. Deploy!

### 4. Connect Bot (2 min)

Railway → Bot Service → Variables:
```
CONWAY_API_URL=https://automaton-xxx.railway.app
```

### 5. Test (1 min)

Telegram:
```
/automaton status
```

---

## Detailed Guides

📖 **DEPLOY_AUTOMATON_RAILWAY_NOW.md** - Full step-by-step
📋 **AUTOMATON_DEPLOY_CHECKLIST.md** - Checklist format
🔐 **AUTOMATON_ENV_VARS.md** - Environment variables

## Architecture

```
Railway
├── Bot Service (Python)
│   ├── main.py
│   ├── CONWAY_API_URL → Automaton
│   └── Port: 8080
│
└── Automaton Service (Node.js)
    ├── dist/index.js
    ├── CONWAY_API_KEY
    └── Port: 3000
```

## Cost

- Bot: $5/month
- Automaton: $5/month
- **Total: $10/month**

## Timeline

1. ✅ Bot deployed (DONE)
2. ⏳ Automaton deploy (NOW - 15 min)
3. ⏳ Connect & test (5 min)
4. ⏳ Monitor & optimize

## Support

Jika ada masalah:
1. Check Railway logs
2. Verify environment variables
3. Test health endpoint
4. Check bot connection

---

**READY TO DEPLOY!** 🚀

Follow: **DEPLOY_AUTOMATON_RAILWAY_NOW.md**
