-- Migration 011: OpenClaw Skills System
-- Purpose: Enable skill upgrades for AI Assistants
-- User can purchase and install skills to enhance assistant capabilities

-- Available Skills Catalog
CREATE TABLE IF NOT EXISTS openclaw_skills_catalog (
    skill_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('crypto', 'trading', 'analysis', 'automation', 'research', 'general')),
    capabilities TEXT[], -- Array of capabilities this skill provides
    system_prompt_addition TEXT, -- Additional system prompt for this skill
    price_credits INTEGER NOT NULL DEFAULT 0, -- One-time purchase price
    is_premium BOOLEAN DEFAULT FALSE,
    version TEXT DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User's Installed Skills
CREATE TABLE IF NOT EXISTS openclaw_assistant_skills (
    id SERIAL PRIMARY KEY,
    assistant_id TEXT NOT NULL REFERENCES openclaw_assistants(assistant_id) ON DELETE CASCADE,
    skill_id TEXT NOT NULL REFERENCES openclaw_skills_catalog(skill_id),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    UNIQUE(assistant_id, skill_id)
);

-- Skill Usage Tracking
CREATE TABLE IF NOT EXISTS openclaw_skill_usage (
    id SERIAL PRIMARY KEY,
    assistant_id TEXT NOT NULL REFERENCES openclaw_assistants(assistant_id) ON DELETE CASCADE,
    skill_id TEXT NOT NULL REFERENCES openclaw_skills_catalog(skill_id),
    conversation_id TEXT REFERENCES openclaw_conversations(conversation_id) ON DELETE CASCADE,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_assistant_skills_assistant ON openclaw_assistant_skills(assistant_id);
CREATE INDEX IF NOT EXISTS idx_assistant_skills_skill ON openclaw_assistant_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_skill_usage_assistant ON openclaw_skill_usage(assistant_id);
CREATE INDEX IF NOT EXISTS idx_skill_usage_skill ON openclaw_skill_usage(skill_id);

-- Insert default free skills
INSERT INTO openclaw_skills_catalog (skill_id, name, description, category, capabilities, system_prompt_addition, price_credits, is_premium) VALUES
('skill_basic_chat', 'Basic Chat', 'Natural conversation and general knowledge', 'general', 
 ARRAY['conversation', 'general_knowledge', 'explanations'], 
 'You can engage in natural conversations and answer general questions.', 
 0, FALSE),

('skill_crypto_analysis', 'Crypto Market Analysis', 'Analyze cryptocurrency markets, trends, and price movements', 'crypto',
 ARRAY['market_analysis', 'price_prediction', 'trend_identification', 'technical_analysis'],
 'You have expertise in cryptocurrency market analysis. You can analyze price charts, identify trends, explain market movements, and provide technical analysis insights. Always remind users that this is not financial advice.',
 500, FALSE),

('skill_trading_signals', 'Trading Signal Generation', 'Generate and explain trading signals for crypto futures', 'trading',
 ARRAY['signal_generation', 'entry_exit_points', 'risk_management', 'position_sizing'],
 'You can generate trading signals with entry/exit points, stop-loss, and take-profit levels. You understand risk management and position sizing. Always emphasize proper risk management.',
 1000, TRUE),

('skill_portfolio_management', 'Portfolio Management', 'Help manage and optimize crypto portfolios', 'trading',
 ARRAY['portfolio_optimization', 'diversification', 'rebalancing', 'risk_assessment'],
 'You can help users manage their crypto portfolios, suggest diversification strategies, and provide rebalancing recommendations based on risk tolerance.',
 750, TRUE),

('skill_onchain_analysis', 'On-Chain Analysis', 'Analyze blockchain data and on-chain metrics', 'analysis',
 ARRAY['blockchain_analysis', 'wallet_tracking', 'transaction_analysis', 'whale_watching'],
 'You can analyze on-chain data, track large transactions, identify whale movements, and explain blockchain metrics.',
 1500, TRUE),

('skill_defi_expert', 'DeFi Expert', 'Deep knowledge of DeFi protocols, yield farming, and liquidity provision', 'crypto',
 ARRAY['defi_protocols', 'yield_farming', 'liquidity_pools', 'smart_contracts'],
 'You are an expert in DeFi (Decentralized Finance). You understand protocols like Uniswap, Aave, Compound, yield farming strategies, and liquidity provision. You can explain risks and opportunities.',
 800, TRUE),

('skill_nft_advisor', 'NFT Advisor', 'NFT market analysis and collection evaluation', 'crypto',
 ARRAY['nft_analysis', 'collection_evaluation', 'rarity_assessment', 'market_trends'],
 'You can analyze NFT collections, evaluate rarity, explain market trends, and provide insights on NFT investments.',
 600, FALSE),

('skill_research_assistant', 'Research Assistant', 'Deep research on crypto projects, whitepapers, and tokenomics', 'research',
 ARRAY['project_research', 'whitepaper_analysis', 'tokenomics_evaluation', 'team_assessment'],
 'You can conduct deep research on crypto projects, analyze whitepapers, evaluate tokenomics, and assess team credibility.',
 500, FALSE),

('skill_automation_helper', 'Automation Helper', 'Help create trading bots and automation strategies', 'automation',
 ARRAY['bot_creation', 'strategy_automation', 'api_integration', 'backtesting'],
 'You can help users create trading bots, automate strategies, integrate with exchange APIs, and explain backtesting concepts.',
 1200, TRUE),

('skill_risk_manager', 'Risk Manager', 'Advanced risk management and position sizing', 'trading',
 ARRAY['risk_calculation', 'position_sizing', 'drawdown_management', 'portfolio_protection'],
 'You specialize in risk management. You can calculate optimal position sizes, manage drawdowns, and protect portfolios from excessive losses.',
 900, TRUE)
ON CONFLICT (skill_id) DO NOTHING;

-- Function to install skill for assistant
CREATE OR REPLACE FUNCTION install_openclaw_skill(
    p_assistant_id TEXT,
    p_skill_id TEXT,
    p_user_id INTEGER
) RETURNS TABLE (
    success BOOLEAN,
    message TEXT,
    credits_spent INTEGER
) AS $$
DECLARE
    v_skill_price INTEGER;
    v_user_credits INTEGER;
    v_already_installed BOOLEAN;
BEGIN
    -- Check if skill exists
    SELECT price_credits INTO v_skill_price
    FROM openclaw_skills_catalog
    WHERE skill_id = p_skill_id;
    
    IF v_skill_price IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Skill not found', 0;
        RETURN;
    END IF;
    
    -- Check if already installed
    SELECT EXISTS(
        SELECT 1 FROM openclaw_assistant_skills
        WHERE assistant_id = p_assistant_id AND skill_id = p_skill_id
    ) INTO v_already_installed;
    
    IF v_already_installed THEN
        RETURN QUERY SELECT FALSE, 'Skill already installed', 0;
        RETURN;
    END IF;
    
    -- Check user credits
    SELECT COALESCE(credits, 0) INTO v_user_credits
    FROM openclaw_user_credits
    WHERE user_id = p_user_id;
    
    IF v_user_credits < v_skill_price THEN
        RETURN QUERY SELECT FALSE, 'Insufficient credits', 0;
        RETURN;
    END IF;
    
    -- Deduct credits if not free
    IF v_skill_price > 0 THEN
        UPDATE openclaw_user_credits
        SET credits = credits - v_skill_price,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = p_user_id;
        
        -- Record transaction
        INSERT INTO openclaw_credit_transactions (
            transaction_id,
            user_id,
            amount_usdc,
            platform_fee,
            net_credits,
            transaction_type,
            description,
            status
        ) VALUES (
            'skill_' || gen_random_uuid()::TEXT,
            p_user_id,
            0,
            0,
            -v_skill_price,
            'skill_purchase',
            'Purchased skill: ' || p_skill_id,
            'completed'
        );
    END IF;
    
    -- Install skill
    INSERT INTO openclaw_assistant_skills (assistant_id, skill_id)
    VALUES (p_assistant_id, p_skill_id);
    
    RETURN QUERY SELECT TRUE, 'Skill installed successfully', v_skill_price;
END;
$$ LANGUAGE plpgsql;

-- Function to get assistant skills with details
CREATE OR REPLACE FUNCTION get_assistant_skills(p_assistant_id TEXT)
RETURNS TABLE (
    skill_id TEXT,
    name TEXT,
    description TEXT,
    category TEXT,
    capabilities TEXT[],
    is_active BOOLEAN,
    installed_at TIMESTAMP,
    usage_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sc.skill_id,
        sc.name,
        sc.description,
        sc.category,
        sc.capabilities,
        oas.is_active,
        oas.installed_at,
        oas.usage_count
    FROM openclaw_assistant_skills oas
    JOIN openclaw_skills_catalog sc ON oas.skill_id = sc.skill_id
    WHERE oas.assistant_id = p_assistant_id
    ORDER BY oas.installed_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get available skills (not yet installed)
CREATE OR REPLACE FUNCTION get_available_skills(p_assistant_id TEXT)
RETURNS TABLE (
    skill_id TEXT,
    name TEXT,
    description TEXT,
    category TEXT,
    price_credits INTEGER,
    is_premium BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sc.skill_id,
        sc.name,
        sc.description,
        sc.category,
        sc.price_credits,
        sc.is_premium
    FROM openclaw_skills_catalog sc
    WHERE sc.skill_id NOT IN (
        SELECT skill_id 
        FROM openclaw_assistant_skills 
        WHERE assistant_id = p_assistant_id
    )
    ORDER BY sc.price_credits ASC, sc.name ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to build enhanced system prompt with skills
CREATE OR REPLACE FUNCTION build_system_prompt_with_skills(p_assistant_id TEXT)
RETURNS TEXT AS $$
DECLARE
    v_base_prompt TEXT;
    v_skills_prompt TEXT := '';
    v_skill RECORD;
BEGIN
    -- Get base system prompt
    SELECT system_prompt INTO v_base_prompt
    FROM openclaw_assistants
    WHERE assistant_id = p_assistant_id;
    
    -- Add skills
    v_skills_prompt := E'\n\n## Your Installed Skills:\n';
    
    FOR v_skill IN 
        SELECT sc.name, sc.system_prompt_addition, sc.capabilities
        FROM openclaw_assistant_skills oas
        JOIN openclaw_skills_catalog sc ON oas.skill_id = sc.skill_id
        WHERE oas.assistant_id = p_assistant_id AND oas.is_active = TRUE
    LOOP
        v_skills_prompt := v_skills_prompt || E'\n### ' || v_skill.name || E'\n';
        v_skills_prompt := v_skills_prompt || v_skill.system_prompt_addition || E'\n';
    END LOOP;
    
    RETURN v_base_prompt || v_skills_prompt;
END;
$$ LANGUAGE plpgsql;

-- Create view for skill analytics
CREATE OR REPLACE VIEW openclaw_skill_analytics AS
SELECT 
    sc.skill_id,
    sc.name,
    sc.category,
    COUNT(DISTINCT oas.assistant_id) as total_installations,
    COUNT(DISTINCT osu.conversation_id) as total_uses,
    sc.price_credits * COUNT(DISTINCT oas.assistant_id) as total_revenue_credits
FROM openclaw_skills_catalog sc
LEFT JOIN openclaw_assistant_skills oas ON sc.skill_id = oas.skill_id
LEFT JOIN openclaw_skill_usage osu ON sc.skill_id = osu.skill_id
GROUP BY sc.skill_id, sc.name, sc.category, sc.price_credits
ORDER BY total_installations DESC;
