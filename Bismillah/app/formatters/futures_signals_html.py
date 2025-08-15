
from __future__ import annotations
from typing import Dict, Any, List

def _money(v: float, short: bool = False) -> str:
    try:
        x = float(v)
    except Exception:
        return str(v)
    if not short:
        return f"${x:,.2f}"
    # short
    n = x
    for unit in ["","K","M","B","T"]:
        if abs(n) < 1000:
            return f"${n:,.2f}{unit}"
        n /= 1000.0
    return f"${n:,.2f}P"

def _pct(v: float) -> str:
    try:
        x = float(v)
        sign = "+" if x > 0 else ""
        return f"{sign}{x:.2f}%"
    except Exception:
        return str(v)

def _rr(rr) -> str:
    try:
        x = float(rr)
        s = f"{x:.1f}".rstrip("0").rstrip(".")
        return f"{s}:1"
    except Exception:
        return str(rr)

def _trend(trend: str):
    t = (trend or "").lower()
    if t == "up": return "Bullish", "🟢", "LONG"
    if t == "down": return "Bearish", "🔴", "SHORT"
    return "Neutral", "😐", "NEUTRAL"

def format_futures_signals_html(rep: Dict[str, Any]) -> str:
    g = rep["global"]
    sigs: List[Dict[str,Any]] = rep["signals"]
    lines = []
    lines.append("🚨 <b>FUTURES SIGNALS – SUPPLY &amp; DEMAND ANALYSIS</b>")
    lines.append("")
    lines.append(f"🕐 <b>Scan Time</b>: {rep['scan_time']}")
    lines.append(f"📊 <b>Signals Found</b>: {len(sigs)} (Confidence ≥ {rep['threshold']:.2f}%)")
    lines.append("")
    lines.append("💰 <b>GLOBAL METRICS:</b>")
    lines.append(f"• Total Market Cap: {_money(g['market_cap'], short=True)}")
    lines.append(f"• 24h Market Change: {_pct(g.get('change_pct_24h', 0.0))}")
    lines.append(f"• Total Volume 24h: {_money(g['volume_24h'], short=True)}")
    lines.append(f"• Active Cryptocurrencies: {int(g.get('active_cryptocurrencies', 0)):,}")
    lines.append(f"• BTC Dominance: {float(g.get('btc_dominance', 0.0)):.1f}%")
    lines.append(f"• ETH Dominance: {float(g.get('eth_dominance', 0.0)):.1f}%")
    lines.append("")

    if not sigs:
        lines += [
            "❌ Tidak ada sinyal memenuhi syarat",
            "",
            "⚠️ TRADING DISCLAIMER:",
            "• Signals berbasis Supply &amp; Demand analysis",
            "• Gunakan proper risk management",
            "• Position sizing sesuai risk level",
            "• DYOR sebelum trading",
            "",
            "📡 Next scan akan mengacak koin berbeda",
            "🔄 Jalankan ulang untuk variasi sinyal",
        ]
        return "\n".join(lines)

    for idx, it in enumerate(sigs, 1):
        trend_word, trend_emoji, side = _trend(it.get("trend"))
        lines.append(f"<b>{idx}. {it.get('coin','?')} {trend_emoji} {side}</b>")
        if "confidence" in it:
            lines.append(f"⭐️ Confidence: {float(it['confidence']):.2f}%")
        if it.get("entry") is not None:
            lines.append(f"💰 Entry: {_money(it['entry'])}")
        if it.get("stop") is not None:
            lines.append(f"🛑 Stop Loss: {_money(it['stop'])}")
        if it.get("tp1") is not None:
            lines.append(f"🎯 TP1: {_money(it['tp1'])}")
        if it.get("tp2") is not None:
            lines.append(f"🎯 TP2: {_money(it['tp2'])}")
        if it.get("rr") is not None:
            lines.append(f"📊 R/R Ratio: {_rr(it['rr'])}")
        lines.append(f"🔄 Trend: {trend_word}")
        if it.get("structure"):
            lines.append(f"⚡️ Structure: {it['structure']}")
        if it.get("reason"):
            lines.append(f"🧠 Reason: {it['reason']}")
        if "change_24h" in it:
            lines.append(f"📈 24h Change: {_pct(it['change_24h'])}")
        lines.append("")  # separator

    lines += [
        "⚠️ <b>TRADING DISCLAIMER:</b>",
        "• Signals berbasis Supply &amp; Demand analysis",
        "• Gunakan proper risk management",
        "• Position sizing sesuai risk level",
        "• DYOR sebelum trading",
        "",
        "📡 Next scan akan mengacak koin berbeda",
        "🔄 Jalankan ulang untuk variasi sinyal",
        "",
        "👑 <b>Admin Access</b> - Unlimited",
    ]
    return "\n".join(lines)
