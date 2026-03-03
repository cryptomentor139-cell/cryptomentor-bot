#!/usr/bin/env python3
"""
SMC (Smart Money Concepts) Formatter
Formats SMC analysis data for display in Telegram messages
"""

def format_smc_analysis(smc_result, compact=False):
    """
    Format SMC analysis for display
    
    Args:
        smc_result: Dict from smc_analyzer.analyze()
        compact: If True, return compact format for multi-coin displays
    
    Returns:
        Formatted string for Telegram message
    """
    if 'error' in smc_result:
        return "⚠️ SMC analysis unavailable"
    
    if compact:
        # Compact format for multi-coin signals
        structure = smc_result.get('structure', {})
        trend = structure.trend if hasattr(structure, 'trend') else 'ranging'
        ema_21 = smc_result.get('ema_21', 0)
        current_price = smc_result.get('current_price', 0)
        
        trend_emoji = "📈" if trend == 'uptrend' else "📉" if trend == 'downtrend' else "↔️"
        ema_pos = "↑" if current_price > ema_21 else "↓"
        
        return f"{trend_emoji} {trend.upper()} | EMA21: {ema_pos}"
    
    # Full format for detailed analysis
    text = "\n📊 SMART MONEY CONCEPTS\n\n"
    
    # Order Blocks
    order_blocks = smc_result.get('order_blocks', [])
    if order_blocks:
        text += "🔷 Order Blocks:\n"
        for ob in order_blocks[:2]:  # Show top 2
            emoji = "🟢" if ob.type == 'bullish' else "🔴"
            text += f"  {emoji} {ob.type.title()}: ${ob.low:,.2f} - ${ob.high:,.2f}\n"
            text += f"     Strength: {ob.strength:.0f}%\n"
    
    # Fair Value Gaps
    fvgs = smc_result.get('fvgs', [])
    if fvgs:
        text += "\n⚡ Fair Value Gaps:\n"
        for fvg in fvgs[:2]:  # Show top 2
            emoji = "🟢" if fvg.type == 'bullish' else "🔴"
            text += f"  {emoji} {fvg.type.title()}: ${fvg.bottom:,.2f} - ${fvg.top:,.2f}\n"
    
    # Market Structure
    structure = smc_result.get('structure', {})
    if structure:
        trend = structure.trend if hasattr(structure, 'trend') else 'ranging'
        trend_emoji = "📈" if trend == 'uptrend' else "📉" if trend == 'downtrend' else "↔️"
        text += f"\n{trend_emoji} Structure: {trend.upper()}\n"
        
        if hasattr(structure, 'last_high') and structure.last_high > 0:
            text += f"  • Last HH: ${structure.last_high:,.2f}\n"
        if hasattr(structure, 'last_low') and structure.last_low > 0:
            text += f"  • Last HL: ${structure.last_low:,.2f}\n"
    
    # Week High/Low
    week_high = smc_result.get('week_high', 0)
    week_low = smc_result.get('week_low', 0)
    if week_high > 0 and week_low > 0:
        text += f"\n📊 Week Range:\n"
        text += f"  • High: ${week_high:,.2f}\n"
        text += f"  • Low: ${week_low:,.2f}\n"
    
    # EMA 21
    ema_21 = smc_result.get('ema_21', 0)
    current_price = smc_result.get('current_price', 0)
    if ema_21 > 0 and current_price > 0:
        ema_diff = ((current_price - ema_21) / ema_21) * 100
        ema_emoji = "↑" if ema_diff > 0 else "↓"
        text += f"\n📉 EMA 21: ${ema_21:,.2f} {ema_emoji}\n"
        text += f"  • Price vs EMA: {ema_diff:+.1f}%\n"
    
    return text
