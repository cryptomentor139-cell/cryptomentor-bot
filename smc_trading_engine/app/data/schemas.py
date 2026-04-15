from pydantic import BaseModel


class SignalSnapshot(BaseModel):
    symbol: str
    timeframe: str
    score: float
    decision: str
