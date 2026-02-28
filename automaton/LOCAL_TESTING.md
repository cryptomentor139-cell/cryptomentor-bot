# Local Testing Guide - Telegram Bot

Panduan untuk test Automaton dengan Telegram bot di lokal (tanpa Railway).

## Prerequisites

1. **Node.js 20+** sudah terinstall
2. **Telegram account**
3. **Conway API key** (untuk automaton)

## Step 1: Setup Telegram Bot

### 1.1 Create Bot dengan @BotFather

1. Buka Telegram, search `@BotFather`
2. Send command: `/newbot`
3. Follow prompts:
   - Bot name: `My Automaton Bot` (atau nama lain)
   - Bot username: `my_automaton_bot` (harus unique, ends with `_bot`)
4. **Save bot token** yang diberikan (format: `123456:ABC-DEF...`)

### 1.2 Get Your Telegram User ID

1. Search `@userinfobot` di Telegram
2. Send `/start`
3. Bot akan reply dengan your user ID (contoh: `987654321`)
4. **Save user ID ini**

## Step 2: Setup Environment Variables

Create file `.env` di root project:

```bash
# Conway API (required)
CONWAY_API_KEY=your_conway_api_key_here
CONWAY_API_URL=https://api.conway.tech

# Telegram Bot (required untuk test)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CREATOR_ID=987654321

# Database (local)
DB_PATH=./local-test.db

# Logging
LOG_LEVEL=info

# Payment (optional)
PAYMENT_AUTO_APPROVE_THRESHOLD=0
PAYMENT_RATE_LIMIT_PER_HOUR=10

# Railway simulation (untuk test Railway mode)
RAILWAY_ENVIRONMENT=development
PORT=3000
```

## Step 3: Build dan Run

```bash
# Install dependencies (jika belum)
npm install

# Build
npm run build

# Run automaton
node dist/index.js --run
```

## Step 4: Test Telegram Bot

### 4.1 Start Conversation

1. Buka Telegram
2. Search bot kamu (username yang kamu buat)
3. Click "Start" atau send `/start`
4. Bot akan respond dengan welcome message

### 4.2 Test Commands

Try these commands:

```
/help          - Show all commands
/status        - System status
/credits       - Financial status
/deposit       - Deposit instructions
/logs          - Recent activity
/children      - List child agents
```

### 4.3 Test Conversational Interface

Send normal messages (bukan commands):

```
Halo, siapa kamu?
Berapa sisa credits saya?
Tolong jelaskan apa yang bisa kamu lakukan
```

Bot akan respond secara natural!

### 4.4 Test Payment Approval

Jika automaton mencoba transfer credits, kamu akan dapat notification dengan inline buttons:

```
💰 Payment Request

To: 0x1234...
Amount: 5.00
Note: test payment
ID: 01HQXYZ123

[✅ Approve] [❌ Reject]
```

Click button atau use command:
```
/approve 01HQXYZ123
/reject 01HQXYZ123 not needed
```

## Troubleshooting

### Bot tidak respond

1. Check console logs untuk errors
2. Verify `TELEGRAM_BOT_TOKEN` correct
3. Verify `TELEGRAM_CREATOR_ID` correct
4. Check bot is not blocked

### "TELEGRAM_CREATOR_ID is required" error

Make sure `.env` file has both:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CREATOR_ID`

### Database errors

Delete `local-test.db` dan restart:
```bash
rm local-test.db
node dist/index.js --run
```

### Conway API errors

Verify `CONWAY_API_KEY` is valid and has credits.

## Expected Behavior

When running successfully, you should see:

```
[2024-01-15T10:00:00.000Z] Conway Automaton v0.1.0 starting...
[2024-01-15T10:00:01.000Z] Railway environment: development
[2024-01-15T10:00:01.000Z] Database path: ./local-test.db
[2024-01-15T10:00:02.000Z] Database initialized
[2024-01-15T10:00:03.000Z] Telegram bot started
[2024-01-15T10:00:03.000Z] Health server listening on port 3000
[2024-01-15T10:00:04.000Z] Starting agent loop...
```

Then you can interact via Telegram!

## Health Check

While running, you can check health endpoint:

```bash
curl http://localhost:3000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00.000Z",
  "uptime": 120,
  "agent": {
    "state": "running",
    "turnCount": 5
  },
  "database": {
    "connected": true
  },
  "telegram": {
    "connected": true
  }
}
```

## Next Steps

After local testing works:
1. Deploy to Railway (see `docs/railway-deployment.md`)
2. Setup Railway volume for persistent database
3. Configure production environment variables
4. Monitor via Telegram and Railway dashboard

## Notes

- Local database (`local-test.db`) will persist between runs
- Conversation history saved in database
- Payment requests saved in database
- Use `/clear` to clear conversation history
- Stop with Ctrl+C (graceful shutdown)

