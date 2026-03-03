# ✅ Pre-Testing Checklist - Automaton System

## 🎯 Tujuan
Memastikan SEMUA komponen automaton system sudah running dengan baik sebelum testing dengan user.

---

## 📋 CHECKLIST LENGKAP

### 1. ✅ Database & Migration

#### A. Supabase Connection
```bash
cd Bismillah
python test_supabase_credentials.py
```
**Expected:** ✅ Connection successful

#### B. Migration Status
```sql
-- Check di Supabase SQL Editor
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_automatons'
ORDER BY ordinal_position;
```
**Expected Columns:**
- [x] id (uuid)
- [x] user_id (bigint)
- [x] agent_name (text)
- [x] agent_wallet (text)
- [x] conway_credits (numeric)
- [x] status (text)
- [x] survival_tier (text)
- [x] parent_agent_id (uuid) ← LINEAGE
- [x] total_children_revenue (numeric) ← LINEAGE
- [x] autonomous_spawn (boolean) ← LINEAGE

#### C. Lineage Tables
```sql
-- Check lineage_transactions table
SELECT * FROM lineage_transactions LIMIT 1;
```
**Expected:** Table exists (bisa kosong)

---

### 2. ✅ Conway API Integration

#### A. Environment Variables
```bash
cd Bismillah
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CONWAY_API_KEY:', 'SET' if os.getenv('CONWAY_API_KEY') else 'MISSING'); print('CONWAY_WALLET_ADDRESS:', 'SET' if os.getenv('CONWAY_WALLET_ADDRESS') else 'MISSING')"
```
**Expected:**
- CONWAY_API_KEY: SET
- CONWAY_WALLET_ADDRESS: SET

#### B. Conway API Test
```bash
cd Bismillah
python test_conway_api.py
```
**Expected:** All tests PASS

---

### 3. ✅ Core Automaton Components

#### A. Automaton Manager
```bash
cd Bismillah
python test_automaton_manager.py
```
**Expected:** All tests PASS

#### B. Revenue Manager
```bash
cd Bismillah
python -c "from database import Database; from app.revenue_manager import get_revenue_manager; db = Database(); rm = get_revenue_manager(db); print('✅ Revenue Manager OK')"
```
**Expected:** ✅ Revenue Manager OK

#### C. Lineage System
```bash
cd Bismillah
python test_lineage_system.py
```
**Expected:** 8/8 tests PASS

---

### 4. ✅ Deposit & Withdrawal System

#### A. Deposit Monitor
```bash
cd Bismillah
python test_deposit_monitor.py
```
**Expected:** Tests PASS

#### B. Withdrawal Handler
```bash
cd Bismillah
python test_withdrawal_handling.py
```
**Expected:** Tests PASS

#### C. Admin Withdrawal Processing
```bash
cd Bismillah
python test_admin_withdrawal_processing.py
```
**Expected:** Tests PASS

---

### 5. ✅ Rate Limiting & Security

#### A. Rate Limiter
```bash
cd Bismillah
python test_rate_limiter.py
```
**Expected:** All tests PASS

#### B. Audit Logger
```bash
cd Bismillah
python test_audit_logger.py
```
**Expected:** All tests PASS

---

### 6. ✅ Bot Handlers

#### A. Automaton Handlers
```bash
cd Bismillah
python test_handlers_automaton.py
```
**Expected:** All handlers registered

#### B. Menu Integration
```bash
cd Bismillah
python test_menu_integration.py
```
**Expected:** All menu handlers working

---

### 7. ✅ Background Services

#### A. Balance Monitor
Check file exists:
```bash
ls -la Bismillah/app/balance_monitor.py
```
**Expected:** File exists

#### B. Deposit Monitor
Check file exists:
```bash
ls -la Bismillah/app/deposit_monitor.py
```
**Expected:** File exists

---

### 8. ✅ User Experience Flow

