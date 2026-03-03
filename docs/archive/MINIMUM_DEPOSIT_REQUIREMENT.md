# ✅ Minimum Deposit Requirement - $30 USDC

## 🎯 New Requirement

**Update:** Semua user (termasuk Admin dan Lifetime Premium) sekarang perlu deposit minimal **$30 USDC** (3.000 credits) untuk spawn AI Agent.

## 📊 Access Control Matrix (Updated)

| User Type | Menu Access | Minimum Deposit | Can Spawn Agent? |
|-----------|-------------|-----------------|------------------|
| **Admin** | ✅ YES | ✅ $30 required | ✅ YES (if $30 deposited) |
| **Lifetime Premium** | ✅ YES | ✅ $30 required | ✅ YES (if $30 deposited) |
| **Monthly Premium** | ⚠️ Need $30 | ✅ $30 required | ✅ YES (if $30 deposited) |
| **Regular User** | ⚠️ Need $30 | ✅ $30 required | ❌ NO (need premium) |

## 🔄 Updated Flow

### Menu Access:
```
User clicks "AI Agent"
    ↓
Check: has deposit >= $30? (3000 credits)
    ↓
NO → Show "Deposit $30 Required" message
    ↓
YES → Show AI Agent menu
```

### Spawn Agent:
```
User clicks "Spawn Agent"
    ↓
Check: is_admin OR has_automaton_access?
    ↓
NO → Show "Automaton Access Required" (Rp2.000.000)
    ↓
YES → Check: is_admin OR is_premium?
    ↓
NO → Show "Premium Required"
    ↓
YES → Check: has deposit >= $30? (3000 credits)
    ↓
NO → Show "Minimum Deposit $30 Required"
    ↓
YES → Check: has credits >= 100k? (spawn fee)
    ↓
NO → Show "Not Enough Credits for Spawn"
    ↓
YES → Proceed to spawn agent
```

## 💰 Deposit Requirements

### Minimum Deposit: $30 USDC = 3.000 Credits

**Why $30?**
- Ensures user has sufficient balance to operate agent
- Prevents spam/abuse
- Covers initial agent operations

**Conversion:**
- 1 USDC = 100 Conway Credits
- $30 USDC = 3.000 Credits
- $5 USDC (minimum) = 500 Credits

### Spawn Fee: 100.000 Credits

**After $30 deposit:**
- User needs additional credits for spawn fee
- Total needed: ~$1.030 USDC (103.000 credits)
- Or user can earn credits through referrals

## 📝 Implementation Details

### 1. Menu Access Check (menu_handlers.py)

```python
async def show_ai_agent_menu(self, query, context):
    # Check minimum deposit ($30 = 3000 credits)
    MINIMUM_DEPOSIT_CREDITS = 3000
    
    # Get user credits
    user_credits = get_user_credits(user_id)
    
    # Check if sufficient deposit
    has_deposit = (user_credits >= MINIMUM_DEPOSIT_CREDITS)
    
    if not has_deposit:
        # Show "Deposit $30 Required" message
        # Display current credits and shortfall
        return
    
    # Show AI Agent menu
```

### 2. Spawn Agent Check (handlers_automaton.py)

```python
async def spawn_agent_command(update, context):
    # Check Automaton access (bypass for admin)
    if not is_admin(user_id) and not db.has_automaton_access(user_id):
        return error
    
    # Check premium status (bypass for admin)
    if not is_admin(user_id) and not db.is_user_premium(user_id):
        return error
    
    # Check minimum deposit ($30 = 3000 credits)
    # APPLIES TO EVERYONE including admin
    MINIMUM_DEPOSIT_CREDITS = 3000
    user_credits = get_user_credits(user_id)
    
    if user_credits < MINIMUM_DEPOSIT_CREDITS:
        # Show "Minimum Deposit $30 Required"
        # Display current credits and shortfall
        return
    
    # Check spawn fee (100k credits)
    SPAWN_FEE = 100000
    if user_credits < SPAWN_FEE:
        # Show "Not Enough Credits for Spawn"
        return
    
    # Proceed to spawn agent
```

## 🚀 Deployment

### Commit Info:
- **Commit:** `122a1f0`
- **Message:** "Update: Require $30 minimum deposit for all users including admin and lifetime premium"
- **Files Changed:** 2 files
  - `app/handlers_automaton.py`
  - `menu_handlers.py`

### Railway Status:
- ✅ Code pushed to GitHub
- ⏳ Railway auto-deploy in progress

## 📱 User Experience

### Scenario 1: User with No Deposit

```
User clicks "AI Agent"
    ↓
Sees message:
"🤖 Selamat Datang di AI Agent!

⚠️ Deposit Minimum: $30 USDC

💰 Status Deposit Anda:
• Credits saat ini: 0
• Minimum required: 3.000 credits
• Kekurangan: 3.000 credits

📝 Cara Deposit:
1. Klik tombol '💰 Deposit Sekarang' di bawah
2. Deposit USDC (Base Network) ke address yang diberikan
3. Credits akan otomatis ditambahkan setelah 12 konfirmasi
4. Setelah deposit $30, Anda bisa spawn agent!

💡 Catatan:
• Admin & Lifetime Premium juga perlu deposit $30"
```

