# Deploy & Test Per-User Credit System

## ✅ Migration Berhasil!

Tables sudah dibuat di Supabase:
- `openclaw_user_credits` - Per-user credit balances
- `openclaw_credit_allocations` - Admin allocation log
- `openclaw_credit_usage` - Per-message usage log
- `openclaw_balance_snapshots` - System balance tracking

## 🚀 Deploy ke Railway

### 1. Commit & Push
```bash
git add .
git commit -m "Implement OpenClaw per-user credit tracking system"
git push origin main
```

### 2. Railway Auto-Deploy
- Railway akan detect changes
- Auto-deploy dalam 2-3 menit
- Tunggu sampai status "Success"

## 🧪 Testing Setelah Deploy

### Test 1: Check System Status (Admin)
Kirim ke bot:
```
/admin_system_status
```

**Expected Result:**
```
📊 OpenClaw System Status

💰 OpenRouter Balance: $XX.XX
📊 Total Allocated: $0.00 (0.0%)
✅ Available to Allocate: $XX.XX

📈 Usage Stats:
• Total Ever Allocated: $0.00
• Total Used: $0.00
• Active Users: 0

✅ Balance is healthy.

🔗 Quick Actions:
• /admin_add_credits - Allocate to user
• /admin_openclaw_balance - Check OpenRouter
• Top-up OpenRouter
```

### Test 2: Allocate Credits to Yourself (Admin)
```
/admin_add_credits YOUR_USER_ID 10 Test allocation
```

**Expected Result:**
```
✅ Credits Allocated Successfully!

User: YOUR_USER_ID
Amount: $10.00
Reason: Test allocation

User Balance:
• Before: $0.00
• After: $10.00

System Status:
💰 OpenRouter Balance: $XX.XX
📊 Total Allocated: $10.00
✅ Available: $XX.XX

✅ Notification sent
```

### Test 3: Check Your Balance (User)
```
/openclaw_balance
```

**Expected Result:**
```
💳 Your OpenClaw Balance

👤 User ID: YOUR_USER_ID
💰 Available Credits: $10.00

📊 Usage Stats:
• Total Used: $0.00
• Messages Sent: 0
• Avg Cost/Message: $0.0000

✅ Balance is healthy.

💰 Top-Up Credits:
Use /subscribe to see payment options

📞 Need Help?
Contact admin: @BillFarr
```

### Test 4: Send Message to OpenClaw
Kirim pesan biasa (OpenClaw default mode):
```
Analyze BTC trend
```

**Expected Result:**
```
[AI Response tentang BTC]

💰 Cost: $0.0234 • 💳 Balance: $9.98
```

### Test 5: Check Balance After Usage
```
/openclaw_balance
```

**Expected Result:**
```
💳 Your OpenClaw Balance

👤 User ID: YOUR_USER_ID
💰 Available Credits: $9.98

📊 Usage Stats:
• Total Used: $0.02
• Messages Sent: 1
• Avg Cost/Message: $0.0200

✅ Balance is healthy.
```

### Test 6: Check System Status Again (Admin)
```
/admin_system_status
```

**Expected Result:**
```
📊 OpenClaw System Status

💰 OpenRouter Balance: $XX.XX
📊 Total Allocated: $9.98 (X.X%)
✅ Available to Allocate: $XX.XX

📈 Usage Stats:
• Total Ever Allocated: $10.00
• Total Used: $0.02
• Active Users: 1

👥 Top Users by Balance:
• YOUR_USER_ID: $9.98 (used: $0.02)
```

### Test 7: Test Over-Allocation Prevention (Admin)
```
/admin_add_credits 123456789 999999 Test over-allocation
```

**Expected Result:**
```
❌ Insufficient OpenRouter Balance!

💰 OpenRouter Balance: $XX.XX
📊 Total Allocated: $9.98
✅ Available to Allocate: $XX.XX

❌ Requested: $999999.00
⚠️ Would exceed balance by $XXXXX.XX

Solution:
1. Top-up OpenRouter first: https://openrouter.ai/settings/billing
2. Or allocate max $XX.XX to this user
```

## ✅ Success Criteria

Semua test di atas harus berhasil:
- ✅ System status menampilkan balance
- ✅ Admin bisa allocate credits
- ✅ User menerima notification
- ✅ User balance tampil benar
- ✅ Credits terpotong per message
- ✅ Cost ditampilkan setelah response
- ✅ System mencegah over-allocation

## 🎯 Workflow Production

### Untuk Admin:

1. **User Request Top-Up**
   - User kirim bukti transfer Rp 100k
   - User mention user ID nya

2. **Verify Payment**
   - Cek transfer bank/e-money/crypto
   - Pastikan amount sesuai

3. **Check System**
   ```
   /admin_system_status
   ```
   - Pastikan ada available balance
   - Jika kurang, top-up OpenRouter dulu

4. **Allocate Credits**
   ```
   /admin_add_credits USER_ID 7 Payment Rp 100k
   ```
   - System auto-validate
   - User auto-notified

5. **Monitor**
   - Check system status berkala
   - Pastikan tidak over-allocated

### Untuk User:

1. **Check Balance**
   ```
   /openclaw_balance
   ```

2. **Top-Up**
   ```
   /subscribe
   ```
   - Lihat payment options
   - Transfer sesuai amount
   - Kirim bukti ke @BillFarr

3. **Use OpenClaw**
   - Chat biasa, no commands
   - Credits auto-deducted
   - Cost shown per message

## 📊 Monitoring Commands

### Admin:
- `/admin_system_status` - System overview
- `/admin_openclaw_balance` - OpenRouter balance
- `/admin_add_credits` - Allocate to user
- `/admin_openclaw_help` - Show all commands

### User:
- `/openclaw_balance` - Personal balance
- `/subscribe` - Payment options

## 🔧 Troubleshooting

### "Over-allocated" Warning
**Solution:** Top-up OpenRouter di https://openrouter.ai/settings/billing

### User Tidak Terima Notification
**Cause:** User block bot
**Solution:** Minta user unblock/start bot lagi

### Credits Tidak Terpotong
**Cause:** Database connection issue
**Solution:** Check Railway logs, restart jika perlu

## 📝 Summary

Sistem per-user credit tracking sudah:
- ✅ Migration berhasil di Supabase
- ✅ Ready untuk deploy ke Railway
- ✅ Semua command sudah terimplementasi
- ✅ Safety checks sudah ada
- ✅ Logging lengkap untuk audit

**Next:** Deploy ke Railway dan test dengan workflow di atas!

