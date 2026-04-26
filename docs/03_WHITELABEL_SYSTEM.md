# Sistem White Label — Dokumentasi Teknis

## Gambaran Umum

Sistem White Label memungkinkan pihak ketiga (WL Owner) menjalankan bot Telegram trading mereka sendiri yang bertenaga mesin CryptoMentor, dengan lisensi berbasis langganan bulanan yang dikelola secara terpusat.

Arsitektur terdiri dari dua bagian utama:
- **License Server** — server pusat yang mengelola lisensi, billing, dan deposit
- **Whitelabel Bot** — instance bot yang berjalan di sisi WL Owner

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│                    Central Server (VPS)                  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ License API  │  │ Billing Cron │  │Deposit Monitor│  │
│  │  (port 8080) │  │ (daily 00:00)│  │ (BSC polling) │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                           │                             │
│                    ┌──────▼──────┐                      │
│                    │  Supabase   │                      │
│                    │  (Pusat)    │                      │
│                    └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
                           │
                    License API (HTTP)
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  Whitelabel Bot (VPS WL)                 │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ License Guard│  │  License     │  │  Supabase    │  │
│  │ (startup +   │  │  Middleware  │  │  (Isolated)  │  │
│  │  periodic)   │  │  (per-update)│  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Komponen License Server

### 1. License API (`license_server/license_api.py`)

FastAPI app yang berjalan di port 8080.

**Endpoint:**

| Method | Path | Deskripsi |
|--------|------|-----------|
| POST | `/api/license/check` | Validasi lisensi WL |

**Request body `/api/license/check`:**
```json
{
  "wl_id": "uuid-v4",
  "secret_key": "uuid-v4"
}
```

**Response:**
```json
{
  "valid": true,
  "expires_in_days": 25,
  "balance": 40.00,
  "warning": false,
  "status": "active"
}
```

**Status codes:**
- `200` — OK (valid atau tidak valid, lihat field `valid`)
- `400` — `secret_key` bukan UUID v4
- `401` — `secret_key` tidak cocok
- `404` — `wl_id` tidak ditemukan
  `429` — Rate limit (60 req/menit per `wl_id`)
- `503` — Supabase error

---

### 2. License Manager (`license_server/license_manager.py`)

CRUD layer ke Supabase pusat. Semua operasi write menggunakan service role key.

**Method utama:**

| Method | Deskripsi |
|--------|-----------|
| `register_wl(admin_telegram_id, monthly_fee)` | Daftarkan WL baru, generate deposit address via HD Wallet |
| `get_license(wl_id)` | Ambil data lisensi |
| `credit_balance(wl_id, amount, tx_hash, block_number)` | Kredit deposit (idempotent via `tx_hash` UNIQUE) |
| `debit_billing(wl_id)` | Trigger billing via Supabase RPC `process_billing` |

---

### 3. Billing Cron (`license_server/billing_cron.py`)

APScheduler job yang berjalan setiap hari pukul 00:00 UTC.

**Alur billing:**
1. Query semua WL dengan `status IN ('active', 'grace_period')` dan `expires_at <= NOW()`
2. Untuk WL yang sudah `grace_period` lebih dari 3 hari → suspend
3. Untuk WL lainnya → jalankan `debit_billing()`
4. Jika billing gagal (saldo kurang) → set `grace_period`, kirim notifikasi Telegram ke WL Owner
5. Jika billing sukses → perpanjang `expires_at` +30 hari

**Status lifecycle:**

```
inactive → active (setelah deposit pertama)
active → grace_period (billing gagal, saldo kurang)
grace_period → active (billing berhasil setelah top-up)
grace_period → suspended (>3 hari tidak top-up)
suspended → active (setelah deposit masuk dan billing berhasil)
```

---

### 4. Deposit Monitor (`license_server/deposit_monitor.py`)

Asyncio polling loop yang memantau deposit USDT BEP-20 via Moralis API.

