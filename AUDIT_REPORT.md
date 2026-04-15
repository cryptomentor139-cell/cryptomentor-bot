# AUDIT REPORT — CryptoMentor v2.2.4 → v2.2.5
**Generated:** 2026-04-15  
**Auditor:** Automated codebase scan + specification comparison  
**Scope:** website-frontend/src/, website-backend/app/, deploy scripts, nginx config  

---

## LEGEND
- **CRITICAL** — Production-breaking, data integrity or security risk, must fix before any deploy
- **HIGH** — Core feature broken or spec regression, must fix in this release
- **MEDIUM** — Incorrect behavior but not immediately destructive, fix in this release
- **LOW** — Cosmetic or advisory

---

## SECTION A — REFERRAL SYSTEM

### A-1 | CRITICAL | Hardcoded Bitunix referral URL in GatekeeperScreen
**File:** `website-frontend/src/App.jsx:2563`  
**Line:** `<a href="https://www.bitunix.com/register?vipCode=sq45" ...>`  
**Impact:** Every new user landing on the onboarding screen is directed to the hardcoded VIP code `sq45`, bypassing any community partner referral routing. Users who arrived via `?ref=navicrypto` (or any partner) will be sent to the wrong referral destination.  
**Fix required:** Replace with dynamic referral URL from backend partner resolution or centralized fallback config.

---

### A-2 | CRITICAL | Hardcoded Bitunix referral URL in RejectedScreen
**File:** `website-frontend/src/App.jsx:2651`  
**Line:** `<a href="https://www.bitunix.com/register?vipCode=sq45" ...>`  
**Impact:** Same as A-1 — rejected users who try to re-register are sent to the wrong hardcoded VIP code.  
**Fix required:** Dynamic referral URL with same resolution logic as GatekeeperScreen.

---

### A-3 | CRITICAL | No `?ref=` URL parameter capture in frontend
**File:** `website-frontend/src/App.jsx` (entire file)  
**Finding:** The frontend reads `URLSearchParams` only at line 257–258 for `t` (JWT token) and `u` (user) parameters. There is NO code anywhere in App.jsx that reads a `?ref=` parameter from the URL.  
**Impact:** When a user lands on `https://cryptomentor.id/?ref=navicrypto`, the referral code is silently discarded. No community partner is resolved. The subsequent UID submission carries no community context. The fallback hardcoded link is always used.  
**Fix required:** On first load, read `params.get('ref')`, validate/sanitize, persist to localStorage under key `cm_referral_code`, and include in UID submission payload.

---

### A-4 | CRITICAL | UID submission notification hardcodes referral code
**File:** `website-backend/app/routes/user.py:175`  
**Line:** `f"🔗 Referral: sq45"`  
**Impact:** Telegram admin notification always shows `sq45` regardless of which partner the user came from. Admins cannot determine which partner should receive credit.  
**Fix required:** Resolve the community partner from DB using `community_code` stored on the user's verification record, and display actual partner name and referral URL.

---

### A-5 | CRITICAL | `community_code` and `partner_id` not stored in verification record
**File:** `website-backend/app/routes/user.py:123–136`  
**Finding:** The `upsert` into `user_verifications` table stores: `telegram_id`, `bitunix_uid`, `status`, `submitted_via`, `submitted_at`, timestamps. It does NOT store: `community_code`, `partner_id`, `bitunix_referral_url`.  
**Impact:** There is no audit trail connecting a verification to its originating community partner. Community partners receive no notification. Referral attribution is permanently lost.  
**Fix required:** Accept `community_code` in `SubmitUIDRequest`, look up matching `community_partners` record, store `community_code`, `partner_telegram_id`, and `bitunix_referral_url` in the verification upsert.

---

### A-6 | HIGH | Telegram UID verification notification goes to admins ONLY
**File:** `website-backend/app/routes/user.py:159–206`  
**Finding:** Notification loop only iterates `admin_ids`. There is no notification to the matched community partner whose `community_code` the user arrived with.  
**Impact:** Community partners are never notified when one of their referred members submits for verification. Spec requires Telegram notification to both admin AND the matched community partner.  
**Fix required:** After admin notifications, also send a Telegram message to the `telegram_id` stored in `community_partners` record matching the user's `community_code`.

