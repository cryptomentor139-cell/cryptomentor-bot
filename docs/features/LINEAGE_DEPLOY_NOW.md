# 🚀 Lineage System - Deploy Sekarang!

## ✅ Status: SIAP DEPLOY

Semua komponen lineage system sudah terintegrasi dan siap untuk testing/production.

---

## 📋 Yang Sudah Selesai

### ✅ Database Migration
- Migration 005 sudah di-apply ke Supabase
- Semua kolom lineage sudah ada
- Table `lineage_transactions` sudah dibuat

### ✅ Core System
- `app/lineage_manager.py` - Logic utama ✅
- `app/lineage_integration.py` - Helper functions ✅
- `app/revenue_manager.py` - Integrasi revenue sharing ✅

### ✅ Bot Handlers
- `app/handlers_automaton.py` - Semua handler updated ✅
  - `/spawn_agent` - Parent selection UI
  - `/agent_status` - Tampilkan lineage info
  - `/agent_lineage` - NEW: Tampilkan lineage tree
  - Callback handler untuk parent selection

### ✅ Menu System
- `menu_system.py` - Button "🌳 Agent Lineage" ditambahkan ✅
- `menu_handlers.py` - Handler untuk lineage button ✅
- `bot.py` - Command dan callback registered ✅

### ✅ Testing
- 8/8 tests PASS ✅
- No diagnostic errors ✅

---

## 🎯 Cara Test (Development)

### 1. Start Bot
```bash
cd Bismillah
python bot.py
```

### 2. Test Basic Flow

#### A. Spawn Root Agent
```
/spawn_agent RootAgent
```
- Tidak ada parent selection (karena belum punya agent)
- Agent dibuat sebagai root

#### B. Spawn Child Agent
```
/spawn_agent ChildAgent
```
- Muncul parent selection menu
- Pilih "Spawn from: RootAgent"
- ChildAgent dibuat dengan parent = RootAgent

#### C. Check Status
```
/agent_status
```
Output akan menampilkan:
```
🌳 Lineage Info
👨 Parent: RootAgent (untuk ChildAgent)
👶 Children: 1 (untuk RootAgent)
💰 Revenue from Children: 0 (belum ada earnings)
```

#### D. Check Lineage Tree
```
/agent_lineage
```
Output akan menampilkan tree:
```
🤖 RootAgent
├─ 🟢 NORMAL
├─ 💰 50,000 credits
└─ Children (1):
   🤖 ChildAgent
   ├─ 🟢 NORMAL
   ├─ 💰 20,000 credits
   └─ Children (0)
```

### 3. Test Revenue Sharing

**Cara Manual Test:**
1. Buka Python console:
```bash
cd Bismillah
python
```

2. Jalankan:
```python
from database import Database
from app.revenue_manager import get_revenue_manager

db = Database()
revenue_manager = get_revenue_manager(db)

# Simulasi ChildAgent dapat profit 1000 credits
# Platform ambil 20% = 200 credits
# Parent dapat 10% dari 1000 = 100 credits
import asyncio
result = asyncio.run(revenue_manager.collect_performance_fee(
    agent_id="<child_agent_id>",  # Ganti dengan ID ChildAgent
    profit=1000
))
print(result)
```

3. Check RootAgent balance:
```
/agent_status
```
- RootAgent seharusnya dapat +100 credits
- "Revenue from Children" seharusnya +100

---

## 🚀 Deploy ke Production

### Option 1: Git Push (Recommended)
```bash
cd Bismillah
git add .
git commit -m "feat: lineage system integration complete"
git push origin main
```
- Railway akan auto-deploy
- Monitor logs di Railway dashboard

### Option 2: Manual Restart
Jika sudah push sebelumnya:
1. Buka Railway dashboard
2. Klik "Redeploy"
3. Monitor logs

---

## 📊 Monitoring After Deploy

### 1. Check Logs
Di Railway dashboard, monitor:
- ✅ "Automaton handlers registered"
- ✅ "Lineage registered: child=..., parent=..."
- ✅ "Distributed X credits from child Y to parent Z"