**Cara kerja:**
- Poll setiap 5 menit
- Cek semua deposit address WL yang `status IN ('active', 'grace_period', 'inactive')`
- Deteksi transfer USDT ke deposit address masing-masing WL
- Panggil `credit_balance()` (idempotent — skip jika `tx_hash` sudah diproses)
- Kirim notifikasi Telegram ke WL Owner jika deposit berhasil dikreditkan

**Konfigurasi:**
- `BSCSCAN_API_KEY` / `MORALIS_API_KEY` — API key Moralis
- `BOT_TOKEN` — token bot pusat untuk notifikasi
- USDT contract: `0x55d398326f99059fF775485246999027B3197955` (BSC)

---

## Komponen Whitelabel Bot

### 1. License Guard (`Whitelabel #1/app/license_guard.py`)

Validasi lisensi saat startup dan secara periodik.

**Alur startup:**
1. Jika `LICENSE_API_URL` kosong → jalankan dalam **DEV MODE** (skip license check)
2. Panggil License API `/api/license/check`
3. Jika API berhasil → simpan ke cache, lanjutkan jika `valid: true`
4. Jika API tidak bisa dijangkau → fallback ke cache (max 48 jam)
5. Jika cache > 48 jam dan API down → halt bot

**Cache:**
- Disimpan di `data/license_cache.json`
- Max age: 48 jam
- Berisi: `valid`, `status`, `expires_in_days`, `balance`, `warning`, `cached_at`

**Periodic check:**
- Setiap 24 jam via `periodic_check_loop()`
- Jika gagal → raise `RuntimeError` untuk trigger shutdown

**Notifikasi admin:**
- Saat lisensi suspended → kirim pesan ke semua `ADMIN_IDS` (hanya 1x, tracked via flag file)
- Saat API down tanpa cache → kirim notifikasi
- Saat hampir expired (`expires_in_days < 5`) → kirim warning

---

### 2. License Middleware (`Whitelabel #1/app/license_middleware.py`)

Telegram handler yang berjalan sebelum semua handler lain (group=-1).

**Cara kerja:**
- Check license setiap 60 detik (cached untuk mengurangi API calls)
- Admin (`ADMIN_IDS`) selalu dilewatkan (bypass)
- Jika license tidak valid → block user, kirim pesan "Bot Temporarily Unavailable"
- Jika license valid → lanjutkan ke handler berikutnya

---

### 3. Bot Entry Point (`Whitelabel #1/bot.py`)

Urutan startup:
1. Inject API keys provider (isolated dari bot utama)
2. `LicenseGuard.startup_check()` — halt jika gagal
3. Register `LicenseMiddleware` di group=-1
4. Register semua command handler
5. Start `periodic_check_loop()` sebagai asyncio task

---

## Database Schema

### Supabase Pusat (License Server)

**Tabel `wl_licenses`:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `wl_id` | UUID PK | ID unik WL |
| `balance_usdt` | DECIMAL | Saldo deposit |
| `expires_at` | TIMESTAMPTZ | Tanggal kadaluarsa lisensi |
| `status` | ENUM | `active`, `grace_period`, `suspended`, `inactive` |
| `monthly_fee` | DECIMAL | Biaya bulanan (default $10) |
| `deposit_address` | VARCHAR(42) | Alamat BSC untuk deposit |
| `deposit_index` | INTEGER UNIQUE | Index HD Wallet |
| `secret_key` | UUID UNIQUE | Kunci autentikasi WL |
| `admin_telegram_id` | BIGINT | Telegram ID WL Owner |

**Tabel `wl_deposits`:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `tx_hash` | VARCHAR(66) UNIQUE | Hash transaksi (idempotency key) |
| `amount_usdt` | DECIMAL | Jumlah deposit |
| `block_number` | BIGINT | Block BSC |
| `confirmed_at` | TIMESTAMPTZ | Waktu konfirmasi |

