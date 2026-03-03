# Railway Deployment Guide for CryptoMentor Telegram Bot

## Overview

This guide will walk you through deploying the CryptoMentor Telegram Bot to Railway platform. The deployment process involves initializing a Railway project, configuring environment variables, deploying the code, and verifying the bot is working correctly.

## Prerequisites

Before starting, ensure you have:
- ✅ Railway CLI installed (install from: https://docs.railway.app/develop/cli)
- ✅ Railway account created (sign up at: https://railway.app)
- ✅ Telegram Bot Token: `8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4`
- ✅ Automaton API URL: `https://automaton-production-a899.up.railway.app`
- ✅ Automaton API Key: `0d69e61760114de226da6292ed388ef8b9873c30438eb8ceab62e92e33029024`

## Step 1: Install Railway CLI

If you haven't installed the Railway CLI yet:

### Windows (PowerShell):
```powershell
iwr https://railway.app/install.ps1 | iex
```

### macOS/Linux:
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Verify Installation:
```bash
railway --version
```

## Step 2: Login to Railway

Open your terminal in the `cryptomentor-bot` directory and login:

```bash
railway login
```

This will open your browser for authentication. Complete the login process.

## Step 3: Initialize Railway Project

### 3.1 Create New Project

Run the following command:

```bash
railway init
```

When prompted:
1. **Select**: "Create new project"
2. **Project Name**: Enter `cryptomentor-telegram-bot`
3. Press Enter to confirm

### 3.2 Verify Project Creation

Check that the project was created:

```bash
railway status
```

You should see your project name and details.

## Step 4: Configure Environment Variables

Set all required environment variables for the bot:

### 4.1 Set Telegram Bot Token

```bash
railway variables set TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
```

### 4.2 Set Automaton API URL

```bash
railway variables set AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
```

### 4.3 Set Automaton API Key

```bash
railway variables set AUTOMATON_API_KEY=0d69e61760114de226da6292ed388ef8b9873c30438eb8ceab62e92e33029024
```

### 4.4 Set Node Environment

```bash
railway variables set NODE_ENV=production
```

### 4.5 Verify All Variables

List all configured variables:

```bash
railway variables
```

You should see all 4 variables listed:
- ✅ TELEGRAM_BOT_TOKEN
- ✅ AUTOMATON_API_URL
- ✅ AUTOMATON_API_KEY
- ✅ NODE_ENV

## Step 5: Deploy to Railway

### 5.1 Deploy the Bot

Run the deployment command:

```bash
railway up
```

This will:
1. Upload your code to Railway
2. Install dependencies (npm install)
3. Start the bot using the start script in package.json
4. Begin polling for Telegram messages

### 5.2 Wait for Deployment

The deployment process typically takes 1-3 minutes. You'll see output showing:
- ✅ Code upload progress
- ✅ Build logs
- ✅ Deployment status

### 5.3 Verify Deployment Success

Once complete, you should see a success message indicating the deployment is live.

## Step 6: Verify Bot is Running

### 6.1 Check Logs

View the bot's logs to confirm it started successfully:

```bash
railway logs
```

Look for the following key messages:
- ✅ `"Bot is ready and listening for messages..."`
- ✅ `"Scheduled notifications configured for 08:00, 14:00, 20:00 WIB"`
- ✅ No error messages

### 6.2 Test Bot Commands

Open Telegram and test each command:

#### Test /start Command
1. Open your bot in Telegram
2. Send: `/start`
3. Expected response: Welcome message with credit balance
4. ✅ Verify you receive a greeting with credits displayed

#### Test /help Command
1. Send: `/help`
2. Expected response: List of all available commands with descriptions
3. ✅ Verify all commands are listed (/start, /status, /help, /talk)

#### Test /status Command
1. Send: `/status`
2. Expected response: Your current status including:
   - Credit balance
   - Conversation count
   - Last activity time
3. ✅ Verify status information is displayed correctly

#### Test /talk Command
1. Send: `/talk Hello, how are you?`
2. Expected response: 
   - Typing indicator appears
   - AI-generated response from Automaton
3. ✅ Verify you receive an AI response

## Step 7: Monitor Deployment

### 7.1 View Real-Time Logs

Keep logs running to monitor bot activity:

```bash
railway logs --follow
```

This will show real-time logs as users interact with the bot.

### 7.2 Check Railway Dashboard

Visit the Railway dashboard to:
1. Go to: https://railway.app/dashboard
2. Select your `cryptomentor-telegram-bot` project
3. View:
   - Deployment status
   - Resource usage (CPU, Memory)
   - Environment variables
   - Logs

## Troubleshooting

### Issue: Bot Not Responding

**Symptoms**: Bot doesn't reply to commands

**Solutions**:
1. Check logs for errors: `railway logs`
2. Verify environment variables: `railway variables`
3. Ensure bot token is correct
4. Check Automaton API is accessible

### Issue: "Bot is ready" Message Not Appearing

**Symptoms**: Logs don't show initialization message

**Solutions**:
1. Check for startup errors in logs
2. Verify all dependencies installed correctly
3. Restart deployment: `railway up --detach`

### Issue: API Connection Errors

**Symptoms**: Errors mentioning Automaton API in logs

**Solutions**:
1. Verify AUTOMATON_API_URL is correct
2. Verify AUTOMATON_API_KEY is correct
3. Check Automaton API is running: Visit the URL in browser
4. Check network connectivity from Railway

### Issue: Scheduled Notifications Not Sending

**Symptoms**: No notifications at 08:00, 14:00, 20:00 WIB

**Solutions**:
1. Check logs at scheduled times
2. Verify timezone is set to Asia/Jakarta in code
3. Ensure bot has active users registered
4. Check notification API endpoint is working

## Scheduled Notifications

The bot will automatically send notifications at:
- 🌅 **08:00 WIB** (01:00 UTC) - Morning update
- 🌤️ **14:00 WIB** (07:00 UTC) - Afternoon update
- 🌙 **20:00 WIB** (13:00 UTC) - Evening update

These notifications are sent to all active users who have started the bot.

## Useful Railway Commands

```bash
# View project status
railway status

# View environment variables
railway variables

# Set a variable
railway variables set KEY=value

# Delete a variable
railway variables delete KEY

# View logs
railway logs

# Follow logs in real-time
railway logs --follow

# Redeploy
railway up

# Open project in dashboard
railway open

# Link to different project
railway link

# Unlink from project
railway unlink
```

## Next Steps

After successful deployment:

1. ✅ **Share Bot**: Share your bot username with users
2. ✅ **Monitor Usage**: Check logs regularly for errors
3. ✅ **Test Notifications**: Wait for scheduled notification times to verify delivery
4. ✅ **Monitor Credits**: Ensure Automaton API credit system is working
5. ✅ **Scale if Needed**: Upgrade Railway plan if you exceed free tier limits

## Support

If you encounter issues:
- Check Railway documentation: https://docs.railway.app
- Review bot logs: `railway logs`
- Check Automaton API status
- Verify all environment variables are set correctly

## Deployment Checklist

Use this checklist to ensure everything is configured correctly:

- [ ] Railway CLI installed and logged in
- [ ] Railway project created: `cryptomentor-telegram-bot`
- [ ] TELEGRAM_BOT_TOKEN environment variable set
- [ ] AUTOMATON_API_URL environment variable set
- [ ] AUTOMATON_API_KEY environment variable set
- [ ] NODE_ENV environment variable set to `production`
- [ ] Code deployed with `railway up`
- [ ] Logs show "Bot is ready" message
- [ ] /start command works
- [ ] /help command works
- [ ] /status command works
- [ ] /talk command works and returns AI responses
- [ ] No errors in Railway logs
- [ ] Bot responds within 2 seconds

## Success Criteria

Your deployment is successful when:
✅ Bot responds to all commands (/start, /help, /status, /talk)
✅ Users can register and receive welcome messages with credits
✅ AI conversations work through /talk command
✅ No errors appear in Railway logs
✅ Bot remains online and responsive

---

**Deployment Date**: _To be filled after deployment_
**Bot Username**: _Your bot's @username_
**Railway Project URL**: _Your Railway dashboard URL_
