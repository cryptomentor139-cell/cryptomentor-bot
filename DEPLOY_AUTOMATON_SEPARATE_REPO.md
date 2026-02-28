# 🤖 Deploy Automaton dari Repo Terpisah

## Situasi

Kamu punya 2 repo terpisah:
1. ✅ **cryptomentor-bot** - Bot Telegram (sudah deploy)
2. ⏳ **Automaton** - Conway Automaton (belum deploy)

Ini adalah setup yang **PROPER dan RECOMMENDED**!

---

## Langkah Deploy Automaton

### 1. Pastikan Repo Automaton Siap (2 menit)

Cek repo Automaton kamu punya file-file ini:
- ✅ `package.json` dengan script `build` dan `start`
- ✅ `src/` folder dengan TypeScript code
- ✅ `.env.example` (optional)

### 2. Deploy ke Railway (5 menit)

#### Via Railway Dashboard:

1. **Login Railway** → https://railway.app

2. **New Project** → Deploy from GitHub repo

3. **Select Repository:**
   - Pilih: `cryptomentor139-cell/Automaton`
   - Branch: `main` (atau `master`)

4. **Railway Auto-Detect:**
   - Railway akan detect Node.js project
   - Auto-install dependencies
   - Auto-build TypeScript
   - Auto-start dengan `npm start`

5. **Click "Deploy"**

### 3. Set Environment Variables (2 menit)

Railway Dashboard → Automaton Service → Variables:

```env
# Conway API (REQUIRED)
CONWAY_API_KEY=your_conway_api_key_here
CONWAY_WALLET_ADDRESS=your_wallet_address_here

# Telegram (same as bot)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Node Environment
NODE_ENV=production

# Optional
DATABASE_PATH=/app/data/automaton.db
LOG_LEVEL=info
PORT=3000
```

#### Cara Get CONWAY_API_KEY:

1. Visit: https://conway.tech
2. Sign up / Login
3. Dashboard → API Keys
4. Create New Key
5. Copy key

### 4. Monitor Deploy (5-10 menit)

Railway Dashboard → Logs

Tunggu sampai muncul:
```
✓ Dependencies installed
✓ TypeScript compiled
✓ Automaton starting...
✓ Database initialized
✓ Wallet loaded
✓ API client connected
✓ Automaton running on port 3000
```

### 5. Get Automaton URL (1 menit)

Railway Dashboard → Automaton Service → Settings → Domains

Copy URL:
```
https://automaton-production-xxxx.up.railway.app
```

### 6. Connect Bot ke Automaton (2 menit)

Railway Dashboard → Bot Service (cryptomentor-bot) → Variables

Add new variable:
```env
CONWAY_API_URL=https://automaton-production-xxxx.up.railway.app
```

Bot akan auto-restart dan connect ke Automaton.

### 7. Test Integration (2 menit)

#### Test 1: Health Check
```bash
curl https://automaton-production-xxxx.up.railway.app/health
```

Expected response:
```json
{"status":"ok","version":"0.1.0"}
```

#### Test 2: Via Telegram Bot
```
/automaton status
```

Bot harus respond dengan status Automaton.

---

## Troubleshooting

### Build Error: Cannot find module 'typescript'

**Fix:** Pastikan `typescript` ada di `devDependencies` di `package.json`:

```json
{
  "devDependencies": {
    "typescript": "^5.9.3"
  }
}
```

### Runtime Error: dist/ not found

**Fix:** Pastikan `package.json` punya script:

```json
{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js --run"
  }
}
```

### Error: CONWAY_API_KEY not set

**Fix:** Set environment variable di Railway Dashboard.

### Bot can't connect to Automaton

**Fix:**
1. Check `CONWAY_API_URL` di bot service
2. Check Automaton is running (Railway logs)
3. Test Automaton URL dengan curl

---

## Advantages of Separate Repos

✅ **Clean separation** - Bot & Automaton independent
✅ **Easy to maintain** - Update one without affecting other
✅ **Better Git history** - Separate commit history
✅ **Flexible deployment** - Deploy to different platforms
✅ **Team collaboration** - Different teams can work on each

---

## Architecture

```
GitHub
├── cryptomentor-bot (Python)
│   └── Railway Service 1
│       ├── Bot running
│       └── CONWAY_API_URL → Automaton
│
└── Automaton (Node.js)
    └── Railway Service 2
        ├── Automaton running
        └── Public URL
```

---

## Cost

- Bot Service: $5/month
- Automaton Service: $5/month
- **Total: $10/month** (Railway Hobby plan)

---

## Next Steps

1. ✅ Deploy Automaton dari repo terpisah
2. ✅ Set environment variables
3. ✅ Get Automaton URL
4. ✅ Connect bot ke Automaton
5. ⏳ Test integration
6. ⏳ Monitor logs & metrics

---

## Summary

Kamu sudah punya setup yang **PROPER**:
- ✅ Bot di repo terpisah
- ✅ Automaton di repo terpisah
- ✅ Deploy independent
- ✅ Connect via HTTP API

Ini adalah **BEST PRACTICE** untuk microservices architecture!

**Ready to deploy?** Follow steps di atas!
