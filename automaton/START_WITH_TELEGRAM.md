# Start Automaton dengan Telegram Bot

## Cara Jalankan dengan Telegram

### 1. Stop Automaton yang Sekarang
```bash
taskkill /F /IM node.exe
```

### 2. Jalankan dengan Telegram Mode
```bash
# Set environment variable untuk enable Telegram
set TELEGRAM_BOT_TOKEN=7733779516:AAE66rempo8VKkDj-m6t3tdfr9Lyu0ClnlU
set TELEGRAM_CREATOR_ID=1187119989

# Jalankan automaton
node dist/index.js --run
```

### 3. Cari Bot di Telegram

1. Buka Telegram
2. Search: `@` + bot username (cek di @BotFather)
3. Atau klik link: `https://t.me/YourBotUsername`
4. Klik "Start"

### 4. Commands yang Bisa Digunakan

```
/start - Start conversation
/status - System status
/credits - Financial status  
/help - Show all commands
/logs - Recent activity logs

Atau chat biasa - automaton akan respond!
```

## Alternatif: Deploy ke Railway untuk 24/7

Kalau mau automaton jalan 24/7 dengan Telegram:

1. Push code ke GitHub
2. Deploy ke Railway
3. Add environment variables:
   - `CONWAY_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CREATOR_ID`
   - `DB_PATH=/data/automaton.db`
4. Add volume `/data`
5. Deploy!

Automaton akan jalan 24/7 dan kamu bisa control via Telegram dari mana saja.

## Bot Token Info

- Token: `7733779516:AAE66rempo8VKkDj-m6t3tdfr9Lyu0ClnlU`
- Creator ID: `1187119989`
- Bot sudah configured di `.env`

## Cek Bot Username

Untuk tahu bot username, buka @BotFather di Telegram dan cek bot yang punya token di atas.
