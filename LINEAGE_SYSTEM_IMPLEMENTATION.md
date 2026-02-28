# Lineage System Implementation - Parent-Child Revenue Sharing

## 🎯 Tujuan Utama

Sistem ini dirancang untuk memastikan **pengguna yang membayar automaton membawa keuntungan bagi platform** melalui beberapa sumber pendapatan:

### 💰 Model Pendapatan Platform

1. **Biaya Akses Automaton**: Rp2.000.000 (satu kali)
   - Setiap user harus bayar untuk akses fitur automaton
   - Pendapatan langsung ke platform

2. **Biaya Deposit**: 2% dari setiap deposit
   - User deposit USDT/USDC untuk fuel agent
   - Platform potong 2% sebelum convert ke Conway credits
   - Contoh: User deposit 100 USDT → Platform dapat 2 USDT → User dapat 9,800 Conway credits

3. **Biaya Performance**: 20% dari profit agent
   - Ketika agent trading dan profit
   - Platform dapat 20% dari profit tersebut
   - Contoh: Agent profit 1000 credits → Platform dapat 200 credits

4. **Biaya Withdrawal**: $1 flat fee
   - Ketika user withdraw USDT dari wallet
   - Minimum withdrawal 10 USDT

5. **Konsumsi Credits Berkelanjutan**:
   - Agent konsumsi Conway credits untuk survive (200 credits/hari normal tier)
   - User harus terus deposit untuk keep agent alive
   - Recurring revenue dari deposits

## 🌳 Sistem Lineage (Parent-Child)

### Konsep

Agent bisa spawn agent baru (children), dan parent agent dapat **10% dari earnings child**. Ini menciptakan:

1. **Passive Income untuk Users**: User dapat passive income dari agent network mereka
2. **Incentive untuk Growth**: User termotivasi spawn lebih banyak agents
3. **Platform Revenue Tetap**: Platform tetap dapat fees dari semua transactions

### Alur Revenue Sharing

```
Child Agent earns 1000 credits
    ↓
Platform ambil 20% performance fee = 200 credits (PLATFORM PROFIT)
    ↓
Child net earnings = 800 credits
    ↓
Parent dapat 10% dari gross (1000) = 100 credits
    ↓
Child keep 700 credits
    ↓
Jika Parent juga punya Parent (Grandparent):
    Grandparent dapat 10% dari Parent's earnings
```

### Contoh Skenario

**Hari 1**: User A spawn Agent Alpha (bayar 100k credits)
- Platform sudah profit dari: Akses fee (Rp2jt) + Deposit fee (2%)

**Hari 5**: Alpha trading, profit 1000 credits
- Platform dapat: 200 credits (20% performance fee)
- Alpha keep: 800 credits

**Hari 7**: Alpha spawn Agent Beta (child)
- Alpha bayar 100k credits untuk spawn
- Beta jadi child dari Alpha

**Hari 10**: User A deposit lagi 100 USDT untuk fuel agents
- Platform dapat: 2 USDT (2% deposit fee)
- User dapat: 9,800 Conway credits