#### A. Commands Available
- [x] `/spawn_agent` - Spawn new agent
- [x] `/agent_status` - Check agent status
- [x] `/agent_lineage` - View lineage tree
- [x] `/deposit` - Get deposit address
- [x] `/balance` - Check balance
- [x] `/agent_logs` - View transaction history
- [x] `/withdraw` - Request withdrawal

#### B. Menu Buttons Available
- [x] 🚀 Spawn Agent
- [x] 📊 Agent Status
- [x] 🌳 Agent Lineage
- [x] 💰 Fund Agent (Deposit)
- [x] 📜 Agent Logs

---

## 🧪 COMPREHENSIVE TEST SCRIPT

Jalankan script ini untuk test semua komponen sekaligus:

```bash
cd Bismillah
python comprehensive_test.py
```

Jika belum ada, buat file `comprehensive_test.py`:

```python
#!/usr/bin/env python3
"""
Comprehensive Test - All Automaton Components
"""

import sys
import asyncio
from datetime import datetime

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_test(name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")

async def main():
    print_header("AUTOMATON SYSTEM - COMPREHENSIVE TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 1. Database Connection
    print_header("1. DATABASE CONNECTION")
    try:
        from database import Database
        db = Database()
        passed = db.supabase_enabled
        print_test("Supabase Connection", passed)
        results.append(("Database", passed))
    except Exception as e:
        print_test("Supabase Connection", False)
        print(f"   Error: {e}")
        results.append(("Database", False))
    
    # 2. Conway API
    print_header("2. CONWAY API")
    try:
        from app.conway_integration import ConwayIntegration
        conway = ConwayIntegration()
        passed = conway.api_key is not None
        print_test("Conway API Key", passed)
        results.append(("Conway API", passed))
    except Exception as e:
        print_test("Conway API Key", False)
        print(f"   Error: {e}")
        results.append(("Conway API", False))
    
    # 3. Automaton Manager
    print_header("3. AUTOMATON MANAGER")
    try:
        from app.automaton_manager import get_automaton_manager
        manager = get_automaton_manager(db)
        passed = manager is not None
        print_test("Automaton Manager", passed)
        results.append(("Automaton Manager", passed))
    except Exception as e:
        print_test("Automaton Manager", False)
        print(f"   Error: {e}")
        results.append(("Automaton Manager", False))
    
    # 4. Revenue Manager
    print_header("4. REVENUE MANAGER")
    try:
        from app.revenue_manager import get_revenue_manager
        revenue_mgr = get_revenue_manager(db)
        passed = revenue_mgr is not None
        print_test("Revenue Manager", passed)
        results.append(("Revenue Manager", passed))
    except Exception as e:
        print_test("Revenue Manager", False)
        print(f"   Error: {e}")
        results.append(("Revenue Manager", False))
    
    # 5. Lineage System
    print_header("5. LINEAGE SYSTEM")
    try:
        from app.lineage_manager import LineageManager
        lineage_mgr = LineageManager()
        passed = lineage_mgr is not None
        print_test("Lineage Manager", passed)
        results.append(("Lineage System", passed))
    except Exception as e:
        print_test("Lineage Manager", False)
        print(f"   Error: {e}")
        results.append(("Lineage System", False))
    
    # 6. Rate Limiter
    print_header("6. RATE LIMITER")
    try:
        from app.rate_limiter import get_rate_limiter
        rate_limiter = get_rate_limiter(db)
        passed = rate_limiter is not None
        print_test("Rate Limiter", passed)
        results.append(("Rate Limiter", passed))
    except Exception as e:
        print_test("Rate Limiter", False)
        print(f"   Error: {e}")
        results.append(("Rate Limiter", False))
    
    # 7. Handlers
    print_header("7. BOT HANDLERS")
    try:
        from app.handlers_automaton import (
            spawn_agent_command,
            agent_status_command,
            agent_lineage_command,
            deposit_command,
            withdraw_command
        )
        passed = True
        print_test("Automaton Handlers", passed)
        results.append(("Bot Handlers", passed))
    except Exception as e:
        print_test("Automaton Handlers", False)
        print(f"   Error: {e}")
        results.append(("Bot Handlers", False))
    
    # 8. Menu System
    print_header("8. MENU SYSTEM")
    try:
        from menu_system import MenuBuilder
        menu = MenuBuilder.build_ai_agent_menu()
        passed = menu is not None
        print_test("Menu System", passed)
        results.append(("Menu System", passed))
    except Exception as e:
        print_test("Menu System", False)
        print(f"   Error: {e}")
        results.append(("Menu System", False))
    
    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL SYSTEMS READY FOR TESTING!")
        return 0
    else:
        print("\n⚠️ SOME SYSTEMS NEED ATTENTION")
        print("\nFailed Components:")
        for name, p in results:
            if not p:
                print(f"  ❌ {name}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

---

## 🚀 QUICK START TESTING

### Step 1: Run Comprehensive Test
```bash
cd Bismillah
python comprehensive_test.py
```

### Step 2: Start Bot (Development)
```bash
cd Bismillah
python bot.py
```

### Step 3: Test Basic Flow

#### A. Test Spawn Agent
```
/spawn_agent TestAgent1
```
**Expected:**
- Agent created successfully
- Deposit address shown
- Spawn fee deducted (100k credits)

#### B. Test Agent Status
```
/agent_status
```
**Expected:**
- Agent info displayed
- Lineage info shown (parent: None for first agent)
- Balance, tier, runtime shown

#### C. Test Spawn with Parent
```
/spawn_agent TestAgent2
```
**Expected:**
- Parent selection menu appears
- Can choose "Spawn from: TestAgent1"
- Agent created with parent relationship

#### D. Test Lineage Tree
```
/agent_lineage
```
**Expected:**
- Hierarchical tree displayed
- Shows TestAgent1 with child TestAgent2

---

## 📊 DATABASE VERIFICATION

### Check Lineage Relationships
```sql
SELECT 
    a.agent_name as child,
    p.agent_name as parent,
    a.conway_credits,
    a.total_children_revenue
