"""
Professional Position Sizing Module
Calculates position size based on risk percentage and stop loss distance.

This enables:
- Safe compounding as balance grows
- Account protection from blow-ups
- Consistent risk management
- Professional money management
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_position_size(
    balance: float,
    risk_pct: float,
    entry_price: float,
    sl_price: float,
    leverage: int,
    symbol: str = "BTCUSDT"
) -> Dict:
    """
    Calculate position size based on risk percentage.
    
    Formula:
    1. Risk Amount = Balance × Risk%
    2. SL Distance% = |Entry - SL| / Entry
    3. Position Size = Risk Amount / SL Distance%
    4. Margin Required = Position Size / Leverage
    5. Quantity = Position Size / Entry Price
    """
    
    try:
        # Validate inputs
        if balance <= 0:
            return {
                'valid': False, 'error': 'Balance must be positive',
                'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': 0, 'sl_distance_pct': 0,
            }
        
        if risk_pct <= 0 or risk_pct > 10:
            return {
                'valid': False, 'error': 'Risk percentage must be between 0 and 10%',
                'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': 0, 'sl_distance_pct': 0,
            }
        
        if entry_price <= 0 or sl_price <= 0:
            return {
                'valid': False, 'error': 'Entry and SL prices must be positive',
                'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': 0, 'sl_distance_pct': 0,
            }
        
        if leverage <= 0:
            return {
                'valid': False, 'error': 'Leverage must be positive',
                'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': 0, 'sl_distance_pct': 0,
            }
        
        # Calculate risk amount
        risk_amount = balance * (risk_pct / 100.0)
        
        # Calculate SL distance as percentage
        sl_distance_pct = abs(entry_price - sl_price) / entry_price
        
        # Validate SL distance (must be reasonable)
        if sl_distance_pct < 0.001:  # Less than 0.1%
            return {
                'valid': False, 'error': 'Stop loss too tight (< 0.1%)',
                'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': risk_amount, 'sl_distance_pct': sl_distance_pct,
            }
        
        if sl_distance_pct > 0.15:  # More than 15%
            return {
                'valid': False, 'error': 'Stop loss too wide (> 15%)',
                'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': risk_amount, 'sl_distance_pct': sl_distance_pct,
            }
        
        # Calculate position size
        position_size_usdt = risk_amount / sl_distance_pct

        # --- HARDENING: Absolute Position Risk Cap ---
        # Ensure position value never exceeds 20% of account balance
        # This protects against catastrophic loss if the SL fails to trigger in CROSS margin
        MAX_POSITION_VALUE_PCT = 0.20 
        absolute_cap = balance * MAX_POSITION_VALUE_PCT
        
        if position_size_usdt > absolute_cap:
            logger.info(f"[Sizing] Position size ${position_size_usdt:.2f} exceeds absolute safety cap (20% of balance). Clamping to ${absolute_cap:.2f}")
            position_size_usdt = absolute_cap

        # Calculate margin required
        margin_required = position_size_usdt / leverage
        
        # Validate margin doesn't exceed balance
        if margin_required > balance:
            margin_required = balance * 0.95
            position_size_usdt = margin_required * leverage
            
        # Calculate quantity
        qty = position_size_usdt / entry_price
        
        # Get quantity precision for symbol
        try:
            from app.autotrade_engine import QTY_PRECISION
            precision = QTY_PRECISION.get(symbol, 3)
        except ImportError:
            precision = 3
        qty = round(qty, precision)
        
        # Validate minimum quantity
        min_qty = 10 ** (-precision) if precision > 0 else 1
        if qty < min_qty:
            return {
                'valid': False, 'error': f'Quantity too small (min: {min_qty})',
                'position_size_usdt': position_size_usdt, 'margin_required': margin_required, 'qty': qty, 'risk_amount': risk_amount, 'sl_distance_pct': sl_distance_pct,
            }
        
        result = {
            'valid': True,
            'error': None,
            'position_size_usdt': round(position_size_usdt, 2),
            'margin_required': round(margin_required, 2),
            'qty': qty,
            'risk_amount': round(risk_amount, 2),
            'sl_distance_pct': round(sl_distance_pct * 100, 2),
        }
        
        logger.info(
            f"[PositionSizing] Calculated for {symbol}: "
            f"balance={balance:.2f}, risk={risk_pct}%, "
            f"entry={entry_price:.2f}, sl={sl_price:.2f}, "
            f"position={result['position_size_usdt']:.2f}, "
            f"margin={result['margin_required']:.2f}, "
            f"qty={result['qty']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"[PositionSizing] Calculation error: {e}")
        return {
            'valid': False, 'error': f'Calculation error: {str(e)}',
            'position_size_usdt': 0, 'margin_required': 0, 'qty': 0, 'risk_amount': 0, 'sl_distance_pct': 0,
        }


def format_risk_info(balance: float, risk_pct: float) -> str:
    """Format risk information for display to user."""
    risk_amount = balance * (risk_pct / 100.0)
    survivability = int(100 / risk_pct)
    
    if risk_pct <= 1.0:
        level, emoji = "Conservative", "🛡️"
    elif risk_pct <= 2.0:
        level, emoji = "Moderate", "⚖️"
    elif risk_pct <= 3.0:
        level, emoji = "Aggressive", "⚡"
    else:
        level, emoji = "Very Aggressive", "🔥"
    
    return (
        f"{emoji} <b>{level}</b>\n"
        f"Risk per trade: <b>{risk_pct}%</b> (${risk_amount:.2f})\n"
        f"Survivability: <b>{survivability}+</b> consecutive losses\n"
    )


def get_recommended_risk(balance: float) -> float:
    """Get recommended risk percentage based on account size."""
    if balance < 50: return 3.0
    elif balance < 200: return 2.0
    elif balance < 1000: return 1.5
    else: return 1.0


def calculate_position_size_pro(
    balance: float,
    risk_pct: float,
    entry_price: float,
    sl_price: float,
    leverage: int,
    symbol: str,
    max_leverage: int = 50,
    min_sl_dist_pct: float = 0.002,
    qty_precision: Optional[Dict[str, int]] = None,
    min_qty_map: Optional[Dict[str, float]] = None,
) -> Dict:
    """Advanced position sizing with Max Leverage efficiency and dynamic SL adjustment."""
    if qty_precision is None:
        try:
            from app.autotrade_engine import QTY_PRECISION
            qty_precision = QTY_PRECISION
        except ImportError:
            qty_precision = {}
            
    if min_qty_map is None:
        try:
            from app.trade_execution import MIN_QTY_MAP
            min_qty_map = MIN_QTY_MAP
        except ImportError:
            min_qty_map = {}

    precision = qty_precision.get(symbol, 3)
    min_qty = min_qty_map.get(symbol, 10 ** (-precision) if precision > 0 else 1)

    risk_amount = balance * (risk_pct / 100.0)
    sl_dist_abs = abs(entry_price - sl_price)
    sl_dist_pct = sl_dist_abs / entry_price

    maintenance_buffer = 0.005 
    safe_max_leverage = int(0.9 / (sl_dist_pct + maintenance_buffer))
    final_max_leverage = min(max_leverage, safe_max_leverage)
    actual_leverage = max(1, final_max_leverage)

    target_qty = risk_amount / sl_dist_abs
    qty = round(target_qty, precision)

    # --- HARDENING: Absolute Position Risk Cap ---
    MAX_POSITION_VALUE_PCT = 0.20 
    absolute_cap = balance * MAX_POSITION_VALUE_PCT
    notional = qty * entry_price
    
    if notional > absolute_cap:
        logger.info(f"[SizingPro] Notional ${notional:.2f} exceeds absolute safety cap (20%). Clamping.")
        qty = round(absolute_cap / entry_price, precision)
        notional = qty * entry_price

    is_dynamic = False
    is_clamped = False
    actual_sl = sl_price
    
    if qty < min_qty:
        is_dynamic = True
        qty = min_qty
        new_sl_dist = risk_amount / qty
        new_sl_dist_pct = new_sl_dist / entry_price
        
        if new_sl_dist_pct < min_sl_dist_pct:
            new_sl_dist_pct = min_sl_dist_pct
            new_sl_dist = entry_price * new_sl_dist_pct
            is_clamped = True
            
        if sl_price < entry_price:
            actual_sl = entry_price - new_sl_dist
        else:
            actual_sl = entry_price + new_sl_dist
            
        sl_dist_pct = new_sl_dist_pct

    notional = qty * entry_price
    margin_required = notional / actual_leverage
    
    if margin_required > balance * 0.95:
        needed_leverage = int(notional / (balance * 0.95)) + 1
        if needed_leverage <= final_max_leverage:
            actual_leverage = needed_leverage
            margin_required = notional / actual_leverage
        else:
            min_bal_needed = (notional / final_max_leverage) / 0.95
            return {
                'valid': False,
                'error': f'Insufficient balance (${balance:.2f}). Min required: ${min_bal_needed:.2f} at {final_max_leverage}x',
                'qty': 0, 'leverage': actual_leverage
            }

    actual_risk_amount = qty * abs(entry_price - actual_sl)
    actual_risk_pct = (actual_risk_amount / balance) * 100

    return {
        'valid': True,
        'error': None,
        'qty': qty,
        'leverage': actual_leverage,
        'sl_price': round(actual_sl, 8),
        'risk_amount': round(actual_risk_amount, 2),
        'risk_pct': round(actual_risk_pct, 2),
        'margin_required': round(margin_required, 2),
        'position_size_usdt': round(notional, 2),
        'sl_distance_pct': round(sl_dist_pct * 100, 2),
        'is_dynamic': is_dynamic,
        'is_clamped': is_clamped,
        'is_max_leverage': True
    }
