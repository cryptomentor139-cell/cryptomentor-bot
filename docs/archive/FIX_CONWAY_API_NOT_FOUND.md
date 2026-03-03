# Fix: Conway API Environment Variable Not Found

## 🔴 Problem
Error: `CONWAY_APKEY environment variable not set`

Bot tidak bisa membaca Conway API key dari environment variables, meskipun sudah ditambahkan di Railway atau file `.env`.

---

## 🔍 Root Cause Analysis

### Kemungkinan Penyebab:

1. **Railway Variables Tidak Ter-save**
   - Variable ditambahkan tapi tidak di-save
   - Typo di nama variable
   - Service tidak di-redeploy setelah update

2. **Typo di Nama Variable**
   - Harus: `CONWAY_API_KEY` (bukan `CONWAY_APKEY`)
   - Case-sensitive!

3. **Service Tidak Restart**
   - Environment variables hanya di-load saat startup
   - Perlu redeploy untuk apply changes

4. **File .env Tidak Ter-commit**
   - `.env` ada di `.gitignore`
   - Railway tidak bisa baca file `.env` dari repo

---

## ✅ SOLUTION

### Step 1: Verify Local .env File

Pastikan file `Bismillah/.env` memiliki:

```env
CONWAY_API_KEY=cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73
CONWAY_API_URL=https://api.conway.tech
CONWAY_WALLET_ADDRESS=0x0000000000000000000000000000000000000000
```

### Step 2: Test Locally

```bash
cd Bismillah
python test_conway_env_railway.py
```

Expected output:
```
✅ CONWAY_API_KEY: Found: cnwy_k_DNl...ENY73
✅ CONWAY_API_URL: https://api.conway.tech
✅ Conway API client initialized successfully
✅ Conway API is accessible
```

### Step 3: Add to Railway Variables

**CRITICAL: Railway TIDAK membaca file .env dari repo!**

Anda HARUS menambahkan variables secara manual di Railway dashboard:

1. **Buka Railway Dashboard**
   - Go to: https://railway.app/dashboard
   - Select project: `cryptomentor-bot`

2. **Go to Variables Tab**
   - Click on your service
   - Click "Variables" tab

3. **Add These Variables:**

   ```
   Variable Name: CONWAY_API_KEY
   Value: cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73
   ```

   ```
   Variable Name: CONWAY_API_URL
   Value: https://api.conway.tech
   ```

   ```
   Variable Name: CONWAY_WALLET_ADDRESS
   Value: 0x0000000000000000000000000000000000000000
   ```

4. **IMPORTANT: Click "Add" for EACH variable!**
   - Don't just type and move to next
   - Must click "Add" button to save

5. **Verify Variables Are Saved**
   - Scroll down to see all variables
   - Confirm `CONWAY_API_KEY` is in the list
   - Confirm `CONWAY_API_URL` is in the list

### Step 4: Redeploy Service

**Option A: Trigger Redeploy (Recommended)**
1. Go to "Deployments" tab
2. Click "Redeploy" on latest deployment
3. Wait for deployment to complete (~2-3 minutes)

**Option B: Push New Commit**
```bash
cd Bismillah
git add test_conway_env_railway.py FIX_CONWAY_API_NOT_FOUND.md
git commit -m "fix: add Conway API environment test and troubleshooting guide"
git push origin main
```

Railway will auto-deploy.

### Step 5: Verify on Railway

**Check Deployment Logs:**
1. Go to "Deployments" tab
2. Click on latest deployment
3. Check logs for:
   ```
   ✅ Conway API client initialized: https://api.conway.tech
   ```

**If you see:**
```
❌ CONWAY_API_KEY environment variable not set
```

Then variables are NOT loaded. Go back to Step 3.

---

## 🧪 Testing After Fix

### Test 1: Check Environment Variables

Run this in Railway shell (if available) or check logs:

```python
import os
print(f"CONWAY_API_KEY: {os.getenv('CONWAY_API_KEY')[:10]}...")
print(f"CONWAY_API_URL: {os.getenv('CONWAY_API_URL')}")
```

### Test 2: Try Spawn Agent

1. Open bot in Telegram
2. Click "AI Agent" menu
3. Click "Spawn Agent"
4. Type agent name

**Expected:**
- No error about CONWAY_APKEY
- Agent spawns successfully
- Deposit address generated

**If Still Error:**
- Check Railway logs
- Verify variables are saved
- Try redeploying again

---

## 🔧 Common Mistakes

### ❌ Mistake 1: Typo in Variable Name
```
CONWAY_APKEY=...  ❌ WRONG (missing 'I')
CONWAY_API_KEY=... ✅ CORRECT
```

### ❌ Mistake 2: Not Clicking "Add" Button
- Just typing in the field doesn't save
- Must click "Add" button!

### ❌ Mistake 3: Not Redeploying
- Variables only load at startup
- Must redeploy after adding variables

### ❌ Mistake 4: Using .env File in Railway
- Railway doesn't read `.env` from repo
- Must add variables in Railway dashboard

---

## 📊 Verification Checklist

After applying fix, verify:

- [ ] `CONWAY_API_KEY` exists in Railway Variables
- [ ] `CONWAY_API_URL` exists in Railway Variables
- [ ] Service has been redeployed
- [ ] Deployment logs show "Conway API client initialized"
- [ ] No error about "CONWAY_APKEY environment variable not set"
- [ ] Bot can spawn agents without errors
- [ ] Deposit addresses are generated

---

## 🆘 Still Not Working?

### Debug Steps:

1. **Check Railway Logs:**
   ```
   Look for: "Conway API client initialized"
   If missing: Variables not loaded
   ```

2. **Verify Variable Names:**
   ```
   Must be EXACT:
   - CONWAY_API_KEY (not CONWAY_APKEY)
   - CONWAY_API_URL (not CONWAY_URL)
   ```

3. **Check API Key Format:**
   ```
   Should start with: cnwy_k_
   Length: ~40 characters
   ```

4. **Test API Key Manually:**
   ```bash
   curl -H "Authorization: Bearer cnwy_k_DNll3zray_o4ccEpRmW0G6pK68BENY73" \
        https://api.conway.tech/api/v1/health
   ```

5. **Contact Support:**
   - If API key is invalid
   - If Conway API is down
   - If all steps above don't work

---

## 📝 Summary

**Problem:** Conway API key not found
**Cause:** Railway doesn't read `.env` file
**Solution:** Add variables manually in Railway dashboard
**Critical:** Must click "Add" and redeploy!

**Quick Fix:**
1. Railway Dashboard → Variables
2. Add `CONWAY_API_KEY` and `CONWAY_API_URL`
3. Click "Add" for each
4. Redeploy service
5. Check logs for "Conway API client initialized"
