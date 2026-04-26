# Whitelabel #1 — CryptoMentor AI (B2B)

Instance whitelabel terpisah dari CryptoMentor utama.
Database, bot token, dan admin dikelola secara independen.

## Setup

1. Copy `.env.example` → `.env` dan isi semua nilai
2. Jalankan SQL di `db/setup.sql` pada Supabase instance kamu
3. Install dependencies: `pip install -r requirements.txt`
4. Jalankan bot: `python bot.py`

## Struktur

```
app/        → core logic (handlers, engine, providers)
data/       → state files runtime
db/         → SQL schema Supabase
```
