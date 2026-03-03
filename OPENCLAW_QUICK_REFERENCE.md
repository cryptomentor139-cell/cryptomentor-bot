# OpenClaw Quick Reference 🚀

## Current Status: DEFAULT MODE ACTIVE ✅

OpenClaw sekarang aktif secara otomatis untuk semua user tanpa perlu command `/openclaw_ask`.

## Cara Kerja

```
User mengirim pesan apa saja → Bot langsung balas dengan AI
```

Tidak perlu command khusus lagi!

## Commands yang Masih Ada

| Command | Fungsi |
|---------|--------|
| `/start` | Welcome message |
| `/menu` | Show menu |
| `/openclaw_balance` | Cek saldo credits |
| `/openclaw_buy` | Beli credits |
| `/openclaw_exit` | Keluar dari OpenClaw mode |
| `/help` | Bantuan |

## Credit System

- **User biasa:** 1 credit per pesan
- **Admin:** GRATIS (unlimited)

## Cek Deployment Railway

1. Buka: https://railway.app
2. Pilih project: `industrious-dream`
3. Pilih service: `web`
4. Cek tab "Deployments"

### Jika Tidak Ada Deploy Baru:

**Cara 1: Deploy Manual**
1. Masuk ke service "web"
2. Klik "Settings"
3. Scroll ke "Deploy"
4. Klik "Deploy Now"

**Cara 2: Trigger via Git**
```bash
cd Bismillah
git commit --allow-empty -m "Force Railway deploy"
git push origin main
```

## Test Bot

### Test 1: Basic Chat
```
Kirim ke bot: "Hello"
Harusnya dapat: "👋 Hi! I'm your AI assistant..."
```

### Test 2: Crypto Query
```
Kirim: "What's Bitcoin price?"
Harusnya dapat: Response dengan harga BTC real-time
```

### Test 3: Credit Check
```
Kirim: /openclaw_balance
Harusnya dapat: Saldo credits kamu
```

## Troubleshooting

### Bot Tidak Respon?
1. Cek Railway logs
2. Pastikan deployment success
3. Cek OPENCLAW_API_KEY di Railway variables

### Error "OpenClaw temporarily unavailable"?
1. Cek API key valid
2. Cek database connection
3. Lihat Railway logs untuk detail error

### User Complain Tidak Bisa Chat?
1. Cek credit balance mereka: `/openclaw_balance`
2. Jika 0 credits, suruh beli: `/openclaw_buy`
3. Admin bisa reset credits via admin panel

## Files yang Diubah

1. `app/openclaw_message_handler.py` - Auto-create session
2. `bot.py` - Route semua pesan ke OpenClaw
3. `OPENCLAW_DEFAULT_MODE.md` - Dokumentasi
4. `test_openclaw_default.py` - Test suite

## Monitoring

### Cek Logs Railway:
```
Look for:
✅ Auto-created OpenClaw session for user {id}
❌ OpenClaw handler error: {error}
```

### Cek Database:
```sql
-- User dengan credits paling banyak
SELECT telegram_id, credits FROM users ORDER BY credits DESC LIMIT 10;

-- User paling aktif di OpenClaw
SELECT user_id, COUNT(*) FROM openclaw_conversations GROUP BY user_id;
```

## Rollback

Jika ada masalah:
```bash
cd Bismillah
git revert HEAD
git push origin main
```

Atau di Railway:
1. Deployments tab
2. Pilih deployment sebelumnya
3. Klik "Redeploy"

## Next Steps

- [ ] Deploy ke Railway (manual atau auto)
- [ ] Test dengan user real
- [ ] Monitor credit usage
- [ ] Optimize response time
- [ ] Add more tools

---

**Last Updated:** 2026-03-04
**Mode:** Default (Auto-Activate)
**Status:** Production Ready
