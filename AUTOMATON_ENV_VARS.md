# 🔐 Automaton Environment Variables

## Required Variables

Copy-paste ini ke Railway Dashboard → Automaton Service → Variables:

### 1. CONWAY_API_KEY
```
CONWAY_API_KEY=your_conway_api_key_here
```

**Cara dapat:**
1. Visit https://conway.tech
2. Sign up / Login
3. Dashboard → API Keys
4. Create New Key
5. Copy key

### 2. CONWAY_WALLET_ADDRESS
```
CONWAY_WALLET_ADDRESS=0x...
```

**Cara dapat:**
- Dari Conway dashboard
- Atau generate baru via Automaton setup wizard

### 3. TELEGRAM_BOT_TOKEN
```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
```

**Note:** Sama dengan bot token yang dipakai di bot service

### 4. NODE_ENV
```
NODE_ENV=production
```

## Optional Variables

### Database Path
```
DATABASE_PATH=/app/data/automaton.db
```

Default: `./automaton.db` di root folder

### Port
```
PORT=3000
```

Railway akan auto-assign port, tapi bisa override

### Log Level
```
LOG_LEVEL=info
```

Options: `debug`, `info`, `warn`, `error`

### Telegram Integration
```
TELEGRAM_ENABLED=true
```

Enable/disable Telegram integration

## Example .env File

Untuk local testing, buat file `automaton/.env`:

```env
# Conway API
CONWAY_API_KEY=sk_test_abc123...
CONWAY_WALLET_ADDRESS=0x1234567890abcdef...

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_ENABLED=true

# Environment
NODE_ENV=development
LOG_LEVEL=debug

# Database
DATABASE_PATH=./data/automaton.db

# Server
PORT=3000
```

**IMPORTANT:** Jangan commit file `.env` ke Git!

## Security Notes

1. **Never commit API keys** to Git
2. **Use Railway env vars** for production
3. **Rotate keys regularly** (monthly)
4. **Use different keys** for dev/prod
5. **Monitor API usage** di Conway dashboard

## Validation

Test env vars loaded correctly:

```bash
# Local
cd Bismillah/automaton
node -e "console.log(process.env.CONWAY_API_KEY ? 'OK' : 'MISSING')"

# Railway (via logs)
# Automaton will log: "✓ API key loaded"
```

## Troubleshooting

### Error: CONWAY_API_KEY not set

**Fix:** Set variable di Railway Dashboard

### Error: Invalid API key

**Fix:** 
1. Check key di Conway dashboard
2. Regenerate key jika perlu
3. Update Railway env var

### Error: Wallet address invalid

**Fix:** 
1. Check format: `0x...` (42 characters)
2. Get from Conway dashboard
3. Or run Automaton setup wizard locally

## Quick Copy-Paste Template

```env
CONWAY_API_KEY=
CONWAY_WALLET_ADDRESS=
TELEGRAM_BOT_TOKEN=
NODE_ENV=production
```

Fill in the values, then paste ke Railway Variables.

---

**Next:** Deploy Automaton dengan env vars ini!
