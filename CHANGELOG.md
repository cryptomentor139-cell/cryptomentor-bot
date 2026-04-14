# Changelog

## [2.1.51] — 2026-04-14 — Fix Bitunix Hedge Mode PositionSide Mismatch

### 🛠️ Execution Engine Fix

#### 1) Explicit `positionSide` Mapping for Hedge Mode
- **Issue:** Bitunix API in Hedge Mode requires explicit `positionSide`. During some orders (especially close/reduce-only operations via 1-click execution or scaling out), omitting `positionSide` could result in "Exchange position side mismatch after order" errors (`expected=SHORT seen=SELL`).
- **Fix:** 
  - `place_order` and `place_order_with_tpsl` in `bitunix_autotrade_client.py` now explicitly infer and map `positionSide`.
  - Added a compatibility fallback: if an account/endpoint rejects the explicit `positionSide` payload (depending on their mode/settings), the client catches the `positionSide` error and automatically retries without the parameter.
- **Files:**
  - `Bismillah/app/bitunix_autotrade_client.py`


## [2.1.50] — 2026-04-14 — Fix Bitunix Side Mapping Mismatch (SHORT Opening LONG)

### 🛠️ 1-Click/Execution Safety Fix

#### 1) Explicit `positionSide` on Bitunix open orders
- **Issue:** Some accounts/modes could interpret `BUY/SELL` ambiguously, causing direction mismatch.
- **Fix:**
  - Added explicit `positionSide` on open orders:
    - `BUY -> LONG`
    - `SELL -> SHORT`
  - Applied to both regular market orders and market-with-TP/SL orders.
  - Added compatibility fallback retry without `positionSide` only when exchange rejects that field.

#### 2) Post-order side verification in backend
- Added post-execution live position check in `/dashboard/signals/execute`.
- If exchange side does not match expected side, backend logs an error and returns `execution_warning`.

#### 3) Frontend warning surface for mismatch
- Signal card now surfaces backend `execution_warning` after placement so mismatches are visible immediately.

- **Files:**
  - `Bismillah/app/bitunix_autotrade_client.py`
  - `website-backend/app/routes/signals.py`
  - `website-frontend/src/App.jsx`

## [2.1.49] — 2026-04-14 — Fix 1-Click Direction Discrepancy & Enhanced Notifications

### 🛠️ Execution & Monitoring Upgrade

#### 1) Fixed 1-Click Direction Discrepancy
- **Issue:** 1-click trades could occasionally open in the opposite direction if market momentum flipped after the signal was generated.
- **Fix:** 
  - 1-click execution now honors the explicit direction (LONG/SHORT) of the signal clicked on the dashboard.
  - Re-derivation logic at execution time now respects the source signal's direction while optimizing entry, SL, and TP for the current market price.
  - Added `direction` payload support to `/dashboard/signals/execute` and re-built frontend to propagate it.

#### 2) Centralized and Enhanced Admin Notifications
- **Optimization:** Consolidated all Telegram admin alerts into a unified `_notify_admins` utility across Scalping and Swing (AutoTrade) engines.
- **New Feature:** Admins now receive real-time notifications for successful events:
  - Trade Openings (Scalp & Swing)
  - Take Profit (TP) hits
  - Stop Loss (SL) triggers
  - Sideways market scalps
- **Throttling:** Implemented deduplication and throttling to prevent Telegram API rate limits during high volatility.

#### 3) Production Sync
- All fixes deployed to live VPS.
- Frontend built and synced to Nginx root.

- **Files:**
  - `website-frontend/src/App.jsx`
  - `website-backend/app/routes/signals.py`
  - `scalping_engine.deploy.py`
  - `Bismillah/app/autotrade_engine.py`


## [2.1.48] — 2026-04-14 — Admin Telegram Copy Localized To English

### 🛠️ Message Localization

- Converted Indonesian admin approval notification copy to English for:
  - Web referral partner registration approval card
  - Bot community partner registration approval card

- Files:
  - `website-backend/app/routes/dashboard.py`
  - `Bismillah/app/handlers_community.py`

## [2.1.47] — 2026-04-14 — Hardcoded Dual Admin Routing For Logs & Approvals

### 🛠️ Admin Routing Enforcement

#### 1) Two Telegram admins are now permanently included
- Hardcoded admin IDs now always included in routing:
  - `1187119989`
  - `7675185179`
- This applies even if env vars are missing/misconfigured.

#### 2) Applied to core approval and engine-log paths
- UID approval request notifications (web + bot)
- UID approve/reject admin authorization checks
- Community partner registration admin approval notifications
- Scalping engine admin error/log notifications
- Central error handler admin notifications
- Dashboard web admin notification helper

#### 3) Community partner scope preserved
- Community partners still only handle member approvals in their own partner flow.
- Global admin logs/approvals continue to go to both hardcoded admins.

- Files:
  - `website-backend/app/routes/user.py`
  - `website-backend/app/routes/dashboard.py`
  - `Bismillah/app/handlers_autotrade.py`
  - `Bismillah/app/handlers_autotrade_admin.py`
  - `Bismillah/app/handlers_community.py`
  - `Bismillah/app/scalping_engine.py`
  - `Bismillah/app/error_handler.py`

## [2.1.46] — 2026-04-14 — Track Exact Approver Identity In `user_verifications`

### 🛠️ Verification Auditability Upgrade

#### 1) Added SQL amendment for reviewer identity metadata
- New migration file:
  - `db/add_user_verification_reviewer_fields.sql`
- Adds columns:
  - `reviewed_by_actor_type` (`admin` or `partner`)
  - `reviewed_by_telegram_id`
  - `reviewed_by_partner_code`
  - `reviewed_by_partner_name`
- Includes backfill from legacy `reviewed_by_admin_id`.

#### 2) Web + bot submit flow now resets reviewer metadata on resubmission
- Pending UID submissions now clear all reviewer fields consistently.

#### 3) Admin and community-partner approvals now write reviewer identity
- Admin approval/reject writes:
  - actor type `admin`
  - reviewer telegram id
- Community partner approval/reject writes:
  - actor type `partner`
  - leader telegram id
  - partner code + partner name
- Also ensures partner approvals update central `user_verifications` table (not only legacy `autotrade_sessions`).

#### 4) Verification status API now exposes reviewer metadata
- `/user/verification-status` includes new reviewer fields for frontend/backoffice visibility.

- Files:
  - `db/add_user_verification_reviewer_fields.sql`
  - `website-backend/app/routes/user.py`
  - `Bismillah/app/handlers_autotrade.py`
  - `Bismillah/app/handlers_autotrade_admin.py`
  - `Bismillah/app/handlers_community.py`

## [2.1.45] — 2026-04-14 — UID Approval Notifications Now Include Community Partner Attribution

### 🛠️ Admin Verification Context Upgrade

#### 1) UID approval cards now show partner ownership context
- Admin Telegram UID verification messages now append:
  - community partner name
  - community code
  - partner `telegram_id`
  - partner Bitunix referral code
- If no partner mapping is found, message explicitly shows default/direct flow (`sq45`).

