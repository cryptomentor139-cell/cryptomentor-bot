import pytest

try:
    from Bismillah.app import stackmentor as sm
    from Bismillah.app.trade_execution import open_managed_position
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "Bismillah"))
    from app import stackmentor as sm
    from app.trade_execution import open_managed_position


def _set_runner_config(monkeypatch, enabled: bool, tp1_pct: float = 0.80, tp3_rr: float = 5.0):
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "runner_enabled", bool(enabled))
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "tp1_pct", float(tp1_pct))
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "tp2_pct", 0.0)
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "tp3_pct", max(0.0, 1.0 - float(tp1_pct)))
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "target_rr", 3.0)
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "tp1_rr", 3.0)
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "tp2_rr", 3.0)
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "tp3_rr", float(tp3_rr))
    monkeypatch.setitem(sm.STACKMENTOR_CONFIG, "breakeven_after_tp1", bool(enabled))


def test_stackmentor_levels_and_splits_runner_on(monkeypatch):
    _set_runner_config(monkeypatch, enabled=True, tp1_pct=0.80, tp3_rr=5.0)

    tp1, tp2, tp3 = sm.calculate_stackmentor_levels(entry_price=100.0, sl_price=95.0, side="LONG")
    assert tp1 == pytest.approx(115.0)
    assert tp2 == pytest.approx(115.0)
    assert tp3 == pytest.approx(125.0)

    q1, q2, q3 = sm.calculate_qty_splits(total_qty=1.0, min_qty=0.0, precision=3)
    assert q1 == pytest.approx(0.8)
    assert q2 == pytest.approx(0.0)
    assert q3 == pytest.approx(0.2)


def test_stackmentor_splits_runner_off(monkeypatch):
    _set_runner_config(monkeypatch, enabled=False, tp1_pct=0.80, tp3_rr=5.0)

    tp1, tp2, tp3 = sm.calculate_stackmentor_levels(entry_price=100.0, sl_price=95.0, side="LONG")
    assert tp1 == pytest.approx(115.0)
    assert tp2 == pytest.approx(115.0)
    assert tp3 == pytest.approx(115.0)

    q1, q2, q3 = sm.calculate_qty_splits(total_qty=1.0, min_qty=0.0, precision=3)
    assert q1 == pytest.approx(1.0)
    assert q2 == pytest.approx(0.0)
    assert q3 == pytest.approx(0.0)


def test_runner_splits_collapse_when_runner_fragment_below_min_qty(monkeypatch):
    _set_runner_config(monkeypatch, enabled=True, tp1_pct=0.80, tp3_rr=5.0)
    q1, q2, q3 = sm.calculate_qty_splits(total_qty=0.01, min_qty=0.005, precision=4)
    assert q1 == pytest.approx(0.01)
    assert q2 == pytest.approx(0.0)
    assert q3 == pytest.approx(0.0)


class _DummyClient:
    def __init__(self):
        self.placed = []

    def get_ticker(self, symbol: str):
        return {"success": True, "mark_price": 100.0}

    def place_order_with_tpsl(self, symbol, side, quantity, tp_price, sl_price):
        self.placed.append(
            {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "tp_price": tp_price,
                "sl_price": sl_price,
            }
        )
        return {"success": True, "order_id": "runner-test-order"}


@pytest.mark.asyncio
async def test_open_managed_position_uses_tp3_as_exchange_tp_when_runner_on(monkeypatch):
    _set_runner_config(monkeypatch, enabled=True, tp1_pct=0.80, tp3_rr=5.0)
    client = _DummyClient()

    result = await open_managed_position(
        client=client,
        user_id=1,
        symbol="BTCUSDT",
        side="LONG",
        entry_price=100.0,
        sl_price=95.0,
        quantity=1.0,
        leverage=5,
        set_leverage=False,
        register_in_stackmentor=False,
        reconcile=False,
    )
    assert result.success is True
    assert client.placed, "place_order_with_tpsl should be called"
    assert client.placed[-1]["tp_price"] == pytest.approx(125.0)
