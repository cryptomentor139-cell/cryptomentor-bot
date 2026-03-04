# 🚀 Deploy OpenClaw Credits Fix to Railway

## ✅ Yang Sudah Diperbaiki (Local)

1. ✅ Tabel `openclaw_user_credits` sudah dibuat
2. ✅ Kolom `credits`, `total_allocated`, `total_used` sudah ditambahkan
3. ✅ Semua index sudah dibuat
4. ✅ Database structure sudah benar

## 📦 Files yang Dibuat

1. `fix_openclaw_credits_sqlite.py` - Script untuk membuat tabel
2. `fix_credits_column.py` - Script untuk menambah kolom
3. `CREDITS_FIX_GUIDE.md` - Dokumentasi lengkap
4. `RUN_CREDITS_FIX.bat` - Batch file untuk Windows

## 🚀 Deploy ke Railway

### Opsi 1: Git Push (Recommended)

```bash
# 1. Add files
git add .

# 2. Commit
git commit -m "Fix OpenClaw credits database - add missing columns"

# 3. Push to Railway
git push

# 4. Railway akan auto-deploy
# Tunggu 2-3 menit
```

### Opsi 2: Railway CLI

```bash
# 1. Login
railway login

# 2. Link project
railway link

# 3. Run migration
railway run python fix_openclaw_credits_sqlite.py
railway run python fix_credits_column.py

# 4. Restart
railway restart
```

### Opsi 3: Manual via Dashboard

1. Buka https://railway.app/dashboard
2. Pilih project bot Anda
3. Klik tab "Deployments"
4. Klik "Deploy" atau tunggu auto-deploy dari git push
5. Monitor logs untuk memastikan tidak ada error

## 🧪 Testing Setelah Deploy

### 1. Check Railway Logs

```bash
railway logs
```

Atau via dashboard: Deployments → Latest → View Logs

### 2. Test Admin Commands

Kirim ke bot Telegram:

```
/admin_openclaw_balance
```

Expected response:
```
🔑 OpenRouter API Status

Account: [Your account]
Tier: Paid/Free

💰 Balance:
• Available: $XX.XX
• Total Limit: $XX.XX
• Used: $XX.XX (XX%)
```

### 3. Test Add Credits

```
/admin_add_credits 1087836223 0.3 coba
```

Expected response:
```
✅ Credits Allocated Successfully!

User: 1087836223
Amount: $0.30
Reason: coba

User Balance:
• Before: $0.00
• After: $0.30

System Status:
💰 OpenRouter Balance: $XX.XX
📊 Total Allocated: $0.30
✅ Available: $XX.XX

✅ Notification sent
```

### 4. Test User Balance Check

User kirim:
```
/openclaw_balance
```

Expected response:
```
💰 Your OpenClaw Credits

Current Balance: $0.30
Total Allocated: $0.30
Total Used: $0.00

✅ You have credits!
Just chat normally to use OpenClaw AI.
```

### 5. Test OpenClaw Usage

User chat biasa:
```
Hello, can you help me?
```

Bot akan:
1. Check user credits
2. Process dengan OpenClaw
3. Deduct credits
4. Reply dengan response

## ⚠️ Troubleshooting

### Error: "no such column: credits"

**Solusi:**
```bash
# Run migration di Railway
railway run python fix_credits_column.py
railway restart
```

### Error: "sqlite3.Cursor object is not callable"

**Penyebab:** Code menggunakan `cursor()` instead of `cursor`

**Sudah diperbaiki di:** `handlers_openclaw_admin_credits.py`

**Verifikasi:**
```python
# WRONG:
cursor = db.cursor()

# CORRECT:
cursor = db.cursor  # Property, not method
```

### Bot tidak respond

**Check:**
1. Railway logs: `railway logs`
2. Database connection: Check `DATABASE_PATH` env var
3. OpenRouter API key: Check `OPENCLAW_API_KEY` env var

**Fix:**
```bash
railway restart
```

### Credits tidak ter-deduct

**Check:**
1. User ada di database: Query `openclaw_user_credits`
2. Credits > 0
3. OpenClaw handler terpanggil

**Debug:**
```bash
railway logs --filter "openclaw"
```

## 📊 Monitoring

### Check System Status

```
/admin_system_status
```

Response:
```
📊 OpenClaw System Status

💰 OpenRouter Balance: $XX.XX
📊 Total Allocated: $XX.XX (XX%)
✅ Available to Allocate: $XX.XX

📈 Usage Stats:
• Total Ever Allocated: $XX.XX
• Total Used: $XX.XX
• Active Users: X

👥 Top Users by Balance:
• 123456789: $X.XX (used: $X.XX)
```

### Check OpenRouter Dashboard

1. https://openrouter.ai/settings/keys
2. https://openrouter.ai/activity
3. Monitor usage dan balance

### Check Railway Metrics

1. Railway Dashboard → Metrics
2. Monitor CPU, Memory, Network
3. Check deployment status

## 💰 Pricing & Commercialization

### Recommended Pricing

```
Rp 100,000 = $7 USD credits
Rp 50,000 = $3.5 USD credits
Rp 200,000 = $14 USD credits
```

Adjust based on:
- Exchange rate (Rp to USD)
- Your margin (10-20%)
- OpenRouter costs

### Payment Methods

1. **Bank Transfer**
   - BCA, Mandiri, BRI, BNI
   - Verify via mobile banking

2. **E-Money**
   - GoPay, OVO, Dana, ShopeePay
   - Verify via transaction history

3. **Crypto**
   - USDT (TRC20/ERC20)
   - Verify via blockchain explorer

### Workflow

1. User request credits
2. User send payment proof
3. Admin verify payment
4. Admin allocate credits: `/admin_add_credits <user_id> <amount> <reason>`
5. System auto-notify user
6. User can use OpenClaw immediately

## 🎯 Success Criteria

✅ `/admin_openclaw_balance` shows correct balance
✅ `/admin_add_credits` allocates credits successfully
✅ User receives notification
✅ `/openclaw_balance` shows user balance
✅ OpenClaw chat deducts credits automatically
✅ No errors in Railway logs

## 🔗 Quick Links

- [Railway Dashboard](https://railway.app/dashboard)
- [OpenRouter Dashboard](https://openrouter.ai/settings/keys)
- [OpenRouter Billing](https://openrouter.ai/settings/billing)
- [OpenRouter Activity](https://openrouter.ai/activity)

## 📞 Next Steps

1. ✅ Push to Railway (git push)
2. ✅ Wait for deployment (2-3 min)
3. ✅ Test admin commands
4. ✅ Test user commands
5. ✅ Start commercializing!

---

**Status:** Ready to deploy! 🚀

**Last Updated:** 2026-03-04