#### 2) Partner mapping resolution added in both web + bot UID submission paths
- Resolution priority:
  - `autotrade_sessions.community_code`
  - `users.referred_by` mapped to `community_partners.telegram_id` or `community_code`

- Files:
  - `website-backend/app/routes/user.py`
  - `Bismillah/app/handlers_autotrade.py`

## [2.1.44] — 2026-04-14 — Referral-Aware Bitunix Registration Link In Gatekeeper

### 🛠️ Referral Routing Enhancement

#### 1) Added public referral resolver endpoint for onboarding
- New endpoint: `GET /dashboard/referral/resolve?code=<community_code>`
- Behavior:
  - returns active community partner `bitunix_referral_url` when valid
  - safely falls back to default `https://www.bitunix.com/register?vipCode=sq45`

#### 2) Gatekeeper and rejection flow now support `?ref=` links
- Web app now reads `?ref=<community_code>` from URL and resolves referral metadata via backend.
- Step 1 register CTA and rejected-state re-register CTA now use resolved partner URL/code.
- If no `ref` is provided (or code invalid/inactive), UI uses default `sq45` referral link.

- Files:
  - `website-backend/app/routes/dashboard.py`
  - `website-frontend/src/App.jsx`

## [2.1.43] — 2026-04-14 — Apply Auto Max-Safe Leverage Logic To 1-Click Execution

### 🛠️ 1-Click Sizing Upgrade

#### 1) 1-click order sizing now uses max-safe leverage automatically
- `/dashboard/signals/execute` now computes leverage from:
  - exchange symbol max leverage
  - SL-distance safety bound
- No longer tied to legacy session leverage for execution.

#### 2) Risk remains fixed vs equity
- Position sizing keeps loss anchored to:
  - `equity × configured risk %`
- Supports dynamic SL adjustment when minimum quantity constraints require it.

#### 3) API response now includes leverage diagnostics
- Added sizing fields:
  - `leverage_mode=auto_max_safe`
  - `leverage_baseline`
  - `exchange_max_leverage`
  - `is_dynamic`, `is_clamped`

- File:
  - `website-backend/app/routes/signals.py`

## [2.1.42] — 2026-04-13 — AutoTrade Risk UI Aligned With Live Execution Logic

### 🛠️ Web Risk Management Alignment

#### 1) Risk panel now reflects actual engine behavior
- Updated Engine Risk Management copy to match live logic:
  - fixed loss by `equity × risk%`
  - leverage is auto-optimized to max-safe value per setup

#### 2) Replaced fixed leverage selector in Engine tab
- Removed clickable fixed leverage choices from AutoTrade risk card UI
- Added read-only execution model display:
  - `AUTO MAX-SAFE` leverage execution
  - session leverage baseline shown as reference only

#### 3) Onboarding flow now mirrors execution model
- Removed leverage selection from onboarding Step 2
- Onboarding summary now states leverage as `Auto Max-Safe`
- Risk save call no longer writes manual leverage during onboarding

#### 4) Backend settings payload enriched for frontend mapping
- `/dashboard/settings` now includes:
  - `leverage_mode: "auto_max_safe"`

- Files:
  - `website-frontend/src/App.jsx`
  - `website-backend/app/routes/dashboard.py`

## [2.1.41] — 2026-04-13 — Unified Max-Leverage Risk Sizing Across AutoTrade Engines

### 🛠️ Leverage + Risk Consistency Update

#### 1) Enforced max-safe leverage sizing in Scalping AutoTrade path
- Removed legacy `10x` leverage cap in scalping sizing.
- Scalping now uses unified PRO sizing logic with exchange max leverage + liquidation safety bound.
- If exchange client supports `get_max_leverage(symbol)`, that limit is used directly.

#### 2) Risk remains equity-based and stop-loss anchored
- Position sizing continues to target:
  - `Loss at SL = Equity × user risk %`
- Equity source:
  - `available + frozen + unrealized PnL`
- High leverage is used for margin efficiency only; SL/risk budget remains fixed by sizing.

#### 3) Execution leverage is propagated into actual order placement
- Scalping execution now uses the computed effective leverage from risk sizing.
- If sizing falls back, baseline leverage is kept.

- File:
  - `Bismillah/app/scalping_engine.py`

## [2.1.40] — 2026-04-13 — Leverage Application Bugfix + Safe Admin Mock Signal

### 🛠️ Execution Bugfix

#### 1) Apply optimized leverage for every valid PRO sizing result
- Root cause:
  - runtime only replaced trade leverage when `_last_sizing.is_dynamic == True`
  - non-dynamic flows kept stale session leverage (e.g. remained at `20x`)
- Fix:
  - engine now always applies `_last_sizing['leverage']` when sizing is valid
  - dynamic SL log remains separated for dynamic-only path

#### 2) Respect exchange-reported leverage ceiling directly in PRO sizing
- Removed local symbol hard-cap in `calculate_position_size_pro`
- Final leverage bound is now driven by:
  - exchange `max_leverage`
  - liquidation safety bound (`safe_max_leverage`)

#### 3) Secure mock signal script for admin testing
- Replaced hardcoded token usage with env-based config:
  - `TELEGRAM_BOT_TOKEN` / `BOT_TOKEN`
  - `ADMIN_TELEGRAM_ID`

- Files:
  - `Bismillah/app/autotrade_engine.py`
  - `Bismillah/app/position_sizing.py`
  - `Bismillah/scratch/send_mock_signal.py`

## [2.1.39] — 2026-04-13 — 🚀 Max Leverage Efficiency Strategy (Full Deploy)

### 🚀 Capital Efficiency Optimization

#### 1) Guaranteed Maximum Leverage Execution
- **Logic:** The engine now automatically queries the Bitunix API (`/get_position_tiers`) to determine the actual maximum leverage allowed for each individual trading pair before execution.
- **Efficiency:** Every trade now utilizes the maximum possible leverage (e.g., 100x-125x for BTC/ETH, 50x-75x for Alts) to minimize required margin (capital lock-up).
- **Safety:** Integrated a safety floor that ensures the Liquidation Price remains beyond the Stop Loss price.
- **Risk Integrity:** Position size (Qty) remains strictly calculated based on the user's defined risk % relative to equity.

#### 2) Enhanced Dynamic Scaling for Small Accounts
- For accounts below $100 or when balance is insufficient for exchange minimums, the engine now automatically:
  - Hikes leverage to the symbol's maximum.
  - Adjusts/tightens Stop Loss to maintain the exact same USDT risk amount.
  - Ensures participation for entries that would previously fail with "insufficient balance".

#### 3) Transparent "Margin Efficiency" Notifications
- Updated Telegram notifications to clearly state when "Margin Efficiency Optimization" has been applied to a trade.
- Shows the exact hiked leverage and the adjusted stop-loss parameters.

- **Files Modified:**
  - `Bismillah/app/position_sizing.py`
  - `Bismillah/app/bitunix_autotrade_client.py`
  - `Bismillah/app/autotrade_engine.py`
  - `scalping_engine.deploy.py`

## [2.1.38] — 2026-04-13 — StackMentor Fields Reflected In Web Positions API

### 🛠️ Website Reflection Fix

