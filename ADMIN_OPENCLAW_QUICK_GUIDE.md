# 🔑 Admin OpenClaw - Quick Guide

## Admin Unlimited Credits Sudah Aktif! ✅

Sistem OpenClaw LangChain sekarang **mengenali admin** dan memberikan **unlimited credits**.

---

## 🎯 Cara Menggunakan (Admin)

### 1. Check Status Admin
```
/openclaw_balance
```

**Response untuk Admin:**
```
🔑 ADMIN MODE - OpenClaw Credits

✅ Status: UNLIMITED CREDITS
🎯 Access Level: Full System Administrator

As an admin, you have:
• Unlimited OpenClaw AI usage
• No credit deductions
• Full access to all features
• Ability to manage user credits
```

### 2. Chat dengan OpenClaw (Unlimited)
```
What's the Bitcoin price?
```

**Response:**
```
[AI response with real-time data]

🔑 ADMIN MODE - Unlimited Credits
```

### 3. Gunakan Admin Tools
```
Show me system statistics
```
AI akan call `get_system_statistics()` tool dan menampilkan:
- Total users
- Total credits allocated
- Total credits used
- Average per user

```
Check balance for user 123456789
```
AI akan call `check_user_balance()` tool dan menampilkan balance user tersebut.

---

## 💰 Manage User Credits

### Add Credits ke User
```
/admin_add_credits <user_id> <amount> [reason]
```

**Example:**
```
/admin_add_credits 123456789 7 Payment Rp 100k
```

**Response:**
```
✅ Credits Allocated Successfully!

User: 123456789
Amount: $7.00
Reason: Payment Rp 100k

User Balance:
• Before: $0.00
• After: $7.00

✅ Notification sent
```

User akan otomatis dapat notifikasi:
```
✅ Credits Added!

💰 Amount Added: $7.00
💳 Your Balance: $7.00

Your OpenClaw credits have been successfully added!

You can now use OpenClaw AI Agent.
Just chat normally - no commands needed!

Check balance: /openclaw_balance

Thank you for your payment! 🎉
```

---

## 📊 View System Stats
```
/admin_system_stats
```

**Response:**
```
📊 OpenClaw System Statistics

Total Users: 5
Total Credits: $35.00
Total Allocated: $50.00
Total Used: $15.00

Average per User: $7.00

🔗 Quick Actions:
• /admin_add_credits - Allocate to user
• /openclaw_balance - Check user balance
```

---

## 🤖 AI Features untuk Admin

### 1. Real-Time Crypto Data
```
What's the current Bitcoin price?
```
AI akan fetch real-time data dari CoinGecko/Binance.

### 2. Market Analysis
```
Analyze Ethereum market trend
```
AI akan provide detailed analysis dengan real data.

### 3. Multiple Coins
```
Compare BTC, ETH, and SOL prices
```
AI akan fetch dan compare multiple coins.

### 4. System Management
```
How many users are using OpenClaw?
```
AI akan call admin tool untuk get stats.

---

## 🔐 Admin Privileges

Sebagai admin, Anda mendapat:

✅ **Unlimited Credits**
- No balance checks
- No credit deductions
- Unlimited usage

✅ **Admin Tools**
- `check_user_balance()` - Check any user's balance
- `get_system_statistics()` - View system stats

✅ **Extended AI Context**
- AI knows you're admin
- Can provide longer responses
- No limitations

✅ **Management Commands**
- `/admin_add_credits` - Allocate credits
- `/admin_system_stats` - View statistics

---

## 📋 User Commands (untuk referensi)

Regular users menggunakan:
- `/openclaw_balance` - Check their balance
- `/openclaw_help` - Get help
- Chat normally (deducted ~$0.02 per message)

---

## 💡 Tips untuk Admin

1. **Testing**
   - Test fitur tanpa khawatir credits
   - Demo ke user dengan unlimited access

2. **Monitoring**
   - Check system stats regularly
   - Monitor user credit usage

3. **Support**
   - Help users dengan add credits
   - Respond to credit requests

4. **Pricing**
   - Standard: Rp 100,000 = $7 USD credits
   - ~$0.02 per message
   - $7 = ~350 messages

---

## 🚀 Deploy ke Production

### 1. Verify Admin IDs di .env
```bash
ADMIN1=YOUR_TELEGRAM_ID
ADMIN2=ANOTHER_ADMIN_ID
ADMIN_IDS=ID1,ID2,ID3
```

### 2. Push ke Railway
```bash
git add .
git commit -m "Add admin unlimited credits for OpenClaw"
git push
```

### 3. Set Environment Variables di Railway
- Go to Railway dashboard
- Select your project
- Go to Variables tab
- Add/verify: `ADMIN1`, `ADMIN2`, `ADMIN_IDS`
- Restart service

### 4. Test Production
```
/openclaw_balance
# Should show: ADMIN MODE - Unlimited Credits

What's the Bitcoin price?
# Should work without credit deduction
```

---

## ✅ Status Implementasi

**COMPLETED & READY TO USE**

✅ Admin recognition from environment variables
✅ Unlimited credits for all admins
✅ No credit checks for admins
✅ No credit deductions for admins
✅ Admin-aware AI system prompt
✅ Admin-only tools (check_user_balance, get_system_statistics)
✅ Admin mode footer in responses
✅ Admin commands for credit management

---

## 🔧 Technical Details

### Files Modified:
1. `app/openclaw_langchain_agent_simple.py`
   - Added `is_admin` parameter
   - Admin-aware system prompt
   - Separate tool sets for admin/users
   - No credit deduction for admins

2. `app/handlers_openclaw_langchain.py`
   - Admin check using `is_admin()`
   - Skip credit checks for admins
   - Admin mode footer
   - Admin-specific balance display

3. `app/admin_auth.py`
   - Already exists - provides admin recognition

### Admin Tools:
```python
@tool
def check_user_balance(user_id: int) -> str:
    """Check a user's credit balance (admin tool)"""

@tool
def get_system_statistics() -> str:
    """Get OpenClaw system statistics (admin only)"""
```

---

## 📞 Support

Jika ada masalah:
1. Check admin IDs di environment variables
2. Restart bot/service
3. Test dengan `/openclaw_balance`
4. Check logs untuk errors

---

**Admin sekarang bisa menggunakan OpenClaw dengan unlimited credits! 🎉**

Semua admin yang terdaftar di `ADMIN1`, `ADMIN2`, atau `ADMIN_IDS` otomatis mendapat unlimited access.
