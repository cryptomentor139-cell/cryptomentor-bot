# 🔄 ROLLBACK: Bot-Only Deployment

## Keputusan

Setelah beberapa kali percobaan, combined deployment (Bot + Automaton dalam 1 service) **terlalu kompleks** untuk Railway's Nixpacks build system.

## Masalah yang Ditemui

1. **Nixpacks build errors** - Derivation issues dengan multi-language setup
2. **Complex dependencies** - Python + Node.js dalam 1 container sulit di-manage
3. **Build time terlalu lama** - Melebihi Railway free tier limits

## Solusi: Rollback ke Bot-Only

Kembali ke deployment yang sudah terbukti stabil:
- ✅ Bot Telegram (Python) - STABLE
- ❌ Automaton - Akan di-deploy terpisah nanti (Opsi 2)

## File yang Dirollback

- ✅ `Procfile` → `web: python main.py`
- ✅ `railway.json` → startCommand: `python main.py`
- ✅ `railway.toml` → DELETED
- ✅ Combined scripts → Tetap ada untuk local testing

## Deploy Sekarang

```bash
cd Bismillah
git add .
git commit -m "rollback: bot-only deployment (stable)"
git push origin main
```

Railway akan deploy bot Python saja (sudah pasti jalan).

## Untuk Automaton

### Opsi A: Deploy Terpisah di Railway (Recommended)
1. Buat Railway service baru
2. Connect ke folder `Bismillah/automaton/`
3. Set environment variables untuk Automaton
4. Deploy independent

### Opsi B: Deploy Automaton di Platform Lain
- Render.com
- Fly.io
- Vercel (untuk API)
- Heroku

### Opsi C: Local Only
Jalankan Automaton di local machine:
```bash
cd Bismillah/automaton
npm install
npm run build
npm start
```

## Bot Sudah Jalan

Setelah rollback, bot Telegram akan:
- ✅ Respond ke commands
- ✅ Handle user interactions
- ✅ Connect ke Supabase
- ✅ Semua fitur bot berfungsi normal

## Automaton Integration

Bot sudah punya integration code untuk Automaton di:
- `app/automaton_manager.py`
- `app/handlers_automaton.py`
- `app/automaton_agent_bridge.py`

Tinggal set `CONWAY_API_URL` ke Automaton service yang terpisah.

## Lesson Learned

Combined deployment bagus untuk:
- ✅ Docker Compose (local)
- ✅ Kubernetes
- ✅ VPS dengan full control

Tidak cocok untuk:
- ❌ Railway Nixpacks (terlalu restrictive)
- ❌ Heroku buildpacks
- ❌ Platform PaaS dengan auto-detection

## Next Steps

1. **Deploy bot-only** (sekarang)
2. **Test bot** di Telegram
3. **Deploy Automaton terpisah** (nanti)
4. **Connect keduanya** via HTTP API

---

**Status:** ROLLBACK COMPLETE ✅
**Bot:** READY TO DEPLOY
**Automaton:** DEPLOY SEPARATELY LATER
