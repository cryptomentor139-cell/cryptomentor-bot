# 🔧 Fix Bot Token Conflict - Automaton vs Bot

## ❌ Masalah

Kedua service di Railway punya `TELEGRAM_BOT_TOKEN` yang sama:
- **Bot Service** → Butuh token untuk terima message dari Telegram
- **Automaton Service** → TIDAK butuh token (pure API service)

Ini menyebabkan konflik karena Telegram hanya bisa connect ke 1 instance.

---

## ✅ Solusi: Hapus Token dari Automaton

### Langkah 1: Buka Railway Dashboard Automaton

1. Login ke https://railway.app
2. Pilih service **Automaton** (automaton-production-a899)
3. Klik tab **"Variables"**

### Langkah 2: Hapus TELEGRAM_BOT_TOKEN

1. Cari variable `TELEGRAM_BOT_TOKEN`
2. Klik icon **trash/delete** di sebelah kanan variable
3. Confirm delete
4. Automaton akan auto-restart

### Langkah 3: Verify Automaton Masih Jalan

Check Railway logs untuk Automaton:

**Expected logs (TANPA error):**
```
Conway Automaton v0.1.0
Initializing...
✓ Database initialized
✓ Wallet loaded
✓ API client connected
✓ Automaton running
Listening on port 3000
```

**TIDAK akan ada:**
```
✓ Telegram bot connected
```

Karena Automaton memang tidak perlu connect ke Telegram!

---

## 📋 Environment Variables yang Benar

### Bot Service (cryptomentor-bot)

**REQUIRED:**
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
CONWAY_API_URL=https://automaton-production-a899.up.railway.app
SUPABASE_URL=...
SUPABASE_KEY=...
# ... other bot variables
```

### Automaton Service

**REQUIRED:**
```env
CONWAY_API_KEY=sk_...
CONWAY_WALLET_ADDRESS=0x...
NODE_ENV=production
```

**OPTIONAL:**
```env
DATABASE_PATH=/app/data/automaton.db
LOG_LEVEL=info
PORT=3000
```

**TIDAK PERLU:**
```env
TELEGRAM_BOT_TOKEN=...  ← HAPUS INI!
```

---

## 🏗️ Architecture yang Benar

```
┌─────────────────────────────────────────────┐
│                                             │
│  User → Telegram API                        │
│           ↓                                 │
│  Telegram API → Bot Service (Railway)       │
│                  ↓                          │
│  Bot → HTTP Request → Automaton (Railway)   │
│                        ↓                    │
│  Automaton → Conway API (External)          │
│                ↓                            │
│  Conway → Blockchain                        │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Points:**
- ✅ Bot = Telegram interface (needs bot token)
- ✅ Automaton = API service (NO bot token needed)
- ✅ Communication via HTTP (CONWAY_API_URL)

---

## 🧪 Test Setelah Fix

### Test 1: Automaton Health Check

```bash
curl https://automaton-production-a899.up.railway.app/health
```

**Expected:**
```json
{"status":"ok","version":"0.1.0"}
```

### Test 2: Bot Telegram

Kirim command ke bot:
```
/start
/automaton status
```

**Expected:**
- Bot respond normal
- Automaton status ditampilkan
- Tidak ada duplicate response

### Test 3: Check Logs

**Bot Logs:**
```
✓ Bot started
✓ Connected to Telegram
✓ Automaton API connected
```

**Automaton Logs:**
```
✓ Automaton running
✓ API endpoints ready
(NO Telegram connection logs)
```

---

## 🔍 Kenapa Automaton Tidak Perlu Bot Token?

### Automaton adalah Pure API Service

**Automaton provides:**
- REST API endpoints
- Conway integration
- Trading logic
- Wallet management

**Automaton TIDAK:**
- ❌ Terima message dari Telegram
- ❌ Send message ke user
- ❌ Handle bot commands

### Bot adalah Telegram Interface

**Bot handles:**
- ✅ Terima message dari user
- ✅ Send response ke user
- ✅ Handle commands
- ✅ Call Automaton API when needed

---

## 📊 Comparison

| Feature | Bot Service | Automaton Service |
|---------|-------------|-------------------|
| Telegram Token | ✅ REQUIRED | ❌ NOT NEEDED |
| Conway API Key | ❌ Optional | ✅ REQUIRED |
| User Interaction | ✅ Direct | ❌ Via Bot |
| HTTP API | ❌ Client | ✅ Server |
| Database | ✅ Supabase | ✅ SQLite |

---

## 🚨 Common Mistakes

### ❌ WRONG: Both services with bot token
```
Bot Service:
  TELEGRAM_BOT_TOKEN=123456:ABC...

Automaton Service:
  TELEGRAM_BOT_TOKEN=123456:ABC...  ← CONFLICT!
```

**Result:** Bot tidak respond atau respond ganda

### ✅ CORRECT: Only bot has token
```
Bot Service:
  TELEGRAM_BOT_TOKEN=123456:ABC...
  CONWAY_API_URL=https://automaton...

Automaton Service:
  CONWAY_API_KEY=sk_...
  (NO bot token)
```

**Result:** Clean separation, no conflict

---

## 🎯 Action Items

1. ✅ Hapus `TELEGRAM_BOT_TOKEN` dari Automaton service
2. ✅ Verify Automaton masih running (check logs)
3. ✅ Test Automaton health endpoint
4. ✅ Tambah `CONWAY_API_URL` ke Bot service (jika belum)
5. ✅ Test bot commands via Telegram

---

## 📝 Summary

**Problem:** Bot token conflict antara 2 services

**Solution:** Hapus token dari Automaton (tidak perlu)

**Result:** 
- ✅ Bot handle Telegram communication
- ✅ Automaton provide API services
- ✅ Clean microservices architecture
- ✅ No conflicts

---

**Ready to fix?** Hapus `TELEGRAM_BOT_TOKEN` dari Automaton service sekarang! 🚀
