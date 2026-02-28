# Database Migrations - Automaton Integration

## Overview
This folder contains SQL migration scripts for the Automaton integration feature. Each migration is numbered sequentially and should be run in order.

## Migration Files

### 001_automaton_tables.sql
**Status:** ✅ Ready to run
**Purpose:** Create 6 new tables for Automaton integration
**Tables:**
- `custodial_wallets` - User-specific Ethereum wallets
- `wallet_deposits` - USDT/USDC deposit tracking
- `wallet_withdrawals` - Withdrawal request management
- `user_automatons` - Autonomous trading agent records
- `automaton_transactions` - Agent transaction history
- `platform_revenue` - Revenue tracking and reporting

**Features:**
- Complete table schemas with constraints
- 20+ performance indexes
- Data validation checks
- Foreign key relationships
- Verification queries included

## How to Run Migrations

### Method 1: Supabase SQL Editor (Recommended)
1. Open Supabase dashboard: https://app.supabase.com
2. Navigate to: SQL Editor
3. Open migration file: `001_automaton_tables.sql`
4. Copy all content
5. Paste in SQL Editor
6. Click "Run" button
7. Verify success message

### Method 2: Supabase CLI
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref <your-project-ref>

# Run migration
supabase db push
```

### Method 3: psql Command Line
```bash
# Connect to Supabase database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run migration
\i migrations/001_automaton_tables.sql
```

## Verification

After running the migration, verify tables were created:

```sql
-- Check table existence
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'custodial_wallets',
  'wallet_deposits', 
  'wallet_withdrawals',
  'user_automatons',
  'automaton_transactions',
  'platform_revenue'
)
ORDER BY table_name;
```

**Expected result:** 6 rows

```sql
-- Check index creation
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN (
  'custodial_wallets',
  'wallet_deposits',
  'wallet_withdrawals', 
  'user_automatons',
  'automaton_transactions',
  'platform_revenue'
)
ORDER BY tablename, indexname;
```

**Expected result:** 20+ rows

## Rollback

If you need to rollback the migration:

```sql
-- Drop all tables (WARNING: This deletes all data!)
DROP TABLE IF EXISTS platform_revenue CASCADE;
DROP TABLE IF EXISTS automaton_transactions CASCADE;
DROP TABLE IF EXISTS user_automatons CASCADE;
DROP TABLE IF EXISTS wallet_withdrawals CASCADE;
DROP TABLE IF EXISTS wallet_deposits CASCADE;
DROP TABLE IF EXISTS custodial_wallets CASCADE;
```

**⚠️ WARNING:** Only run rollback in development/testing. Never in production with real user data!

## Migration Status Tracking

Keep track of which migrations have been run:

| Migration | Status | Date Run | Notes |
|-----------|--------|----------|-------|
| 001_automaton_tables.sql | ⏳ Pending | - | Initial schema |

Update this table after running each migration.

## Best Practices

1. **Always backup before migration**
   ```sql
   -- Create backup of existing data
   pg_dump -h db.your-project.supabase.co -U postgres -d postgres > backup_$(date +%Y%m%d).sql
   ```

2. **Test in development first**
   - Run migration in development environment
   - Verify all tables and indexes created
   - Test application functionality
   - Then run in production

3. **Run during low traffic**
   - Schedule migrations during off-peak hours
   - Notify users of maintenance window
   - Monitor for errors

4. **Verify after migration**
   - Check all tables exist
   - Check all indexes created
   - Check constraints active
   - Test basic queries

5. **Document any issues**
   - Record any errors encountered
   - Document workarounds applied
   - Update migration notes

## Troubleshooting

### Error: "relation already exists"
**Cause:** Tables already created
**Fix:** Skip migration or drop tables first (if safe)

### Error: "permission denied"
**Cause:** Insufficient database permissions
**Fix:** Use service role key or database owner account

### Error: "syntax error"
**Cause:** SQL syntax issue
**Fix:** Check PostgreSQL version compatibility

### Error: "constraint violation"
**Cause:** Existing data conflicts with new constraints
**Fix:** Clean up data before migration

## Future Migrations

Future migrations will be added here:
- `002_*.sql` - Next migration
- `003_*.sql` - Following migration
- etc.

Each migration should:
- Be idempotent (safe to run multiple times)
- Include rollback instructions
- Be well documented
- Be tested in development

## Support

If you encounter issues:
1. Check Supabase logs for error details
2. Verify database permissions
3. Review migration SQL syntax
4. Contact support with error messages

## Related Documentation

- **Setup Guide:** `../RAILWAY_ENV_SETUP.md`
- **Quick Start:** `../AUTOMATON_QUICK_START.md`
- **Deployment Checklist:** `../AUTOMATON_DEPLOYMENT_CHECKLIST.md`
- **Task 1 Summary:** `../AUTOMATON_TASK1_COMPLETE.md`

---

**Last Updated:** 2026-02-20
**Version:** 1.0.0
**Status:** Ready for deployment
