# 🔗 Connect Bot ke Automaton - FINAL STEP

## ✅ Status Saat Ini

- ✅ Bot deployed dan running
- ✅ Automaton deployed dan running
- ✅ Automaton URL: `https://automaton-production-a899.up.railway.app`

---

## 🎯 Langkah Terakhir: Tambah Environment Variable

### Step 1: Buka Railway Dashboard Bot Service

1. Login ke https://railway.app
2. Pilih project **Bot** (cryptomentor-bot)
3. Klik tab **"Variables"**

### Step 2: Tambah Variable Baru

Klik button **"New Variable"** atau **"Add Variable"**

Isi dengan:

**Variable Name:**
```
CONWAY_API_URL
```

**Value:**
```
https://automaton-production-a899.up.railway.app
```

### Step 3: Save & Wait Auto-Restart

1. Klik **"Add"** atau **"Save"**
2. Railway akan otomatis restart bot (tunggu 30-60 detik)
3. Check logs untuk konfirmasi bot restart sukses

---

## ✅ Test Integration

### Test 1: Health Check Automaton

Buka browser atau gunakan curl:

```bash
curl https://automaton-production-a899.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime": 123
}
```

### Test 2: Via Telegram Bot

Kirim command ke bot:

```
/automaton status
```

**Expected Response:**
Bot akan respond dengan status Automaton yang sedang running, termasuk:
- Automaton version
- Uptime
- Wallet address
- Balance
- Active strategies

### Test 3: Check Bot Logs

Railway Dashboard → Bot Service → Logs

Cari output seperti:
```
✓ Connected to Automaton API
✓ Automaton URL: https://automaton-production-a899.up.railway.app
✓ Automaton health check: OK
```

---

## 🎉 Selesai!

Setelah langkah ini, sistem kamu sudah fully integrated:

```
┌─────────────────────────────────────────────┐
│                                             │
│  User → Telegram Bot (Railway)              │
│           ↓                                 │
│  Bot → Automaton API (Railway)              │
│           ↓                                 │
│  Automaton → Conway API (External)          │
│           ↓                                 │
│  Conway → Blockchain (Base Network)         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### Bot tidak bisa connect ke Automaton

**Check:**
1. Variable `CONWAY_API_URL` sudah benar?
2. Automaton masih running? (check Railway logs)
3. URL accessible? (test dengan curl)

**Fix:**
```bash
# Test Automaton URL
curl https://automaton-production-a899.up.railway.app/health

# Jika error, check Automaton logs di Railway
```

### Automaton respond tapi bot error

**Check Bot Logs:**
Railway Dashboard → Bot Service → Logs

Cari error message seperti:
```
Error: Failed to connect to Automaton
Error: Automaton API timeout
Error: Invalid Automaton response
```

**Fix:**
1. Check `CONWAY_API_URL` format (harus include `https://`)
2. Check Automaton environment variables
3. Restart bot service

### Command `/automaton status` tidak respond

**Possible Causes:**
1. Bot belum restart setelah add variable
2. Automaton down atau error
3. Network issue antara Railway services

**Fix:**
1. Manual restart bot service di Railway
2. Check Automaton logs
3. Test Automaton URL dengan curl

---

## 📊 Monitoring

### Daily Checks

1. **Bot Status:**
   - Railway Dashboard → Bot Service → Metrics
   - Check CPU, RAM, uptime

2. **Automaton Status:**
   - Railway Dashboard → Automaton Service → Metrics
   - Check CPU, RAM, uptime

3. **Integration Health:**
   - Test `/automaton status` via Telegram
   - Check bot logs for errors

### Weekly Checks

1. **API Usage:**
   - Conway Dashboard → API Usage
   - Monitor credit consumption

2. **Performance:**
   - Railway Metrics → Response times
   - Check for slow requests

3. **Errors:**
   - Railway Logs → Filter by "error"
   - Investigate any recurring issues

---

## 🚀 Next Steps

Setelah integration sukses:

1. ✅ Test semua fitur Automaton via bot
2. ✅ Monitor logs untuk 24 jam pertama
3. ✅ Setup alerts (optional)
4. ✅ Document any issues
5. ✅ Optimize based on usage patterns

---

## 📝 Summary

**What You Did:**
1. ✅ Deployed Bot to Railway
2. ✅ Deployed Automaton to Railway (separate service)
3. ✅ Got Automaton URL: `automaton-production-a899.up.railway.app`
4. ⏳ Add `CONWAY_API_URL` to Bot service
5. ⏳ Test integration

**Architecture:**
- ✅ Microservices (Bot + Automaton separate)
- ✅ Independent deployment
- ✅ HTTP API communication
- ✅ Scalable and maintainable

**Cost:**
- Bot: $5/month
- Automaton: $5/month
- **Total: $10/month**

---

**Ready?** Tambah environment variable sekarang! 🚀
