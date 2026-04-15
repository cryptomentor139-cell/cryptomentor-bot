from dataclasses import dataclass


@dataclass(frozen=True)
class ExitPlan:
    stop_loss: float
    take_profit_1: float
    take_profit_2: float


def build_exit_plan(entry_price: float, side: str, atr: float) -> ExitPlan:
    atr = max(atr, entry_price * 0.002)
    if side == "BUY":
        return ExitPlan(
            stop_loss=entry_price - atr,
            take_profit_1=entry_price + atr * 1.5,
            take_profit_2=entry_price + atr * 2.5,
        )
    return ExitPlan(
        stop_loss=entry_price + atr,
        take_profit_1=entry_price - atr * 1.5,
        take_profit_2=entry_price - atr * 2.5,
    )