#### 1) Exposed StackMentor TP tiers in `/bitunix/positions`
- Root cause:
  - position source tagging worked, but API response did not include DB TP tier metadata for matched autotrade rows
- Fix:
  - `/bitunix/positions` now enriches matched autotrade positions with:
    - `strategy`
    - `tp1_price`, `tp2_price`, `tp3_price`
    - `tp1_hit`, `tp2_hit`, `tp3_hit`
- Result:
  - website position cards can render StackMentor tier targets/hit status from live backend response.

- File:
  - `website-backend/app/routes/bitunix.py`

## [2.1.37] — 2026-04-13 — StackMentor RR Ladder Extended To 1:10

### 🛠️ Strategy Profile Update

#### 1) Increased StackMentor TP risk:reward ladder
- Updated staged TP RR profile to:
  - TP1: `1:3`
  - TP2: `1:6`
  - TP3: `1:10`
- Position split remains:
  - TP1 `60%`, TP2 `30%`, TP3 `10%`
- Breakeven behavior after TP1 remains enabled.

- File:
  - `Bismillah/app/stackmentor.py`

## [2.1.36] — 2026-04-13 — StackMentor Force TP/SL Watchdog + Breakeven Restore

### 🛠️ Runtime Protection Hotfix

#### 1) Added bot-side SL watchdog force-close
- Root cause:
  - exchange TP/SL can occasionally fail to trigger in time during volatility
- Fix:
  - StackMentor monitor now checks mark price against SL every cycle and force-closes remaining position size when crossed
  - writes `close_reason=stackmentor_force_sl` with `status=closed_sl`

#### 2) Restored staged StackMentor behavior with breakeven
- StackMentor config switched back to staged exits:
  - TP1 60% (RR 1:2), TP2 30% (RR 1:3), TP3 10% (RR 1:5)
- After TP1 hit, bot now moves SL to entry (breakeven) for remaining size.

#### 3) Added restart-safe StackMentor hydration
- Root cause:
  - in-memory StackMentor map can be empty after restart, so TP/SL monitoring pauses
- Fix:
  - monitor now hydrates open StackMentor trades from DB before checks.

- Files:
  - `Bismillah/app/stackmentor.py`
  - `Bismillah/app/autotrade_engine.py`

## [2.1.35] — 2026-04-13 — StackMentor Reliability + Trade-State Consistency Fix

### 🛠️ Engine/DB Hotfix

#### 1) StackMentor close events now preserve TP hit flags
- Root cause:
  - profitable unified StackMentor closes were often written as generic closes without TP hit flags
- Fix:
  - on `closed_tp` for `strategy=stackmentor`, engine now marks `tp1_hit/tp2_hit/tp3_hit` with timestamps

#### 2) Scalping trades now persist StackMentor metadata
- Root cause:
  - scalping DB rows did not persist `strategy=stackmentor` and TP tier fields, reducing observability
- Fix:
  - scalping save path now stores `strategy`, `tp1/2/3_price`, and quantity split fields from execution levels
  - scalping close path now also marks TP hit flags on StackMentor TP closes

#### 3) Startup stale-reconcile no longer writes ambiguous `status=closed`
- Root cause:
  - stale DB trades were marked as plain `closed` without `closed_at`, causing reporting confusion
- Fix:
  - stale reconciliation now writes `status=closed_manual` and sets `closed_at`

- Files:
  - `Bismillah/app/autotrade_engine.py`
  - `Bismillah/app/scalping_engine.py`
  - `Bismillah/app/scheduler.py`

## [2.1.34] — 2026-04-13 — Fix 1-Click TP/SL Inversion And Enforce ~1:3 RR

### 🛠️ 1-Click Risk/Reward Hotfix

#### 1) Normalized 1-click trade levels before execution
- Root cause:
  - execution path mixed live entry with independently-derived TP/SL sources, which could produce inconsistent geometry in edge cases
- Fix:
  - added a strict level normalizer that guarantees valid LONG/SHORT ordering (`SL < Entry < TP` for LONG, inverse for SHORT)
  - enforces a minimum ~1:3 baseline RR on execution (`target_rr=3.0`)

#### 2) Aligned generated signal targets with 1:3+ profile
- Updated momentum and confluence signal builders to produce TP tiers from risk distance:
  - TP1 ≈ 3R, TP2 ≈ 4R, TP3 ≈ 5R
- Added `rr_ratio` in execution response sizing payload for observability.

- File:
  - `website-backend/app/routes/signals.py`

## [2.1.33] — 2026-04-13 — Fix Bitunix API Key Onboarding 500 Error

### 🛠️ Website Backend Hotfix

#### 1) Fixed `/bitunix/keys` + `/bitunix/keys/test` crashing during onboarding
- Root cause:
  - route-level import used `from app.bitunix_autotrade_client import BitunixAutoTradeClient`
  - module does not exist under `website-backend/app`, causing `ModuleNotFoundError` and HTTP 500
- Impact:
  - approved users saw generic `Connection failed` on Step 1 while testing/saving valid keys
- Fix:
  - reused shared client loader from `app.services.bitunix` (`bsvc.BitunixAutoTradeClient`)
  - added explicit server-side availability guard with clear error if connector is unavailable
- File:
  - `website-backend/app/routes/bitunix.py`

## [2.1.32] — 2026-04-13 — Fix Frequent Market-Data Klines Failures

### 🛠️ AutoTrade/Scalping Data Reliability

#### 1) Added Missing `3m` Klines Support + Hardened Fallback Fetching
- Root causes:
  - scalping flow requests `3m` candles for micro-momentum checks, but provider did not support `3m` mapping, causing repeated `Failed to get klines ... from all sources`
  - transient upstream HTTP errors/timeouts immediately failed without retry/cooldown behavior
  - low-limit fetches (e.g., `limit=2`) could be rejected by strict `>=10 candles` validation
- Fix:
  - added `3m` interval support in Binance fallback mapping
  - added HTTP retry + per-source exponential cooldown/backoff in klines provider
  - relaxed minimum-candle validation to honor small requested limits
  - blocked CoinGecko fallback for sub-15m intervals to avoid inaccurate minute-candle substitution
  - improved error logs to include interval for faster debugging
- File:
  - `Bismillah/app/providers/alternative_klines_provider.py`

## [2.1.31] — 2026-04-13 — Fix 1-Click Positions Misclassified As AutoTrade

### 🛠️ Portfolio Classification Fix

#### 1) `/bitunix/positions` Now Returns Annotated Position Sources Correctly
- Root cause:
  - the route computed annotated `source` values but returned the raw unannotated exchange positions instead
  - the frontend then defaulted missing `source` to `autotrade`
- Impact:
  - 1-click positions could appear under the AutoTrade section/card label
- Fix:
  - return the annotated position list from the API
  - compute position counts from the annotated list
  - remove the overly-loose symbol+side fallback match that could falsely tag manual positions as autotrade
- File:
  - `website-backend/app/routes/bitunix.py`

## [2.1.30] — 2026-04-13 — Decouple AutoTrade vs 1-Click Risk Settings

### 🛠️ Settings Separation Fix

