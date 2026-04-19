"""Helpers for open-trade risk audit messaging and logging."""

from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def format_risk_audit_line(
    *,
    base_risk_pct: Any,
    overlay_pct: Any,
    effective_risk_pct: Any,
    implied_risk_usdt: Any,
) -> str:
    """Format one-line risk audit text for Telegram notifications."""
    base = _as_float(base_risk_pct, 0.0)
    overlay = _as_float(overlay_pct, 0.0)
    effective = _as_float(effective_risk_pct, 0.0)
    implied = _as_float(implied_risk_usdt, 0.0)
    return (
        f"Risk Audit: base {base:.2f}% | overlay {overlay:+.2f}% | "
        f"effective {effective:.2f}% | implied ${implied:.4f}"
    )


def emit_order_open_risk_audit(
    logger,
    *,
    user_id: int,
    symbol: str,
    side: str,
    order_id: str,
    base_risk_pct: Any,
    overlay_pct: Any,
    effective_risk_pct: Any,
    implied_risk_usdt: Any,
) -> None:
    """Emit one structured backend log line for per-order risk audit."""
    base = _as_float(base_risk_pct, 0.0)
    overlay = _as_float(overlay_pct, 0.0)
    effective = _as_float(effective_risk_pct, 0.0)
    implied = _as_float(implied_risk_usdt, 0.0)
    logger.info(
        "order_open_risk_audit user_id=%s symbol=%s side=%s order_id=%s "
        "base_risk=%.2f overlay=%+.2f effective_risk=%.2f implied_risk_usdt=%.4f",
        int(user_id),
        str(symbol),
        str(side),
        str(order_id or "-"),
        base,
        overlay,
        effective,
        implied,
    )
