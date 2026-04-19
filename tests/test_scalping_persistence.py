import os
import sys
from types import SimpleNamespace

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BISMILLAH = os.path.join(_ROOT, "Bismillah")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _BISMILLAH not in sys.path:
    sys.path.insert(0, _BISMILLAH)

import app.scalping_engine as scalping_engine  # type: ignore
from app.scalping_engine import ScalpingEngine  # type: ignore


@pytest.mark.asyncio
async def test_scalping_save_position_persists_rr_ratio_and_consistent_qty(monkeypatch):
    captured = {}

    class _FakeInsert:
        def __init__(self, row):
            self._row = row

        def execute(self):
            captured["row"] = self._row
            return SimpleNamespace(data=[{"id": 321}])

    class _FakeTable:
        def insert(self, row):
            return _FakeInsert(row)

    class _FakeClient:
        def table(self, _name):
            return _FakeTable()

    monkeypatch.setattr(scalping_engine, "_client", lambda: _FakeClient())

    engine = ScalpingEngine.__new__(ScalpingEngine)
    engine.user_id = 777

    position = SimpleNamespace(
        symbol="BTCUSDT",
        side="BUY",
        entry_price=100.0,
        quantity=0.25,
        leverage=10,
        tp_price=103.0,
        sl_price=98.0,
    )
    signal = SimpleNamespace(
        confidence=76,
        rr_ratio=9.9,  # should be overridden by derived levels
        reasons=["trend_align"],
        playbook_match_score=0.0,
        effective_risk_pct=1.0,
        risk_overlay_pct=0.0,
    )

    trade_id = await engine._save_position_to_db(position, signal, order_id="OID-1")
    assert trade_id == 321
    assert captured["row"]["qty"] == pytest.approx(0.25)
    assert captured["row"]["quantity"] == pytest.approx(0.25)
    assert captured["row"]["original_quantity"] == pytest.approx(0.25)
    assert captured["row"]["remaining_quantity"] == pytest.approx(0.25)
    assert captured["row"]["rr_ratio"] == pytest.approx(1.5)


@pytest.mark.asyncio
async def test_scalping_save_position_rejects_non_positive_quantity(monkeypatch):
    class _FakeInsert:
        def execute(self):
            raise AssertionError("insert must not be called for non-positive qty")

    class _FakeTable:
        def insert(self, _row):
            return _FakeInsert()

    class _FakeClient:
        def table(self, _name):
            return _FakeTable()

    monkeypatch.setattr(scalping_engine, "_client", lambda: _FakeClient())

    engine = ScalpingEngine.__new__(ScalpingEngine)
    engine.user_id = 778

    position = SimpleNamespace(
        symbol="ETHUSDT",
        side="SELL",
        entry_price=2000.0,
        quantity=0.0,
        leverage=10,
        tp_price=1970.0,
        sl_price=2015.0,
    )
    signal = SimpleNamespace(
        confidence=80,
        rr_ratio=1.5,
        reasons=[],
        playbook_match_score=0.0,
        effective_risk_pct=1.0,
        risk_overlay_pct=0.0,
    )

    trade_id = await engine._save_position_to_db(position, signal, order_id="OID-2")
    assert trade_id is None