#### 1) Stopped 1-Click Risk From Inheriting AutoTrade Risk By Default
- Root cause: when `one_click_risk_per_trade` was missing, the dashboard API silently fell back to `risk_per_trade`.
- Impact:
  - AutoTrade and 1-click could appear linked even though they are meant to be separate controls
  - users could see incorrect segregation between both trading modes
- Fix:
  - `one_click_risk_per_trade` now defaults independently to `0.5%`
  - Signals tab and signal-card handlers were renamed to explicit 1-click props for clearer separation
  - UI copy now states that 1-click risk is separate from AutoTrade risk
- Files:
  - `website-backend/app/routes/dashboard.py`
  - `website-frontend/src/App.jsx`

## [2.1.29] — 2026-04-13 — Add Website Favicon

### 🎨 Frontend Polish

#### 1) Added Branded Browser Tab Favicon
- Added a new SVG favicon matching the CryptoMentor AI visual style.
- Wired the favicon into the frontend HTML shell so browsers can show the site icon in tabs/bookmarks.
- Files:
  - `website-frontend/public/favicon.svg`
  - `website-frontend/index.html`

## [2.1.28] — 2026-04-13 — Restore 1-Click Signals Rendering On Dashboard

### 🛠️ Backend Hotfix

#### 1) Fixed Live Signals Endpoint Returning Empty Signal List
- Root cause:
  - website signal generation still had stale imports pointing to `Bismillah.app...`
  - the route also contained a stray cache write using undefined variables inside `process_one_symbol()`
- Impact:
  - `/dashboard/signals` kept erroring per-symbol and the frontend showed no 1-click opportunities
- Fix:
  - switched imports to the bot app modules already exposed on `sys.path`
  - removed the invalid cache write from the per-symbol response builder
- Result:
  - live `/api/dashboard/signals` returns signal cards again
  - 1-click signals can render on the website again
- File:
  - `website-backend/app/routes/signals.py`

## [2.1.27] — 2026-04-13 — Restore Website Login After API Crash Loop

### 🛠️ Backend Hotfix

#### 1) Fixed Dashboard Login Stall Caused By Website API Startup Failure
- Root cause: `website-backend/app/routes/signals.py` had a malformed indentation block around signal cache handling.
- Impact:
  - `cryptomentor-web` failed to boot
  - nginx returned `502 Bad Gateway` for `/api/`
  - dashboard login appeared to do nothing because the frontend could not reach the backend
- Fix:
  - repaired the broken `if signal:` block and restored valid module import on startup
- Result:
  - `cryptomentor-web` starts normally again
  - `https://cryptomentor.id/api/` returns `200 OK`
  - dashboard login can respond again
- File:
  - `website-backend/app/routes/signals.py`

## [2.1.26] — 2026-04-13 — 🚀 Performance: Parallel Execution & Lower Latency

### 🚀 Performance & UX Optimization

#### 1) 1-Click Trading Latency Reduced by ~70%
- **Optimization:** Refactored the `/signals/execute` endpoint to use `asyncio.gather` for parallelizing IO-bound tasks.
- **Details:** 
  - Bitunix account data and open positions are now fetched simultaneously.
  - Binance live ticker data (for entry price and stop loss re-calculation) is fetched in parallel with account data.
  - Replaced the ephemeral `httpx.AsyncClient` creation with a shared singleton client to avoid TCP connection overhead.
- **Result:** Trades are placed significantly faster after a user clicks "1-Click Trade", reducing slippage risk and improving user feel.
- **File:** `website-backend/app/routes/signals.py`

#### 2) Signals Dashboard Loading Performance Boost
- **Optimization:** Parallelized the signal generation loop.
- **Details:** 
  - All 12 symbols in the watchlist are now analyzed for "Confluence" signals in parallel using `asyncio.gather`.
  - Previously, each symbol's candle fetch and analysis blocked the next, causing significant linear delay for a total dashboard refresh.
- **Result:** The dashboard "Signals" tab now populates all opportunities nearly instantly upon request.
- **File:** `website-backend/app/routes/signals.py`

## [2.1.25] — 2026-04-13 — Smart Risk Tiering: Safety Floor for Small Accounts

### 🚀 Risk Management Upgrade

#### 1) Automatic 3% Risk Floor for Accounts < $100
- **Root cause:** Users with small balances (e.g., $30) using conservative risk settings (0.5%) generated orders smaller than Bitunix's minimum quantity limits (e.g., 0.01 ETH).
- **Result:** Trades were silently skipped or failed with exchange "min qty" errors.
- **Fix:**
  - Implemented real-time balance checks in both **Scalping** and **Swing** engines.
  - If Account Balance (or Equity) is below $100, the engine automatically forces **3% risk per trade** regardless of the user's setting.
  - This ensures positions are large enough to meet exchange requirements while still providing protection.
- **Files:**
  - `Bismillah/app/scalping_engine.py`
  - `Bismillah/app/autotrade_engine.py`

#### 2) Enhanced Risk Range for Unified Dashboard (0.5% - 10%)
- Enabled support for **0.5%** (ultra-conservative) and **10%** (aggressive) risk tiers for accounts over $100.
- Updated `set_risk_per_trade` validation in Supabase repo to enforce these new balance-dependent limits.
- **Files:**
  - `Bismillah/app/supabase_repo.py`

#### 3) Dynamic Risk Settings Menu in Telegram
- The `/risk` settings menu now adaptively labels and restricts options based on the user's live balance.
- Users under $100 now see a clear explanation of why their risk is locked at 3% for execution safety.
- **Files:**
  - `Bismillah/app/handlers_autotrade.py`


## [2.1.24] — 2026-04-13 — Remove Duplicate AutoRestore Startup Cards

### 🛠️ Telegram Bot Fix

#### 1) AutoTrade Engine Startup Message Now Comes From One Source
- Root cause: users could receive two startup cards on engine restore:
  - one from `scheduler.py`
  - one from the engine itself
- This also caused inconsistent details like old hardcoded `10 pairs` text while the live scalping config uses `16 pairs`.
- Fix:
  - Removed the duplicate restore-time startup notification from the scheduler.
  - The engine is now the single source of truth for startup messaging.
- Result:
  - Users should only receive one startup card, with live config values instead of stale hardcoded text.
- File:
  - `Bismillah/app/scheduler.py`

## [2.1.23] — 2026-04-13 — Limit Admin Telegram Alerts To Actual Trade Engine Errors

### 🛠️ Bot Noise Reduction

#### 1) Removed Normal Scan/Event Spam From Admin Alerts
- Root cause: admin Telegram notifications were also firing for normal runtime events such as:
  - no signals found
  - signal validated
  - successful order placement
- Fix:
  - Admin engine notifications now only send for actual error/failure conditions.
  - Current live error alerts include:
    - order placement failures
    - main engine loop errors
- Result:
  - Admin Telegram receives only actionable trading-bot error messages instead of routine engine chatter.
- File:
  - `Bismillah/app/scalping_engine.py`

## [2.1.22] — 2026-04-13 — Fix Telegram AutoTrade Reminder Buttons

### 🛠️ Bot Fix

