# CryptoMentor V2.0 Changelog

All notable changes to the CryptoMentor Artificial Intelligence Trading project will be documented in this file.

## [Unreleased / Latest] - 2026-04-08

### Web App Architecture (V2)
- 🔥 **Bot Start/Stop Controls**: Added a prominent Start/Stop bot toggle button in the sidebar (always visible) and a full Engine Controls card in the Engine tab with a live pulsing indicator showing whether the engine is running or stopped.
- 🔥 **Post-API-Save Bot Launch Prompt**: After successfully saving Bitunix API keys in the Settings tab, a modal confirmation overlay (`BotStartModal`) is displayed — allowing users to immediately launch the AutoTrade engine or defer startup with "Start Later". Includes a risk disclaimer banner.
- 🔥 **Bitunix Web Bridge Configured**: Exposes the same `API Key` and `API Secret` storage architecture behind AES-256-GCM encryption natively through the React Web Dashboard `SettingsTab`. Users can setup their bot's credentials without touching Telegram.
- 🔥 **Web Dashboard PnL Synchronization**: Corrected the logic in the web app's `PortfolioTab` to utilize backend Engine statistics (`engine.total_profit` and `engine.current_balance`). This perfectly mirrors what the AutoTrade session holds, curing discrepancies (e.g., where `Total PnL (30D)` rendered `$0.00`).
- 🔥 **Graceful UI Emptiness**: When users have zero active positions, the system will natively render a beautifully mapped `No Open Positions` card instead of dummy mockup placeholder fields. 
- 🛠️ **Test Endpoint**: A `POST /api/bitunix/keys/test` dry run engine was released to allow users to trial their API configuration natively via the web before persistent storage commits.
- 🛠️ **Dev Mode Auth Bypass**: Refactored `handleTelegramLogin` in `App.jsx` to directly consume the Telegram widget's user object without requiring a backend `/api/auth/telegram` server, enabling standalone local frontend development.
- 🛠️ **Vite IPv4 Binding + Localtunnel Support**: Forced Vite dev server to bind on `127.0.0.1` (IPv4) to resolve Telegram widget iframe security blocks; added `allowedHosts` whitelist to allow secure `localtunnel` HTTPS proxying for Telegram OAuth domain verification.

### Bitunix Client (Telegram & Web Core) 
- 🚀 **Thread-Safe Proxy Rate Limiter**: Implemented a globally-enforced `RateLimiter` token bucket strictly enforcing API payloads (e.g. `get_ticker`) across the application to <10req/s strictly, negating 429 penalties during heavy parallel validation.
- 🚀 **Smart Proxy Rotation & Blacklisting**: Integrated dynamic proxy health-checks into the `BitunixAutoTradeClient` which dynamically tracks and forcefully isolates broken gateways (from HTTP 403 blocks or massive timeouts) into temporary blackout pools.
- 🚀 **Parallel Signal Scanning (Concurrency)**: Refactored `ScalpingEngine` loops into pure `asyncio.gather` wraps, dropping portfolio signal generation latency from 15 seconds to under ~500ms whilst accurately retaining local `max_concurrent_positions` constraints.
- 🛠️ **StackMentor Fragment Protection (MIN_QTY Check)**: Crushed a critical math issue where closing small positions safely tripped below Bitunix's Exchange limits (e.g. TP3 fragment: 0.0005 BTC). If `qty_tp3` calculates below MIN_QTY, it intrinsically blends the payout forward into `tp2` or `tp1` fully to protect users seamlessly.
- 🚀 **Self-Healing TP/SL Endpoint Rotation**: The outdated `/api/v1/futures/tpsl/place_order` was universally substituted with the verified, highly elastic `modify_order` endpoint for real time partial adjustment.
- 🛠️ **Dual-Leg Safety Submissions**: Fixed an API schema conflict where issuing an updated Take Profit dynamically erased Stop Losses. The client now inherently mirrors existing unset targets (`slPrice=""`) without clearing bounds or halting rate limits.
- 🛠️ **Dynamic Position Resourcing**: `set_position_tpsl` and `set_position_sl` now aggressively resolve positional mappings internally without relying on fragile UUID callbacks.

## [Previous] - 2026-04-07

### AutoTrade System
- 🔥 **Swing Trade Engine Fix (13 Pairs)**: Expanded the Swing Engine to 13 altcoin pairs.
- 🔥 **StackMentor 3-Tier TP**: Implemented professional TP scale outs (at 1:2, 1:3 and 1:10) dropping minimum required bounds.
- 🔥 **Auto Mode Switcher**: Aggressive automatic pivoting between SCALPING vs SWING based on ADX/ATR metrics natively displayed on Dashboards.
- 🛠️ **Scalping Edge Safety**: 10x safety limitation cap with dynamic Max position risk caps running at 5% ceilings. 
  - Added XAUUSDT, CLUSDT, QQQUSDT as verifiable trading pairs.
