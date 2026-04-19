import pytest
from datetime import datetime, timedelta, timezone
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BISMILLAH = os.path.join(_ROOT, "Bismillah")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _BISMILLAH not in sys.path:
    sys.path.insert(0, _BISMILLAH)

try:
    from Bismillah.app.adaptive_confluence import (
        classify_outcome_class,
        build_adaptive_metrics,
        compute_next_adaptive_state,
        default_adaptive_state,
    )
except ImportError:
    from app.adaptive_confluence import (  # type: ignore
        classify_outcome_class,
        build_adaptive_metrics,
        compute_next_adaptive_state,
        default_adaptive_state,
    )


def _mk_trade(status, pnl, close_reason=None, loss_reasoning="", entry_reasons=None, closed_at=None):
    if closed_at is None:
        closed_at = datetime.now(timezone.utc).isoformat()
    return {
        "status": status,
        "close_reason": close_reason,
        "pnl_usdt": pnl,
        "loss_reasoning": loss_reasoning,
        "entry_reasons": entry_reasons or [],
        "closed_at": closed_at,
    }


def test_classification_status_primary_with_missing_close_reason():
    row = _mk_trade(status="closed_sl", pnl=-1.0, close_reason=None)
    assert classify_outcome_class(row) == "strategy_loss"


def test_classification_ops_reconcile_detected_from_reasoning():
    row = _mk_trade(
        status="closed_sl",
        pnl=-0.1,
        loss_reasoning="Reconciled from exchange — position no longer open",
    )
    assert classify_outcome_class(row) == "ops_reconcile"


def test_classification_ops_reconcile_detected_from_status():
    row = _mk_trade(status="stale_reconcile", pnl=0.0, close_reason="stale_reconcile")
    assert classify_outcome_class(row) == "ops_reconcile"


def test_classification_zero_pnl_reconcile_not_strategy_win():
    row = _mk_trade(
        status="closed_tp",
        pnl=0.0,
        close_reason="closed_tp",
        loss_reasoning="Reconciled from exchange — position no longer open; reason=stale_reconcile; near_flat=1",
    )
    assert classify_outcome_class(row) == "ops_reconcile"


def test_build_metrics_counts_weak_confluence_shares():
    now = datetime.now(timezone.utc)
    trades = [
        _mk_trade(
            status="closed_sl",
            pnl=-1,
            entry_reasons=["RSI Oversold"],
            closed_at=(now - timedelta(days=1)).isoformat(),
        ),
        _mk_trade(
            status="closed_sl",
            pnl=-1,
            entry_reasons=["Volume spike 1.3x"],
            closed_at=(now - timedelta(days=1)).isoformat(),
        ),
        _mk_trade(
            status="closed_tp",
            pnl=1,
            entry_reasons=["Bullish OB", "Volume spike 1.5x"],
            closed_at=(now - timedelta(days=1)).isoformat(),
        ),
    ]
    m = build_adaptive_metrics(trades, now_utc=now)
    assert m["strategy_sample_size"] == 3
    assert pytest.approx(m["entry_without_ob_fvg_loss_share"], rel=1e-3) == 1.0
    assert pytest.approx(m["entry_without_volume_loss_share"], rel=1e-3) == 0.5


def test_controller_tightens_when_loss_high_and_volume_healthy():
    prev = default_adaptive_state()
    prev["strategy_sample_size"] = 120
    prev["baseline_loss_rate"] = 0.30
    prev["target_loss_lower"] = 0.27
    prev["target_loss_upper"] = 0.33
    prev["baseline_trade_count_per_day"] = 8.0
    prev["last_adapted_at"] = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
    metrics = {
        "strategy_loss_rate": 0.42,
        "entry_without_ob_fvg_loss_share": 0.60,
        "entry_without_volume_loss_share": 0.55,
        "trade_count_per_day": 9.0,
        "strategy_sample_size": 180,
        "ops_reconcile_rate": 0.2,
    }
    nxt = compute_next_adaptive_state(prev, metrics)
    assert nxt["conf_delta"] > prev["conf_delta"]
    assert nxt["volume_min_ratio_delta"] >= prev["volume_min_ratio_delta"]
    assert nxt["ob_fvg_requirement_mode"] == "required_when_risk_high"


def test_controller_relaxes_when_loss_low_but_trade_count_collapses():
    prev = default_adaptive_state()
    prev["conf_delta"] = 2
    prev["volume_min_ratio_delta"] = 0.10
    prev["baseline_loss_rate"] = 0.30
    prev["target_loss_lower"] = 0.27
    prev["target_loss_upper"] = 0.33
    prev["baseline_trade_count_per_day"] = 10.0
    prev["last_adapted_at"] = (datetime.now(timezone.utc) - timedelta(hours=9)).isoformat()
    metrics = {
        "strategy_loss_rate": 0.20,
        "entry_without_ob_fvg_loss_share": 0.2,
        "entry_without_volume_loss_share": 0.2,
        "trade_count_per_day": 4.0,
        "strategy_sample_size": 100,
        "ops_reconcile_rate": 0.1,
    }
    nxt = compute_next_adaptive_state(prev, metrics)
    assert nxt["conf_delta"] < prev["conf_delta"]
    assert nxt["volume_min_ratio_delta"] <= prev["volume_min_ratio_delta"]
