# 🎉 AI Agent Automaton - SIAP DIGUNAKAN!

## ✅ Status Deposit Anda

**Deposit berhasil di-credit!**

- 💰 **Balance**: 1,000 Conway Credits
- 💵 **Equivalent**: $10 USDC
- 🤖 **Dapat spawn**: 10 agent(s)
- 📍 **User ID**: 1187119989

---

## 🚀 Cara Menggunakan AI Agent

### Step 1: Buka Telegram Bot

1. Buka bot Telegram Anda
2. Klik menu **🤖 AI Agent**

### Step 2: Cek Balance (Opsional)

1. Klik **📊 Agent Status**
2. Anda akan melihat:
   - Available Credits: 1,000
   - Active Agents: 0
   - Total Profit/Loss: 0

### Step 3: Spawn Agent Pertama Anda!

1. Klik **🚀 Spawn Agent**
2. Bot akan meminta nama agent (contoh: "TradingBot1")
3. Bot akan meminta genesis prompt (instruksi untuk agent)
   - Contoh: "Trade BTC/USDT with conservative strategy, max 2% risk per trade"
4. Konfirmasi spawn (akan potong 100 credits)
5. Agent akan mulai berjalan!

### Step 4: Monitor Agent

1. Klik **📊 Agent Status** untuk melihat:
   - Agent ID
   - Balance agent
   - Status (active/inactive)
   - Total trades
   - Profit/Loss

2. Klik **📜 Agent Logs** untuk melihat:
   - Trading history
   - Decisions yang dibuat agent
   - Performance metrics

---

## 🔧 Troubleshooting

### Masalah 1: Conway API Error 404

**Status**: ⚠️ Conway API endpoint belum tersedia

**Solusi Sementara**:
- Deposit sudah di-credit ke database ✅
- Agent bisa di-spawn ✅
- Tapi agent belum bisa trading karena Conway API belum ready

**Yang Perlu Dilakukan**:
1. Tunggu Conway Dashboard API endpoint ready
2. Atau gunakan mock mode untuk testing

### Masalah 2: Agent Tidak Trading

**Kemungkinan Penyebab**:
1. Conway API belum ready (lihat Masalah 1)
2. Agent balance habis
3. Market conditions tidak memenuhi kriteria

**Solusi**:
- Cek agent balance di menu "📊 Agent Status"
- Top up agent jika balance < 100 credits
- Cek logs untuk lihat kenapa agent tidak trading

### Masalah 3: Deposit Tidak Terdeteksi (Future Deposits)

**Untuk deposit berikutnya via MetaMask**:
1. Deposit ke address: `0x63116672bef9f26fd906cd2a57550f7a13925822`
2. Tunggu 12 konfirmasi (~5-10 menit)
3. Jika tidak auto-credit, jalankan:
   ```bash
   cd Bismillah
   python credit_my_deposit.py
   ```
4. Edit `DEPOSIT_AMOUNT_USDC` di file tersebut sesuai jumlah deposit

---

## 📊 Sistem Architecture

### Centralized Wallet System

```
User Deposit (MetaMask)
    ↓
Centralized Wallet (0x6311...5822)
    ↓
Conway Dashboard (Auto-detect)
    ↓
Webhook → Bot
    ↓
Credit User Account
    ↓
User Can Spawn Agents
```

### Agent Lifecycle

```
1. User Spawn Agent (100 credits)
   ↓
2. Agent Created in Database
   ↓
3. Agent Gets Deposit Address
   ↓
4. User Funds Agent
   ↓
5. Agent Starts Trading
   ↓
6. Agent Consumes Credits
   ↓
7. Agent Stops When Balance Low
```

---

## 💡 Tips & Best Practices

### 1. Agent Naming

- Gunakan nama yang deskriptif
- Contoh: "BTC_Conservative", "ETH_Aggressive", "Multi_Scalper"

### 2. Genesis Prompt

**Good Prompts**:
```
"Trade BTC/USDT with conservative strategy. 
Max 2% risk per trade. 
Target 1-2% profit per trade. 
Stop loss at 1.5%."
```

```
"Scalp ETH/USDT on 5m timeframe. 
Quick in and out. 
0.5% profit target. 
Max 5 trades per hour."
```

**Bad Prompts**:
```
"Make money" (terlalu vague)
"Trade everything" (terlalu risky)
"YOLO" (no strategy)
```

### 3. Risk Management

- Jangan spawn terlalu banyak agent sekaligus
- Start dengan 1-2 agent dulu
- Monitor performance sebelum scale up
- Set stop loss di genesis prompt

### 4. Credit Management

- 1 agent = 100 credits untuk spawn
- Agent consume credits saat trading
- Top up agent sebelum balance habis
- Monitor balance di "📊 Agent Status"

---

## 🔮 Roadmap & Future Features

### Tahap 3: Webhook Integration (Next)

- Conway Dashboard webhook untuk auto-detect deposits
- Real-time credit updates
- Automatic attribution

### Tahap 4: Deposit Monitor

- Background service monitor blockchain
- Detect deposits tanpa webhook
- Fallback jika webhook fail

### Tahap 5: Advanced Features

- Agent lineage system (agent spawn child agents)
- Performance analytics dashboard
- Auto-rebalancing
- Multi-strategy agents

---

## 📞 Support

### Jika Ada Masalah:

1. **Cek Logs**:
   ```bash
   cd Bismillah
   python check_automaton_health.py
   ```

2. **Cek Balance**:
   ```bash
   python check_my_deposit.py
   ```

3. **Manual Credit** (jika deposit tidak terdeteksi):
   ```bash
   python credit_my_deposit.py
   ```

4. **Railway Logs** (jika bot di Railway):
   - Buka Railway dashboard
   - Klik project Anda
   - Klik tab "Deployments"
   - Klik "View Logs"

---

## 🎯 Quick Reference

### Environment Variables (Railway)

```env
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822
CONWAY_API_KEY=cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73
CONWAY_API_URL=https://api.conway.tech
SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOi...
```

### Database Tables

- `user_credits_balance` - User credit balances
- `deposit_transactions` - All deposits
- `pending_deposits` - Users waiting to deposit
- `user_automatons` - Spawned agents
- `automaton_transactions` - Agent trading history
- `credit_transactions` - Credit movement logs

### Key Files

- `app/automaton_manager.py` - Agent management
- `app/conway_integration.py` - Conway API client
- `app/background_services.py` - Background monitors
- `app/handlers_automaton.py` - Telegram handlers
- `menu_handlers.py` - Menu callbacks

---

## ✅ Checklist Sebelum Deploy ke Railway

- [x] Database migration applied
- [x] Centralized wallet configured
- [x] Deposit credited
- [x] Menu handlers updated (USDC Base only)
- [ ] Push ke GitHub
- [ ] Deploy ke Railway
- [ ] Test di Telegram
- [ ] Spawn first agent
- [ ] Monitor agent performance

---

**Last Updated**: 2026-02-22
**Status**: ✅ Ready to Use (Conway API pending)
**Your Balance**: 1,000 Conway Credits ($10 USDC)

🎉 **Selamat! Sistem Anda sudah siap digunakan!**