### 2. Test Commands
```
/spawn_agent TestAgent
/agent_status
/agent_lineage
```

### 3. Check Database
Di Supabase:
```sql
-- Check lineage relationships
SELECT agent_name, parent_agent_id, total_children_revenue
FROM user_automatons
WHERE parent_agent_id IS NOT NULL;

-- Check lineage transactions
SELECT * FROM lineage_transactions
ORDER BY timestamp DESC
LIMIT 10;
```

---

## 🎯 Expected Behavior

### Spawn Flow
1. User: `/spawn_agent MyAgent`
2. Bot: Shows parent selection (if user has agents)
3. User: Clicks "Spawn from: ParentAgent"
4. Bot: Creates agent, registers lineage
5. Bot: Shows success message with parent info

### Revenue Flow
1. ChildAgent earns 1000 credits
2. Platform collects 20% = 200 credits
3. Parent receives 10% of 1000 = 100 credits
4. Grandparent receives 10% of 100 = 10 credits
5. All transactions recorded in `lineage_transactions`

### Status Display
```
🤖 Status Agent

📛 Nama: ChildAgent
💰 Conway Credits: 800

🌳 Lineage Info
👨 Parent: ParentAgent
👶 Children: 0
💰 Revenue from Children: 0
```

---

## 🐛 Troubleshooting

### Issue: Parent selection tidak muncul
**Penyebab:** User belum punya agent
**Solusi:** Spawn agent pertama dulu (akan jadi root agent)

### Issue: Revenue tidak distribute
**Penyebab:** 
- Child agent belum punya parent_agent_id
- Child agent balance tidak cukup

**Solusi:**
```sql
-- Check parent relationship
SELECT agent_name, parent_agent_id FROM user_automatons WHERE id = '<agent_id>';

-- Check balance
SELECT agent_name, conway_credits FROM user_automatons WHERE id = '<agent_id>';
```

### Issue: Lineage tree tidak tampil
**Penyebab:** Agent tidak ada atau tidak punya children

**Solusi:** Spawn child agent dulu

---

## 📞 Quick Commands

### Check Lineage in Database
```sql
-- All agents with parents
SELECT 
    a.agent_name as child,
    p.agent_name as parent,
    a.total_children_revenue
FROM user_automatons a
LEFT JOIN user_automatons p ON a.parent_agent_id = p.id
WHERE a.parent_agent_id IS NOT NULL;

-- Lineage transactions
SELECT 
    p.agent_name as parent,
    c.agent_name as child,
    lt.child_earnings,
    lt.parent_share,
    lt.timestamp
FROM lineage_transactions lt
JOIN user_automatons p ON lt.parent_agent_id = p.id
JOIN user_automatons c ON lt.child_agent_id = c.id
ORDER BY lt.timestamp DESC
LIMIT 20;
```

### Test Revenue Distribution
```python
# In Python console
from database import Database
from app.lineage_integration import on_performance_fee_collected
import asyncio

db = Database()

# Simulate child earning 1000 credits
asyncio.run(on_performance_fee_collected(
    agent_id="<child_agent_id>",
    profit=1000,
    fee=200
))
```

---

## ✅ Checklist Deploy

- [x] Migration 005 applied
- [x] All code integrated
- [x] Tests passing (8/8)
- [x] No diagnostic errors
- [ ] Test in development
- [ ] Deploy to production
- [ ] Monitor logs
- [ ] Test with real users

---

## 🎉 Summary

**Lineage system sudah 100% siap!**

Yang bisa user lakukan:
1. ✅ Spawn agent dengan parent (optional)
2. ✅ Lihat lineage info di status
3. ✅ Lihat lineage tree lengkap
4. ✅ Dapat passive income dari children (10% recursive)

**Tinggal deploy dan test!** 🚀

---

## 📝 Notes

- Lineage maksimal 10 level
- Parent dapat 10% dari GROSS earnings (sebelum platform fee)
- Platform tetap dapat 20% dari SEMUA earnings
- Revenue sharing otomatis saat agent dapat profit
- Circular reference dicegah otomatis

**Ready to deploy!** 🎯
