# Railway Deployment Guide for Automaton

Complete guide for deploying Automaton to Railway with Telegram bot integration and payment approval system.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with Automaton code
- Telegram account for bot setup
- Conway API key

## Initial Railway Setup

### 1. Create Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your Automaton repository
5. Railway will automatically detect Node.js project

### 2. Create Persistent Volume

1. In your Railway project, click "New" → "Volume"
2. Name: `automaton-data`
3. Mount path: `/data`
4. Size: 1GB (minimum)
5. Attach to your service

## Environment Variables Configuration

Configure these in Railway dashboard under "Variables":

### Required Variables

```bash
# Conway API
CONWAY_API_KEY=your_api_key_here
CONWAY_API_URL=https://api.conway.tech

# Database
DB_PATH=/data/automaton.db

# Inference
INFERENCE_MODEL=gpt-4o
MAX_TOKENS_PER_TURN=4096
```

### Optional - Telegram Bot

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CREATOR_ID=your_telegram_user_id
```

### Optional - Payment Settings

```bash
PAYMENT_AUTO_APPROVE_THRESHOLD=0
PAYMENT_RATE_LIMIT_PER_HOUR=10
LOG_LEVEL=info
```

## Telegram Bot Setup

### 1. Create Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the bot token (format: `123456:ABC-DEF...`)
5. Set token as `TELEGRAM_BOT_TOKEN` in Railway

### 2. Get Your Telegram User ID

1. Search for `@userinfobot` in Telegram
2. Send `/start`
3. Copy your user ID (numeric)
4. Set as `TELEGRAM_CREATOR_ID` in Railway

### 3. Configure Bot Commands (Optional)

Send to @BotFather:
```
/setcommands
```

Then paste:
```
status - System synopsis
logs - Recent activity logs
credits - Financial status
deposit - Deposit USDC instructions
approve - Approve payment request
reject - Reject payment request
children - List child agents
clear - Clear conversation history
help - Show help message
```

## Deployment Process

### Automatic Deployment

Railway automatically deploys when you push to your repository:

1. Push code to GitHub
2. Railway detects changes
3. Build process runs:
   - `pnpm install --frozen-lockfile`
   - `pnpm build`
4. Application starts: `node dist/index.js --run`
5. Health check monitors `/health` endpoint

### Manual Deployment

Via Railway CLI:
```bash
railway up
```

## Health Check Configuration

Railway automatically configures health checks:

- **Path**: `/health`
- **Timeout**: 300 seconds
- **Interval**: 60 seconds
- **Restart Policy**: ON_FAILURE
- **Max Retries**: 10

Health endpoint returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00.000Z",
  "uptime": 3600,
  "agent": {
    "state": "active",
    "turnCount": 42
  },
  "database": {
    "connected": true
  },
  "telegram": {
    "connected": true
  }
}
```

## Monitoring

### Railway Dashboard

- View logs in real-time
- Monitor CPU and memory usage
- Check deployment status
- View environment variables

### Telegram Bot

Use these commands to monitor:

- `/status` - Current system state
- `/logs` - Recent activity
- `/credits` - Financial status
- `/children` - Child agents

### Payment Notifications

Telegram bot automatically sends notifications for:
- New payment requests (with approve/reject buttons)
- Payment approvals/rejections
- Critical state alerts

## Troubleshooting

### Database Issues

**Problem**: Database not persisting

**Solution**:
1. Verify volume is mounted at `/data`
2. Check `DB_PATH=/data/automaton.db` in environment
3. View logs for database initialization errors

### Telegram Bot Not Responding

**Problem**: Bot doesn't respond to commands

**Solution**:
1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Check `TELEGRAM_CREATOR_ID` matches your user ID
3. Ensure bot is not blocked
4. Check logs for polling errors

### Build Failures

**Problem**: Build fails during deployment

**Solution**:
1. Ensure `pnpm-lock.yaml` is committed
2. Check Node.js version (requires 20+)
3. Verify all dependencies are in `package.json`
4. Check build logs for specific errors

### Health Check Failures

**Problem**: Railway restarts service repeatedly

**Solution**:
1. Check `/health` endpoint returns 200
2. Verify database connection is working
3. Increase health check timeout if needed
4. Check logs for application errors

### Payment System Issues

**Problem**: Payments not executing

**Solution**:
1. Check Conway API key is valid
2. Verify sufficient credits balance
3. Check payment approval status in database
4. Review payment system logs

## Rollback Procedure

### Automatic Rollback

Railway automatically rolls back if:
- Health checks fail repeatedly
- Build process fails
- Application crashes on startup

### Manual Rollback

Via Railway Dashboard:
1. Go to "Deployments" tab
2. Find previous successful deployment
3. Click "Redeploy"

Via Railway CLI:
```bash
railway rollback
```

## Best Practices

1. **Monitor Logs**: Regularly check Railway logs for errors
2. **Test Locally**: Test with Railway environment variables locally first
3. **Backup Database**: Periodically backup `/data/automaton.db`
4. **Rate Limiting**: Configure payment rate limits appropriately
5. **Security**: Never commit API keys or tokens to repository
6. **Updates**: Keep dependencies updated for security patches

## Cost Optimization

1. Use production dependencies only
2. Configure appropriate resource limits
3. Monitor usage in Railway dashboard
4. Use caching for node_modules
5. Optimize database queries

## Support

- Railway Documentation: https://docs.railway.app
- Conway Documentation: https://docs.conway.tech
- Telegram Bot API: https://core.telegram.org/bots/api

## Next Steps

After successful deployment:

1. Test Telegram bot commands
2. Verify payment approval workflow
3. Monitor system status
4. Set up alerts for critical states
5. Document any custom configurations
