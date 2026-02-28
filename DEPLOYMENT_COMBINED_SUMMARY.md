# ✅ DEPLOYMENT COMBINED: Bot Telegram + Automaton

## Status: READY TO DEPLOY 🚀

Semua file sudah dibuat dan dikonfigurasi untuk menjalankan Bot Telegram (Python) dan Automaton (Node.js) dalam 1 Railway service.

---

## 📁 File yang Dibuat/Diupdate

### 1. **start_combined.sh** ⭐ (BARU)
Script utama yang menjalankan kedua service secara parallel:
- Install Python dependencies
- Install Node.js dependencies  
- Build Automaton TypeScript
- Start Bot Python di background
- Start Automaton Node.js di background
- Handle graceful shutdown

### 2. **Procfile** (UPDATED)
```
web: bash start_combined.sh
```

### 3. **railway.json** (UPDATED)
```json
{
  "deploy": {
    "startCommand": "bash start_combined.sh"
  }
}
```

### 4. **nixpacks.toml** ⭐ (BARU)
Konfigurasi build untuk Railway:
- Python 3.10
- Node.js 20
- Install dependencies keduanya
- Build Automaton

### 5. **.railwayignore** ⭐ (BARU)
Ignore files yang tidak perlu di-deploy

### 6. **COMBINED_DEPLOYMENT_GUIDE.md** ⭐ (BARU)
Dokumentasi lengkap deployment

### 7. **QUICK_DEPLOY_COMBINED.md** ⭐ (BARU)
Quick reference untuk deploy

---

## 🎯 Cara Deploy

### Langkah 1: Push ke GitHub
```bash
cd Bismillah
git add .
git commit -m "feat: combined deployment bot + automaton"
git push origin main
```

### Langkah 2: Railway Auto-Deploy
Railway akan otomatis:
1. Detect `nixpacks.toml`
2. Install Python + Node.js
3. Install semua dependencies
4. Build Automaton
5. Run `start_combined.sh`

### Langkah 3: Monitor Logs
Cek Railway logs untuk:
```
✓ Bot started (PID: xxxx)
✓ Automaton started (PID: xxxx)
Both services are running!
```

### Langkah 4: Test
- Test bot di Telegram: `/start`
- Test Automaton via bot commands

---

## 💰 Resource Usage

**Railway Free Tier:**
- 512MB RAM
- 1 vCPU
- $5 credit/month

**Estimasi:**
- Bot Python: ~150-200MB
- Automaton: ~200-250MB
- **Total: ~400-450MB** ✅ Masih cukup!

---

## 🔧 Environment Variables

Pastikan semua env vars sudah di-set di Railway:

### Bot Telegram
- TELEGRAM_BOT_TOKEN
- SUPABASE_URL
- SUPABASE_KEY
- ENCRYPTION_KEY
- (semua env vars bot lainnya dari .env)

### Automaton
- CONWAY_API_KEY
- CONWAY_WALLET_ADDRESS
- (env vars automaton dari automaton/.env)

---

## 🧪 Test Local (Opsional)

```bash
cd Bismillah
bash start_combined.sh
```

Tekan Ctrl+C untuk stop.

---

## 🐛 Troubleshooting

### Bot tidak respond
1. Cek logs: `Bot started (PID: xxxx)` muncul?
2. Cek TELEGRAM_BOT_TOKEN
3. Test dengan `/start` di Telegram

### Automaton tidak respond
1. Cek logs: `Automaton started (PID: xxxx)` muncul?
2. Cek CONWAY_API_KEY
3. Cek `automaton/dist/` folder ada

### Out of Memory
- Upgrade Railway ke Hobby ($5/month)
- Atau migrate ke deploy terpisah

---

## 📊 Monitoring

### Cek Status
- Railway Dashboard → Logs
- Lihat CPU & Memory usage
- Monitor restart count

### Health Check
- Bot respond ke Telegram commands
- Automaton respond ke API calls

---

## 🔄 Rollback Plan

Jika ada masalah, rollback ke bot-only:

```bash
echo "web: python main.py" > Procfile
git add Procfile
git commit -m "rollback: bot only"
git push
```

---

## 📈 Upgrade Path

Jika traffic tinggi atau resource tidak cukup:

1. **Opsi A:** Upgrade Railway plan
   - Hobby: $5/month (1GB RAM)
   - Pro: $20/month (8GB RAM)

2. **Opsi B:** Deploy terpisah (2 services)
   - Bot di 1 service
   - Automaton di service lain
   - Komunikasi via HTTP API

---

## ✅ Checklist Deploy

- [ ] Semua file sudah di-commit
- [ ] Push ke GitHub
- [ ] Railway connected ke repo
- [ ] Environment variables sudah di-set
- [ ] Deploy berhasil (cek logs)
- [ ] Bot respond di Telegram
- [ ] Automaton berjalan (cek logs)
- [ ] Monitor resource usage

---

## 🎉 Next Steps

1. **Push ke GitHub** - `git push origin main`
2. **Monitor Railway logs** - Tunggu deploy selesai
3. **Test bot** - Kirim `/start` di Telegram
4. **Test Automaton** - Coba fitur AI agent
5. **Monitor resource** - Cek RAM/CPU usage

---

## 📚 Dokumentasi

- **COMBINED_DEPLOYMENT_GUIDE.md** - Panduan lengkap
- **QUICK_DEPLOY_COMBINED.md** - Quick reference
- **start_combined.sh** - Script startup (baca komentar)

---

## 🆘 Support

Jika ada masalah:
1. Cek Railway logs
2. Cek environment variables
3. Test local dengan `bash start_combined.sh`
4. Lihat troubleshooting di COMBINED_DEPLOYMENT_GUIDE.md

---

**Status:** READY TO DEPLOY ✅
**Estimasi Deploy Time:** 5-10 menit
**Estimasi Resource:** 400-450MB RAM (dalam free tier)
