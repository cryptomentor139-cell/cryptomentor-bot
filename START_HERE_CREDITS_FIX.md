# 🎯 START HERE - Fix OpenClaw Credits

## ❌ Masalah Saat Ini

Dari screenshot Anda, error yang terjadi:
```
❌ Error: no such column: credits
❌ Error: sqlite3.Cursor object is not callable
```

## ✅ Solusi Sudah Dibuat

Saya sudah:
1. ✅ Membuat script fix database
2. ✅ Menjalankan fix di local (berhasil)
3. ✅ Push ke GitHub (berhasil)
4. ✅ Railway akan auto-deploy

## 🚀 Langkah Selanjutnya (MUDAH!)

### Opsi 1: Tunggu Auto-Deploy (PALING MUDAH)

1. **Tunggu 2-3 menit** - Railway sedang deploy otomatis
2. **Check Railway Dashboard:**
   - Buka: https://railway.app/dashboard
   - Pilih project bot Anda
   - Tab "Deployments" → Lihat status
   - Tunggu sampai status "Success" ✅

3. **Setelah deploy selesai, test di Telegram:**
   ```
   /admin_openclaw_balance
   ```
   
   Jika berhasil, akan muncul:
   ```
   🔑 OpenRouter API Status
   Account: ...
   💰 Balance: $XX.XX
   ```

4. **Jika masih error, lanjut ke Opsi 2**

### Opsi 2: Manual Migration via Railway CLI

Jika setelah auto-deploy masih error, jalankan migration manual:

```bash
# 1. Login ke Railway
railway login

# 2. Link project (pilih project bot Anda)
railway link

# 3. Run migration
railway run python fix_openclaw_credits_sqlite.py
railway run python fix_credits_column.py

# 4. Restart bot
railway restart

# 5. Check logs
railway logs
```

### Opsi 3: Manual via Railway Dashboard

1. Buka Railway Dashboard
2. Pilih service bot
3. Tab "Settings" → Scroll ke bawah
4. Klik "Restart" button
5. Tunggu restart selesai
6. Test lagi di Telegram

## 🧪 Testing - Pastikan Berhasil

### Test 1: Admin Balance Check

Kirim ke bot:
```
/admin_openclaw_balance
```

**Expected:** Muncul OpenRouter balance info
**Jika error:** Lanjut ke troubleshooting

### Test 2: Add Credits

Kirim ke bot:
```
/admin_add_credits 1087836223 0.3 coba
```

**Expected:**
```
✅ Credits Allocated Successfully!

User: 1087836223
Amount: $0.30
Reason: coba

User Balance:
• Before: $0.00
• After: $0.30
```

**Jika error:** Lanjut ke troubleshooting

### Test 3: User Check Balance

User (1087836223) kirim:
```
/openclaw_balance
```

**Expected:**
```
💰 Your OpenClaw Credits

Current Balance: $0.30
Total Allocated: $0.30
Total Used: $0.00
```

### Test 4: Use OpenClaw

User chat biasa:
```
Hello, can you help me analyze Bitcoin?
```

**Expected:** Bot reply dengan analisis, credits ter-deduct

## ⚠️ Troubleshooting

### Error: "no such column: credits" (Masih Muncul)

**Penyebab:** Migration belum jalan di Railway

**Solusi:**
```bash
# Via Railway CLI
railway run python fix_credits_column.py
railway restart
```

### Error: "sqlite3.Cursor object is not callable"

**Penyebab:** Code lama masih terpakai

**Solusi:**
```bash
# Force restart
railway restart

# Check logs
railway logs
```

### Bot Tidak Respond

**Check:**
1. Railway status: https://railway.app/dashboard
2. Logs: `railway logs`
3. Environment variables: Check `OPENCLAW_API_KEY`

**Fix:**
```bash
railway restart
```

### Credits Tidak Ter-deduct

**Check:**
1. User sudah punya credits? `/openclaw_balance`
2. OpenClaw handler aktif? Check logs
3. Database connection OK? Check logs

**Debug:**
```bash
railway logs --filter "openclaw"
```

## 📊 Setelah Berhasil

### Workflow Komersial

1. **User Request Credits**
   - User kirim bukti transfer Rp 100k

2. **Admin Verify**
   - Cek bukti transfer di bank/e-wallet

3. **Admin Allocate**
   ```
   /admin_add_credits <user_id> 7 "Payment Rp 100k via BCA"
   ```

4. **System Auto-Notify User**
   - Bot kirim notif ke user
   - Credits langsung bisa dipakai

5. **User Use OpenClaw**
   - Chat biasa dengan bot
   - Credits auto-deduct per message

6. **Admin Monitor**
   ```
   /admin_system_status
   /admin_openclaw_balance
   ```

### Pricing Recommendation

```
Rp 50,000  = $3.5 USD
Rp 100,000 = $7 USD
Rp 200,000 = $14 USD
```

Adjust based on:
- Exchange rate
- Your margin (10-20%)
- OpenRouter costs

## 🎯 Success Checklist

- [ ] Railway deployment success
- [ ] `/admin_openclaw_balance` works
- [ ] `/admin_add_credits` works
- [ ] User receives notification
- [ ] `/openclaw_balance` shows balance
- [ ] OpenClaw chat deducts credits
- [ ] No errors in logs

## 🔗 Quick Links

- [Railway Dashboard](https://railway.app/dashboard)
- [OpenRouter Dashboard](https://openrouter.ai/settings/keys)
- [GitHub Repo](https://github.com/cryptomentor139-cell/cryptomentor-bot)

## 📞 Status Check

**Current Status:**
- ✅ Code fixed and pushed to GitHub
- ⏳ Railway auto-deploying (wait 2-3 min)
- ⏳ Waiting for you to test

**Next Action:**
1. Wait for Railway deployment
2. Test `/admin_openclaw_balance`
3. If works → Start commercializing! 🚀
4. If error → Run Opsi 2 (Railway CLI migration)

---

**Dibuat:** 2026-03-04
**Status:** Ready to test! 🎯
