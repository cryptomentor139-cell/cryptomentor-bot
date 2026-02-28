# ⚡ Quick Deploy: Bot + Automaton (1 Service)

## Status Saat Ini

✅ Bot Telegram (Python) - READY
✅ Automaton (Node.js) - READY
✅ Combined startup script - CREATED
✅ Railway config - UPDATED

## Yang Sudah Dibuat

1. **start_combined.sh** - Script untuk run keduanya
2. **Procfile** - Updated ke `bash start_combined.sh`
3. **railway.json** - Updated startCommand
4. **nixpacks.toml** - Config untuk Python + Node.js
5. **COMBINED_DEPLOYMENT_GUIDE.md** - Dokumentasi lengkap

## Langkah Deploy ke Railway

### 1. Commit & Push ke GitHub

```bash
cd Bismillah
git add .
git commit -m "feat: combined deployment bot + automaton"
git push origin main
```

### 2. Railway Auto-Deploy

Railway akan otomatis:
- Detect `nixpacks.toml`
- Install Python 3.10 + Node.js 20
- Install dependencies untuk keduanya
- Build Automaton TypeScript
- Run `start_combined.sh`

### 3. Set Environment Variables

Di Railway dashboard, pastikan semua env vars sudah ada:

**Bot Telegram:**
- TELEGRAM_BOT_TOKEN
- SUPABASE_URL
- SUPABASE_KEY
- ENCRYPTION_KEY
- (semua env vars bot lainnya)

**Automaton:**
- CONWAY_API_KEY
- CONWAY_WALLET_ADDRESS
- (env vars automaton lainnya)

### 4. Verify Deployment

Cek logs Railway untuk:
```
✓ Bot started (PID: xxxx)
✓ Automaton started (PID: xxxx)
Both services are running!
```

## Test Local (Opsional)

```bash
cd Bismillah
bash start_combined.sh
```

## Resource Monitoring

**Railway Free Tier:**
- 512MB RAM
- 1 vCPU
- $5 credit/month

**Estimasi Usage:**
- Bot: ~150-200MB
- Automaton: ~200-250MB
- Total: ~400-450MB ✅ (masih cukup!)

## Troubleshooting

### Jika Bot tidak respond:
```bash
# Cek logs Railway
# Pastikan TELEGRAM_BOT_TOKEN benar
# Test dengan /start di Telegram
```

### Jika Automaton tidak respond:
```bash
# Cek logs Railway
# Pastikan CONWAY_API_KEY benar
# Cek automaton/dist/ folder ada
```

### Jika Out of Memory:
- Upgrade Railway ke Hobby plan ($5/month)
- Atau migrate ke deploy terpisah (Opsi 2)

## Next Steps

1. Push ke GitHub
2. Railway auto-deploy
3. Monitor logs
4. Test bot di Telegram
5. Test Automaton via bot commands

## Rollback Plan

Jika ada masalah, rollback ke bot-only:

```bash
# Update Procfile
echo "web: python main.py" > Procfile

# Push
git add Procfile
git commit -m "rollback: bot only"
git push
```

Railway akan auto-deploy versi lama.
