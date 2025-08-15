
from __future__ import annotations
from typing import Dict, Any

def _money(v: float, short: bool = False) -> str:
    try:
        x = float(v)
    except Exception:
        return str(v)
    if not short:
        return f"${x:,.2f}"
    # short format
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

def format_market_report(rep: Dict[str, Any]) -> str:
    """Format market report as HTML"""
    g = rep["global"]
    
    lines = []
    lines.append("🌐 <b>COMPREHENSIVE MARKET ANALYSIS</b>")
    lines.append("")
    lines.append(f"🕐 <b>Update Time</b>: {rep['report_time']}")
    lines.append("")
    lines.append("💰 <b>GLOBAL MARKET METRICS:</b>")
    lines.append(f"• Total Market Cap: {_money(g['market_cap'], short=True)}")
    lines.append(f"• 24h Market Change: {_pct(g.get('market_cap_change_pct_24h', 0.0))}")
    lines.append(f"• Total Volume 24h: {_money(g['total_volume_24h'], short=True)}")
    lines.append(f"• Active Cryptocurrencies: {int(g.get('active_cryptocurrencies', 0)):,}")
    lines.append("")
    lines.append("👑 <b>MARKET DOMINANCE:</b>")
    lines.append(f"• Bitcoin (BTC): {float(g.get('btc_dominance', 0.0)):.1f}%")
    lines.append(f"• Ethereum (ETH): {float(g.get('eth_dominance', 0.0)):.1f}%")
    lines.append("")
    
    # Market sentiment analysis
    change_pct = g.get('market_cap_change_pct_24h', 0.0)
    if change_pct > 3:
        sentiment = "🟢 <b>Bullish</b> - Strong upward momentum"
    elif change_pct > 0:
        sentiment = "🟡 <b>Neutral-Bullish</b> - Slight positive trend"
    elif change_pct > -3:
        sentiment = "🟡 <b>Neutral-Bearish</b> - Slight negative trend"
    else:
        sentiment = "🔴 <b>Bearish</b> - Strong downward momentum"
    
    lines.append("📊 <b>MARKET SENTIMENT:</b>")
    lines.append(f"• Current: {sentiment}")
    lines.append("")
    lines.append("💡 <b>TRADING INSIGHTS:</b>")
    lines.append("• Use proper risk management")
    lines.append("• Monitor volume for confirmation")
    lines.append("• Consider market dominance shifts")
    lines.append("")
    lines.append("🔄 <b>Data Sources:</b> CoinMarketCap, CoinGecko, Binance")
    
    return "\n".join(lines)
