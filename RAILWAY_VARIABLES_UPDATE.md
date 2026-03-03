# Railway Variables Update - GPT-4.1 Configuration

## Variables to Update in Railway

Buka Railway Dashboard → Your Project → Variables, lalu update:

### 1. OpenClaw API Key (REQUIRED)
```
OPENCLAW_API_KEY=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
```

### 2. DeepSeek API Key (Optional - for signal generation)
```
DEEPSEEK_API_KEY=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
```

### 3. Base URL (Should already be set)
```
OPENCLAW_BASE_URL=https://openrouter.ai/api/v1
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
```

## How to Update

### Via Railway Dashboard (Recommended)
1. Go to https://railway.app/dashboard
2. Select your project
3. Click "Variables" tab
4. Find `OPENCLAW_API_KEY`
5. Click "Edit" and paste new key
6. Click "Save"
7. Railway will auto-redeploy

### Via Railway CLI
```bash
railway variables set OPENCLAW_API_KEY=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
railway variables set DEEPSEEK_API_KEY=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
```

## Verify Update

### Check Variables
```bash
railway variables
```

### Check Deployment Logs
```bash
railway logs
```

Look for:
- ✅ "Bot started successfully"
- ✅ No "401 Unauthorized" errors
- ✅ OpenClaw commands working

## After Update

1. Wait for auto-redeploy (1-2 minutes)
2. Test bot in Telegram:
   - Send `/openclaw_start`
   - Should see welcome message
   - Try chatting with AI
3. Monitor logs for errors

## Troubleshooting

### Bot still shows 401 error
- Check if variables saved correctly
- Force redeploy: Railway Dashboard → Deployments → Redeploy

### Variables not updating
- Clear Railway cache
- Delete old deployment
- Trigger new deployment

### Bot not responding
- Check Railway logs: `railway logs`
- Check bot is running: `railway status`
- Restart service: `railway restart`

## Status
✅ Variables updated locally in `.env`
⏳ Need to update in Railway Dashboard
⏳ Wait for auto-redeploy
⏳ Test in Telegram

## Quick Commands

```bash
# Check Railway status
railway status

# View logs
railway logs --follow

# Restart service
railway restart

# Force redeploy
railway up --detach
```
