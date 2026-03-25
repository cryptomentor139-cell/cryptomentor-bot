-- ============================================================
-- Whitelabel #1 — Supabase Schema
-- Jalankan di SQL Editor Supabase project WL#1
-- ============================================================

-- Users
CREATE TABLE IF NOT EXISTS users (
    id              BIGSERIAL PRIMARY KEY,
    telegram_id     BIGINT UNIQUE NOT NULL,
    username        TEXT,
    full_name       TEXT,
    credits         NUMERIC DEFAULT 0,
    is_premium      BOOLEAN DEFAULT FALSE,
    is_lifetime     BOOLEAN DEFAULT FALSE,
    premium_until   TIMESTAMPTZ,
    referral_code   TEXT UNIQUE,
    referred_by     BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys (enkripsi AES-256-GCM di aplikasi)
CREATE TABLE IF NOT EXISTS user_api_keys (
    telegram_id     BIGINT PRIMARY KEY,
    exchange        TEXT DEFAULT 'bitunix',
    api_key         TEXT NOT NULL,
    api_secret_enc  TEXT NOT NULL,
    key_hint        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- AutoTrade Sessions
CREATE TABLE IF NOT EXISTS autotrade_sessions (
    telegram_id       BIGINT PRIMARY KEY,
    bitunix_uid       TEXT,
    status            TEXT DEFAULT 'pending_verification',
    initial_deposit   NUMERIC DEFAULT 0,
    current_balance   NUMERIC DEFAULT 0,
    total_profit      NUMERIC DEFAULT 0,
    leverage          INTEGER DEFAULT 10,
    margin_mode       TEXT DEFAULT 'cross',
    started_at        TIMESTAMPTZ,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Trade History
CREATE TABLE IF NOT EXISTS autotrade_trades (
    id                BIGSERIAL PRIMARY KEY,
    telegram_id       BIGINT,
    symbol            TEXT,
    side              TEXT,
    entry_price       NUMERIC,
    exit_price        NUMERIC,
    qty               NUMERIC,
    leverage          INTEGER,
    tp_price          NUMERIC,
    sl_price          NUMERIC,
    pnl_usdt          NUMERIC,
    status            TEXT DEFAULT 'open',
    confidence        INTEGER,
    rr_ratio          NUMERIC,
    trend_1h          TEXT,
    market_structure  TEXT,
    rsi_15            NUMERIC,
    atr_pct           NUMERIC,
    entry_reasons     JSONB,
    loss_reasoning    TEXT,
    is_flip           BOOLEAN DEFAULT FALSE,
    order_id          TEXT,
    opened_at         TIMESTAMPTZ DEFAULT NOW(),
    closed_at         TIMESTAMPTZ
);

-- Index untuk query cepat
CREATE INDEX IF NOT EXISTS idx_trades_telegram_id ON autotrade_trades(telegram_id);
CREATE INDEX IF NOT EXISTS idx_trades_status ON autotrade_trades(status);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
