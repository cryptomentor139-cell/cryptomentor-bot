# AI Agent Menu - Alur Lengkap User Flow

## 📋 OVERVIEW
Dokumen ini menjelaskan tahapan lengkap saat user klik tombol "AI Agent" di menu bot.

---

## 🔄 ALUR LENGKAP (Step-by-Step)

### TAHAP 1: User Klik Tombol "AI Agent"
**Lokasi:** Main Menu → Tombol "🤖 AI Agent"

**Yang Terjadi:**
1. User melihat Main Menu dengan 8 tombol
2. User klik tombol "🤖 AI Agent"
3. Bot menerima callback query dengan data: `ai_agent_menu`

**Kode yang Dijalankan:**
- File: `menu_handlers.py`
- Handler: `handle_callback_query()`
- Kondisi: `elif callback_data == AI_AGENT_MENU:`
- Memanggil: `show_ai_agent_menu(query, context)`

---

### TAHAP 2: Bot Menampilkan AI Agent Submenu
**Yang Ditampilkan:**
```
🤖 AI AGENT - AUTONOMOUS TRADING

Spawn dan kelola AI trading agents yang bekerja 24/7.

Fitur:
• Autonomous trading
• Conway Credits system
• Parent-child lineage (10% revenue sharing)
• Real-time monitoring

[🚀 Spawn Agent]
[📊 Agent Status]
[💰 Fund Agent]
[📜 Agent Logs]
[🌳 Agent Lineage]
[🔙 Back to Main Menu]
```

**Kode yang Dijalankan:**
- File: `menu_handlers.py`
- Function: `show_ai_agent_menu()`
- Mengambil user language dari database
- Menampilkan menu dengan `MenuBuilder.build_ai_agent_menu()`

---

### TAHAP 3A: User Klik "🚀 Spawn Agent"

**Yang Terjadi:**
1. Bot menerima callback: `automaton_spawn`
2. Handler: `handle_automaton_spawn()` dipanggil
3. Bot answer callback query
4. Bot kirim pesan baru: "⏳ Preparing to spawn agent..."
5. Bot set context: `awaiting_agent_name = True`

**User Diminta:**
"Please type the agent name you want to create."

**Next Step:**
- User ketik nama agent (contoh: "TradingBot1")
- Bot akan proses di `handle_message()` karena `awaiting_agent_name = True`
- Bot panggil `spawn_agent_command()` dengan nama yang diketik

**Validasi yang Dilakukan:**
1. ✅ Rate limit check (1 spawn per hour)
2. ✅ Automaton access check (Rp2,000,000 one-time fee)
3. ✅ Premium status check
4. ✅ Credit balance check (>= 100,000 credits)

**Jika Berhasil:**
- Agent dibuat dengan nama yang diketik
- Deduct 100,000 credits
- Generate wallet address
- Tampilkan deposit address + QR code

---

### TAHAP 3B: User Klik "📊 Agent Status"

**Yang Terjadi:**
1. Bot menerima callback: `automaton_status`
2. Handler: `handle_automaton_status()` dipanggil
3. Bot answer callback query
4. Bot buat proper Update object
5. Bot panggil `agent_status_command()`

**Yang Ditampilkan:**
```
🤖 Status Agent

📛 Nama: TradingBot1
💼 Wallet: 0xABC...
💰 Conway Credits: 500.00

🟢 Survival Tier: NORMAL
⏱️ Runtime Estimate: 25.5 hari
🕐 Last Active: 2026-02-21 10:30:00

📊 Performance
💵 Total Earnings: 1,250.00
💸 Total Expenses: 750.00
📈 Net P&L: +500.00

🌳 Lineage Info
👨 Parent: None (Root Agent)
👶 Children: 2
💰 Revenue from Children: 125.50 credits

📍 Deposit Address:
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

**Kode yang Dijalankan:**
- File: `menu_handlers.py` → `handle_automaton_status()`
- File: `app/handlers_automaton.py` → `agent_status_command()`
- Mengambil data agent dari `automaton_manager.get_user_agents()`
- Mengambil lineage info dari `get_agent_lineage_info()`

---

### TAHAP 3C: User Klik "💰 Fund Agent"

**Yang Terjadi:**
1. Bot menerima callback: `automaton_deposit`
2. Handler: `handle_automaton_deposit()` dipanggil
3. Bot answer callback query
4. Bot buat proper Update object
5. Bot panggil `deposit_command()`

**Yang Ditampilkan:**
```
💰 Deposit USDT/USDC

📍 Deposit Address:
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb

📱 QR Code:
https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=0x742d35...

🌐 Supported Networks:
• Polygon (Recommended - Low fees)
• Base
• Arbitrum

💱 Conversion Rates:
• 1 USDT = 100 Conway Credits
• 1 USDC = 100 Conway Credits

⚠️ Important:
• Minimum deposit: 5 USDT/USDC
• Only send USDT or USDC
• DO NOT send other tokens
• Credits will be added automatically after 12 confirmations

💡 Tip: Use Polygon network untuk biaya gas terendah!
```

**Proses Background:**
- Deposit monitor service berjalan setiap 5 menit
- Cek blockchain untuk deposit baru
- Auto-convert USDT/USDC → Conway Credits (1:100)
- Update balance agent otomatis

---

### TAHAP 3D: User Klik "📜 Agent Logs"

**Yang Terjadi:**
1. Bot menerima callback: `automaton_logs`
2. Handler: `handle_automaton_logs()` dipanggil
3. Bot answer callback query
4. Bot buat proper Update object
5. Bot panggil `agent_logs_command()`

**Yang Ditampilkan:**
```
📜 Transaction History

