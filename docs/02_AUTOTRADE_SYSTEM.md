# AutoTrade System - Complete Documentation

**Status:** Production  
**Last Updated:** 2026-04-17

---

## Overview

AutoTrade adalah sistem execution automation yang:
- Scan market 24/7
- Generate and validate signals
- Execute trades with risk controls
- Persist trade lifecycle to Supabase
- Sync behavior across Telegram runtime and web control-plane

---

## Trading Modes

### 1. SCALPING Mode (5m focus)
**Best for:** Sideways/ranging conditions

**Current behavior:**
- Scan interval: **15 seconds** (`ScalpingConfig.scan_interval`)
- Max hold time: **30 minutes** (timeout close policy)
- Confidence + anti-flip + cooldown filters active
- Uses managed execution path (`trade_execution.open_managed_position`)
- Timeout protection: feature-flagged (see section below)

### 2. SWING Mode (15m/1h confluence)
**Best for:** Trending and higher-timeframe continuation setups

**Current behavior:**
- Scan interval: **45 seconds** (`ENGINE_CONFIG.scan_interval`)
- Dynamic candidate queue with confidence/risk gating
- Reversal/flip protections and coordinator ownership rules
- Managed execution with SL/TP validation and reconcile paths

---

## Pair Universe Standard

Pair routing for both swing + scalp is runtime dynamic:
- Source: Bitunix futures tickers (`quoteVol`)
- Selection: **Top 10 USDT pairs**, highest volume first
- API/selector: `get_ranked_top_volume_pairs(10)`
- Refresh TTL: 300s cache window in selector

Fallback policy (fixed):
1. Fresh ticker fetch
2. Last-good cache fallback
3. Bootstrap list fallback (only when cache unavailable)

---

## Adaptive Confluence (Global)

Adaptive fields used by engines:
- `conf_delta`
- `volume_min_ratio_delta`
- `ob_fvg_requirement_mode` (`soft` or `required_when_risk_high`)

Important runtime rules:
- Engine refresh cadence: every **10 minutes**
- Controller minimum adaptation interval: **6 hours**
- Minimum strategy sample for adaptation: **40 trades**
- Decision reasons include `rate_limited`, `insufficient_sample`, `tighten_quality`, `relax_for_volume`

---

## Runtime Risk Overlay (Win Playbook)

Overlay behavior is runtime-only and does not overwrite base stored risk.

Risk bounds:
- Base risk clamp: `0.25%-5.0%`
- Overlay max: `+5.0%`
- Effective risk cap: `10.0%`

Effective formula:
- `effective_risk_pct = min(10.0, base_risk_pct + risk_overlay_pct)`

Guardrails and actions:
- Ramp only when win-rate/expectancy guardrails are healthy
- Ramp step: `+0.25%`
- Brake step: `-0.50%`
- Overlay update minimum interval: `120s`

---

## Timeout Protection Policy (Scalping)

Timeout protection is feature-flagged and backward-safe:
- Primary key: `SCALPING_ADAPTIVE_TIMEOUT_PROTECTION_ENABLED`
- Legacy alias key: `SCALPING_TIMEOUT_PROTECTION_ENABLED`
- Runtime parser supports both keys

Defaults:
- Enabled default: `false`
- Minimum update gap: `SCALPING_TIMEOUT_PROTECTION_MIN_UPDATE_SECONDS` default `45`

---

## Pending Lock Safety

Symbol ownership coordination enforces no stale pending lock drift:
- Pending TTL auto-clear for no-position states: **90 seconds**
- Startup sanitize clears orphan pending locks
- Reconcile paths clear pending-only orphans when exchange has no position
- Stop/restart cleanup calls pending-clear paths

---

## StackMentor Exit Model (Current Runtime)

Default runtime behavior remains **Unified Single-Target Strategy**:
- Fixed target RR uses `target_rr = 3.0`
- Position closes fully at TP target (`qty_tp1=100%`, `qty_tp2=0`, `qty_tp3=0`)

Optional runner mode is feature-flagged (default OFF):
- `STACKMENTOR_RUNNER_ENABLED=false` (default)
- `STACKMENTOR_TP1_CLOSE_PCT=0.80` (default when runner enabled)
- `STACKMENTOR_TP3_RR=5.0` (default when runner enabled)

When runner mode is enabled:
- TP1 remains fixed at **3R** and closes partial size (`qty_tp1=80%` by default)
- SL is moved to breakeven after TP1 fill
- Remaining runner size (`qty_tp3=20%` by default) targets **5R**
- Exchange TP is attached at TP3 while StackMentor monitor executes TP1 partial logic

---

## Terminology Standard

- Use **Equity** for account-value/risk basis.
- Use **Available balance** only for free margin context.