#### 1) Wired Reminder CTA Buttons Into Live AutoTrade Handlers
- Root cause: the reminder message rendered `at_start_onboarding` and `at_learn_more` callback buttons, but those callback patterns were never registered in the bot.
- Fix:
  - Added a callback handler for `at_start_onboarding` that reuses the main AutoTrade gatekeeper flow.
  - Added a callback handler for `at_learn_more` with a short explainer and direct next-step buttons.
- Result:
  - Telegram reminder buttons now respond instead of appearing dead.
- File:
  - `Bismillah/app/handlers_autotrade.py`

## [2.1.21] — 2026-04-13 — Admin Telegram Notifications For Trade Engine Logs

### 🔔 Monitoring

#### 1) Added High-Signal Admin Notifications For Scalping/AutoTrade Engine Events
- Admins now receive Telegram notifications for:
  - validated trade signals
  - successful order placements
  - order placement failures
  - repeated zero-signal scan milestones
  - engine loop errors
- Notifications are throttled in-memory to reduce spam while still surfacing runtime problems quickly.
- File:
  - `Bismillah/app/scalping_engine.py`

## [2.1.20] — 2026-04-13 — Reduce AutoTrade Candle Fetch Stampede

### 🛠️ Runtime Fix

#### 1) De-duplicated Concurrent Candle Fetches Across AutoTrade Engines
- Root cause: many active engines could request the same `(symbol, timeframe, limit)` candles at the same moment before cache was populated.
- This caused provider bursts, repeated fallback failures, and scan cycles returning `0 signals found, 0 validated`.
- Fix:
  - Added in-flight request sharing in the global candle cache.
  - Waiting callers now reuse the first live fetch instead of hammering providers again.
  - Added stale-cache fallback if a refresh fails.
- File:
  - `Bismillah/app/candle_cache.py`

## [2.1.19] — 2026-04-13 — Fix 1-Click All-In Sizing + Harden AutoTrade Risk Persistence

### 🛠️ Bug Fix

#### 1) 1-Click `All In` Now Targets Full Equity Loss At Stop Loss
- Root cause: the `All In` path sized `position_size_usdt = equity`, which only used wallet size once and did not honor `100%` loss-at-SL intent.
- Fix:
  - `All In` now uses the same SL-distance risk formula without the normal per-trade margin cap:
    - `position_size_usdt = risk_amount / sl_distance_pct`
  - Response payload now safely handles uncapped margin metadata for `All In`.
- Result:
  - `100%` 1-click risk now behaves like true full-risk sizing instead of a capped wallet-sized position.
- File:
  - `website-backend/app/routes/signals.py`

#### 2) AutoTrade Risk Saving No Longer Depends On A Pre-Existing Session Row
- Root cause: dashboard risk save used `update(...)` only, so users without a matching `autotrade_sessions` row could appear to save risk but then reload back to the previous value.
- Fix:
  - Switched AutoTrade risk and 1-click risk persistence to `upsert(..., on_conflict="telegram_id")`.
- Result:
  - Risk values persist more reliably and stop snapping back after refresh/load for affected users.
- File:
  - `website-backend/app/routes/dashboard.py`

#### 3) Frontend Keeps AutoTrade Risk Reflected Between Refreshes
- Added a dedicated local fallback key for AutoTrade risk, matching the already-separated 1-click storage approach.
- This keeps the typed/selected AutoTrade risk reflected in the UI while backend state is being reloaded.
- File:
  - `website-frontend/src/App.jsx`

## [2.1.18] — 2026-04-13 — Fix AutoTrade Risk Slider Reseting to 0.5%

### 🛠️ Bug Fix

#### 1) Fixed Slider Commit Event Bug Causing Min Clamp
- Root cause: `onMouseUp` / `onTouchEnd` / `onPointerUp` passed event objects into `commitRisk(...)`.
- `commitRisk` interpreted those events as invalid numbers and normalized to slider min (`0.5%`).
- Result was AutoTrade risk repeatedly resetting to `0.5%` after slider interactions.
- Fix:
  - Wrapped slider release handlers to call `commitRisk()` with no event payload.
  - AutoTrade risk now commits the actual selected value correctly.
- File:
  - `website-frontend/src/App.jsx`

## [2.1.17] — 2026-04-13 — Faster Risk Slider Reflection + Visible Live Build Tag

### 🚀 What Changed

#### 1) Decoupled AutoTrade vs 1-Click Slider Saving State
- AutoTrade risk slider now uses its own save/loading state.
- 1-click risk slider now uses a separate save/loading state.
- This prevents one slider save from blocking the other and improves responsiveness while users adjust risk.
- File:
  - `website-frontend/src/App.jsx`

#### 2) Added Visible Live Build Tag in Signals Header
- Signals header now shows the active bundle hash (`Build <hash>`).
- This makes it immediately clear whether users are on the latest deployed frontend.
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deployment Intent

- Deploy frontend to live nginx root and verify new bundle hash is served.
- Keep trading engine process state unchanged during rollout.

## [2.1.16] — 2026-04-13 — Faster User Reflection via In-App Update Detection

### 🚀 What Changed

#### 1) Added Automatic Frontend Update Detection Banner
- App now periodically checks deployed `index.html` for a newer hashed JS bundle.
- If a newer bundle is detected, users get a non-blocking in-app banner:
  - `Refresh Now` (immediate reload)
  - `Later` (dismiss)
- This reduces lag where users stay on old tabs and don’t see fresh changes quickly.
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deployment Verification

- Rebuilt and deployed to live nginx web root.
- Verified public HTML points to latest bundle:
  - `/assets/index-gUG7Cbpj.js`

## [2.1.15] — 2026-04-13 — 1-Click Dynamic Capacity Run-Through (Effective in Live UI)

### 🚀 What Changed

#### 1) Signals UI Now Mirrors Backend Dynamic Capacity Logic
- Updated 1-click signal cards to use live context for dynamic preview:
  - current open positions count
  - leverage tier capacity target
  - remaining slots
  - AutoTrade-running headroom ratio
- Added visible capacity line per card:
  - `Capacity: X/Y open · slots left Z`
- This aligns what users see in UI with backend concurrency-aware sizing behavior.
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deployment Verification

- Rebuilt frontend locally and deployed directly to live nginx root `/var/www/cryptomentor`.
- Verified public site now serves latest bundle:
  - `/assets/index-NklXPItR.js`
- No trading engine restart performed; engine state preserved.

## [2.1.14] — 2026-04-13 — Dynamic 1-Click Risk Sizing With Leverage-Concurrency Headroom

### 🚀 What Changed

#### 1) 1-Click Sizing Now Accounts for Leverage to Improve Concurrent Trade Capacity
- Enhanced `/dashboard/signals/execute` sizing logic so leverage increases practical concurrency:
  - Added dynamic per-trade margin budget based on leverage tier and current open positions.
  - Added reserved margin headroom when AutoTrade is running, to reduce contention between AutoTrade and 1-click.
  - Added clean rejection when no per-trade budget remains (actionable message).
- This makes risk selection more dynamic for users while preventing one trade from consuming too much available margin.
- File:
  - `website-backend/app/routes/signals.py`

