# 🚀 DEPLOY BOT SEKARANG (Bot-Only)

## Status

✅ Rollback complete
✅ Bot-only configuration ready
✅ Stable deployment config

## Deploy Command

```bash
cd Bismillah
git add .
git commit -m "rollback: stable bot-only deployment"
git push origin main
```

## What Will Happen

Railway akan:
1. ✅ Detect Python project
2. ✅ Install requirements.txt
3. ✅ Run `python main.py`
4. ✅ Bot online dalam 2-3 menit

## Verify Deployment

### 1. Check Railway Logs
```
Starting bot...
Bot started successfully
Polling for updates...
```

### 2. Test di Telegram
```
/start
```

Bot harus respond dengan welcome message.

### 3. Test Commands
```
/help
/signal
/autosignal
```

Semua harus berfungsi normal.

## Environment Variables Checklist

Pastikan di Railway:
- [ ] TELEGRAM_BOT_TOKEN
- [ ] SUPABASE_URL
- [ ] SUPABASE_KEY
- [ ] ENCRYPTION_KEY
- [ ] DEEPSEEK_API_KEY (optional)
- [ ] CEREBRAS_API_KEY (optional)

## Automaton Nanti

Setelah bot stable, deploy Automaton terpisah:
- Baca: `AUTOMATON_SEPARATE_DEPLOY_GUIDE.md`

## Rollback Reason

Combined deployment (Bot + Automaton dalam 1 service) terlalu kompleks untuk Railway Nixpacks build system. Errors:
- Nixpacks derivation issues
- Multi-language build conflicts
- Build time exceeded limits

## Files Changed

- ✅ `Procfile` → `web: python main.py`
- ✅ `railway.json` → Simple Python config
- ✅ `railway.toml` → Deleted
- ✅ Combined scripts → Kept for local use

## Local Testing (Optional)

Test bot locally sebelum deploy:

```bash
cd Bismillah
python main.py
```

Tekan Ctrl+C untuk stop.

## Monitoring

After deploy:
- Railway Dashboard → Metrics
- Check CPU usage (should be low)
- Check RAM usage (should be ~150-200MB)
- Check logs for errors

## Support

Jika ada masalah:
1. Check Railway logs
2. Check environment variables
3. Test bot commands di Telegram
4. Check Supabase connection

---

**READY TO DEPLOY!** 🚀

Run:
```bash
git add . && git commit -m "rollback: bot-only stable" && git push
```
