# AI Commands Not Responding - Troubleshooting

## Problem
User types `/ai btc` or `/chat` but gets no response from bot.

## Root Cause Analysis

### ✅ What's Working:
1. Menu button "🤖 Ask AI" appears (menu fix successful)
2. Cerebras AI initializes locally
3. AI handlers code is correct
4. Code is pushed to GitHub

### ❌ What's NOT Working:
1. `/ai` command gets no response
2. `/chat` command gets no response
3. `/aimarket` command gets no response

## Possible Causes

### 1. Railway Hasn't Deployed Latest Code ⚠️
**Most Likely Cause!**

Railway might still be running old code without AI handlers.

**How to Check:**
- Go to Railway dashboard
- Check "Deployments" tab
- Look for latest commit: `da921cf` or `1816e51`
- Check deployment status

**How to Fix:**
- Wait for auto-deployment to complete (2-5 minutes)
- Or manually trigger redeploy in Railway
- Check deployment logs for errors

### 2. CEREBRAS_API_KEY Not Set in Railway ⚠️
**Second Most Likely!**

The API key might not be in Railway environment variables.

**How to Check:**
1. Go to Railway dashboard
2. Click on your service
3. Go to "Variables" tab
4. Look for `CEREBRAS_API_KEY`

**How to Fix:**
1. Click "New Variable"
2. Name: `CEREBRAS_API_KEY`
3. Value: `csk-8ee6jd8ekjcwyhtdx6yk3r3dhkewe88t9mv54k5yce295p3n`
4. Click "Add"
5. Railway will auto-redeploy

### 3. Handler Registration Failed 🔍

Check Railway logs for errors like:
```
⚠️ AI handlers failed to register: <error>
```

**How to Fix:**
- Check Railway logs
- Look for import errors
- Verify all dependencies installed

## Step-by-Step Fix

### Step 1: Verify Railway Deployment

```bash
# Check latest commit
git log --oneline -3

# Should show:
# 1816e51 Add AI menu fix documentation
# da921cf Fix: Uncomment ask_ai_callback registration
# e0c5543 Force Railway redeploy
```

### Step 2: Check Railway Environment Variables

Required variables:
- ✅ `TELEGRAM_BOT_TOKEN`
- ✅ `CEREBRAS_API_KEY` ← **CHECK THIS!**
- ✅ Other API keys...

### Step 3: Check Railway Logs

Look for these lines in startup logs:
```
✅ Cerebras AI initialized (Llama 3.1 8B)
✅ AI handlers registered (Cerebras - ultra fast)
```

If you see:
```
⚠️ CEREBRAS_API_KEY not found - AI features disabled
```
Then API key is missing!

### Step 4: Test Commands

After deployment completes:
1. Send `/ai btc` to bot
2. Should get response within 1-2 seconds
3. If no response, check logs

## Quick Fix Commands

### Force Railway Redeploy:
```bash
# Create empty commit to trigger deploy
git commit --allow-empty -m "Force Railway redeploy for AI"
git push origin main
```

### Check if handlers are registered:
Look for this in Railway logs:
```
✅ AI handlers registered (Cerebras - ultra fast)
```

## Expected Behavior After Fix

### Command: `/ai btc`
**Response:**
```
🤖 CryptoMentor AI sedang menganalisis BTC...

⏳ Mohon tunggu, AI sedang memproses data market...

[After 1-2 seconds]

🤖 AI Analysis: BTC

**Kondisi Market 💸**
Harga BTC kembali meningkat...
[analysis continues]

━━━━━━━━━━━━━━━━━━━━━━
⚡ Powered by Cerebras AI (Llama 3.1 8B)
```

### Command: `/chat gimana market hari ini?`
**Response:**
```
[Typing indicator]

[After 0.5-1 second]

📈 Bull Market: Apa itu?
------------------------
[AI response]

━━━━━━━━━━━━━━━━━━━━━━
⚡ Powered by Cerebras AI
```

## Debugging Checklist

- [ ] Latest code pushed to GitHub (commit `da921cf` or later)
- [ ] Railway deployment completed successfully
- [ ] `CEREBRAS_API_KEY` set in Railway variables
- [ ] Railway logs show "✅ AI handlers registered"
- [ ] Railway logs show "✅ Cerebras AI initialized"
- [ ] No errors in Railway startup logs
- [ ] Bot responds to `/menu` (basic functionality works)
- [ ] Menu shows "🤖 Ask AI" button
- [ ] Test `/ai btc` command
- [ ] Test `/chat` command

## If Still Not Working

### Check Railway Logs:
```
# Look for these errors:
- ImportError: No module named 'cerebras_ai'
- ModuleNotFoundError: No module named 'openai'
- ⚠️ CEREBRAS_API_KEY not found
- ⚠️ AI handlers failed to register
```

### Verify Dependencies:
Make sure `requirements.txt` has:
```
openai>=1.0.0
```

### Manual Test:
Run locally:
```bash
python test_ai_commands.py
```

Should show:
```
✅ CEREBRAS_API_KEY found
✅ Cerebras AI initialized
✅ AI handlers imported successfully
```

---

## Summary

**Most Likely Issue:** Railway hasn't deployed latest code OR CEREBRAS_API_KEY not set.

**Quick Fix:**
1. Go to Railway → Variables → Add `CEREBRAS_API_KEY`
2. Wait for auto-redeploy (2-5 min)
3. Test `/ai btc` command

**Status:** Waiting for Railway deployment
**ETA:** 2-5 minutes after API key is set