---

### A-7 | HIGH | No backend endpoint to resolve `?ref=` community partner
**File:** `website-backend/app/routes/` (all files checked)  
**Finding:** There is no GET endpoint like `/dashboard/partner-resolve?code=navicrypto` that accepts a community code and returns the matching `bitunix_referral_url`. The frontend has no way to dynamically resolve referral destinations.  
**Fix required:** Add `GET /dashboard/partner?code={community_code}` endpoint returning `bitunix_referral_url`, `community_name`, `partner_id`.

---

## SECTION B — RISK MANAGEMENT

### B-1 | HIGH | AutoTrade risk preset max is 5%, spec requires max 10%
**File:** `website-frontend/src/App.jsx:112`  
**Line:** `const RISK_OPTIONS = [0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0];`  
**Also:** Line 1053 label reads `"Risk Per Trade (0.25% - 5%)"`  
**Impact:** AutoTrade users cannot set risk above 5%. The spec requires the range to extend to 10% with a warning above 5%.  
**Fix required:** Extend `RISK_OPTIONS` to include `7.5` and `10.0`. Update the UI label to `0.25% – 10%`. Add warning text/styling for values >5%.

---

### B-2 | HIGH | AutoTrade has NO slider + numeric input — only preset buttons
**File:** `website-frontend/src/App.jsx:1050–1075`  
**Finding:** The Engine tab Risk Management panel uses a grid of preset buttons (0.25%, 0.5%, 0.75%… 5.0%). There is no continuous slider and no free-text numeric input for AutoTrade.  
**Impact:** Users cannot enter arbitrary precise risk percentages (e.g. 3.7% or 8%). The spec mandates both a slider and numeric text input for AutoTrade, bi-directionally synchronized.  
**Fix required:** Add a slider (range input, 0.25–10%, step 0.25) and a numeric text input to the AutoTrade risk section. Retain preset buttons as shortcuts. Implement bi-directional sync.

---

### B-3 | HIGH | AutoTrade uses leverage preset buttons, not auto max-safe leverage
**File:** `website-frontend/src/App.jsx:1082–1096`  
**Finding:** Leverage is selected from preset buttons: `[5, 10, 20]`. Line 693 in signals.py: `leverage = int(sess.get("leverage") or 10)` reads this preset directly.  
**Impact:** Risk-based position sizing computes the correct `position_size_usdt` but divides by a preset leverage instead of dynamically computing the minimum safe leverage needed. This contradicts the auto max-safe leverage pipeline requirement.  
**Fix required:** Backend should compute `required_leverage = position_size_usdt / available_balance`, cap by exchange rules and safety buffer, and use that. Preset buttons become a "maximum leverage cap" input, not the sole leverage input.

---

### B-4 | MEDIUM | `getRiskDescription()` warning threshold is 1%, should be 5% for AutoTrade
**File:** `website-frontend/src/App.jsx:132–139`  
**Line:** `return '🟠 Amber-Red Risk Zone (>1%) — high exposure...'`  
**Impact:** The amber-red warning fires above 1% for AutoTrade. Spec says AutoTrade warning should appear above 5%. 1-Click Trade can warn at a different threshold. Using the same function for both creates confusion.  
**Fix required:** Separate `getAutoTradeRiskDescription()` (warn above 5%) from `getOneClickRiskDescription()` (keep existing thresholds). Update the Engine tab to use the AutoTrade version.

---

### B-5 | MEDIUM | `risk_zone` in backend signals.py uses 1.0% threshold
**File:** `website-backend/app/routes/signals.py:728`  
**Line:** `risk_zone = "amber_red" if risk_pct > 1.0 else "normal"`  
**Impact:** Backend marks risk zone as amber_red above 1%, inconsistent with intended 5% threshold for AutoTrade.  
**Fix required:** Change threshold to `risk_pct > 5.0` (or make it configurable per `source` field).

---