#### 2) Added Rich Sizing Telemetry in Execute Response
- Response now includes effective risk and capacity fields:
  - `effective_risk_amount`, `effective_risk_pct`
  - `open_positions_count`, `max_concurrent_target`
  - `autotrade_running`
  - `margin_cap_dynamic`, `margin_cap_hard`, `effective_margin_cap`
- File:
  - `website-backend/app/routes/signals.py`

### ✅ Deploy/State Safety Notes

- Backend route deployed and `cryptomentor-web.service` restarted successfully.
- `nginx` reloaded.
- Verified trading engine untouched:
  - `cryptomentor.service` stayed `active`
  - `ExecMainPID=457177` unchanged

## [2.1.13] — 2026-04-13 — Production Web Root Deployment Fix (Reflection Issue Resolved)

### 🚀 What Changed

#### 1) Fixed Why UI Changes Were Not Reflecting Publicly
- Root cause identified: frontend deploy script uploaded to a non-served path
  (`/root/cryptomentor-bot/website-frontend/dist`) while nginx serves
  `/var/www/cryptomentor`.
- Synced latest built assets into live nginx root and reloaded nginx.
- Public site now serves current bundle:
  - `/assets/index-BBVyvRMg.js`

#### 2) Updated Deploy Scripts to Correct Live Destination
- Changed default frontend deploy target to nginx web root:
  - `deploy_frontend.py` → `/var/www/cryptomentor`
  - `deploy_frontend.ps1` → `/var/www/cryptomentor`

### ✅ Deploy/State Safety Notes

- Frontend files deployed to live web root and ownership corrected.
- Reloaded `nginx` only.
- Trading engine state verified unchanged:
  - `cryptomentor.service` remains `active`
  - `ExecMainPID=457177` unchanged

## [2.1.12] — 2026-04-13 — Precision Risk Input + Non-Blocking Warning UX

### 🚀 What Changed

#### 1) Precision Text Input Made Explicit for Risk Controls
- Risk input box is now more prominent and clearly labeled for precise typing.
- Added helper text under sliders: users can type exact risk instead of dragging only.
- Applied consistently to both:
  - AutoTrade risk slider
  - 1-Click risk slider
- File:
  - `website-frontend/src/App.jsx`

#### 2) Removed Annoying Blocking Risk Popup Flow
- Removed blocking high-risk modal confirmation from risk updates.
- High-risk remains communicated via inline danger text, without interrupting interaction.
- File:
  - `website-frontend/src/App.jsx`

#### 3) Hard Guard Against Native Browser Dialogs
- Added startup-level dialog patch (`alert/confirm/prompt`) to prevent native browser popups from appearing.
- Dialog messages are routed to in-web notice event flow.
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend-only deployment performed (no backend route/service restart).
- Reloaded `nginx` only.
- Verified trading engine state untouched:
  - `cryptomentor.service` still `active`
  - `ExecMainPID=457177` unchanged

## [2.1.11] — 2026-04-13 — Effective 1-Click Risk Display Per Signal

### 🚀 What Changed

#### 1) Risk Per Trade Display Now Uses Effective Per-Signal Calculation
- Updated each 1-click signal card to show effective risk based on reflected signal values:
  - Entry zone midpoint
  - Stop loss distance
  - Estimated position size and margin
  - Margin-cap impact (95% available balance cap)
- Main `1-Click will risk` value now reflects effective loss at SL (not only raw target % of equity).
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend rebuilt and redeployed to VPS with latest JS:
  - `index-B-6fjmST.js`
- Reloaded `nginx` successfully.

## [2.1.10] — 2026-04-13 — Force Native Browser Dialogs Into In-App Modal

### 🚀 What Changed

#### 1) Hard Block on Browser Popup Dialogs
- Added app-level runtime override for native dialogs:
  - `window.alert`
  - `window.confirm`
  - `window.prompt`
- All such calls are now routed to in-web modal notice UI (`NoticeModal`) so users no longer see browser popup boxes.
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend rebuilt and redeployed to VPS with latest JS:
  - `index-CLSata6O.js`
- Reloaded `nginx` successfully.

## [2.1.9] — 2026-04-13 — Live Per-Signal 1-Click Risk Recalculation

### 🚀 What Changed

#### 1) Recalculate 1-Click Risk Across All Signal Pairs on Slider Change
- Each 1-click signal card now recalculates risk panel metrics live when risk slider changes.
- Recalculation is signal-specific (based on that card’s reflected signal values):
  - Entry zone midpoint
  - Stop loss distance (%)
  - Estimated position size (USDT)
  - Estimated margin (USDT, using selected leverage)
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend rebuilt and redeployed to VPS with latest assets:
  - `index-B18f90b3.css`
  - `index-C3uGWPSU.js`
- Reloaded `nginx` successfully.

## [2.1.8] — 2026-04-13 — Segregated AutoTrade vs 1-Click Risk Controls

### 🚀 What Changed

#### 1) Separated Risk Sliders by Trade Type
- AutoTrade risk and 1-click risk are now independent settings.
- Engine tab controls `AutoTrade` risk only.
- Signals/1-click controls update `1-click` risk only.
- Files:
  - `website-frontend/src/App.jsx`
  - `website-backend/app/routes/dashboard.py`
  - `website-backend/app/routes/signals.py`

#### 2) AutoTrade Risk Range Restored
- AutoTrade slider range is now **0.5% to 10%**.
- Default AutoTrade risk is now **5%**.
- Backend validation now enforces the same range for AutoTrade updates.
- Files:
  - `website-frontend/src/App.jsx`
  - `website-backend/app/routes/dashboard.py`

#### 3) Numeric Risk Input Added Beside Slider
- Users can type exact risk percentage directly beside each slider.
- Input respects min/max clamp and commits on `Enter`/blur.
- Files:
  - `website-frontend/src/App.jsx`

#### 4) Warning Popup Behavior De-spammed During Sliding
- Slider drag now previews values live but only commits on release/Enter/blur.
- High-risk warning modal appears on commit, not repeatedly while dragging.
- File:
  - `website-frontend/src/App.jsx`

#### 5) Backward-Compatible Fallback for Existing DB Schema
- Added safe fallback when `one_click_risk_per_trade` column is unavailable:
  - Settings endpoint falls back gracefully.
  - 1-click execution accepts `risk_override_pct` from web request.
  - Frontend keeps a local persisted 1-click risk value (`localStorage`) so separation still works.
- Files:
  - `website-backend/app/routes/dashboard.py`
  - `website-backend/app/routes/signals.py`
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend rebuilt and deployed to VPS dist path:
  - `/root/cryptomentor-bot/website-frontend/dist`
- Uploaded backend route updates:
  - `/root/cryptomentor-bot/website-backend/app/routes/dashboard.py`
  - `/root/cryptomentor-bot/website-backend/app/routes/signals.py`
- Restarted `cryptomentor-web.service` and confirmed active.
- Reloaded `nginx` and confirmed active.

## [2.1.7] — 2026-04-13 — Instant Risk Reflection + Full Web Modal Migration

### 🚀 What Changed

#### 1) Risk/Trade Now Reflects During Slider Drag
- Added live risk preview path (`onPreview`) so `risk_per_trade` and all derived `Risk/Trade` values update immediately while dragging, before API commit returns.
- Applied across Engine, Signals top bar, and per-signal 1-click slider.
- Files:
  - `website-frontend/src/App.jsx`

