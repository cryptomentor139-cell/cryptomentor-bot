# 🔧 OpenClaw Credits Database Fix

## ❌ Masalah yang Terjadi

Error di screenshot menunjukkan:
```
Error: no such column: credits
Error: sqlite3.Cursor object is not callable
```

Ini berarti:
1. Tabel `openclaw_user_credits` belum dibuat
2. Migrasi database belum dijalankan
3. Sistem credits tidak bisa berfungsi

## ✅ Solusi Lengkap

### Opsi 1: Fix di Local (Recommended)

1. **Jalankan script fix:**
   ```bash
   cd Bismillah
   python fix_openclaw_credits_sqlite.py
   ```

   Atau double-click: `RUN_CREDITS_FIX.bat`

2. **Verifikasi:**
   ```bash
   python -c "import sqlite3; conn = sqlite3.connect('cryptomentor.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name LIKE \"openclaw_%\"'); print(cursor.fetchall())"
   ```

3. **Push ke Railway:**
   ```bash
   git add .
   git commit -m "Fix OpenClaw credits database"
   git push
   ```

### Opsi 2: Fix di Railway (Via Railway CLI)

1. **Connect ke Railway:**
   ```bash
   railway login
   railway link
   ```

2. **Run migration:**
   ```bash
   railway run python fix_openclaw_credits_sqlite.py
   ```

3. **Restart service:**
   ```bash
   railway restart
   ```

### Opsi 3: Manual via Railway Dashboard

1. Buka Railway Dashboard
2. Pilih service bot Anda
3. Buka tab "Variables"
4. Klik "Deploy" untuk trigger rebuild
5. Tunggu deployment selesai

## 📊 Struktur Database yang Dibuat

Script akan membuat 4 tabel:

### 1. `openclaw_user_credits`
- `user_id` (PRIMARY KEY)
- `credits` (REAL) - Balance saat ini
- `total_allocated` (REAL) - Total pernah dialokasi
- `total_used` (REAL) - Total sudah dipakai
- `created_at`, `updated_at`

### 2. `openclaw_credit_allocations`
- Log setiap kali admin add credits
- Tracking OpenRouter balance before/after
- Reason untuk audit trail

### 3. `openclaw_credit_usage`
- Log setiap message yang pakai credits
- Token usage tracking
- Model yang dipakai

### 4. `openclaw_balance_snapshots`
- Snapshot berkala OpenRouter vs Allocated
- Untuk monitoring dan analytics

## 🧪 Testing Setelah Fix

### 1. Test Admin Commands

```bash
# Check OpenRouter balance
/admin_openclaw_balance

# Add credits to user
/admin_add_credits 1087836223 0.3 coba

# Check system status
/admin_system_status
```

### 2. Test User Commands

```bash
# Check balance
/openclaw_balance

# Use OpenClaw (auto-deduct credits)
Just chat normally with the bot
```

### 3. Verify Database

```python
import sqlite3
conn = sqlite3.connect('cryptomentor.db')
cursor = conn.cursor()

# Check tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'openclaw_%'")
print(cursor.fetchall())

# Check user credits
cursor.execute("SELECT * FROM openclaw_user_credits")
print(cursor.fetchall())
```

## 🚀 Workflow Komersial

Setelah fix berhasil:

### 1. User Request Credits
User kirim bukti transfer:
- Bank: Rp 100,000
- E-money: Rp 100,000  
- Crypto: ~$7 USDT

### 2. Admin Verify Payment
Cek bukti transfer di bank/e-wallet/blockchain

### 3. Admin Allocate Credits
```bash
/admin_add_credits <user_id> <amount> <reason>

# Example:
/admin_add_credits 123456789 7 "Payment Rp 100k via BCA"
```

### 4. System Auto-Notify User
Bot otomatis kirim notifikasi ke user:
```
✅ Credits Added!
💰 Amount Added: $7.00
💳 Your Balance: $7.00

You can now use OpenClaw AI Agent.
Just chat normally - no commands needed!
```

### 5. User Uses OpenClaw
- User chat biasa dengan bot
- System auto-deduct credits per message
- User bisa cek balance: `/openclaw_balance`

### 6. Admin Monitor
```bash
# Check system status
/admin_system_status

# Check OpenRouter balance
/admin_openclaw_balance
```

## ⚠️ Important Notes

1. **OpenRouter Balance**
   - Total allocated tidak boleh melebihi OpenRouter balance
   - System akan reject allocation jika over-limit
   - Top-up OpenRouter dulu jika perlu

2. **Credit Pricing**
   - Rp 100,000 = ~$7 USD
   - Adjust sesuai exchange rate
   - Bisa set margin untuk profit

3. **Monitoring**
   - Cek `/admin_system_status` secara berkala
   - Monitor OpenRouter usage di dashboard
   - Track user usage patterns

4. **Database Backup**
   - Railway auto-backup database
   - Bisa export manual via Railway CLI
   - Keep local backup untuk safety

## 🔗 Quick Links

- [OpenRouter Dashboard](https://openrouter.ai/settings/keys)
- [OpenRouter Billing](https://openrouter.ai/settings/billing)
- [OpenRouter Activity](https://openrouter.ai/activity)
- [Railway Dashboard](https://railway.app/dashboard)

## 📞 Support

Jika masih ada error:
1. Check Railway logs: `railway logs`
2. Check database: `railway run python -c "import sqlite3; ..."`
3. Restart service: `railway restart`

---

**Status:** Ready to commercialize! 🚀
