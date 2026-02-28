# 🚀 START HERE: Deploy Bot + Automaton

## TL;DR - 3 Langkah Deploy

```bash
# 1. Commit semua perubahan
git add .
git commit -m "feat: combined deployment"
git push origin main

# 2. Railway akan auto-deploy (tunggu 5-10 menit)

# 3. Cek logs Railway untuk:
# ✓ Bot started (PID: xxxx)
# ✓ Automaton started (PID: xxxx)
```

---

## ✅ Yang Sudah Siap

- ✅ Bot Telegram (Python) - main.py
- ✅ Automaton (Node.js) - automaton/
- ✅ Combined startup script - start_combined.sh
- ✅ Railway config - Procfile, railway.json, nixpacks.toml
- ✅ Documentation - 3 guide files

---

## 🎯 Deploy Sekarang

### Step 1: Push ke GitHub (2 menit)

```bash
cd Bismillah
git add .
git commit -m "feat: combined deployment bot + automaton"
git push origin main
```

### Step 2: Railway Auto-Deploy (5-10 menit)

Railway akan otomatis:
1. ✅ Install Python 3.10
2. ✅ Install Node.js 20
3. ✅ Install Python dependencies
4. ✅ Install Node.js dependencies
5. ✅ Build Automaton TypeScript
6. ✅ Run start_combined.sh

### Step 3: Verify (1 menit)

Buka Railway logs, cari:
```
✓ Bot started (PID: 123)
✓ Automaton started (PID: 456)
Both services are running!
```

### Step 4: Test (1 menit)

- Buka Telegram bot
- Kirim `/start`
- Bot harus respond
- Coba fitur Automaton

---

## 📋 Environment Variables Checklist

Pastikan sudah di-set di Railway:

### Bot (Python)
- [ ] TELEGRAM_BOT_TOKEN
- [ ] SUPABASE_URL
- [ ] SUPABASE_KEY
- [ ] ENCRYPTION_KEY
- [ ] (env vars lainnya dari .env)

### Automaton (Node.js)
- [ ] CONWAY_API_KEY
- [ ] CONWAY_WALLET_ADDRESS
- [ ] (env vars lainnya dari automaton/.env)

---

## 🔍 Monitoring

### Cek Logs
Railway Dashboard → Logs tab

### Cek Resource
Railway Dashboard → Metrics tab
- RAM usage: harus < 512MB
- CPU usage: monitor spikes

### Cek Health
- Bot respond di Telegram
- Automaton berjalan (lihat logs)

---

## 🐛 Jika Ada Masalah

### Bot tidak respond
```bash
# Cek logs Railway
# Pastikan TELEGRAM_BOT_TOKEN benar
# Test dengan /start
```

### Automaton tidak start
```bash
# Cek logs Railway
# Pastikan CONWAY_API_KEY benar
# Cek automaton/dist/ folder ada
```

### Out of Memory
```bash
# Upgrade Railway plan
# Atau rollback ke bot-only
```

---

## 📚 Dokumentasi Lengkap

1. **DEPLOYMENT_COMBINED_SUMMARY.md** - Overview lengkap
2. **COMBINED_DEPLOYMENT_GUIDE.md** - Panduan detail
3. **QUICK_DEPLOY_COMBINED.md** - Quick reference

---

## 🔄 Rollback (Jika Perlu)

```bash
echo "web: python main.py" > Procfile
git add Procfile
git commit -m "rollback: bot only"
git push
```

---

## 💡 Tips

1. **Monitor logs** saat first deploy
2. **Test bot** segera setelah deploy
3. **Check resource usage** di Railway metrics
4. **Backup .env** sebelum deploy

---

## 🎉 Setelah Deploy Berhasil

- [ ] Bot respond di Telegram
- [ ] Automaton berjalan (cek logs)
- [ ] Resource usage normal (< 512MB)
- [ ] No error di logs
- [ ] Test semua fitur bot
- [ ] Test fitur Automaton

---

**READY TO DEPLOY!** 🚀

Jalankan:
```bash
git add . && git commit -m "feat: combined deployment" && git push
```
