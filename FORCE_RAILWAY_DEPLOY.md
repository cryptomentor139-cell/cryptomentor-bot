# Force Railway Deploy - Manual Steps

## Railway Tidak Auto-Deploy

Railway tidak otomatis deploy setelah push ke GitHub. Ini bisa terjadi karena:
1. Railway belum terhubung ke GitHub repo
2. Auto-deploy disabled
3. Perlu manual trigger

## Cara Force Deploy

### Option 1: Manual Redeploy (TERCEPAT)
1. Buka Railway Dashboard: https://railway.app
2. Pilih project "industrious-dream"
3. Pilih service "web" atau "production"
4. Klik tab "Deployments"
5. Klik tombol "Deploy" di kanan atas
6. Atau klik "..." pada deployment terakhir → "Redeploy"

### Option 2: Connect GitHub (untuk auto-deploy di masa depan)
1. Railway Dashboard → Settings tab
2. Scroll ke "Source"
3. Klik "Connect GitHub"
4. Pilih repository: cryptomentor139-cell/cryptomentor-bot
5. Pilih branch: main
6. Save
7. Railway akan auto-deploy setiap kali ada push ke GitHub

### Option 3: Deploy via Railway CLI
```bash
# Install Railway CLI (jika belum)
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

## Cek Status Deployment

Setelah deploy:
1. Klik tab "Deployments"
2. Klik deployment terbaru
3. Klik tab "Deploy Logs"
4. Seharusnya muncul:
```
🚀 Starting CryptoMentor AI Bot...
✅ Bot initialized with 2 admin(s)
...
🚀 CryptoMentor AI Bot is running...
```

## Environment Variables

Pastikan Railway punya env vars ini (tab Variables):
```
TELEGRAM_BOT_TOKEN=8025048597:AAEng-pPhDmTKsiRb1BtJ50P8CC-FamGCb4
ADMIN1=1187119989
ADMIN2=7079544380

# Database
PGHOST=ep-divine-wind-aes4g3k8.c-2.us-east-2.aws.neon.tech
PGDATABASE=neondb
PGUSER=neondb_owner
PGPASSWORD=npg_PXo7pTdgJ4ny
PGPORT=5432

# AI Keys
DEEPSEEK_API_KEY=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
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=google/gemini-flash-1.5
CEREBRAS_API_KEY=csk-8ee6jd8ekjcwyhtdx6yk3r3dhkewe88t9mv54k5yce295p3n

# Automaton
CONWAY_API_URL=https://automaton-production-a899.up.railway.app
CONWAY_API_KEY=cnwy_k_HeT-F6vsVC_z6pmhYbBOyo1UJHtFhXyr
ENCRYPTION_KEY=Gq-ymFPUufXwh-OvL4HM2BnrB--_WBecaUmwuEpm_KI=
CENTRALIZED_WALLET_ADDRESS=0x63116672bef9f26fd906cd2a57550f7a13925822

# Other
SESSION_SECRET=FZ+1sD4r0TLgs7r7vs1bZtPNerUjVDwtdgFM0DQ8TAJcKbs6wwGd6rSSZFdtIYGjsCoG4ANGf6+rdW+0tz6/XA==
WELCOME_CREDITS=100
USE_LEGACY_FUTURES_SIGNALS=true
```

## Test Bot

Setelah deploy selesai:
```
/start
/menu
/help
/price btc
```

## Troubleshooting

### Jika deploy gagal:
1. Cek Build Logs untuk error saat install dependencies
2. Cek Deploy Logs untuk error saat startup
3. Pastikan requirements.txt lengkap
4. Pastikan Python version compatible (3.11)

### Jika bot tidak merespon:
1. Cek logs untuk error messages
2. Pastikan TELEGRAM_BOT_TOKEN benar
3. Test bot token dengan BotFather
4. Cek apakah bot sudah running (logs harus show "Polling for updates...")
