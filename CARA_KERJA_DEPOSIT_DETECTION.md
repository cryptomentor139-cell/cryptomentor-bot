# 🔍 Cara Kerja Deposit Detection System

## 📋 Overview

Sistem deposit detection bekerja secara otomatis untuk mendeteksi deposit USDC yang masuk ke centralized wallet dan mengupdate tampilan menu AI Agent dari "Deposit-First" menjadi "Full AI Agent Menu".

## 🔄 Alur Kerja Lengkap

### 1️⃣ User Melakukan Deposit

**User Action:**
```
1. User klik "💰 Deposit Sekarang" di menu AI Agent
2. Bot menampilkan address centralized wallet
3. User transfer USDC (Base Network) ke address tersebut
4. User menunggu konfirmasi blockchain (12 confirmations)
```

**Centralized Wallet Address:**
```
0x63116672bef9f26fd906cd2a57550f7a13925822
```

### 2️⃣ Background Service Monitoring

**Deposit Monitor Service** (`app/deposit_monitor.py`) berjalan di background:

```python
# Service ini berjalan setiap 30 detik (default)
while is_running:
    # 1. Query semua custodial wallets dari database
    wallets = db.get_all_custodial_wallets()
    
    # 2. Cek balance on-chain untuk setiap wallet
    for wallet in wallets:
        current_balance = check_usdc_balance(wallet.address)
        
        # 3. Bandingkan dengan balance terakhir yang diketahui
        if current_balance > last_known_balance:
            # DEPOSIT TERDETEKSI!
            deposit_amount = current_balance - last_known_balance
            
            # 4. Process deposit
            process_deposit(wallet, deposit_amount)
```

### 3️⃣ Deposit Processing

Ketika deposit terdeteksi, sistem melakukan:

```python
async def process_deposit(wallet, deposit_amount):
    # 1. Validasi minimum deposit (5 USDC)
    if deposit_amount < 5.0:
        return False
    
    # 2. Hitung platform fee (2%)
    platform_fee = deposit_amount * 0.02
    net_amount = deposit_amount - platform_fee
    
    # 3. Convert ke Conway Credits (1 USDC = 100 credits)
    conway_credits = net_amount * 100
    
    # 4. Update database Supabase
    supabase.table('user_credits_balance').upsert({
        'user_id': wallet.user_id,
        'available_credits': conway_credits,
        'total_conway_credits': conway_credits
    })
    
    # 5. Record deposit history
    supabase.table('wallet_deposits').insert({
        'wallet_id': wallet.id,
        'user_id': wallet.user_id,
        'amount': deposit_amount,
        'platform_fee': platform_fee,
        'credited_conway': conway_credits,
        'status': 'confirmed'
    })
    
    # 6. Send notification ke user (Telegram)
    await send_telegram_notification(wallet.user_id, conway_credits)
```

### 4️⃣ Database Update

**Tabel yang diupdate:**

1. **`user_credits_balance`** (Supabase):
```sql
INSERT INTO user_credits_balance (user_id, available_credits, total_conway_credits)
VALUES (1187119989, 1000.0, 1000.0)
ON CONFLICT (user_id) DO UPDATE
SET available_credits = available_credits + 1000.0,
    total_conway_credits = total_conway_credits + 1000.0;
```

2. **`custodial_wallets`** (Supabase):
```sql
UPDATE custodial_wallets
SET balance_usdc = balance_usdc + 10.0,
    conway_credits = conway_credits + 980.0,  -- after 2% fee
    total_deposited = total_deposited + 10.0,
    last_deposit_at = NOW()
WHERE user_id = 1187119989;
```

3. **`wallet_deposits`** (Supabase):
```sql
INSERT INTO wallet_deposits (
    wallet_id, user_id, amount, platform_fee, 
    credited_conway, status, confirmed_at
) VALUES (
    'wallet_123', 1187119989, 10.0, 0.2, 
    980.0, 'confirmed', NOW()
);
```

### 5️⃣ Menu Detection Logic

**File:** `menu_handlers.py` → `show_ai_agent_menu()`

```python
async def show_ai_agent_menu(self, query, context):
    user_id = query.from_user.id
    
    # Check if user has credits
    has_deposit = False
    
    if db.supabase_enabled:
        from supabase_client import supabase
        
        # Query user_credits_balance table
        credits_result = supabase.table('user_credits_balance')\
            .select('available_credits, total_conway_credits')\
            .eq('user_id', user_id)\
            .execute()
        
        if credits_result.data:
            balance = credits_result.data[0]
            available = float(balance.get('available_credits', 0))
            total = float(balance.get('total_conway_credits', 0))
            
            # User has deposit if they have any credits
            has_deposit = (available > 0 or total > 0)
    
    # Show appropriate menu
    if has_deposit:
        # ✅ FULL AI AGENT MENU
        await query.edit_message_text(
            get_menu_text(AI_AGENT_MENU, user_lang),
            reply_markup=MenuBuilder.build_ai_agent_menu()
        )
    else:
        # ⚠️ DEPOSIT-FIRST MENU
        await query.edit_message_text(
            "Deposit diperlukan...",
            reply_markup=deposit_first_menu
        )
```

## 🎯 Kondisi Tampilan Menu

### Kondisi 1: User BELUM Deposit
**Database State:**
```sql
SELECT * FROM user_credits_balance WHERE user_id = 1187119989;
-- Result: No rows (atau available_credits = 0)
```