### B-6 | MEDIUM | No shared position-sizing utility module
**File:** Entire backend  
**Finding:** Position sizing logic exists only inline inside `signals.py:724–748`. The AutoTrade engine path, 1-Click path, and any future SMC path all need the same formula but there is no shared utility function.  
**Fix required:** Extract a shared utility `utils/position_sizing.py` with `compute_position_size(equity, risk_pct, sl_distance_pct, leverage, max_balance_pct=0.95)` and use it from all order paths.

---

## SECTION C — CONFLICT GATE

### C-1 | CRITICAL | No conflict gate exists before order submission
**File:** `website-backend/app/routes/signals.py:624–791` (execute_signal endpoint)  
**Finding:** The 1-click trade execution path does NOT check:
- Whether the user already has an open position on the same symbol/side
- Whether a pending order for the same symbol is already in-flight  
- Cooldown windows after a recent trade or stop-out  
- Anti-flip window (e.g. just closed a LONG, cannot immediately open a SHORT)  
- Re-entry restrictions  
- Stale payload mismatch  
**Impact:** Users can open duplicate positions, flip sides immediately after a stop-out, or exceed position limits.  
**Fix required:** Create `app/services/conflict_gate.py` with a `check_conflicts(tg_id, symbol, side)` function that performs all checks and returns `{allowed: bool, reason: str}`. Call it from every order entry path before placement.

---

### C-2 | HIGH | AutoTrade engine execution path has no conflict gate either
**File:** `website-backend/app/services/bitunix.py` (and any bot engine path)  
**Finding:** No conflict gate call visible in the engine execution layer.  
**Fix required:** Same conflict gate must be invoked from the AutoTrade engine execution path.

---

## SECTION D — SMC TRADING ENGINE

### D-1 | HIGH | SMC engine not implemented
**Finding:** No `smc_trading_engine/` directory or equivalent exists anywhere in the repository. The entire Codex build specification (decision flow, module families, analytics endpoints) has not been implemented.  
**Fix required:** Build the full SMC engine structure as specified in the Codex build document, integrated at the decision/orchestration layer. Execution layer remains the existing Bitunix client.

---

## SECTION E — DEPLOYMENT

### E-1 | HIGH | Frontend deploy script does not build before deploying
**File:** `deploy_frontend.sh`  
**Finding:** The script skips `npm run build`. It copies whatever is in `dist/` — which may be a stale build from a previous session. If a developer forgets to rebuild locally, the VPS receives an outdated bundle.  
**Fix required:** Add `cd website-frontend && npm ci && npm run build` before the rsync step.

---

### E-2 | HIGH | No build version marker in frontend
**File:** `website-frontend/src/App.jsx`, `website-frontend/index.html`, `vite.config.js`  
**Finding:** No `window.__BUILD_VERSION__` injection, no visible version tag in the UI footer, no timestamp baked into the build.  
**Impact:** After deploy it is impossible to verify from the live site which bundle is being served.  
**Fix required:** Inject `window.__BUILD_VERSION__ = "v2.2.5+BUILDDATE"` via `vite.config.js` `define` block. Add a visible version badge in the app footer.

---

### E-3 | MEDIUM | Nginx config missing explicit `Cache-Control` for `/` SPA route
**File:** `website-backend/nginx-www.conf`  
**Finding:** `location = /index.html` correctly sets `no-cache`. The fallback `location /` block (`try_files $uri $uri/ /index.html`) has no explicit cache header. Browsers may cache the HTML response for the root path separately.  
**Fix required:** Add `add_header Cache-Control "no-cache, no-store, must-revalidate"` to the root `location /` block as well.

---

### E-4 | MEDIUM | `deploy.sh` does not clean Python `__pycache__` before restart
**File:** `deploy.sh`  
**Finding:** After `git pull`, the script installs deps and restarts services but does not remove stale `__pycache__` directories. This can cause Python to serve stale bytecode if a .py file was deleted or renamed.  
**Fix required:** Add `find ${PROJECT_DIR} -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true` after git pull.

---

### E-5 | LOW | Backup directories accumulate indefinitely on VPS
**File:** `deploy_frontend.sh:16`  
**Line:** `BACKUP_DIR="/root/cryptomentor-bot/website-frontend/dist.backup.$(date +%Y%m%d_%H%M%S)"`  
**Finding:** Each deploy creates a new backup. No cleanup of old backups.  
**Fix required:** After successful deploy, prune backups older than 7 days.

