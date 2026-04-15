from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Position(BaseModel):
    symbol: str
    side: Literal["LONG", "SHORT"]
    entry_price: float
    size: float
    leverage: int
    unrealized_pnl: float = 0.0
    opened_at: datetime


class OrderRequest(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT"] = "MARKET"
    size: float
    leverage: int
    reduce_only: bool = False
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None


class OrderResult(BaseModel):
    success: bool
    order_id: str = ""
    symbol: str
    side: str = ""
    message: str = ""


class AccountInfo(BaseModel):
    equity: float = 0.0
    available_margin: float = 0.0
    unrealized_pnl: float = 0.0


class TradeContext(BaseModel):
    symbol: str
    market_state: str
    liquidity_sweep: bool
    bos_confirmed: bool
    confidence_score: float = Field(ge=0, le=1)
    entry_zone_low: float
    entry_zone_high: float


class TradeDecision(BaseModel):
    symbol: str
    action: Literal["OPEN_LONG", "OPEN_SHORT", "HOLD", "CLOSE"]
    reason: str
    confidence_score: float = Field(ge=0, le=1)
