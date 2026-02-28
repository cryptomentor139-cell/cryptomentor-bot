# 🤖 Deploy Automaton ke Railway - Step by Step

## Prerequisites

✅ Bot sudah deploy dan jalan
✅ Punya Railway account
✅ Punya CONWAY_API_KEY

## Langkah 1: Commit File Automaton

```bash
cd Bismillah
git add automaton/.railwayignore automaton/Procfile automaton/railway.json
git commit -m "feat: automaton railway config"
git push origin main
```

## Langkah 2: Buat Service Baru di Railway

### Via Railway Dashboard:

1. **Login ke Railway** → https://railway.app
2. **New Project** → Deploy from GitHub repo
3. **Select Repository** → Pilih repo kamu
4. **Configure Service:**
   - Service Name: `automaton`
   - Root Directory: `Bismillah/automaton`
   - Branch: `main`

### Via Railway CLI (Alternative):

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
cd Bismillah/automaton
railway link

# Deploy
railway up
```

## Langkah 3: Set Environment Variables

Di Railway Dashboard → Automaton Service → Variables:

### Required Variables:

```env
# Conway API
CONWAY_API_KEY=your_conway_api_key_here
CONWAY_WALLET_ADDRESS=your_wallet_address_here

# Telegram (same as bot)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Node Environment
NODE_ENV=production

# Optional: Database path
DATABASE_PATH=/app/data/automaton.db
```

### Cara Get CONWAY_API_KEY:

1. Visit: https://conway.tech
2. Sign up / Login
3. Dashboard → API Keys
4. Create New Key
5. Copy key

## Langkah 4: Deploy

Railway akan otomatis:
1. ✅ Detect Node.js project
2. ✅ Install dependencies (`npm ci`)
3. ✅ Build TypeScript (`npm run build`)
4. ✅ Start Automaton (`node dist/index.js --run`)

## Langkah 5: Monitor Logs

Railway Dashboard → Automaton Service → Logs

Cari output seperti:
```
Conway Automaton v0.1.0
Initializing...
✓ Database initialized
✓ Wallet loaded
✓ API client connected
✓ Automaton running
Listening on port 3000
```

## Langkah 6: Get Automaton URL

Railway akan provide public URL:
```
https://automaton-production-xxxx.up.railway.app
```

Copy URL ini!

## Langkah 7: Connect Bot ke Automaton

Di Railway Dashboard → Bot Service → Variables:

Tambah variable baru:
```env
CONWAY_API_URL=https://automaton-production-xxxx.up.railway.app
```

Bot akan otomatis restart dan connect ke Automaton.

## Langkah 8: Test Integration

### Test via Telegram Bot:

```
/automaton status
```

Bot harus respond dengan status Automaton.

### Test via API (Optional):

```bash
curl https://automaton-production-xxxx.up.railway.app/health
```

Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime": 123
}
```

## Troubleshooting

### Build Error: tsc not found

Railway logs menunjukkan:
```
Error: Cannot find module 'typescript'
```

**Fix:** TypeScript sudah ada di devDependencies, Railway harus install otomatis. Jika tidak:

```bash
cd Bismillah/automaton
npm install --save-dev typescript
git add package.json package-lock.json
git commit -m "fix: ensure typescript in devDeps"
git push
```

### Runtime Error: dist/ not found

**Fix:** Build phase gagal. Cek Railway logs untuk error saat `npm run build`.

### Error: CONWAY_API_KEY not set

**Fix:** Set environment variable di Railway Dashboard.

### Bot can't connect to Automaton

**Fix:** 
1. Check CONWAY_API_URL di bot service
2. Check Automaton is running (Railway logs)
3. Check Automaton URL accessible (curl test)

## Resource Usage

**Automaton Estimasi:**
- RAM: ~200-250MB
- CPU: Low (idle most of time)
- Disk: ~50MB

**Railway Free Tier:**
- $5 credit/month
- 512MB RAM
- 1 vCPU

**Cost:**
- Bot: $5/month
- Automaton: $5/month
- **Total: $10/month** (Hobby plan)

## Monitoring

### Health Check

```bash
# Check Automaton
curl https://automaton-url/health

# Check Bot can reach Automaton
# Via Telegram: /automaton status
```

### Logs

Railway Dashboard → Logs untuk masing-masing service

### Metrics

Railway Dashboard → Metrics:
- CPU usage
- RAM usage
- Network traffic

## Next Steps

1. ✅ Deploy Automaton
2. ✅ Set environment variables
3. ✅ Connect bot ke Automaton
4. ✅ Test integration
5. ⏳ Monitor logs & metrics
6. ⏳ Test fitur Automaton via bot

## Rollback Plan

Jika ada masalah:

```bash
# Stop Automaton service
Railway Dashboard → Automaton → Settings → Delete Service

# Bot akan fallback ke mode tanpa Automaton
```

---

**Status:** READY TO DEPLOY ✅
**Estimated Time:** 10-15 menit
**Difficulty:** Easy (Railway auto-detect)