### Scenario 2: User with $10 Deposit (1000 credits)

```
User clicks "AI Agent"
    ↓
Sees message:
"💰 Status Deposit Anda:
• Credits saat ini: 1.000
• Minimum required: 3.000 credits
• Kekurangan: 2.000 credits

Anda perlu deposit $20 USDC lagi untuk mencapai minimum $30."
```

### Scenario 3: User with $30 Deposit (3000 credits)

```
User clicks "AI Agent"
    ↓
Sees AI Agent menu with options:
• 🤖 Spawn Agent
• 📊 Agent Status
• 🌳 Agent Lineage
• 💰 Fund Agent (Deposit)
• 📜 Agent Logs

User clicks "Spawn Agent"
    ↓
Sees message:
"❌ Kredit Tidak Cukup untuk Spawn

Spawn agent membutuhkan 100.000 kredit.
Kredit Anda: 3.000

Gunakan /credits untuk mendapatkan lebih banyak kredit."
```

### Scenario 4: Admin with $30 Deposit + 100k Credits

```
Admin clicks "AI Agent"
    ↓
Sees AI Agent menu (has $30 deposit)
    ↓
Clicks "Spawn Agent"
    ↓
✅ Bypasses Automaton access check (admin)
✅ Bypasses premium status check (admin)
✅ Has minimum deposit ($30)
✅ Has spawn fee (100k credits)
    ↓
Proceeds to spawn agent
```

## 💡 Key Points

### What Changed:
1. ✅ Menu access now requires $30 deposit (everyone)
2. ✅ Spawn agent requires $30 deposit (everyone including admin)
3. ✅ Clear error messages showing current credits and shortfall
4. ✅ Admin still bypasses Automaton access & premium checks

### What Stayed the Same:
1. ✅ Admin bypasses Automaton access check (Rp2.000.000)
2. ✅ Admin bypasses premium status check
3. ✅ Spawn fee still 100k credits
4. ✅ Signal generation works for all premium users

### Why This Change:
1. 💰 Ensures users have sufficient balance
2. 🛡️ Prevents spam/abuse
3. ⚖️ Fair for everyone (including admin)
4. 💡 Clear expectations upfront

## 🧪 Testing Checklist

### Test as Admin with No Deposit:
- [ ] Click "AI Agent" menu
- [ ] Should see "Deposit $30 Required" message
- [ ] Should show current credits: 0
- [ ] Should show shortfall: 3.000 credits

### Test as Admin with $30 Deposit:
- [ ] Click "AI Agent" menu
- [ ] Should see AI Agent menu
- [ ] Click "Spawn Agent"
- [ ] Should ask for agent name (if has 100k credits)
- [ ] Or show "Not Enough Credits" (if < 100k credits)

### Test as Lifetime Premium with $30 Deposit:
- [ ] Click "AI Agent" menu
- [ ] Should see AI Agent menu
- [ ] Click "Spawn Agent"
- [ ] Should ask for agent name (if has 100k credits)

### Test as Regular User with $30 Deposit:
- [ ] Click "AI Agent" menu
- [ ] Should see AI Agent menu
- [ ] Click "Spawn Agent"
- [ ] Should show "Automaton Access Required" (Rp2.000.000)

## 📊 Summary

### Access Requirements:

| Requirement | Admin | Lifetime Premium | Monthly Premium | Regular User |
|-------------|-------|------------------|-----------------|--------------|
| **Menu Access** | $30 deposit | $30 deposit | $30 deposit | $30 deposit |
| **Automaton Access** | ✅ Bypass | Need to pay | Need to pay | Need to pay |
| **Premium Status** | ✅ Bypass | ✅ Has | ✅ Has | ❌ Need |
| **Minimum Deposit** | ✅ $30 | ✅ $30 | ✅ $30 | ✅ $30 |
| **Spawn Fee** | 100k credits | 100k credits | 100k credits | 100k credits |

### Total Cost to Spawn Agent:

**Admin:**
- Automaton Access: FREE (bypass)
- Premium: FREE (bypass)
- Minimum Deposit: $30 USDC
- Spawn Fee: 100k credits (~$1.000 USDC)
- **Total: ~$1.030 USDC**

**Lifetime Premium:**
- Automaton Access: Rp2.000.000 (one-time)
- Premium: Already paid
- Minimum Deposit: $30 USDC
- Spawn Fee: 100k credits (~$1.000 USDC)
- **Total: Rp2.000.000 + ~$1.030 USDC**

**Regular User:**
- Premium: Need to subscribe
- Automaton Access: Rp2.000.000 (one-time)
- Minimum Deposit: $30 USDC
- Spawn Fee: 100k credits (~$1.000 USDC)
- **Total: Premium + Rp2.000.000 + ~$1.030 USDC**

---

**Status:** ✅ IMPLEMENTED

**Commit:** `122a1f0`

**Railway:** ⏳ Auto-deploying

**Applies To:** Everyone (Admin, Lifetime Premium, Monthly Premium, Regular Users)

**Minimum Deposit:** $30 USDC (3.000 credits)

**Next:** Test in production after Railway deploy completes

