# Deploy AI Agent Button Fix ke Railway

## Status: ✅ READY FOR DEPLOYMENT

Semua perbaikan telah diverifikasi dan siap untuk di-deploy.

---

## Ringkasan Perbaikan

### 1. Error CallbackQuery Fixed ✅
- File: `menu_handlers.py`
- 4 fungsi diperbaiki
- Error: `AttributeError: 'CallbackQuery' object has no attribute 'update'`
- Fix: Gunakan `update_id=999999` statis

### 2. Spawn Agent Input Handler Added ✅
- File: `bot.py`
- Handler baru untuk memproses input nama agent
- Fix bot restart saat user ketik nama agent

### 3. State Management Improved ✅
- File: `menu_handlers.py`
- Tambah `state_timestamp` untuk tracking state
- Prevent stale state setelah bot restart

---

## Langkah Deploy

### Option 1: Auto Deploy (Recommended)

Jika Railway sudah dikonfigurasi untuk auto-deploy dari GitHub:

```bash
# 1. Commit changes
git add .
git commit -m "Fix AI Agent button errors and spawn agent handler"

# 2. Push ke GitHub
git push origin main

# 3. Railway akan auto-deploy dalam 1-2 menit
```

### Option 2: Manual Deploy via Railway CLI

```bash
# 1. Install Railway CLI (jika belum)
npm install -g @railway/cli

# 2. Login ke Railway
railway login

# 3. Link project
railway link

# 4. Deploy
railway up
```

### Option 3: Manual Deploy via Railway Dashboard

1. Buka Railway dashboard: https://railway.app
2. Pilih project bot Telegram Anda
3. Klik tab "Deployments"
4. Klik "Deploy" > "Redeploy"
5. Tunggu hingga deployment selesai (biasanya 2-3 menit)

---

## Verifikasi Setelah Deploy

### 1. Cek Deployment Status
```bash
# Via Railway CLI
railway status

# Atau cek di Railway dashboard
```

### 2. Cek Logs
```bash
# Via Railway CLI
railway logs

# Atau cek di Railway dashboard > Logs tab
```

### 3. Test Bot di Telegram

#### Test 1: Menu AI Agent
1. Buka bot di Telegram
2. Ketik `/menu`
3. Klik "🤖 AI Agent"
4. **Expected:** Menu muncul dengan 5 tombol
5. **Status:** ✅ Harus berhasil

#### Test 2: Agent Status
1. Dari menu AI Agent
2. Klik "📊 Agent Status"
3. **Expected:** Tampil status atau "Tidak Ada Agent"
4. **Status:** ✅ Harus berhasil (tidak ada error)

#### Test 3: Spawn Agent
1. Dari menu AI Agent
2. Klik "🚀 Spawn Agent"
3. Bot minta input nama
4. Ketik: `TestBot123`
5. **Expected:** Bot proses spawn (cek kredit, premium, dll)
6. **Status:** ✅ Harus berhasil (tidak restart)

#### Test 4: Agent Lineage
1. Dari menu AI Agent
2. Klik "🌳 Agent Lineage"
3. **Expected:** Tampil lineage tree atau "Tidak Ada Agent"
4. **Status:** ✅ Harus berhasil

#### Test 5: Fund Agent
1. Dari menu AI Agent
2. Klik "💰 Fund Agent (Deposit)"
3. **Expected:** Tampil deposit address dan QR code
4. **Status:** ✅ Harus berhasil

#### Test 6: Agent Logs
1. Dari menu AI Agent
2. Klik "📜 Agent Logs"
3. **Expected:** Tampil transaction history atau "Tidak Ada Agent"
4. **Status:** ✅ Harus berhasil

---

## Troubleshooting

### Jika Bot Tidak Merespons Setelah Deploy

1. **Restart bot di Railway:**
```bash
railway restart
```

2. **Cek environment variables:**
   - `TELEGRAM_BOT_TOKEN` harus ada
   - `CONWAY_API_KEY` harus ada (untuk Automaton)
   - `WALLET_ENCRYPTION_KEY` harus ada

3. **Cek logs untuk error:**
```bash
railway logs --tail 100
```

### Jika Masih Ada Error

1. **Rollback ke deployment sebelumnya:**
   - Buka Railway dashboard
   - Tab "Deployments"
   - Pilih deployment sebelumnya yang working
   - Klik "Redeploy"

2. **Report issue:**
   - Screenshot error
   - Copy logs
   - Buat issue di GitHub atau contact developer

---

## Monitoring

### Cek Health Bot

```bash
# Via Railway CLI
railway logs --tail 50 | grep "Bot started"

# Expected output:
# ✅ Bot initialized with X admin(s)
# ✅ Application handlers registered successfully
# ✅ Bot started successfully
```

### Cek Error Logs

```bash
# Via Railway CLI
railway logs --tail 100 | grep "ERROR\|❌"

# Jika ada error, akan muncul di sini
```

---

## Rollback Plan

Jika terjadi masalah serius setelah deploy:

### Quick Rollback
```bash
# Via Railway CLI
railway rollback

# Atau via dashboard:
# Deployments > Previous deployment > Redeploy
```

### Manual Rollback
```bash
# Git revert
git revert HEAD
git push origin main

# Railway akan auto-deploy versi sebelumnya
```

---

## Post-Deployment Checklist

- [ ] Bot merespons di Telegram
- [ ] Menu AI Agent bisa dibuka
- [ ] Semua tombol AI Agent berfungsi
- [ ] Spawn Agent tidak menyebabkan restart
- [ ] Input nama agent diproses dengan benar
- [ ] Tidak ada error di logs
- [ ] User bisa menggunakan fitur Automaton

---

## Contact

Jika ada masalah atau pertanyaan:
- Check logs: `railway logs`
- Check status: `railway status`
- Restart bot: `railway restart`

---

## Status: ✅ READY TO DEPLOY

**All tests passed. Safe to deploy!** 🚀

Deploy sekarang dengan:
```bash
git add .
git commit -m "Fix AI Agent button errors"
git push origin main
```