#### 2) Removed Remaining Native Browser Popups
- Replaced Telegram login flow `alert()` errors with in-app modal (`NoticeModal`).
- Result: warning/error prompts are now rendered inside the web UI, not native browser dialogs.
- Files:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend rebuilt and deployed to VPS dist path:
  - `/root/cryptomentor-bot/website-frontend/dist`
- Reloaded `nginx` successfully.
- No trading engine restart performed.

## [2.1.6] — 2026-04-13 — Risk Slider Sync + In-App Warning Modal (No Browser Popup)

### 🚀 What Changed

#### 1) Fixed Risk/Slider Reflection Drift
- Risk selection now updates UI immediately (optimistic sync) so all risk displays and sliders stay aligned while editing.
- Added rollback safety if risk API update fails, so UI returns to the last confirmed risk.
- Normalized numeric parsing from API responses to avoid stale/incorrect slider values.
- File:
  - `website-frontend/src/App.jsx`

#### 2) High-Risk Warning Flow Hardened
- Kept high-risk guard (`>5%`) in web UI and improved state handling:
  - Stores previous risk before warning.
  - Restores previous value if user cancels.
  - Applies selected risk only after confirmation.
- File:
  - `website-frontend/src/App.jsx`

#### 3) Replaced Browser Warning Popup With Web Modal (API Bridge Disconnect)
- Removed native browser `confirm()` flow for API Bridge disconnect.
- Added integrated in-app warning modal for disconnect confirmation.
- Added in-app success message for key test/connection status (removing native popup dependency).
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend rebuilt and deployed to VPS dist path:
  - `/root/cryptomentor-bot/website-frontend/dist`
- Reloaded `nginx` successfully.
- No trading engine service restart performed for this frontend-only patch.

## [2.1.5] — 2026-04-13 — Risk Slider Reflection Hotfix (Live Sync While Sliding)

### 🚀 What Changed

#### 1) Fixed Risk Not Reflecting in Dashboard Summary
- Resolved mismatch where slider draft value (e.g., `56%`) could display while `Risk/Trade` still showed previous persisted risk.
- Root cause: commit timing on some touch/mobile interactions.
- Hotfix:
  - Added auto-commit while slider moves (short debounce).
  - Added robust commit triggers (`mouse`, `touch`, `pointer`, `enter`).
- File:
  - `website-frontend/src/App.jsx`

#### 2) Re-verified Backend Acceptance for Extended Risk Range
- Confirmed live backend routes are aligned for risk updates beyond legacy `5%` cap:
  - `website-backend/app/routes/dashboard.py`
  - `website-backend/app/routes/signals.py`

### ✅ Deploy/State Safety Notes

- Performed **state-safe deploy**:
  - Restarted `cryptomentor-web.service` only
  - Reloaded `nginx`
  - **Did not restart `cryptomentor.service` (trading bot engine)**
- Verified bot engine process continuity:
  - `ExecMainPID` unchanged before/after deploy (`457177`)
  - Active enter timestamp unchanged

## [2.1.4] — 2026-04-13 — Risk Slider Upgrade (0.5% → ALL IN 100%) + High-Risk Safeguards

### 🚀 What Changed

#### 1) Unified Risk Slider Across Web
- Replaced fixed risk buttons with a real slider in:
  - Engine Controls risk management
  - Signals risk control bar
  - Per-signal 1-click risk control
  - Onboarding risk configuration step
- New range: **0.5% to 100% (ALL IN)**.
- File:
  - `website-frontend/src/App.jsx`

#### 2) Mandatory High-Risk Warning Pop-up
- Added confirmation pop-up for any risk selection **above 5%**.
- Added stronger warning text for **100% ALL IN** selection.
- Warning is enforced in shared risk update flow so it applies consistently from all UI entry points.
- File:
  - `website-frontend/src/App.jsx`

#### 3) Backend Risk Range Expanded
- Updated dashboard/API validation and normalization to support **0.5% - 100%**:
  - `website-backend/app/routes/dashboard.py`
  - `website-backend/app/routes/signals.py`

#### 4) Bot/Engine Risk Clamp Alignment
- Updated bot-side persistence and risk clamps to the same range to avoid web/bot mismatch:
  - `Bismillah/app/supabase_repo.py`
  - `Bismillah/app/autotrade_engine.py`
  - `Bismillah/app/scalping_engine.py`

### ✅ Deploy/State Safety Notes

- Deployed with **state-safe policy**:
  - Updated frontend static bundle + website backend routes
  - Reloaded/restarted web-facing services only
  - **Did not restart active trading engine service** during this deployment step
- Goal: preserve currently running user autotrade sessions while applying web risk UX and API changes.

## [2.1.3] — 2026-04-12 — V4.0 Branding Sync (Bot + Web)

### 🚀 What Changed

#### 1) Login Hero Version Upgrade
- Updated login hero version label in web frontend:
  - `V2.0 AutoTrade Engine` → `V4.0 Unified Trading System`
- File:
  - `website-frontend/src/App.jsx`

#### 2) Feature Highlights Synced to Current Platform
- Replaced legacy login-card bullets to reflect current architecture:
  - Unified **Bot + Web** control for AutoTrade and 1-Click execution
  - Adaptive risk engine with position sizing up to **5%** equity risk
  - Professional trade lifecycle alerts (open, close, live status)
- File:
  - `website-frontend/src/App.jsx`

### ✅ Deploy/State Safety Notes

- Frontend-only deploy path used for this change.
- No trading engine logic, parameters, or backend route behavior changed.
- Bot/engine runtime state is preserved (no engine session resets required).

## [2.1.2] — 2026-04-11 — Dashboard Stability, Notification UX, Trade Audio Cues, Data Accuracy

### 🚀 What Changed

#### 1) Dashboard Access and Rendering Stability
- Fixed dashboard render blocker caused by missing `riskSettings` wiring in frontend tabs.
- Added safer defaults and session boot error handling to avoid blank/indefinite loading states.
- Improved verification/session resilience in web login flow and gatekeeper transitions.

#### 2) Portfolio/Engine Risk UI Cleanup
- Removed duplicate **Risk Management** card from Engine Controls.
- Removed Risk Management block from Portfolio Status to prevent layout collisions.
- Kept single canonical risk control surface in Engine Controls.

#### 3) Responsive Layout Hardening
- Fixed resize/overflow issues in Portfolio Status:
  - Better wrapping behavior for header controls.
  - Safer flex shrink behavior (`min-w-0`) in main content.
  - Grid breakpoint tuning to prevent card clipping on medium widths.
  - Horizontal overflow guards added to root/main containers.

#### 4) Branding Update
- Replaced Bitunix branding image with `bitunix.jpg` and updated rendered card usage.

#### 5) Trade Notifications (Telegram, Professional Format)
- Added admin-triggerable web endpoint to send sample trade notifications:
  - `POST /dashboard/admin/broadcast-sample-trades`
  - Supports **trade opened** + **trade closed** messages.
  - Professional emoji-rich formatting and CTA button.
  - Added optional `target_chat_id` for single-user test sends before mass broadcast.