**Menu yang Ditampilkan:**
```
🤖 Selamat Datang di AI Agent!

⚠️ Deposit Diperlukan
Untuk menggunakan fitur AI Agent, Anda perlu melakukan deposit terlebih dahulu.

[💰 Deposit Sekarang]
[❓ Cara Deposit]
[🔙 Kembali]
```

### Kondisi 2: User SUDAH Deposit
**Database State:**
```sql
SELECT * FROM user_credits_balance WHERE user_id = 1187119989;
-- Result: available_credits = 1000.0, total_conway_credits = 1000.0
```

**Menu yang Ditampilkan:**
```
🤖 AI Agent Menu

[🚀 Spawn Agent]
[📊 Agent Status]
[🌳 Agent Lineage]
[💰 Deposit Credits]
[📜 Agent Logs]
[🔙 Back]
```

## ⏱️ Timeline Deposit

```
T+0s    : User transfer USDC ke centralized wallet
T+30s   : Deposit Monitor check pertama (belum terdeteksi - butuh 12 confirmations)
T+60s   : Deposit Monitor check kedua (belum terdeteksi)
...
T+360s  : Setelah 12 confirmations (~6 menit), deposit terdeteksi
T+361s  : System process deposit:
          - Hitung fee (2%)
          - Convert ke Conway Credits (1 USDC = 100 credits)
          - Update database Supabase
          - Send notification ke user
T+362s  : User klik "AI Agent" button
T+363s  : Bot query database, menemukan credits > 0
T+364s  : Bot tampilkan FULL AI AGENT MENU ✅
```

## 🔧 Configuration

**Environment Variables:**
```bash
# Deposit Monitor Settings
DEPOSIT_CHECK_INTERVAL=30          # Check every 30 seconds
MIN_CONFIRMATIONS=12                # Wait for 12 confirmations
MIN_DEPOSIT_USDC=5.0               # Minimum 5 USDC
PLATFORM_FEE_RATE=0.02             # 2% platform fee

# Base Network
BASE_RPC_URL=https://mainnet.base.org
BASE_USDC_ADDRESS=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

# Centralized Wallet
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
```

## 🚀 Cara Start Deposit Monitor

**Di Railway (Production):**
```python
# File: bot.py
from app.deposit_monitor import get_deposit_monitor
from app.background_services import start_background_services

async def main():
    # Initialize bot
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Start background services (includes deposit monitor)
    await start_background_services(application, db)
    
    # Start bot
    await application.run_polling()
```

**Manual Testing (Local):**
```bash
cd Bismillah
python -c "
from database import Database
from app.deposit_monitor import get_deposit_monitor
import asyncio

db = Database()
monitor = get_deposit_monitor(db)
asyncio.run(monitor.start())
"
```

## 📊 Monitoring Logs

**Deposit Terdeteksi:**
```
🔍 Checking 1 custodial wallets...
💰 New deposit detected!
   Wallet: 0x63116672bef9f26fd906cd2a57550f7a13925822
   Amount: 10.0 USDC
💰 Processing deposit:
   User: 1187119989
   Amount: 10.0 USDC
   Platform Fee: 0.2 USDC (2%)
   Net Amount: 9.8 USDC
   Conway Credits: 980.0
✅ Current balance: 980.0 credits
✅ Deposit processed: +980.0 credits
✅ Updated wallet balance in database
✅ Recorded deposit in database
✅ Recorded platform fee: 0.2 USDC
✅ Deposit processed successfully for user 1187119989
```

## 🔍 Troubleshooting

### Problem: Menu masih menampilkan "Deposit Diperlukan" padahal sudah deposit

**Solution 1: Check Database**
```bash
cd Bismillah
python check_my_deposit.py
```

**Solution 2: Manual Credit (Admin Only)**
```bash
cd Bismillah
python credit_my_deposit.py
```

**Solution 3: Check Deposit Monitor Status**
```python
# Check if deposit monitor is running
from app.background_services import get_background_services_status

status = get_background_services_status()
print(status['deposit_monitor'])  # Should be 'running'
```

### Problem: Deposit Monitor tidak berjalan

**Check:**
1. Environment variables configured?
2. Web3 connection to Base network OK?
3. Background services started in bot.py?

**Fix:**
```bash
# Restart bot di Railway
railway up

# Atau restart manual
python bot.py
```

## 📝 Summary

**Cara Bot Mengetahui User Sudah Deposit:**

1. ✅ **Deposit Monitor** berjalan di background setiap 30 detik
2. ✅ **Check Balance** on-chain untuk semua custodial wallets
3. ✅ **Detect Deposit** jika balance bertambah
4. ✅ **Process & Update** database Supabase (`user_credits_balance`)
5. ✅ **Menu Check** query database saat user klik "AI Agent"
6. ✅ **Show Full Menu** jika `available_credits > 0`

**Key Tables:**
- `user_credits_balance` → Menyimpan Conway Credits user
- `custodial_wallets` → Menyimpan wallet address & balance
- `wallet_deposits` → History semua deposit

**Key Files:**
- `app/deposit_monitor.py` → Background service untuk detect deposit
- `menu_handlers.py` → Logic untuk show menu berdasarkan credits
- `supabase_client.py` → Connection ke Supabase database

---

**Status**: ✅ System berjalan otomatis
**Next Action**: Deploy ke Railway untuk production testing
