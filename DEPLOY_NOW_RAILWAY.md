# 🚀 DEPLOY KE RAILWAY - STEP BY STEP

## ✅ Status: SIAP DEPLOY
**Comprehensive Test:** 11/11 PASS (100%)

---

## 📋 LANGKAH 1: CHECK GIT STATUS

```bash
cd Bismillah
git status
```

**Expected Output:**
```
On branch main
Changes not staged for commit:
  modified:   comprehensive_test.py
  modified:   app/lineage_integration.py
  ...
```

---

## 📋 LANGKAH 2: COMMIT SEMUA PERUBAHAN

```bash
# Add semua file
git add .

# Commit dengan message yang jelas
git commit -m "feat: lineage system complete - parent-child agent relationships with 10% recursive revenue sharing

- Implemented LineageManager for parent-child relationships
- Added 10% recursive revenue distribution to parents
- Integrated lineage UI in bot handlers and menu
- Added /agent_lineage command for tree visualization
- Updated comprehensive_test.py with dotenv loading
- All tests passing (11/11 - 100%)
- Ready for production deployment"

# Check commit berhasil
git log -1
```

**Expected Output:**
```
commit abc123def456...
Author: Your Name <your@email.com>
Date:   Fri Feb 21 16:20:00 2026

    feat: lineage system complete - parent-child agent relationships...
```

---

## 📋 LANGKAH 3: PUSH KE GITHUB

```bash
# Push ke GitHub (triggers Railway auto-deploy)
git push origin main
```

**Expected Output:**
```
Enumerating objects: 25, done.
Counting objects: 100% (25/25), done.
Delta compression using up to 8 threads
Compressing objects: 100% (15/15), done.
Writing objects: 100% (15/15), 12.34 KiB | 1.23 MiB/s, done.
Total 15 (delta 10), reused 0 (delta 0)
To https://github.com/your-username/Bismillah.git
   def456..abc123  main -> main
```

**⏱️ Estimated Time:** 10-30 seconds

---

## 📋 LANGKAH 4: MONITOR RAILWAY DEPLOYMENT

### A. Buka Railway Dashboard
1. Go to: https://railway.app/dashboard
2. Login dengan akun Anda
3. Pilih project "Bismillah" (atau nama project Anda)

### B. Check Deployment Status
1. Klik tab **"Deployments"**
2. Lihat deployment terbaru di top
3. Status akan berubah:
   - 🟡 **Building** (1-2 menit)
   - 🟡 **Deploying** (30 detik)
   - 🟢 **Active** (SUCCESS!)

### C. View Logs
1. Klik deployment yang sedang running
2. Klik tab **"View Logs"**
3. Monitor output real-time

**Expected Logs (Success):**
```
✅ Bot initialized
✅ Supabase client initialized
✅ Conway API client initialized
✅ Automaton Manager initialized
✅ Revenue Manager initialized
✅ Lineage Manager initialized
✅ Automaton handlers registered
✅ Menu system loaded
✅ Bot started successfully
```

**⏱️ Total Deployment Time:** ~2-3 menit

---

## 📋 LANGKAH 5: VERIFY ENVIRONMENT VARIABLES

Pastikan semua environment variables sudah set di Railway:

### A. Check Variables
1. Di Railway dashboard, klik tab **"Variables"**
2. Verify variables berikut ada:

**Required Variables:**
```
TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
ADMIN1=1187119989
ADMIN2=7079544380

SUPABASE_URL=https://xrbqnocovfymdikngaza.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

CONWAY_API_KEY=cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73
CONWAY_API_URL=https://api.conway.tech
CONWAY_WALLET_ADDRESS=0x0000000000000000000000000000000000000000

DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=google/gemini-flash-1.5
```

### B. Add Missing Variables (Jika Ada)
1. Klik **"+ New Variable"**
2. Masukkan Name dan Value
3. Klik **"Add"**
4. Railway akan auto-redeploy

---

## 📋 LANGKAH 6: TEST BOT DI TELEGRAM

### A. Test Basic Commands
```
/start
```
**Expected:** Bot responds dengan menu

```
/spawn_agent TestAgent1
```
**Expected:** Agent created successfully

```
/agent_status
```
**Expected:** Shows agent with lineage info

### B. Test Lineage System
```
/spawn_agent TestAgent2
```
**Expected:** Parent selection menu appears

**Click:** "Spawn from: TestAgent1"
**Expected:** TestAgent2 created with parent

```
/agent_lineage
```
**Expected:** Tree shows TestAgent1 → TestAgent2

---

## 🔧 TROUBLESHOOTING

### Issue 1: Deployment Failed (Build Error)

**Symptom:** Railway shows "Build Failed" dengan red status

**Solution:**
```bash
# Check Railway logs untuk error message
# Common issues:
# - Missing dependencies
# - Syntax errors
# - Import errors

# Fix locally, then redeploy:
git add .
git commit -m "fix: deployment issue"
git push origin main
```

### Issue 2: Bot Not Responding

**Symptom:** Bot tidak respond di Telegram setelah deployment

