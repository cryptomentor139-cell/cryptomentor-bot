# Quick Deployment Commands

## Copy and paste these commands in order:

### 1. Navigate to bot directory
```bash
cd cryptomentor-bot
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Railway project
```bash
railway init
```
- Select: "Create new project"
- Name: `cryptomentor-telegram-bot`

### 4. Set environment variables (copy all at once)
```bash
railway variables set TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
railway variables set AUTOMATON_API_URL=https://automaton-production-a899.up.railway.app
railway variables set AUTOMATON_API_KEY=0d69e61760114de226da6292ed388ef8b9873c30438eb8ceab62e92e33029024
railway variables set NODE_ENV=production
```

### 5. Verify variables
```bash
railway variables
```

### 6. Deploy
```bash
railway up
```

### 7. View logs
```bash
railway logs
```

### 8. Follow logs in real-time
```bash
railway logs --follow
```

---

## Testing Commands (in Telegram)

Send these to your bot:
1. `/start` - Register and get welcome message
2. `/help` - View all commands
3. `/status` - Check your credits and stats
4. `/talk Hello!` - Test AI conversation

---

## Troubleshooting Commands

```bash
# Check deployment status
railway status

# Redeploy if needed
railway up

# Open Railway dashboard
railway open

# View recent logs
railway logs --tail 100
```
