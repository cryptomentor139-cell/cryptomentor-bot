# Admin Unlimited Credits - OpenClaw LangChain

## 🔑 Fitur Admin dengan Unlimited Credits

Sistem OpenClaw LangChain sekarang **mengenali admin** dan memberikan **unlimited credits** untuk semua admin yang terdaftar.

---

## ✅ Implementasi

### 1. **Admin Recognition**
- Sistem menggunakan `admin_auth.py` untuk mengenali admin
- Admin IDs diambil dari environment variables:
  - `ADMIN1`, `ADMIN2` (primary admins)
  - `ADMIN_IDS` (comma-separated list)
  - `ADMIN3` - `ADMIN9` (individual admins)
  - `ADMIN_USER_ID` (legacy fallback)

### 2. **Unlimited Credits untuk Admin**
Admin mendapat privilege khusus:
- ✅ **No credit checks** - Tidak ada pengecekan balance
- ✅ **No credit deductions** - Tidak ada pemotongan credits
- ✅ **Unlimited usage** - Bisa menggunakan OpenClaw tanpa batas
- ✅ **Full access** - Akses ke semua fitur dan tools

### 3. **Admin-Aware AI Agent**
LangChain agent mengenali admin dengan:
- **System prompt khusus** yang memberitahu AI bahwa user adalah admin
- **Extended tools** - Admin mendapat akses ke tools tambahan:
  - `check_user_balance()` - Cek balance user lain
  - `get_system_statistics()` - Lihat statistik sistem
- **No limitations** - AI bisa memberikan response lebih panjang untuk admin

---

## 🎯 Cara Kerja

### Untuk Admin:

1. **Chat Normal**
   ```
   Admin: What's the Bitcoin price?
   OpenClaw: [Fetches real-time data and responds]
   
   Footer: 🔑 ADMIN MODE - Unlimited Credits
   ```

2. **Check Balance**
   ```
   /openclaw_balance
   
   Response:
   🔑 ADMIN MODE - OpenClaw Credits
   ✅ Status: UNLIMITED CREDITS
   🎯 Access Level: Full System Administrator
   ```

3. **Admin Tools**
   Admin bisa bertanya:
   - "Check balance for user 123456789"
   - "Show me system statistics"
   - "How many users are using OpenClaw?"

### Untuk User Biasa:

1. **Credit Check**
   - Sistem cek balance sebelum processing
   - Jika balance < $0.01, ditolak
   - Setiap message ~$0.02

2. **Normal Usage**
   ```
   User: What's the Bitcoin price?
   OpenClaw: [Response]
   
   Footer: 💰 Credits used: $0.02 | Balance: $6.98
   ```

---

## 📋 Commands

### User Commands:
- `/openclaw_balance` - Cek balance credits
- `/openclaw_help` - Bantuan penggunaan

### Admin Commands:
- `/openclaw_balance` - Lihat status admin (unlimited)
- `/admin_add_credits <user_id> <amount> [reason]` - Tambah credits ke user
- `/admin_system_stats` - Lihat statistik sistem

---

## 🔧 Technical Details

### File yang Dimodifikasi:

1. **`app/openclaw_langchain_agent_simple.py`**
   - Added `is_admin` parameter to `chat()` method
   - Admin-aware system prompt
   - Separate tool sets for admin vs regular users
   - No credit deduction for admins

2. **`app/handlers_openclaw_langchain.py`**
   - Check admin status using `is_admin(user_id)`
   - Skip credit checks for admins
   - Pass `is_admin` flag to agent
   - Different footer for admin vs regular users

3. **`app/admin_auth.py`**
   - Already exists - provides `is_admin()` function
   - Reads admin IDs from environment variables

### Admin Tools:

```python
@tool
def check_user_balance(user_id: int) -> str:
    """Check a user's credit balance (admin tool)"""
    # Returns user's balance

@tool
def get_system_statistics() -> str:
    """Get OpenClaw system statistics (admin only)"""
    # Returns system-wide stats
```

---

## 🚀 Testing

### Test sebagai Admin:

1. **Set Admin ID di .env**
   ```bash
   ADMIN1=YOUR_TELEGRAM_USER_ID
   ```

2. **Restart Bot**
   ```bash
   python bot.py
   ```

3. **Test Commands**
   ```
   /openclaw_balance
   # Should show: ADMIN MODE - Unlimited Credits
   
   What's the Bitcoin price?
   # Should work without credit deduction
   # Footer: 🔑 ADMIN MODE - Unlimited Credits
   ```

4. **Test Admin Tools**
   ```
   Show me system statistics
   # AI will call get_system_statistics() tool
   
   Check balance for user 123456789
   # AI will call check_user_balance() tool
   ```

---

## 🎉 Benefits

### Untuk Admin:
- ✅ Test sistem tanpa khawatir credits
- ✅ Demo ke user tanpa biaya
- ✅ Monitor sistem dengan tools khusus
- ✅ Unlimited access untuk management

### Untuk User:
- ✅ Fair usage dengan credit system
- ✅ Transparent pricing
- ✅ Pay-per-use model
- ✅ Admin bisa bantu top-up

---

## 📊 System Prompt untuk Admin

Ketika admin chat, AI mendapat context tambahan:

```
🔑 ADMIN MODE ACTIVE:
- You are interacting with a SYSTEM ADMINISTRATOR
- This user has UNLIMITED CREDITS and FULL ACCESS to all features
- No credit checks or limitations apply to this user
- You can provide extended analysis and unlimited responses
- Admin has access to all system commands and features
```

Ini membuat AI:
- Lebih aware bahwa user adalah admin
- Bisa memberikan response lebih detail
- Tidak perlu khawatir tentang credit usage
- Bisa menggunakan admin-only tools

---

## ✅ Status

**IMPLEMENTED & READY TO USE**

Semua admin yang terdaftar di environment variables sekarang:
- ✅ Dikenali oleh sistem
- ✅ Mendapat unlimited credits
- ✅ Bisa menggunakan semua fitur tanpa batas
- ✅ Mendapat akses ke admin tools
- ✅ AI agent aware dengan status admin

---

## 🔐 Security

- Admin IDs stored in environment variables (secure)
- Admin check dilakukan di setiap request
- Admin tools hanya available untuk admin
- Regular users tidak bisa akses admin tools
- Logging untuk semua admin actions

---

## 📝 Next Steps

1. **Deploy ke Railway**
   ```bash
   git add .
   git commit -m "Add admin unlimited credits for OpenClaw LangChain"
   git push
   ```

2. **Set Environment Variables di Railway**
   - Pastikan `ADMIN1`, `ADMIN2`, dll sudah di-set
   - Restart service setelah update

3. **Test Production**
   - Login sebagai admin
   - Test `/openclaw_balance`
   - Test chat dengan OpenClaw
   - Verify "ADMIN MODE" footer muncul

---

**Admin sekarang bisa menggunakan OpenClaw dengan unlimited credits! 🎉**
