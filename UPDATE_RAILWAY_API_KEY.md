# 🔑 Update Railway API Key - URGENT

## Problem Identified ✅

Local API key works perfectly, but Railway doesn't have the correct API key!

**Test Results:**
- ✅ Local API key: VALID
- ✅ GPT-4.1 accessible
- ✅ Usage: $0.034404
- ❌ Railway: 401 error (API key missing or wrong)

---

## Solution: Update Railway Environment Variables

### Step 1: Go to Railway Dashboard

**URL:** https://railway.app/project/industrious-dream

1. Click service "web"
2. Click tab "Variables"

### Step 2: Add/Update These Variables

Copy these EXACT values from your local `.env`:

```bash
OPENCLAW_API_KEY=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
OPENCLAW_BASE_URL=https://openrouter.ai/api/v1
```

### Step 3: Verify Other Required Variables

Make sure these are also set:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4

# Admin IDs
ADMIN1=1187119989
ADMIN2=7079544380

# Database (should already be set by Railway)
PGHOST=ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=npg_PXo7pTdgJ4ny
PGPORT=5432
```

### Step 4: Save & Redeploy

1. Click "Save" or "Add" for each variable
2. Railway will automatically redeploy
3. Wait 2-3 minutes for deployment to complete

---

## Quick Copy-Paste for Railway

### Variables to Add:

| Variable Name | Value |
|--------------|-------|
| `OPENCLAW_API_KEY` | `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` |
| `OPENCLAW_BASE_URL` | `https://openrouter.ai/api/v1` |

---

## After Update: Test Bot

### Test 1: Basic Chat
```
Open Telegram bot
Send: "Hello"
Expected: AI response (not 401 error)
```

### Test 2: Check Model
```
Send: "What model are you?"
Expected: Should mention GPT-4.1 or similar
```

### Test 3: Admin Mode
```
As admin, send: "Test"
Expected: Response with "👑 Admin (Free)"
```

---

## Troubleshooting

### If Still Getting 401 Error:

**Check Railway Logs:**
1. Service "web" → View Logs
2. Look for: "OpenClawManager initialized with GPT-4.1"
3. If not found, API key not loaded

**Verify Variables:**
1. Variables tab
2. Check OPENCLAW_API_KEY exists
3. Check value matches local .env
4. No extra spaces or quotes

**Force Restart:**
1. Settings → Deploy
2. Click "Redeploy"
3. Wait for new deployment

### If API Key Not Working:

**Get New API Key:**
1. Go to: https://openrouter.ai/keys
2. Create new API key
3. Update both local .env and Railway
4. Test locally first: `python test_openrouter_key.py`
5. Then update Railway

---

## Expected Behavior After Fix

### Before (Current):
```
User: "Hello"
Bot: ❌ Error: OpenRouter API error: 401 - {"error":{"message":"User not found","code":401}}
```

### After (Fixed):
```
User: "Hello"
Bot: 👋 Hi! I'm your AI assistant powered by GPT-4.1. How can I help you today?

💰 Cost: 1 credit • 💳 Balance: 99 credits
```

---

## Why This Happened

Railway environment variables are separate from local `.env` file. When you:
1. Add variables to local `.env` ✅
2. Push code to GitHub ✅
3. Railway deploys code ✅
4. But Railway doesn't have the `.env` file ❌

**Solution:** Manually add environment variables in Railway dashboard.

---

## Quick Action Checklist

- [ ] Go to Railway dashboard
- [ ] Click service "web"
- [ ] Click "Variables" tab
- [ ] Add `OPENCLAW_API_KEY` with value from .env
- [ ] Add `OPENCLAW_BASE_URL` = `https://openrouter.ai/api/v1`
- [ ] Save changes
- [ ] Wait for auto-redeploy (2-3 minutes)
- [ ] Test bot in Telegram
- [ ] Verify no more 401 errors

---

**Priority:** HIGH - Bot cannot work without this!
**Time to Fix:** 2-3 minutes
**Impact:** OpenClaw will work immediately after fix

---

## Screenshots Guide

1. **Railway Dashboard** → Select "web" service
2. **Variables Tab** → Click to open
3. **Add Variable** → Click "+ New Variable"
4. **Name:** `OPENCLAW_API_KEY`
5. **Value:** Paste the API key
6. **Save** → Click "Add"
7. **Repeat** for `OPENCLAW_BASE_URL`
8. **Wait** for automatic redeploy

---

**Next:** Update Railway variables NOW!
