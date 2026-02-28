# 🚀 CryptoMentor Bot Deployment Checklist

## Pre-Deployment

- [ ] Railway CLI installed
- [ ] Railway account created
- [ ] Logged into Railway (`railway login`)
- [ ] In `cryptomentor-bot` directory
- [ ] Bot token ready: `8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4`

## Step 1: Initialize Railway Project

```bash
railway init
```

- [ ] Command executed
- [ ] Selected "Create new project"
- [ ] Named project: `cryptomentor-telegram-bot`
- [ ] Project created successfully

**Verify**: Run `railway status` - should show project name

---

## Step 2: Configure Environment Variables

### Set TELEGRAM_BOT_TOKEN
```bash
railway variables set TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
```
- [ ] Command executed
- [ ] Success message received

### Set AUTOMATON_API_URL
```bash
railway variables set AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
```
- [ ] Command executed
- [ ] Success message received

### Set AUTOMATON_API_KEY
```bash
railway variables set AUTOMATON_API_KEY=0d69e61760114de226da6292ed388ef8b9873c30438eb8ceab62e92e33029024
```
- [ ] Command executed
- [ ] Success message received

### Set NODE_ENV
```bash
railway variables set NODE_ENV=production
```
- [ ] Command executed
- [ ] Success message received

### Verify All Variables
```bash
railway variables
```
- [ ] TELEGRAM_BOT_TOKEN listed
- [ ] AUTOMATON_API_URL listed
- [ ] AUTOMATON_API_KEY listed
- [ ] NODE_ENV listed
- [ ] All 4 variables present

---

## Step 3: Deploy to Railway

```bash
railway up
```

- [ ] Command executed
- [ ] Code uploaded
- [ ] Build started
- [ ] Dependencies installed
- [ ] Deployment completed
- [ ] Success message received

**Expected time**: 1-3 minutes

---

## Step 4: Verify Deployment

### Check Logs
```bash
railway logs
```

Look for these messages:
- [ ] "Bot is ready and listening for messages..."
- [ ] "Scheduled notifications configured for 08:00, 14:00, 20:00 WIB"
- [ ] No error messages

### Follow Logs (Optional)
```bash
railway logs --follow
```
- [ ] Real-time logs displaying
- [ ] No errors appearing

---

## Step 5: Test Bot in Telegram

### Test /start Command
1. Open Telegram
2. Find your bot
3. Send: `/start`

- [ ] Bot responds
- [ ] Welcome message received
- [ ] Credits displayed (e.g., "1000 free credits")
- [ ] Response time < 2 seconds

### Test /help Command
Send: `/help`

- [ ] Bot responds
- [ ] All commands listed:
  - [ ] /start
  - [ ] /status
  - [ ] /help
  - [ ] /talk
- [ ] Descriptions provided
- [ ] Examples shown

### Test /status Command
Send: `/status`

- [ ] Bot responds
- [ ] Credit balance shown
- [ ] Conversation count shown
- [ ] Last activity time shown
- [ ] Information formatted correctly

### Test /talk Command
Send: `/talk Hello, how are you?`

- [ ] Typing indicator appears
- [ ] Bot responds with AI message
- [ ] Response is relevant
- [ ] Response time reasonable (< 30 seconds)

---

## Step 6: Verify Scheduled Notifications

**Note**: This requires waiting for scheduled times

### Morning Notification (08:00 WIB / 01:00 UTC)
- [ ] Notification received at correct time
- [ ] Content is relevant
- [ ] All registered users received it

### Afternoon Notification (14:00 WIB / 07:00 UTC)
- [ ] Notification received at correct time
- [ ] Content is relevant
- [ ] All registered users received it

### Evening Notification (20:00 WIB / 13:00 UTC)
- [ ] Notification received at correct time
- [ ] Content is relevant
- [ ] All registered users received it

---

## Step 7: Monitor and Maintain

### Check Railway Dashboard
Visit: https://railway.app/dashboard

- [ ] Project visible
- [ ] Status: Running
- [ ] No errors
- [ ] Resource usage normal (< 512MB RAM)

### Monitor Logs Regularly
```bash
railway logs --tail 100
```

- [ ] No recurring errors
- [ ] User interactions logged
- [ ] API calls successful

### Performance Checks
- [ ] Bot responds within 2 seconds
- [ ] No timeout errors
- [ ] Memory usage stable
- [ ] No crash/restart loops

---

## Troubleshooting

### If Bot Doesn't Respond

1. Check logs:
```bash
railway logs
```
- [ ] Logs checked
- [ ] Error identified (if any)

2. Verify variables:
```bash
railway variables
```
- [ ] All 4 variables present
- [ ] Values correct

3. Restart deployment:
```bash
railway up
```
- [ ] Redeployed
- [ ] Issue resolved

### If API Errors Occur

1. Test Automaton API:
   - Visit: https://automaton-production-a899.up.railway.app
   - [ ] API is accessible

2. Check API key:
   - [ ] AUTOMATON_API_KEY is correct
   - [ ] No typos in environment variable

3. Check logs for specific error:
```bash
railway logs | grep -i error
```
- [ ] Error identified
- [ ] Solution applied

---

## Success Criteria

Your deployment is successful when ALL of these are true:

- ✅ Bot responds to /start command
- ✅ Bot responds to /help command
- ✅ Bot responds to /status command
- ✅ Bot responds to /talk command with AI responses
- ✅ Users can register and receive welcome messages
- ✅ Credits are displayed correctly
- ✅ No errors in Railway logs
- ✅ Bot remains online continuously
- ✅ Response time < 2 seconds for commands
- ✅ Scheduled notifications send at correct times

---

## Post-Deployment Tasks

- [ ] Share bot username with users
- [ ] Document bot username: `@_______________`
- [ ] Set up monitoring alerts (optional)
- [ ] Create user documentation
- [ ] Plan for scaling if needed
- [ ] Schedule regular maintenance checks

---

## Quick Reference

### Essential Commands
```bash
# View status
railway status

# View logs
railway logs

# Follow logs
railway logs --follow

# List variables
railway variables

# Redeploy
railway up

# Open dashboard
railway open
```

### Bot Commands (in Telegram)
- `/start` - Register and get welcome
- `/help` - View all commands
- `/status` - Check credits and stats
- `/talk <message>` - Chat with AI

---

## Support

If you encounter issues:

1. **Check Documentation**:
   - `RAILWAY_DEPLOYMENT_GUIDE.md` - Full guide
   - `DEPLOYMENT_COMMANDS.md` - Quick commands
   - `PHASE_7_DEPLOYMENT_COMPLETE.md` - Summary

2. **Check Logs**:
   ```bash
   railway logs --tail 100
   ```

3. **Verify Configuration**:
   ```bash
   railway variables
   railway status
   ```

4. **Railway Documentation**:
   - https://docs.railway.app

---

## Completion

**Deployment Date**: _______________
**Bot Username**: @_______________
**Railway Project URL**: _______________
**Deployed By**: _______________

**Status**: 
- [ ] Deployment Complete
- [ ] All Tests Passed
- [ ] Bot Live and Operational
- [ ] Users Can Access Bot

---

**🎉 Congratulations! Your CryptoMentor Telegram Bot is now live on Railway!**
