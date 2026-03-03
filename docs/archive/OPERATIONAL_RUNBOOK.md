# CryptoMentor Telegram Bot - Operational Runbook

## Quick Reference Guide

This runbook provides quick access to common operational procedures for the CryptoMentor Telegram Bot.

---

## Emergency Contacts

**Bot Owner:** [Your Name]
**Railway Account:** [Your Email]
**Telegram Bot:** @CryptoMentorBot
**Automaton API:** https://automaton-production-a899.up.railway.app

---

## Quick Commands

### Check Bot Status
```bash
railway logs --tail 20
```

### View Real-Time Logs
```bash
railway logs --follow
```

### Check for Errors
```bash
railway logs --since 1h | grep "ERROR"
```

### Restart Bot
```bash
railway restart
```

### View Environment Variables
```bash
railway variables
```

---

## Common Issues & Solutions

### Issue: Bot Not Responding

**Quick Check:**
```bash
railway logs --tail 50 | grep "Bot is ready"
```

**Solution:**
1. Check if bot is running
2. Verify environment variables
3. Restart: `railway restart`
4. Check Telegram API status

---

### Issue: High Error Rate

**Quick Check:**
```bash
railway logs --since 1h | grep "ERROR" | wc -l
```

**Solution:**
1. Identify error type
2. Check Automaton API health
3. Review recent deployments
4. Rollback if needed

---

### Issue: Notifications Not Sent

**Quick Check:**
```bash
railway logs | grep "Notifications sent"
```

**Solution:**
1. Verify cron jobs scheduled
2. Check timezone (Asia/Jakarta)
3. Verify API connectivity
4. Check active user list

---

### Issue: API Timeouts

**Quick Check:**
```bash
railway logs | grep "timeout"
```

**Solution:**
1. Check Automaton API status
2. Verify API credentials
3. Increase timeout if needed
4. Implement retry logic

---

## Daily Checklist

- [ ] Check Railway logs for errors
- [ ] Verify bot responding to /start
- [ ] Check notification delivery (08:00, 14:00, 20:00 WIB)
- [ ] Review error count
- [ ] Check memory usage

---

## Weekly Checklist

- [ ] Analyze error patterns
- [ ] Review performance metrics
- [ ] Check API response times
- [ ] Review user feedback
- [ ] Update issue tracker
- [ ] Check for dependency updates

---

## Monthly Checklist

- [ ] Update dependencies: `npm update`
- [ ] Security audit: `npm audit`
- [ ] Performance optimization review
- [ ] Documentation update
- [ ] Feature planning
- [ ] Backup review

---

## Monitoring Thresholds

### Response Time
- ✅ Normal: < 2 seconds
- ⚠️ Warning: 2-5 seconds
- ❌ Critical: > 5 seconds

### Error Rate
- ✅ Normal: < 1%
- ⚠️ Warning: 1-5%
- ❌ Critical: > 5%

### Memory Usage
- ✅ Normal: < 300 MB
- ⚠️ Warning: 300-400 MB
- ❌ Critical: > 400 MB

### Notification Delivery
- ✅ Normal: > 95%
- ⚠️ Warning: 90-95%
- ❌ Critical: < 90%

---

## Deployment Procedure

### Standard Deployment

1. **Test locally:**
   ```bash
   node index.js
   ```

2. **Commit changes:**
   ```bash
   git add .
   git commit -m "Description"
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Monitor:**
   ```bash
   railway logs --follow
   ```

5. **Verify:**
   - Test /start command
   - Test /status command
   - Test /talk command
   - Check logs for errors

### Rollback Procedure

1. **Identify last good deployment:**
   ```bash
   railway logs --since 24h | grep "Deployment"
   ```

2. **Rollback in Railway dashboard:**
   - Go to Deployments
   - Find last working deployment
   - Click "Redeploy"

3. **Verify rollback:**
   ```bash
   railway logs --tail 50
   ```

---

## Testing Procedures

### Quick Smoke Test (5 minutes)

1. Send `/start` - Verify welcome message
2. Send `/status` - Verify status display
3. Send `/help` - Verify help message
4. Send `/talk Hello` - Verify AI response
5. Check logs for errors

### Full Test Suite (30 minutes)

See: `PHASE_9_TESTING_GUIDE.md`

---

## Notification Schedule

| Time | Timezone | UTC |
|------|----------|-----|
| 08:00 | WIB (UTC+7) | 01:00 |
| 14:00 | WIB (UTC+7) | 07:00 |
| 20:00 | WIB (UTC+7) | 13:00 |

**After each notification:**
```bash
railway logs --since 10m | grep "Notifications sent"
```

---

## Environment Variables

### Required Variables

```bash
TELEGRAM_BOT_TOKEN=<your-bot-token>
AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
AUTOMATON_API_KEY=<your-api-key>
NODE_ENV=production
```

### Update Variable

```bash
railway variables set VARIABLE_NAME=value
```

### View All Variables

```bash
railway variables
```

---

## Log Analysis

### View Specific Time Period

```bash
# Last hour
railway logs --since 1h