**Solution:**
1. Check Railway logs:
   - Look for "Bot started successfully"
   - Check for error messages
2. Verify TELEGRAM_BOT_TOKEN correct
3. Check bot process is running (status should be "Active")
4. Try restart deployment:
   - Railway dashboard → Deployments
   - Click "..." → "Restart"

### Issue 3: Lineage Commands Not Working

**Symptom:** `/agent_lineage` tidak ada atau error

**Solution:**
1. Check Railway logs:
   ```
   ✅ Automaton handlers registered
   ✅ Lineage Manager initialized
   ```
2. Verify migration 005 applied di Supabase:
   - Go to Supabase SQL Editor
   - Run: `SELECT parent_agent_id FROM user_automatons LIMIT 1;`
   - Should not error
3. Check database has lineage columns

### Issue 4: Conway API Error

**Symptom:** "CONWAY_API_KEY not set" di logs

**Solution:**
1. Check Railway Variables tab
2. Verify CONWAY_API_KEY exists
3. Verify CONWAY_WALLET_ADDRESS exists
4. If missing, add them and Railway will auto-redeploy

---

## ✅ POST-DEPLOYMENT CHECKLIST

Setelah deployment selesai, verify:

- [ ] Railway status: **Active** (green)
- [ ] Bot responds: `/start` works
- [ ] Spawn works: `/spawn_agent TestAgent`
- [ ] Parent selection: Shows menu when spawning 2nd agent
- [ ] Lineage tree: `/agent_lineage` displays tree
- [ ] Database: Has lineage data (check Supabase)
- [ ] Logs: No errors in Railway logs

---

## 📊 VERIFY DATABASE

### Check Lineage Data di Supabase

1. Go to: https://supabase.com/dashboard
2. Select project: xrbqnocovfymdikngaza
3. Click **"SQL Editor"**
4. Run query:

```sql
-- Check lineage relationships
SELECT 
    a.agent_name as child,
    p.agent_name as parent,
    a.conway_credits,
    a.total_children_revenue
FROM user_automatons a
LEFT JOIN user_automatons p ON a.parent_agent_id = p.id
WHERE a.parent_agent_id IS NOT NULL
ORDER BY a.created_at DESC
LIMIT 10;
```

**Expected:** Shows child-parent relationships

```sql
-- Check lineage transactions
SELECT * FROM lineage_transactions
ORDER BY timestamp DESC
LIMIT 10;
```

**Expected:** Shows revenue distribution transactions (after agents earn)

---

## 🎯 SUCCESS CRITERIA

Deployment dianggap **SUKSES** jika:

✅ Railway deployment status: **Active**
✅ Bot responds di Telegram
✅ `/spawn_agent` works
✅ Parent selection UI appears
✅ `/agent_lineage` shows tree
✅ Database has lineage data
✅ No errors in Railway logs

---

## 📞 MONITORING

### Check Logs Secara Berkala

**Railway Dashboard → Deployments → View Logs**

**Look for:**
- ✅ Success messages (green checkmarks)
- ⚠️ Warnings (yellow)
- ❌ Errors (red)

**Common Success Patterns:**
```
✅ Bot initialized
✅ Automaton handlers registered
✅ Lineage system ready
✅ Bot started successfully
```

**Common Error Patterns:**
```
❌ CONWAY_API_KEY not set
❌ Failed to register lineage
❌ Database connection failed
```

---

## 🔄 ROLLBACK PLAN (Jika Ada Masalah)

### Option 1: Rollback via Railway Dashboard
1. Railway dashboard → Deployments
2. Find previous stable deployment
3. Click "..." → "Redeploy"
4. Confirm

### Option 2: Rollback via Git
```bash
# Find previous commit
git log --oneline

# Revert to previous commit
git revert HEAD

# Push
git push origin main

# Railway will auto-deploy previous version
```

---

## 🚀 QUICK DEPLOY COMMAND

**One-liner untuk deploy:**

```bash
cd Bismillah && git add . && git commit -m "feat: lineage system complete" && git push origin main
```

**Then:**
1. Open Railway dashboard
2. Watch deployment progress
3. Test bot when Active
4. Celebrate! 🎉

---

## 📈 EXPECTED TIMELINE

| Step | Time | Status |
|------|------|--------|
| Git commit | 10s | ✅ |
| Git push | 20s | ✅ |
| Railway build | 1-2 min | 🟡 |
| Railway deploy | 30s | 🟡 |
| Bot starts | 10s | 🟢 |
| **Total** | **~3 min** | **✅** |

---

## 🎉 READY TO DEPLOY!

**Status:** ✅ ALL SYSTEMS GO
**Risk Level:** LOW (all tests passing)
**Rollback:** Easy (via Railway dashboard)
**Downtime:** 0 seconds (zero-downtime deployment)

**DEPLOY SEKARANG!** 🚀

---

**Next Steps After Deployment:**
1. ✅ Test di Telegram
2. ✅ Monitor Railway logs
3. ✅ Verify database
4. ✅ Test lineage system
5. ✅ Celebrate success! 🎉