FROM user_automatons a
LEFT JOIN user_automatons p ON a.parent_agent_id = p.id
ORDER BY a.created_at DESC
LIMIT 10;
```

### Check Transactions
```sql
SELECT 
    type,
    amount,
    description,
    timestamp
FROM automaton_transactions
ORDER BY timestamp DESC
LIMIT 20;
```

---

## ⚠️ COMMON ISSUES & FIXES

### Issue 1: Supabase Connection Failed
**Fix:**
```bash
# Check .env file
cat .env | grep SUPABASE

# Should have:
# SUPABASE_URL=https://...
# SUPABASE_SERVICE_KEY=eyJ...
```

### Issue 2: Conway API Not Working
**Fix:**
```bash
# Check Conway credentials
cat .env | grep CONWAY

# Should have:
# CONWAY_API_KEY=...
# CONWAY_WALLET_ADDRESS=0x...
```

### Issue 3: Migration Not Applied
**Fix:**
```bash
cd Bismillah
python apply_lineage_migration.py
```

### Issue 4: Handlers Not Registered
**Fix:**
- Restart bot
- Check bot.py for handler registration
- Check logs for errors

---

## ✅ FINAL CHECKLIST BEFORE TESTING

- [ ] Comprehensive test: ALL PASS
- [ ] Bot starts without errors
- [ ] `/spawn_agent` works
- [ ] `/agent_status` shows lineage info
- [ ] `/agent_lineage` displays tree
- [ ] `/deposit` shows address
- [ ] `/withdraw` creates request
- [ ] Parent selection UI appears
- [ ] Database has lineage columns
- [ ] Conway API responds

---

## 🎯 READY FOR TESTING?

Jika SEMUA checklist di atas ✅, maka sistem siap untuk:
1. Testing dengan real user
2. Deploy ke production
3. Monitor dan scale

**Next Step:** Run `comprehensive_test.py` dan pastikan semua PASS!