# Last 24 hours
railway logs --since 24h

# Last 50 lines
railway logs --tail 50
```

### Filter Logs

```bash
# Errors only
railway logs | grep "ERROR"

# Warnings only
railway logs | grep "WARN"

# API calls
railway logs | grep "API"

# User commands
railway logs | grep "Command:"

# Notifications
railway logs | grep "Notifications sent"
```

### Count Occurrences

```bash
# Count errors
railway logs --since 1h | grep "ERROR" | wc -l

# Count API calls
railway logs --since 1h | grep "API" | wc -l

# Most common errors
railway logs --since 24h | grep "ERROR" | sort | uniq -c | sort -rn
```

---

## Performance Monitoring

### Check Response Times

```bash
railway logs | grep "response time"
```

### Check Memory Usage

```bash
railway logs | grep "Memory usage"
```

### Check API Health

```bash
curl https://automaton-production-a899.up.railway.app/health
```

---

## User Management

### Get Active User Count

```bash
railway logs | grep "Active users:" | tail -1
```

### Check User Registration

```bash
railway logs | grep "User registered"
```

### Check Conversation Activity

```bash
railway logs | grep "/talk" | wc -l
```

---

## Troubleshooting Decision Tree

```
Bot not responding?
├─ Yes → Check Railway logs
│   ├─ "Bot is ready" found?
│   │   ├─ Yes → Check Telegram API
│   │   └─ No → Restart bot
│   └─ Errors found?
│       ├─ Yes → Fix errors
│       └─ No → Check environment variables
└─ No → All good!

High error rate?
├─ Yes → Check error type
│   ├─ API errors → Check Automaton API
│   ├─ Network errors → Check connectivity
│   ├─ Rate limit → Implement throttling
│   └─ Other → Investigate logs
└─ No → Continue monitoring

Notifications not sent?
├─ Yes → Check logs
│   ├─ Cron triggered? → Check timezone
│   ├─ API call failed? → Check API
│   └─ Delivery failed? → Check users
└─ No → All good!
```

---

## Escalation Procedures

### Level 1: Self-Service (0-15 minutes)
- Check logs
- Restart bot
- Verify environment variables
- Test basic commands

### Level 2: Investigation (15-60 minutes)
- Analyze error patterns
- Check API health
- Review recent changes
- Attempt fixes

### Level 3: Escalation (> 60 minutes)
- Contact Automaton API team
- Check Railway status
- Consider rollback
- Notify users

---

## Maintenance Windows

### Preferred Times
- **Low traffic:** 02:00-06:00 WIB
- **Avoid:** 08:00, 14:00, 20:00 WIB (notification times)

### Maintenance Procedure
1. Announce to users (if major)
2. Deploy changes
3. Monitor for 30 minutes
4. Verify all functionality
5. Announce completion

---

## Backup & Recovery

### Configuration Backup
```bash
# Export environment variables
railway variables > env-backup.txt

# Backup code
git push origin main
```

### Recovery Procedure
1. Restore from git: `git pull origin main`
2. Restore environment variables
3. Deploy: `railway up`
4. Verify functionality

---

## Useful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Telegram Bot API Docs:** https://core.telegram.org/bots/api
- **Node.js Docs:** https://nodejs.org/docs
- **Project README:** `README.md`
- **Testing Guide:** `PHASE_9_TESTING_GUIDE.md`
- **Monitoring Guide:** `PHASE_10_MONITORING_MAINTENANCE_GUIDE.md`

---

## Contact Information

**For Bot Issues:**
- Check this runbook first
- Review logs: `railway logs`
- Check Railway status page

**For API Issues:**
- Check Automaton API health
- Contact API team
- Review API documentation

**For Telegram Issues:**
- Check Telegram Bot API status
- Review Telegram documentation
- Check bot token validity

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial runbook |

---

**Last Updated:** 2024
**Maintained By:** Bot Operations Team
**Review Frequency:** Monthly
