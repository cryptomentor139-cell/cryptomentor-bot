# 🤖 Automaton: Deploy Terpisah (Recommended)

## Kenapa Terpisah?

Combined deployment dengan bot terlalu kompleks untuk Railway Nixpacks. Deploy terpisah lebih:
- ✅ Stable
- ✅ Mudah di-maintain
- ✅ Independent scaling
- ✅ Isolated failures

## Cara Deploy Automaton Terpisah

### Opsi 1: Railway Service Baru (Easiest)

1. **Buat Service Baru di Railway**
   - Dashboard → New Project
   - Deploy from GitHub repo
   - Root directory: `Bismillah/automaton`

2. **Set Environment Variables**
   ```
   CONWAY_API_KEY=your_api_key
   CONWAY_WALLET_ADDRESS=your_wallet
   TELEGRAM_BOT_TOKEN=same_as_bot
   NODE_ENV=production
   ```

3. **Railway Auto-Detect**
   Railway akan detect `package.json` dan:
   - Install dependencies
   - Run `npm run build`
   - Start dengan `npm start`

4. **Get Automaton URL**
   Railway akan provide URL seperti:
   `https://automaton-production-xxxx.up.railway.app`

5. **Connect ke Bot**
   Di bot service, tambah env var:
   ```
   CONWAY_API_URL=https://automaton-production-xxxx.up.railway.app
   ```

### Opsi 2: Render.com (Free Tier)

1. **Sign up di Render.com**
2. **New Web Service**
   - Connect GitHub repo
   - Root directory: `Bismillah/automaton`
   - Build command: `npm ci && npm run build`
   - Start command: `node dist/index.js --run`

3. **Set Environment Variables**
   Same as Railway

4. **Get URL**
   Render provides: `https://automaton.onrender.com`

### Opsi 3: Fly.io (Global Edge)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
cd Bismillah/automaton
flyctl launch
flyctl deploy
```

### Opsi 4: VPS (Full Control)

```bash
# SSH ke VPS
ssh user@your-vps.com

# Clone repo
git clone your-repo.git
cd repo/Bismillah/automaton

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install dependencies
npm ci

# Build
npm run build

# Run with PM2
npm install -g pm2
pm2 start dist/index.js --name automaton -- --run
pm2 save
pm2 startup
```

## Komunikasi Bot ↔ Automaton

### Bot Side (Python)

```python
# app/automaton_manager.py
import os
import requests

AUTOMATON_URL = os.getenv('CONWAY_API_URL')

def call_automaton(task):
    response = requests.post(
        f"{AUTOMATON_URL}/api/task",
        json={"task": task},
        headers={"Authorization": f"Bearer {CONWAY_API_KEY}"}
    )
    return response.json()
```

### Automaton Side (Node.js)

Automaton sudah punya HTTP API built-in di `src/telegram/` atau bisa tambah Express endpoint.

## Cost Comparison

### Railway (2 Services)
- Bot: $5/month (Hobby plan)
- Automaton: $5/month (Hobby plan)
- **Total: $10/month**

### Render (Free Tier)
- Bot: Free (sleeps after 15min inactive)
- Automaton: Free (sleeps after 15min inactive)
- **Total: $0/month** (with sleep)

### Fly.io
- Bot: ~$3/month (shared CPU)
- Automaton: ~$3/month (shared CPU)
- **Total: $6/month**

### VPS (DigitalOcean/Linode)
- 1 Droplet: $6/month (1GB RAM)
- Run both on same VPS
- **Total: $6/month**

## Recommended Setup

**For Production:**
- Bot: Railway ($5/month)
- Automaton: Railway ($5/month)
- Total: $10/month, 24/7 uptime, no sleep

**For Testing:**
- Bot: Render Free
- Automaton: Render Free
- Total: $0/month, sleeps after 15min

**For Budget:**
- Both: VPS $6/month
- Full control, 24/7 uptime

## Monitoring

### Health Checks

Bot:
```bash
curl https://bot-url.railway.app/health
```

Automaton:
```bash
curl https://automaton-url.railway.app/health
```

### Logs

Railway Dashboard → Logs tab untuk masing-masing service

## Troubleshooting

### Bot can't reach Automaton
- Check `CONWAY_API_URL` env var
- Check Automaton is running
- Check network/firewall

### Automaton not responding
- Check logs for errors
- Check CONWAY_API_KEY valid
- Restart service

## Next Steps

1. ✅ Deploy bot-only (sekarang)
2. ⏳ Test bot di Telegram
3. ⏳ Deploy Automaton terpisah
4. ⏳ Set CONWAY_API_URL di bot
5. ⏳ Test integration

---

**Recommendation:** Deploy Automaton di Railway service terpisah untuk consistency.
