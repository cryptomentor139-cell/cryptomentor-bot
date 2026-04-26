-- ============================================================
-- Marketing AI Agent — Database Schema
-- marketing/agent/db/setup_marketing.sql
-- ============================================================

-- 1. Tabel kampanye (harus dibuat sebelum marketing_content karena di-referensi)
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_number     INTEGER NOT NULL,
    market_sentiment VARCHAR(20),
    campaign_angle   TEXT,
    target_persona   VARCHAR(30),
    emotion_trigger  VARCHAR(20),
    strategist_notes TEXT,
    analyst_feedback JSONB,
    status           VARCHAR(20) DEFAULT 'active',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    completed_at     TIMESTAMPTZ
);

-- 2. Tabel konten marketing
CREATE TABLE IF NOT EXISTS marketing_content (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id      UUID REFERENCES marketing_campaigns(id),
    content_type     VARCHAR(20) NOT NULL CHECK (content_type IN ('feed', 'reels', 'carousel', 'threads')),
    topic_category   VARCHAR(30) NOT NULL CHECK (topic_category IN ('product_highlight', 'crypto_education', 'trading_psychology', 'market_update', 'community')),
    target_persona   VARCHAR(30) CHECK (target_persona IN ('Beginner', 'Intermediate_Trader', 'Fear_Driven', 'Greed_Driven')),
    emotion_trigger  VARCHAR(20) CHECK (emotion_trigger IN ('fear', 'greed', 'security')),
    hook             TEXT NOT NULL,
    caption          TEXT NOT NULL,
    hashtags         TEXT[],
    image_path       TEXT,
    video_path       TEXT,
    pas_problem      TEXT,
    pas_agitate      TEXT,
    pas_solution     TEXT,
    pas_cta          TEXT,
    status           VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'published', 'failed')),
    rejection_reason TEXT,
    ai_provider      VARCHAR(20),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    approved_at      TIMESTAMPTZ,
    published_at     TIMESTAMPTZ
);

-- 3. Tabel publikasi per platform
CREATE TABLE IF NOT EXISTS marketing_publications (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id       UUID REFERENCES marketing_content(id),
    platform         VARCHAR(20) NOT NULL CHECK (platform IN ('instagram', 'facebook', 'tiktok', 'threads')),
    platform_post_id TEXT,
    post_url         TEXT,
    scheduled_at     TIMESTAMPTZ,
    published_at     TIMESTAMPTZ,
    status           VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'published', 'failed', 'retrying')),
    retry_count      INTEGER DEFAULT 0,
    error_message    TEXT,
    ab_test_variant  VARCHAR(5) CHECK (ab_test_variant IN ('A', 'B', NULL))
);

-- 4. Tabel lead (hanya Telegram)
CREATE TABLE IF NOT EXISTS marketing_leads (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_platform      VARCHAR(20),
    source_content_id    UUID REFERENCES marketing_content(id),
    contact_id           TEXT NOT NULL,  -- telegram_id sebagai string
    contact_type         VARCHAR(20) DEFAULT 'telegram' CHECK (contact_type IN ('telegram')),
    telegram_chat_id     BIGINT,         -- Telegram chat ID untuk Sales Agent
    persona              VARCHAR(30) CHECK (persona IN ('Beginner', 'Intermediate_Trader', 'Fear_Driven', 'Greed_Driven')),
    segment              VARCHAR(10) DEFAULT 'Cold' CHECK (segment IN ('Cold', 'Warm', 'Hot')),
    status               VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'engaged', 'converted', 'opted_out', 'inactive')),
    followup_count       INTEGER DEFAULT 0,
    last_interaction_at  TIMESTAMPTZ,
    converted_at         TIMESTAMPTZ,
    notes                TEXT,
    created_at           TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Tabel interaksi sales
CREATE TABLE IF NOT EXISTS marketing_lead_interactions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id          UUID REFERENCES marketing_leads(id),
    direction        VARCHAR(10) CHECK (direction IN ('outbound', 'inbound')),
    message_type     VARCHAR(30),  -- followup, objection_handling, closing, re_engagement
    message_content  TEXT,
    objection_type   VARCHAR(30),  -- takut_scam, bisa_rugi, worth_it, ribet_setup, gratis_beneran
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Tabel analytics
CREATE TABLE IF NOT EXISTS marketing_analytics (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id    UUID REFERENCES marketing_publications(id),
    content_id        UUID REFERENCES marketing_content(id),
    platform          VARCHAR(20),
    measured_at       TIMESTAMPTZ DEFAULT NOW(),
    likes             INTEGER DEFAULT 0,
    comments          INTEGER DEFAULT 0,
    shares            INTEGER DEFAULT 0,
    saves             INTEGER DEFAULT 0,
    reach             INTEGER DEFAULT 0,
    impressions       INTEGER DEFAULT 0,
    clicks            INTEGER DEFAULT 0,
    ctr               DECIMAL(5,4),   -- Click-Through Rate (0.0000 - 1.0000)
    engagement_rate   DECIMAL(5,4),
    leads_generated   INTEGER DEFAULT 0,
    conversion_rate   DECIMAL(5,4),
    scale_decision    BOOLEAN DEFAULT FALSE,
    kill_decision     BOOLEAN DEFAULT FALSE
);

-- 7. Tabel A/B Tests
CREATE TABLE IF NOT EXISTS marketing_ab_tests (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id           UUID REFERENCES marketing_campaigns(id),
    test_variable         VARCHAR(30) NOT NULL,  -- hook_type, content_format, post_time, caption_length
    variant_a_content_id  UUID REFERENCES marketing_content(id),
    variant_b_content_id  UUID REFERENCES marketing_content(id),
    started_at            TIMESTAMPTZ DEFAULT NOW(),
    evaluation_at         TIMESTAMPTZ,           -- started_at + 24 jam
    winner_variant        VARCHAR(5) CHECK (winner_variant IN ('A', 'B', NULL)),
    variant_a_ctr         DECIMAL(5,4),
    variant_b_ctr         DECIMAL(5,4),
    status                VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'killed'))
);

-- 8. Tabel audience personas
CREATE TABLE IF NOT EXISTS marketing_audience_personas (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_type         VARCHAR(30) NOT NULL CHECK (persona_type IN ('Beginner', 'Intermediate_Trader', 'Fear_Driven', 'Greed_Driven')),
    pain_points          TEXT[],
    emotion_trigger      VARCHAR(20),
    effective_hooks      TEXT[],
    effective_formats    TEXT[],
    avg_conversion_rate  DECIMAL(5,4),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Tabel riset topik
CREATE TABLE IF NOT EXISTS marketing_research_topics (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic            TEXT NOT NULL,
    category         VARCHAR(30) NOT NULL,
    relevance_score  DECIMAL(3,2),
    used_at          TIMESTAMPTZ,
    platform_used    TEXT[],
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Indexes untuk query yang sering
-- ============================================================

-- Status konten — dipakai Distribution Agent untuk ambil konten approved
CREATE INDEX IF NOT EXISTS idx_marketing_content_status
    ON marketing_content(status);

-- Telegram chat ID — dipakai Sales Agent untuk lookup lead
CREATE INDEX IF NOT EXISTS idx_marketing_leads_telegram_chat_id
    ON marketing_leads(telegram_chat_id);

-- content_id + platform — dipakai Distribution Agent & Analyst
CREATE INDEX IF NOT EXISTS idx_marketing_publications_content_platform
    ON marketing_publications(content_id, platform);