**Hari 15**: Beta trading, profit 1000 credits
- Platform dapat: 200 credits (20% performance fee) ✅
- Beta net: 800 credits
- Alpha dapat: 100 credits (10% dari Beta's gross) - PASSIVE INCOME UNTUK USER
- Beta keep: 700 credits

**Hari 20**: Beta spawn Agent Gamma (grandchild)
- Beta bayar 100k credits
- Gamma jadi child dari Beta, grandchild dari Alpha

**Hari 25**: Gamma profit 1000 credits
- Platform dapat: 200 credits (20% performance fee) ✅
- Gamma net: 800 credits
- Beta dapat: 100 credits (10% dari Gamma)
- Alpha dapat: 10 credits (10% dari Beta's 100 credits)
- Gamma keep: 700 credits

## 💡 Mengapa Ini Menguntungkan Platform?

### 1. Multiple Revenue Streams
- Akses fee (one-time, besar)
- Deposit fee (recurring, 2%)
- Performance fee (recurring, 20%)
- Withdrawal fee (occasional, $1)

### 2. Network Effect
- Semakin banyak agents, semakin banyak trading
- Semakin banyak trading, semakin banyak performance fees
- Lineage system incentivize users untuk spawn lebih banyak agents

### 3. Recurring Revenue
- Agents perlu fuel terus-menerus (200 credits/hari)
- Users harus deposit regularly
- Setiap deposit = 2% fee untuk platform

### 4. Zero Capital Risk
- Platform tidak provide capital untuk trading
- Users deposit ke custodial wallets mereka sendiri
- Platform hanya collect fees

### 5. Scalability
- Tidak ada limit berapa banyak agents
- Tidak ada limit berapa banyak users
- Automated fee collection

## 📊 Proyeksi Pendapatan

### Asumsi:
- 100 users aktif
- Setiap user punya 2 agents (rata-rata)
- Setiap agent trading 10x per bulan
- Average profit per trade: 100 credits
- Average deposit per user per bulan: 100 USDT

### Perhitungan Bulanan:

**Akses Fees** (one-time, tapi new users):
- 10 new users/bulan × Rp2.000.000 = Rp20.000.000

**Deposit Fees**:
- 100 users × 100 USDT × 2% = 200 USDT/bulan

**Performance Fees**:
- 200 agents × 10 trades × 100 credits profit × 20% = 40,000 credits
- = 400 USDT/bulan

**Total Revenue per Bulan**:
- Rp20.000.000 (akses fees)
- 600 USDT (deposit + performance fees)
- ≈ Rp29.000.000/bulan (assuming 1 USDT = Rp15.000)

**Per Tahun**: ≈ Rp348.000.000

Dan ini dengan hanya 100 users! Scale ke 1000 users = Rp3.48 Miliar/tahun.

## 🚀 Yang Sudah Diimplementasi

### 1. Lineage Manager (`app/lineage_manager.py`)
✅ Register parent-child relationships
✅ Distribute 10% revenue dari child ke parent
✅ Recursive revenue sharing (grandparents, great-grandparents, etc.)
✅ Query lineage tree
✅ Calculate lineage statistics
✅ Prevent circular references
✅ Depth limit (max 10 levels)

### 2. Database Migration (`migrations/005_add_lineage_system.sql`)
✅ Add parent_agent_id column
✅ Add total_children_revenue tracking
✅ Add autonomous spawning fields
✅ Create lineage_transactions table
✅ Add indexes for performance

### 3. Revenue Manager (`app/revenue_manager.py`)
✅ Calculate deposit fees (2%)
✅ Calculate performance fees (20%)
✅ Record platform revenue
✅ Generate revenue reports

## 📋 Yang Perlu Dilakukan Selanjutnya

### 1. Update Handlers untuk Lineage
- [ ] Modify spawn_agent_command untuk support parent selection
- [ ] Update agent_status_command untuk show lineage info
- [ ] Create agent_lineage_command untuk display tree

### 2. Run Database Migration
```bash
python run_migration_005.py
```
Atau run SQL directly di Supabase Dashboard.

### 3. Integrate Lineage Manager
- [ ] Call lineage_manager.register_child_agent() saat spawn with parent
- [ ] Call lineage_manager.distribute_child_revenue() saat agent earns
- [ ] Display lineage info di agent status

### 4. Testing
- [ ] Test parent-child registration
- [ ] Test revenue distribution
- [ ] Test recursive sharing
- [ ] Test circular reference prevention

### 5. Autonomous Spawning (Optional, Future)
- [ ] Webhook handlers untuk Conway Cloud callbacks
- [ ] Agent decision logic untuk autonomous spawn
- [ ] Rate limiting (max 1 spawn per 24h per agent)
- [ ] User controls untuk enable/disable

## 🎯 Kesimpulan

**Model bisnis ini WIN-WIN:**

### Untuk Platform (Anda):
✅ Multiple revenue streams
✅ Recurring income dari deposits
✅ Performance fees dari trading
✅ Zero capital risk
✅ Scalable tanpa batas

### Untuk Users:
✅ Autonomous trading agents
✅ Passive income dari lineage (10% dari children)
✅ No manual trading needed
✅ Potential untuk build agent networks
✅ Zero risk (hanya lose deposit jika agent fail)

### Untuk Agents:
✅ Autonomous operation
✅ Self-sustaining dengan proper fuel
✅ Can spawn children untuk expand network
✅ Earn dari trading performance

**Bottom Line**: Setiap user yang bayar automaton access dan deposit funds = PROFIT untuk platform, baik dari fees maupun dari recurring deposits untuk fuel agents.

## 📞 Next Steps

1. **Run Migration**: Execute migration 005 untuk add lineage tables
2. **Test Lineage Manager**: Test basic parent-child registration
3. **Update Handlers**: Add lineage support ke spawn dan status commands
4. **Deploy**: Push ke production
5. **Monitor**: Track revenue dari fees

Apakah Anda ingin saya lanjutkan dengan update handlers dan integration?
