# 💡 Jawaban: Bagaimana Bot Mengetahui User Sudah Deposit?

## 🎯 Pertanyaan Anda:
> "Lalu misal user sudah deposit, bagaimana cara bot mengetahui user tersebut telah deposit, dan tampilan berubah masuk ke tampilan AI Agent yang spawn AI?"

## ✅ Jawaban Singkat:

Bot mengetahui user sudah deposit dengan cara:

1. **Background Service** memonitor blockchain setiap 30 detik
2. Ketika detect deposit → **Update database** Supabase
3. User klik "AI Agent" → Bot **query database**
4. Jika credits > 0 → **Tampilkan menu lengkap** ✅

## 🔄 Alur Lengkap (Step by Step):

### 1️⃣ User Deposit USDC
```
User → MetaMask → Transfer 10 USDC
         ↓
Base Network Blockchain
         ↓
Centralized Wallet: 0x6311...5822
```

### 2️⃣ Background Service Detect
```
Deposit Monitor (berjalan otomatis setiap 30s):
   ↓
Cek balance on-chain via Web3
   ↓
Balance bertambah? → DEPOSIT DETECTED! 💰
   ↓
Hitung:
   • Deposit: 10 USDC
   • Fee (2%): 0.2 USDC
   • Net: 9.8 USDC
   • Credits: 980 Conway Credits (9.8 × 100)
```

### 3️⃣ Update Database Supabase
```sql
-- Bot otomatis insert/update ke tabel:
INSERT INTO user_credits_balance (user_id, available_credits, total_conway_credits)
VALUES (1187119989, 980, 980);

-- Sekarang user punya 980 credits ✅
```

### 4️⃣ User Klik "AI Agent" Lagi
```
User klik button "🤖 AI Agent"
   ↓
Bot jalankan function: show_ai_agent_menu()
   ↓
Query database:
   SELECT available_credits 
   FROM user_credits_balance 
   WHERE user_id = 1187119989
   ↓
Result: 980 credits ✅
   ↓
Kondisi: credits > 0? → YES!
   ↓
Tampilkan FULL AI AGENT MENU:
   • 🚀 Spawn Agent
   • 📊 Agent Status
   • 🌳 Agent Lineage
   • 💰 Deposit Credits
   • 📜 Agent Logs
```

## 🔍 Kode yang Mendeteksi:

### File: `menu_handlers.py`
```python
async def show_ai_agent_menu(self, query, context):
    user_id = query.from_user.id
    
    # 1. Query database Supabase
    from supabase_client import supabase
    credits_result = supabase.table('user_credits_balance')\
        .select('available_credits, total_conway_credits')\
        .eq('user_id', user_id)\
        .execute()
    
    # 2. Check apakah user punya credits
    has_deposit = False
    if credits_result.data:
        balance = credits_result.data[0]
        available = float(balance.get('available_credits', 0))
        total = float(balance.get('total_conway_credits', 0))
        has_deposit = (available > 0 or total > 0)
    
    # 3. Tampilkan menu sesuai kondisi
    if has_deposit:
        # ✅ FULL MENU (user sudah deposit)
        await query.edit_message_text(
            "🤖 AI Agent Menu",
            reply_markup=full_ai_agent_menu
        )
    else:
        # ⚠️ DEPOSIT-FIRST MENU (user belum deposit)
        await query.edit_message_text(
            "⚠️ Deposit Diperlukan",
            reply_markup=deposit_first_menu
        )
```

## 📊 Tabel Database yang Digunakan:

### Tabel: `user_credits_balance`
```
┌──────────┬────────────────────┬──────────────────────┐
│ user_id  │ available_credits  │ total_conway_credits │
├──────────┼────────────────────┼──────────────────────┤
│ 1187119989│      1000.0       │        1000.0        │ ← Anda
│ 2345678  │        0.0        │          0.0         │ ← User baru
│ 3456789  │      500.0        │        500.0         │ ← User lain
└──────────┴────────────────────┴──────────────────────┘
```

**Logic:**
- Jika `available_credits > 0` → Show FULL menu ✅
- Jika `available_credits = 0` → Show DEPOSIT menu ⚠️

## ⏱️ Timeline Real:

```
T+0s      User transfer 10 USDC via MetaMask
T+30s     Deposit Monitor check #1 (belum 12 confirmations)
T+60s     Deposit Monitor check #2 (belum 12 confirmations)
...
T+360s    Deposit Monitor check #12 (12 confirmations ✅)
          → DEPOSIT DETECTED!
          → Update database: +980 credits
          → Send notification ke user
          
T+361s    User klik "AI Agent" button
          → Bot query database
          → Find 980 credits ✅
          → Show FULL menu
```

## 🎯 Untuk Kasus Anda:

**Status Sekarang:**
```
User ID: 1187119989 (admin)
Credits: 1,000 Conway Credits ✅
Database: user_credits_balance table
```

**Ketika Anda Klik "AI Agent":**
```
1. Bot query: SELECT * FROM user_credits_balance WHERE user_id = 1187119989
2. Result: available_credits = 1000 ✅
3. Kondisi: 1000 > 0? → YES!
4. Action: Show FULL AI Agent menu
```

**Menu yang Akan Tampil:**
```
🤖 AI Agent Menu

🚀 Spawn Agent       ← Bisa spawn agent baru
📊 Agent Status      ← Lihat status agent
🌳 Agent Lineage     ← Lihat lineage tree
💰 Deposit Credits   ← Tambah credits
📜 Agent Logs        ← Lihat logs
🔙 Back              ← Kembali
```

## 🔧 Komponen Sistem:

### 1. Deposit Monitor (`app/deposit_monitor.py`)
- Berjalan di background setiap 30 detik
- Check balance USDC on-chain via Web3
- Detect deposit baru
- Update database Supabase

### 2. Menu Handler (`menu_handlers.py`)
- Handle button click "AI Agent"
- Query database untuk check credits
- Tampilkan menu sesuai kondisi

### 3. Database Supabase
- Tabel `user_credits_balance`
- Menyimpan Conway Credits setiap user
- Diupdate otomatis saat deposit terdeteksi

### 4. Web3 Connection
- Connect ke Base network
- Query USDC contract
- Check balance real-time

## 💡 Kesimpulan:

**Bot mengetahui user sudah deposit dengan:**

1. ✅ **Monitoring blockchain** setiap 30 detik (otomatis)
2. ✅ **Update database** saat deposit terdeteksi
3. ✅ **Query database** saat user klik "AI Agent"
4. ✅ **Show menu** berdasarkan credits (> 0 = full menu)

**Tidak perlu manual refresh atau restart bot!**

User cukup:
1. Deposit USDC
2. Tunggu ~6 menit (12 confirmations)
3. Klik "AI Agent" button lagi
4. Menu otomatis berubah ✅

---

**Status Anda Sekarang:**
- ✅ Sudah punya 1,000 credits
- ✅ Menu akan langsung tampil lengkap
- ✅ Bisa langsung spawn agent
- ✅ Tidak perlu deposit lagi

**Next Action:**
Deploy ke Railway dan test dengan user baru!
