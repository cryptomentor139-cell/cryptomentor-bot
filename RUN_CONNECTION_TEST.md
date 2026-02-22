# 🚀 Quick Start: Test Koneksi Bot-Automaton

## Langkah Cepat

### 1. Jalankan Test
```bash
cd Bismillah
python prove_bot_automaton_connected.py
```

### 2. Lihat Hasil

#### ✅ Jika Berhasil (8/8 tests PASS):
```
🎉 ALL TESTS PASSED!
✅ PROOF: Bot and Automaton are CONNECTED and WORKING!
```

**Artinya:** Bot dan Automaton SUDAH TERHUBUNG! 🎉

#### ⚠️ Jika Ada Masalah:
Script akan memberikan troubleshooting guide spesifik.

---

## 🔍 Apa yang Di-Test?

1. ✅ Environment Variables - Apakah CONWAY_API_URL sudah di-set?
2. ✅ Automaton Health - Apakah service online?
3. ✅ API Endpoints - Apakah endpoint accessible?
4. ✅ Conway Client - Apakah client bisa initialize?
5. ✅ Database - Apakah database connection OK?
6. ✅ Handler Routing - Apakah routing ke API handlers?
7. ✅ End-to-End Flow - Apakah complete flow berfungsi?
8. ✅ Network Latency - Berapa lama response time?

---

## 📊 Interpretasi Hasil

### Scenario 1: Semua Test PASS ✅
**Status:** CONNECTED dan WORKING

**Action:** Tidak perlu action, sudah sempurna!

**Test di Telegram:**
```
/automaton status
/automaton spawn
/automaton balance
```

### Scenario 2: Test 1 FAIL (Environment Variables) ❌
**Problem:** CONWAY_API_URL belum di-set

**Fix:**
1. Buka Railway Dashboard
2. Bot Service → Variables
3. Add: `CONWAY_API_URL` = `https://automaton-production-a899.up.railway.app`
4. Save (service auto-restart)

### Scenario 3: Test 2 FAIL (Automaton Health) ❌
**Problem:** Automaton service offline

**Fix:**
1. Buka Railway Dashboard
2. Automaton Service → Check status
3. Jika crash, restart service
4. Check logs untuk error

### Scenario 4: Test 4 FAIL (Conway Client) ❌
**Problem:** Code belum di-deploy atau import error

**Fix:**
```bash
cd Bismillah
git add .
git commit -m "Deploy automaton API handlers"
git push origin main
```

Wait 2-3 minutes for Railway auto-deploy.

### Scenario 5: Test 6 FAIL (Handler Routing) ❌
**Problem:** Routing masih pakai old handlers

**Fix:**
1. Verify commit `85b5fa9` deployed
2. Check Railway → Bot Service → Deployments
3. Redeploy if needed

---

## 🎯 Expected Output (Success)

```
================================================================================
  🔍 PROOF OF CONNECTION: Bot ↔ Automaton
================================================================================

This script will prove that Railway Bot is connected to Railway Automaton
by running comprehensive tests on all integration points.

================================================================================
  TEST 1: Environment Variables Check
================================================================================

📋 Required Variables:
✅ CONWAY_API_URL: https://automaton-production-a899.up.railway.app
✅ SUPABASE_URL: https://xxx.supabase.co
✅ SUPABASE_KEY: eyJhbG...
✅ TELEGRAM_BOT_TOKEN: 1234567890:ABC...

✅ PASS - Environment Variables
   ✅ CONWAY_API_URL: Automaton service URL
   ✅ SUPABASE_URL: Database URL
   ✅ SUPABASE_KEY: Database key
   ✅ TELEGRAM_BOT_TOKEN: Bot token

================================================================================
  TEST 2: Automaton Service Health Check
================================================================================

🔍 Testing endpoint: https://automaton-production-a899.up.railway.app/health
⏱️  Response time: 150ms
📊 Status code: 200
✅ Automaton service is ONLINE and HEALTHY

✅ PASS - Automaton Health
   Status: healthy
   Uptime: 12345 seconds
   Response time: 150ms

... (tests 3-8) ...

================================================================================
  FINAL SUMMARY
================================================================================

📊 Test Results: 8/8 passed

   ✅ Environment Variables
   ✅ Automaton Health
   ✅ API Endpoints
   ✅ Conway Client
   ✅ Database Integration
   ✅ Handler Routing
   ✅ End-to-End Flow
   ✅ Network Latency

================================================================================
  🎉 ALL TESTS PASSED!
================================================================================

✅ PROOF: Bot and Automaton are CONNECTED and WORKING!

You can now use these commands in Telegram:
   • /automaton status
   • /automaton spawn
   • /automaton balance
   • /automaton deposit
```

---

## 🔧 Troubleshooting Quick Reference

| Test Failed | Problem | Solution |
|-------------|---------|----------|
| Test 1 | Env vars not set | Set CONWAY_API_URL in Railway |
| Test 2 | Automaton offline | Check Automaton service status |
| Test 3 | API not accessible | Check Automaton deployment |
| Test 4 | Client init failed | Remove CONWAY_API_KEY from Bot |
| Test 5 | Database error | Check SUPABASE credentials |
| Test 6 | Wrong routing | Deploy latest code (commit 85b5fa9) |
| Test 7 | E2E flow failed | Check Railway logs for errors |
| Test 8 | High latency | Network issue, retry later |

---

## 📞 Jika Masih Bermasalah

### 1. Check Railway Bot Logs
```
Railway Dashboard → Bot Service → Deployments → View Logs
```

Cari error message saat user ketik `/automaton status`

### 2. Check Automaton Logs
```
Railway Dashboard → Automaton Service → Deployments → View Logs
```

Cari error atau crash messages

### 3. Manual Health Check
```bash
curl https://automaton-production-a899.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "uptime": 12345,
  "agent": {
    "state": "idle"
  }
}
```

### 4. Verify Environment Variables
```
Railway Dashboard → Bot Service → Variables
```

Must have:
- `CONWAY_API_URL` = `https://automaton-production-a899.up.railway.app`
- `SUPABASE_URL` = your Supabase URL
- `SUPABASE_KEY` = your Supabase key
- `TELEGRAM_BOT_TOKEN` = your bot token

Should NOT have:
- `CONWAY_API_KEY` (only Automaton needs this)
- `CONWAY_WALLET_ADDRESS` (only Automaton needs this)

---

## ✅ Success Criteria

Bot dan Automaton TERHUBUNG jika:

1. ✅ Script shows 8/8 tests PASS
2. ✅ `/automaton status` merespons (even if "Tidak Ada Agent")
3. ✅ `/automaton spawn` merespons dengan instruksi
4. ✅ No import errors in Railway logs
5. ✅ No connection errors in Railway logs

---

## 🎯 Next Steps After Connection Confirmed

1. **Test Commands:**
   ```
   /automaton status
   /automaton spawn MyAgent
   /automaton balance
   /automaton deposit
   ```

2. **Create Agent:**
   - Use `/automaton spawn` to create agent
   - Get deposit address
   - Deposit $30 USDC to activate

3. **Monitor:**
   - Use `/automaton status` to check agent
   - Use `/automaton balance` to check credits

---

**Jalankan test sekarang:**
```bash
python prove_bot_automaton_connected.py
```
