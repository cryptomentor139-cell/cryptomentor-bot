# ✅ Automaton Deploy Checklist

## Pre-Deploy

- [ ] Bot sudah deploy dan jalan di Railway
- [ ] Punya CONWAY_API_KEY dari https://conway.tech
- [ ] Punya CONWAY_WALLET_ADDRESS
- [ ] File config sudah di-commit:
  - [ ] `automaton/.railwayignore`
  - [ ] `automaton/Procfile`
  - [ ] `automaton/railway.json`

## Step 1: Commit & Push (2 menit)

```bash
cd Bismillah
git add automaton/
git commit -m "feat: automaton railway deployment config"
git push origin main
```

- [ ] Git push berhasil

## Step 2: Create Railway Service (3 menit)

1. [ ] Login ke Railway → https://railway.app
2. [ ] New Project → Deploy from GitHub
3. [ ] Select repository
4. [ ] Configure:
   - [ ] Service name: `automaton`
   - [ ] Root directory: `Bismillah/automaton`
   - [ ] Branch: `main`
5. [ ] Click "Deploy"

## Step 3: Set Environment Variables (2 menit)

Railway Dashboard → Automaton Service → Variables:

- [ ] `CONWAY_API_KEY` = (dari Conway dashboard)
- [ ] `CONWAY_WALLET_ADDRESS` = (dari Conway dashboard)
- [ ] `TELEGRAM_BOT_TOKEN` = (sama dengan bot)
- [ ] `NODE_ENV` = `production`

## Step 4: Wait for Deploy (5-10 menit)

Railway akan:
- [ ] Install dependencies
- [ ] Build TypeScript
- [ ] Start Automaton

Monitor di: Railway Dashboard → Logs

## Step 5: Verify Deployment (1 menit)

Cek logs untuk:
```
✓ Database initialized
✓ Wallet loaded
✓ API client connected
✓ Automaton running
```

- [ ] Automaton started successfully
- [ ] No errors in logs

## Step 6: Get Automaton URL (1 menit)

Railway Dashboard → Automaton Service → Settings → Domains

Copy URL:
```
https://automaton-production-xxxx.up.railway.app
```

- [ ] URL copied

## Step 7: Connect Bot to Automaton (2 menit)

Railway Dashboard → Bot Service → Variables

Add new variable:
```
CONWAY_API_URL=https://automaton-production-xxxx.up.railway.app
```

- [ ] Variable added
- [ ] Bot restarted automatically

## Step 8: Test Integration (2 menit)

### Test 1: Health Check
```bash
curl https://automaton-production-xxxx.up.railway.app/health
```

- [ ] Returns `{"status":"ok"}`

### Test 2: Via Telegram Bot
```
/automaton status
```

- [ ] Bot responds with Automaton status

### Test 3: Check Logs
Railway Dashboard → Both services → Logs

- [ ] No errors
- [ ] Bot connected to Automaton
- [ ] Automaton processing requests

## Post-Deploy

- [ ] Monitor resource usage (RAM < 512MB)
- [ ] Test Automaton features via bot
- [ ] Check Conway dashboard for API usage
- [ ] Set up monitoring/alerts (optional)

## Troubleshooting

### If Build Fails:
- [ ] Check Railway logs for error
- [ ] Verify `package.json` has `build` script
- [ ] Check TypeScript installed in devDependencies

### If Runtime Fails:
- [ ] Check environment variables set correctly
- [ ] Check CONWAY_API_KEY valid
- [ ] Check dist/ folder exists after build

### If Bot Can't Connect:
- [ ] Check CONWAY_API_URL in bot service
- [ ] Check Automaton URL accessible
- [ ] Check both services running

## Success Criteria

✅ Automaton deployed and running
✅ Bot connected to Automaton
✅ No errors in logs
✅ `/automaton status` works in Telegram
✅ Resource usage normal

## Total Time

- Commit & Push: 2 min
- Create Service: 3 min
- Set Env Vars: 2 min
- Deploy Wait: 5-10 min
- Connect & Test: 5 min

**Total: ~15-20 menit**

## Cost

- Bot Service: $5/month
- Automaton Service: $5/month
- **Total: $10/month** (Railway Hobby plan)

---

**Ready to deploy?** Follow: `DEPLOY_AUTOMATON_RAILWAY_NOW.md`
