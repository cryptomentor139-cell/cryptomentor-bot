# Migration 005 - Complete Error Fix Guide

## Error yang Terjadi

```
ERROR: 42P01: relation "user_automatons" does not exist
```

## Penyebab

Tabel `user_automatons` belum ada di database. Ini berarti migration sebelumnya (001 dan 002) belum dijalankan.

## Solusi: Run Migrations Secara Berurutan

Migration harus dijalankan secara berurutan:
1. Migration 001 - Create automaton tables
2. Migration 002 - Simplify automaton schema  
3. Migration 005 - Add lineage system

### Step 1: Check Existing Tables

Run SQL ini di Supabase SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('user_automatons', 'automaton_transactions', 'custodial_wallets');
```

**Expected Result:**
- Jika return 3 rows → Tables sudah ada, skip ke Step 3
- Jika return 0 rows → Tables belum ada, lanjut ke Step 2

### Step 2: Run Migration 001 & 002

#### Option A: Run Migrations Individually

**Migration 001:**
```bash
cd Bismillah
# Copy SQL from migrations/001_automaton_tables.sql
# Paste to Supabase SQL Editor and Run
```

**Migration 002:**
```bash
# Copy SQL from migrations/002_automaton_simplified.sql
# Paste to Supabase SQL Editor and Run
```

#### Option B: Run All Migrations at Once

Saya akan buat file SQL yang menggabungkan semua migrations:

### Step 3: Run Migration 005

Setelah migration 001 & 002 berhasil, run migration 005:

```bash
# Copy SQL from MIGRATION_005_TO_APPLY.sql
# Paste to Supabase SQL Editor and Run
```

## Quick Fix: Combined Migration File

**EASIEST SOLUTION:** Run file `MIGRATION_ALL_COMBINED.sql`

File ini menggabungkan Migration 002 + 005 dalam satu file.

**Steps:**
1. Buka Supabase Dashboard → SQL Editor
2. Klik "New Query"
3. Copy SEMUA SQL dari `MIGRATION_ALL_COMBINED.sql`
4. Paste ke SQL Editor
5. Klik "Run" atau Ctrl+Enter
6. Wait for "Success" message

**Expected Result:**
```
Success. No rows returned
```

Jika ada error "already exists", itu normal - artinya table/column sudah ada.

## Verification Steps

Setelah semua migrations berhasil:

1. **Check Tables Created:**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'user_automatons', 
  'automaton_transactions', 
  'custodial_wallets',
  'wallet_deposits',
  'wallet_withdrawals',
  'platform_revenue',
  'lineage_transactions'
);
```

Expected: 7 tables

2. **Check Lineage Columns:**
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_automatons' 
AND column_name IN (
  'parent_agent_id',
  'total_children_revenue',
  'autonomous_spawn_enabled',
  'last_autonomous_spawn_at',
  'autonomous_spawn_count'
);
```

Expected: 5 columns

3. **Run Test Suite:**
```bash
cd Bismillah
python test_lineage_system.py
```

Expected: 8/8 tests PASS ✅

## Common Issues

### Issue 1: "relation already exists"
**Solution:** Table sudah ada, skip migration tersebut

### Issue 2: "column already exists"  
**Solution:** Column sudah ada, skip ALTER TABLE tersebut

### Issue 3: "constraint already exists"
**Solution:** Constraint sudah ada, migration akan skip otomatis (karena kita pakai IF NOT EXISTS check)

## Next Steps After Migration Success

1. ✅ Verify all tests pass (8/8)
2. Update handlers untuk lineage support
3. Update revenue_manager untuk distribute 10% ke parent
4. Update menu system dengan tombol "🌳 Agent Lineage"
5. Deploy ke production

---

**Status**: Waiting for user to run migrations
**Action Required**: Run migrations 001, 002, then 005 in order
**ETA**: 10 minutes to complete all migrations