**Tabel `wl_billing_history`:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `status` | ENUM | `success` atau `failed` |
| `balance_before/after` | DECIMAL | Saldo sebelum/sesudah billing |
| `expires_at_before/after` | TIMESTAMPTZ | Tanggal kadaluarsa sebelum/sesudah |

**Supabase RPC:**
- `process_billing(p_wl_id)` — atomic billing dengan row lock
- `increment_balance(p_wl_id, p_amount)` — atomic balance update

### Supabase WL (Isolated per WL)

Setiap WL memiliki Supabase instance sendiri dengan tabel:
- `users` — data user Telegram
- `user_api_keys` — API key exchange (enkripsi AES-256-GCM)
- `autotrade_sessions` — sesi trading aktif
- `autotrade_trades` — riwayat trade

---

## Konfigurasi Environment

### License Server (`.env`)

```env
SUPABASE_URL=https://...supabase.co
SUPABASE_SERVICE_KEY=...
MASTER_SEED_MNEMONIC=...   # HD Wallet untuk generate deposit address
BOT_TOKEN=...              # Bot pusat untuk notifikasi
BSCSCAN_API_KEY=...        # Moralis API key
LICENSE_API_PORT=8080
```

### Whitelabel Bot (`.env`)

```env
# Telegram
BOT_TOKEN=...
ADMIN1=...

# Supabase (instance terpisah)
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# License
WL_ID=...
WL_SECRET_KEY=...
LICENSE_API_URL=http://CENTRAL_VPS_IP:8080

# Bot
BOT_NAME=CryptoMentor AI
BOT_TAGLINE=Your AI Crypto Trading Assistant
WELCOME_CREDITS=100
ENCRYPTION_KEY=...
```

---

## Cara Mendaftarkan WL Baru

1. Jalankan script registrasi di Central Server:
   ```bash
   cd license_server
   python register_wl.py
   ```
2. Masukkan Telegram ID admin WL Owner
3. Script akan output: `WL_ID`, `SECRET_KEY`, `DEPOSIT_ADDRESS`
4. Isi nilai tersebut ke `.env` Whitelabel Bot
5. Berikan `DEPOSIT_ADDRESS` ke WL Owner untuk top-up saldo

---

## Perbedaan Bot Utama vs Whitelabel

| Fitur | Bot Utama (Bismillah) | Whitelabel |
|-------|-----------------------|------------|
| Signal Generation | ✅ | ❌ |
| AI Analysis | ✅ | ❌ |
| AutoTrade | ✅ | ✅ |
| License System | ❌ | ✅ |
| Database | Shared | Isolated |
| API Rate Limits | Shared | Isolated |
| Multi-exchange | ✅ | Bitunix only |

---

## Deployment

### Central Server

```bash
# License API
uvicorn license_server.license_api:app --host 0.0.0.0 --port 8080

# Billing Cron (systemd service terpisah)
python -m license_server.billing_cron

# Deposit Monitor (systemd service terpisah)
python -m license_server.deposit_monitor
```

### Whitelabel Bot

```bash
cd "Whitelabel #1"
python bot.py
```

Untuk production, gunakan systemd service. Lihat `Whitelabel #1/README_DEPLOYMENT.md` untuk detail lengkap.

---

## Troubleshooting

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|----------------------|--------|
| Bot tidak start | License check gagal | Cek `WL_ID`, `WL_SECRET_KEY`, koneksi ke `LICENSE_API_URL` |
| Bot DEV MODE | `LICENSE_API_URL` kosong | Set `LICENSE_API_URL` di `.env` |
| User diblokir | License suspended | Top-up saldo USDT ke `DEPOSIT_ADDRESS` |
| Deposit tidak terdeteksi | Moralis API error | Cek `BSCSCAN_API_KEY`, pastikan gunakan BSC network |
| Cache expired | API down > 48 jam | Perbaiki koneksi ke License Server |