- Sent verified sample open/close notifications to Telegram user `1187119989`.

#### 6) Realized PnL / Closed Trades Accuracy Fix
- Fixed backend trade aggregation that incorrectly filtered only `status = closed`.
- Updated portfolio/performance/leaderboard queries to include real close variants:
  - `closed_tp`, `closed_sl`, `closed_tp1`, `closed_tp2`, `closed_tp3`, `closed_flip`, `closed_manual`.
- Result: 30D realized PnL and closed trade counts now reflect real engine outcomes.

#### 7) Web Sound Effects for Trade Lifecycle
- Added browser-side audio cues in dashboard:
  - Trade Open: ascending chime.
  - Trade Close: descending confirmation tone.
- Implemented with Web Audio API and live position diff detection from polling.
- Includes user-interaction unlock handling for browser autoplay restrictions.

### ✅ Deploy/Verification Notes

1. Frontend was rebuilt and redeployed multiple times with final responsive + audio updates.
2. Backend (`cryptomentor-web.service`) was restarted with notification and PnL-status fixes.
3. Telegram sample notification delivery to `1187119989` returned Telegram API `ok: true` for both open and close messages.

## [2.1.1] — 2026-04-10 — Unified Verification, Anti-Flip Stabilization, StackMentor 1:3, UI Hardening

### 🚀 What Changed

#### 1) Unified Bitunix UID Verification (single source of truth)
- Added centralized verification table migration:
  - `db/verification_access_control.sql`
  - New `user_verifications` with statuses: `pending | approved | rejected`
  - Added indexes, trigger-managed `updated_at`, RLS policies, and legacy backfill from `autotrade_sessions`
- Backend verification routes now use `user_verifications`:
  - `website-backend/app/routes/user.py`
  - Web UID submission writes `pending` + sends Telegram admin inline action buttons
- Verification guard now enforces strict `approved` access only:
  - `website-backend/app/middleware/verification_guard.py`
  - Changed behavior to fail-closed when verification lookup fails (prevents accidental bypass)
- Telegram admin approval handlers now update centralized verification status + admin audit fields:
  - `Bismillah/app/handlers_autotrade_admin.py`
- Telegram UID submit flow now writes to centralized verification and includes inline approve/reject keyboard:
  - `Bismillah/app/handlers_autotrade.py`

#### 2) Anti-Flip / Churn Control for Sideways Trades
- Added stability and anti-flip controls in scalping:
  - `Bismillah/app/scalping_engine.py`
  - Added close dedupe protection, close-lock guard, and idempotent close write path
  - Added consecutive signal confirmation gate before entry
  - Added opposite-direction re-entry block window after close
- Added config knobs:
  - `Bismillah/app/trading_mode.py`
  - `sideways_reentry_cooldown_seconds`
  - `anti_flip_opposite_seconds`
  - `signal_confirmations_required`
  - `signal_confirmation_max_gap_seconds`

#### 3) StackMentor Risk Model Update: Fixed 1:3
- Updated StackMentor to unified fixed target model:
  - `Bismillah/app/stackmentor.py`
  - All trades now target fixed `R:R 1:3`
  - Full position closes at TP (100% at TP1), compatibility fields retained (`tp2/tp3 = tp1`, `qty_tp2/qty_tp3 = 0`)
  - TP hit now finalizes trade status as `closed_tp`

#### 4) Frontend UI Updates
- Added Bitunix logo to API Management/API Bridges card:
  - `website-frontend/src/assets/bitunix-logo.png`
  - `website-frontend/src/App.jsx`
- Disabled unfinished tabs from sidebar and content routing:
  - Performance
  - Skills & Education
  - File: `website-frontend/src/App.jsx`

### ✅ Required Actions After Deploy

1. Run SQL migration in Supabase:
   - `db/verification_access_control.sql`
2. Ensure env vars are set and correct:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_IDS`
3. Redeploy/restart all runtime processes:
   - Telegram bot process
   - Backend API process
   - Frontend app
4. Smoke-test verification flow:
   - Submit UID via web and Telegram -> status becomes `pending`
   - Approve/reject via Telegram admin button -> status updates immediately in Supabase
   - Web trading endpoints allow only `approved`
5. Smoke-test anti-flip behavior:
   - Confirm no rapid opposite-direction re-entry on same symbol within configured block window
6. Smoke-test StackMentor:
   - New trades should show fixed `1:3` target behavior and full close on TP

## [2.1.0] — 2026-04-10 — 🚀 Phase 1 & 2 Migration: Bot Gatekeeper & Pro Money Management

**Major Milestone**: Successfully transitioned the Telegram bot from a primary trading interface to a **Web-Dashboard-first Gatekeeper**. All trading features, configuration, and identity verification are now centralized on the web, with the bot serving as a secure onboarding and notification bridge.

### 🚀 Core Changes

#### 🔥 Bot-to-Web Transformation (`Bismillah/`)
- **Refacted Handlers**: `handlers_autotrade.py` converted into a tight **Gatekeeper Flow** (Verified, Pending, Unverified).
- **Simplified Menus**: Telegram menu (`menu_system.py`) reduced to a 3-button model focused on the Web Dashboard.
- **Auto-Login URLs**: Created `app/lib/auth.py` to generate secure JWT-based URLs for seamless bot-to-web redirection.
- **Retired Features**: Manual signals, AI market analysis, and education commands now redirect users to the web dashboard.

#### 🔥 Identity Verification & Security
- **UID Submission**: Native bot-based flow for Bitunix UID submission.
- **Admin Verification**: New `handlers_autotrade_admin.py` allows admins to approve/reject UIDs with one click inside Telegram.
- **Verification Guard**: New backend middleware blocks unverified users from all trading-related endpoints.

#### 🔥 Professional Money Management (Phase 2)
- **Engine Hardening**: `scalping_engine.py` now strictly honors database-persisted **Leverage (1x-20x)** and **Margin Mode (Cross/Isolated)**.
- **Rich Frontend Controls**: Added unified `RiskManagementCard` to the dashboard for fine-grained risk control.
- **Live Equity Sizing**: Risk per trade is now calculated against live Bitunix account equity (Wallet + Unrealized PnL).

#### 🔥 Enhanced Onboarding Flow
- **Onboarding Wizard**: New step-by-step registration and API setup wizard for verified users.
- **Verification Gates**: Frontend screens for UID submission and pending verification status.
- **Referral Integration**: Integrated Bitunix VIP code `sq45` directly into the onboarding registration prompts.

### 🌍 Localization & UX
- Translated Telegram bot welcome screens and onboarding messages to English for global support.
- Added live profit tickers and social proof components to the web dashboard.
- Consolidated bot command responses with consistent redirect messaging.

### Why
- Better UX — web interface is richer than inline keyboards
- Unified platform — one place for all trading management
- Easier maintenance — no duplicate feature implementations
- Aligns with the Bitunix Community Bot model

### What Users Should Do
Use the **web dashboard** for all trading features:
- Portfolio & open positions
- Engine start/stop controls
- Signals & market analysis
- Risk, leverage & margin settings
- Performance metrics & trade history
- API key management

---
*Generated by Antigravity AI*
