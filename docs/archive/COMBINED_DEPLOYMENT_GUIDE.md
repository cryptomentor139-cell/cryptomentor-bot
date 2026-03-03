# 🚀 Combined Deployment Guide: Bot Telegram + Automaton

## Arsitektur

Proyek ini menjalankan 2 service dalam 1 Railway deployment:

```
Railway Service (512MB RAM, 1 vCPU)
├── Python Bot (main.py)          ← Telegram Bot
└── Node.js Automaton (dist/)     ← Conway Automaton AI
```

## Cara Kerja

1. **start_combined.sh** menjalankan kedua proses secara parallel
2. Bot Python berjalan di background (PID disimpan)
3. Automaton Node.js berjalan di background (PID disimpan)
4. Script menunggu kedua proses dan handle graceful shutdown

## File Penting

- `start_combined.sh` - Script utama untuk menjalankan keduanya
- `Procfile` - Railway entry point: `web: bash start_combined.sh`
- `railway.json` - Konfigurasi Railway deployment
- `nixpacks.toml` - Build configuration untuk Python + Node.js

## Environment Variables yang Dibutuhkan

### Bot Telegram (Python)
```
TELEGRAM_BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ENCRYPTION_KEY=your_encryption_key
# ... (semua env vars bot lainnya)
```

### Automaton (Node.js)
```
CONWAY_API_KEY=your_conway_api_key
CONWAY_WALLET_ADDRESS=your_wallet_address
TELEGRAM_BOT_TOKEN=same_as_above
# ... (env vars automaton lainnya)
```

## Deploy ke Railway

### 1. Push ke GitHub
```bash
cd Bismillah
git add .
git commit -m "Combined deployment: Bot + Automaton"
git push origin main
```

### 2. Connect ke Railway
- Buka Railway dashboard
- Connect repository GitHub
- Railway akan auto-detect `nixpacks.toml`
- Set semua environment variables

### 3. Deploy
Railway akan otomatis:
1. Install Python dependencies
2. Install Node.js dependencies
3. Build Automaton TypeScript
4. Run `start_combined.sh`

## Monitoring

### Cek Logs
```bash
# Di Railway dashboard, lihat logs untuk:
✓ Bot started (PID: xxxx)
✓ Automaton started (PID: xxxx)
Both services are running!
```

### Health Check
Bot Python akan respond ke Telegram commands
Automaton akan respond ke API calls di port yang dikonfigurasi

## Resource Usage

**Estimasi:**
- Python Bot: ~150-200MB RAM
- Node.js Automaton: ~200-250MB RAM
- Total: ~400-450MB (masih dalam 512MB Railway free tier)

## Troubleshooting

### Bot tidak respond
- Cek logs: `Bot started (PID: xxxx)` muncul?
- Cek TELEGRAM_BOT_TOKEN di environment variables
- Cek Supabase connection

### Automaton tidak respond
- Cek logs: `Automaton started (PID: xxxx)` muncul?
- Cek CONWAY_API_KEY di environment variables
- Cek `automaton/dist/` folder ada setelah build

### Out of Memory
- Upgrade Railway plan ke Hobby ($5/month)
- Atau migrate ke Opsi 2 (deploy terpisah)

### Restart Loop
- Cek `restartPolicyMaxRetries: 10` di railway.json
- Lihat error di logs sebelum restart
- Pastikan semua dependencies terinstall

## Local Testing

```bash
cd Bismillah
bash start_combined.sh
```

Tekan Ctrl+C untuk stop kedua service.

## Upgrade ke Opsi 2 (Deploy Terpisah)

Jika traffic tinggi atau resource tidak cukup:

1. Deploy bot Python sebagai service terpisah
2. Deploy Automaton sebagai service terpisah
3. Update komunikasi dari localhost ke HTTP API
4. Set environment variables di masing-masing service

## Support

Jika ada masalah:
1. Cek Railway logs
2. Cek environment variables
3. Test local dulu dengan `bash start_combined.sh`