---

## SECTION F — SUMMARY TABLE

| ID  | Severity | Area             | File / Location                                  | Short Description                                              |
|-----|----------|------------------|--------------------------------------------------|----------------------------------------------------------------|
| A-1 | CRITICAL | Referral         | App.jsx:2563                                     | Hardcoded vipCode=sq45 in GatekeeperScreen                     |
| A-2 | CRITICAL | Referral         | App.jsx:2651                                     | Hardcoded vipCode=sq45 in RejectedScreen                       |
| A-3 | CRITICAL | Referral         | App.jsx (entire)                                 | No ?ref= URL parameter capture or persistence                  |
| A-4 | CRITICAL | Referral         | user.py:175                                      | Telegram notification hardcodes "Referral: sq45"               |
| A-5 | CRITICAL | Referral         | user.py:123–136                                  | community_code / partner_id not stored in verification record  |
| A-6 | HIGH     | Referral         | user.py:159–206                                  | Telegram UID notification goes to admins only, not partner     |
| A-7 | HIGH     | Referral         | Backend routes (missing endpoint)                | No GET /partner?code= endpoint for frontend partner resolution |
| B-1 | HIGH     | Risk             | App.jsx:112                                      | AutoTrade RISK_OPTIONS max is 5%, spec requires 10%            |
| B-2 | HIGH     | Risk             | App.jsx:1050–1075                                | AutoTrade has no slider+numeric input, only preset buttons     |
| B-3 | HIGH     | Risk             | App.jsx:1082–1096 / signals.py:693               | Leverage preset used instead of auto max-safe leverage         |
| B-4 | MEDIUM   | Risk             | App.jsx:132–139                                  | Warning threshold 1% instead of 5% for AutoTrade              |
| B-5 | MEDIUM   | Risk             | signals.py:728                                   | Backend risk_zone threshold 1.0% instead of 5%                |
| B-6 | MEDIUM   | Risk             | Backend (missing utility)                        | No shared position-sizing utility module                       |
| C-1 | CRITICAL | Conflict Gate    | signals.py:624–791                               | No conflict gate before 1-Click order submission               |
| C-2 | HIGH     | Conflict Gate    | services/bitunix.py                              | No conflict gate in AutoTrade execution path                   |
| D-1 | HIGH     | SMC Engine       | Repository root                                  | SMC engine not implemented — Codex build spec unbuilt          |
| E-1 | HIGH     | Deployment       | deploy_frontend.sh                               | Frontend not rebuilt before deploy                             |
| E-2 | HIGH     | Deployment       | App.jsx / vite.config.js                         | No build version marker in frontend                            |
| E-3 | MEDIUM   | Deployment       | nginx-www.conf                                   | Root SPA route missing explicit no-cache header                |
| E-4 | MEDIUM   | Deployment       | deploy.sh                                        | __pycache__ not cleaned before backend restart                 |
| E-5 | LOW      | Deployment       | deploy_frontend.sh:16                            | Old backup directories accumulate on VPS                       |

**Critical:** 5 findings  
**High:** 8 findings  
**Medium:** 5 findings  
**Low:** 1 finding  
**Total:** 19 findings

---

## WHAT IS CORRECT (not regressions)

- Nginx `index.html` cache headers are correct (`no-cache, no-store, must-revalidate`) ✓
- Nginx `/assets/` uses `immutable` cache — hash-named assets will never stale ✓
- No service worker present — no SW stale cache risk ✓
- `deploy_frontend.sh` uses `rsync --delete` — removes old files not in new dist ✓
- Backend risk formula is correct: `risk_amount = equity × risk_pct; position_size_usdt = risk_amount / sl_distance_pct` ✓
- 1-Click Trade slider already has `max="100"` (not capped at 10) ✓
- 1-Click numeric input already allows up to 100 ✓
- Community partner registration flow stores `bitunix_referral_url` in DB ✓
- Referral tab in dashboard shows `bitunix_referral_url` from DB ✓

---

*End of AUDIT_REPORT.md*