🤖 Agent: TradingBot1

💚 EARN +125.50
   Trading profit from BTC/USDT
   2026-02-21 10:15:00

❤️ SPEND -20.00
   API call to Binance
   2026-02-21 10:10:00

💙 FUND +500.00
   Deposit from user
   2026-02-21 09:00:00

💚 EARN +75.25
   Revenue from child agent
   2026-02-21 08:30:00
```

**Data Source:**
- Supabase table: `automaton_transactions`
- Limit: 20 transaksi terakhir
- Sorted by: timestamp DESC

---

### TAHAP 3E: User Klik "🌳 Agent Lineage"

**Yang Terjadi:**
1. Bot menerima callback: `agent_lineage`
2. Handler: `handle_agent_lineage()` dipanggil
3. Bot answer callback query
4. Bot buat proper Update object
5. Bot panggil `agent_lineage_command()`

**Yang Ditampilkan:**
```
🌳 Lineage Tree: TradingBot1

TradingBot1 (Root)
├── ChildBot1
│   ├── GrandchildBot1
│   └── GrandchildBot2
└── ChildBot2
    └── GrandchildBot3

💡 Lineage System:
• Parents receive 10% of children's gross earnings
• Revenue sharing is recursive (up to 10 levels)
• Build your agent network for passive income!
```

**Cara Kerja Lineage:**
1. Agent spawn dengan parent → parent dapat 10% dari gross earnings
2. Recursive hingga 10 level
3. Platform fee 20% diambil SEBELUM revenue sharing
4. Contoh: Child earn 100 → Platform 20 → Parent 8 (10% dari 80)

---

## 🔧 TECHNICAL FLOW DIAGRAM

```
User Click "AI Agent"
        ↓
MenuCallbackHandler.handle_callback_query()
        ↓
show_ai_agent_menu()
        ↓
Display AI Agent Submenu
        ↓
User Click Button (Spawn/Status/Deposit/Logs/Lineage)
        ↓
handle_automaton_[action]()
        ↓
Create proper Update object
        ↓
Call command handler from handlers_automaton.py
        ↓
Execute business logic
        ↓
Display result to user
```

---

## 📊 DATABASE INTERACTIONS

### Tables Used:
1. **users** - User data, credits, premium status
2. **automatons** - Agent data, balance, status
3. **custodial_wallets** - Wallet addresses, balances
4. **automaton_transactions** - Transaction history
5. **agent_lineage** - Parent-child relationships
6. **rate_limits** - Spawn/withdrawal rate limiting

### Key Queries:
- `get_user_agents(user_id)` - Get all user's agents
- `get_agent_lineage_info(agent_id)` - Get lineage data
- `get_agent_lineage_tree(agent_id)` - Get full tree
- `automaton_manager.spawn_agent()` - Create new agent

---

## ⚠️ ERROR HANDLING

### Jika User Belum Punya Automaton Access:
```
❌ Akses Automaton Diperlukan

Untuk menggunakan fitur AI Agent, Anda perlu membayar biaya satu kali sebesar Rp2.000.000.

Gunakan /subscribe untuk upgrade ke Automaton access.
```

### Jika User Belum Premium:
```
❌ Premium Diperlukan

Fitur AI Agent hanya tersedia untuk pengguna premium.

Gunakan /subscribe untuk upgrade.
```

### Jika Credit Tidak Cukup:
```
❌ Kredit Tidak Cukup

Spawn agent membutuhkan 100.000 kredit.
Kredit Anda: 50,000

Gunakan /credits untuk mendapatkan lebih banyak kredit.
```

### Jika Rate Limit Exceeded:
```
❌ Rate Limit Exceeded

Anda hanya bisa spawn 1 agent per jam.
Silakan coba lagi dalam 45 menit.
```

### Jika Terjadi Error Teknis:
```
❌ Error: [error message]

Please use /[command] command directly.
```

---

## 🎯 USER EXPERIENCE IMPROVEMENTS (SETELAH FIX)

### Sebelum Fix:
❌ Duplicate output (2x)
❌ Looping back to main menu
❌ Buttons tidak respond
❌ Error messages tidak jelas

### Setelah Fix:
✅ Single output (no duplicates)
✅ No looping
✅ All buttons respond correctly
✅ Clear error messages
✅ Proper Update objects
✅ Better error handling

---

## 📝 TESTING CHECKLIST

Setelah Railway deployment selesai, test:

- [ ] Klik "AI Agent" → Muncul submenu
- [ ] Klik "Spawn Agent" → Minta nama agent
- [ ] Klik "Agent Status" → Tampil status
- [ ] Klik "Fund Agent" → Tampil deposit info
- [ ] Klik "Agent Logs" → Tampil transaction history
- [ ] Klik "Agent Lineage" → Tampil lineage tree
- [ ] Tidak ada duplicate output
- [ ] Tidak ada looping ke main menu
- [ ] Error messages jelas dan helpful

---

## 🔗 RELATED FILES

- `menu_handlers.py` - Menu callback handlers
- `app/handlers_automaton.py` - Command handlers
- `app/automaton_manager.py` - Business logic
- `app/lineage_integration.py` - Lineage system
- `menu_system.py` - Menu builder
- `bot.py` - Main bot setup

---

## 📞 SUPPORT COMMANDS

Jika user mengalami masalah, arahkan ke:
- `/spawn_agent <name>` - Direct spawn command
- `/agent_status` - Direct status command
- `/deposit` - Direct deposit command
- `/agent_logs` - Direct logs command
- `/agent_lineage` - Direct lineage command
