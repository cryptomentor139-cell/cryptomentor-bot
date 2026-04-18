import importlib
import os
import sys
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WEB_BACKEND = os.path.join(_ROOT, "website-backend")
if _WEB_BACKEND not in sys.path:
    sys.path.insert(0, _WEB_BACKEND)

# Ensure this test imports the website-backend `app` package, not Bismillah's `app`.
for _name in list(sys.modules.keys()):
    if _name == "app" or _name.startswith("app."):
        del sys.modules[_name]

dashboard = importlib.import_module("app.routes.dashboard")


class _Result:
    def __init__(self, data):
        self.data = data


class _FakeTable:
    def __init__(self, db, table_name: str):
        self._db = db
        self._table_name = table_name
        self._op = "select"
        self._filters = {}
        self._payload = {}

    def select(self, _fields: str = "*"):
        self._op = "select"
        return self

    def eq(self, key: str, value):
        self._filters[key] = value
        return self

    def limit(self, _n: int):
        return self

    def update(self, payload: dict):
        self._op = "update"
        self._payload = dict(payload)
        return self

    def upsert(self, payload: dict, on_conflict: str | None = None):
        self._op = "upsert"
        self._payload = dict(payload)
        _ = on_conflict
        return self

    def execute(self):
        if self._table_name != "autotrade_sessions":
            return _Result([])

        sessions = self._db["autotrade_sessions"]
        tg_id = self._filters.get("telegram_id")

        if self._op == "select":
            if tg_id is None:
                rows = list(sessions.values())
            else:
                row = sessions.get(int(tg_id))
                rows = [dict(row)] if row else []
            return _Result(rows)

        if self._op == "update":
            row = sessions.setdefault(int(tg_id), {"telegram_id": int(tg_id)})
            row.update(self._payload)
            return _Result([dict(row)])

        if self._op == "upsert":
            upsert_tg = int(self._payload["telegram_id"])
            row = sessions.setdefault(upsert_tg, {"telegram_id": upsert_tg})
            row.update(self._payload)
            return _Result([dict(row)])

        return _Result([])


class _FakeSupabase:
    def __init__(self, sessions: dict[int, dict]):
        self._db = {"autotrade_sessions": sessions}

    def table(self, name: str):
        return _FakeTable(self._db, name)


@pytest.mark.asyncio
async def test_auto_mode_mixed_forces_off_and_locked(monkeypatch):
    sessions = {
        101: {
            "telegram_id": 101,
            "trading_mode": "mixed",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "active",
            "engine_active": True,
        }
    }
    fake = _FakeSupabase(sessions)
    monkeypatch.setattr(dashboard, "_client", lambda: fake)

    result = await dashboard.update_engine_auto_mode(
        dashboard.EngineAutoModePayload(enabled=True),
        tg_id=101,
    )

    assert result["success"] is True
    assert result["engine"]["auto_mode_enabled"] is False
    assert result["engine"]["auto_mode_locked"] is True
    assert sessions[101]["auto_mode_enabled"] is False


@pytest.mark.asyncio
async def test_mode_switch_stopped_persists_only_without_live_switch(monkeypatch):
    sessions = {
        102: {
            "telegram_id": 102,
            "trading_mode": "swing",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "stopped",
            "engine_active": False,
        }
    }
    fake = _FakeSupabase(sessions)
    switch_mock = AsyncMock(return_value={"success": True})

    monkeypatch.setattr(dashboard, "_client", lambda: fake)
    monkeypatch.setattr(dashboard, "_is_engine_runtime_running", lambda _tg, _row=None: False)
    monkeypatch.setattr(dashboard, "_switch_user_mode_runtime", switch_mock)

    result = await dashboard.update_engine_mode(
        dashboard.EngineModePayload(trading_mode="scalping"),
        tg_id=102,
    )

    assert result["runtime_action"] == "persisted_only"
    assert result["engine"]["trading_mode"] == "scalping"
    switch_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_mode_switch_running_uses_live_switch_path(monkeypatch):
    sessions = {
        103: {
            "telegram_id": 103,
            "trading_mode": "swing",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "active",
            "engine_active": True,
        }
    }
    fake = _FakeSupabase(sessions)

    async def _switch_and_persist(tg_id: int, trading_mode: str):
        sessions[int(tg_id)]["trading_mode"] = trading_mode
        return {"success": True, "message": "ok"}

    switch_mock = AsyncMock(side_effect=_switch_and_persist)

    monkeypatch.setattr(dashboard, "_client", lambda: fake)
    monkeypatch.setattr(dashboard, "_is_engine_runtime_running", lambda _tg, _row=None: True)
    monkeypatch.setattr(dashboard, "_switch_user_mode_runtime", switch_mock)

    result = await dashboard.update_engine_mode(
        dashboard.EngineModePayload(trading_mode="scalping"),
        tg_id=103,
    )

    assert result["runtime_action"] == "switched_live"
    assert result["engine"]["trading_mode"] == "scalping"
    switch_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_mode_switch_running_dependency_missing_returns_503_and_keeps_db_mode(monkeypatch):
    sessions = {
        106: {
            "telegram_id": 106,
            "trading_mode": "swing",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "active",
            "engine_active": True,
        }
    }
    fake = _FakeSupabase(sessions)
    switch_mock = AsyncMock(
        return_value={
            "success": False,
            "error_code": "runtime_dependency_missing",
            "dependency": "telegram",
            "message": "runtime_dependency_missing:telegram Install required runtime dependencies.",
        }
    )

    monkeypatch.setattr(dashboard, "_client", lambda: fake)
    monkeypatch.setattr(dashboard, "_is_engine_runtime_running", lambda _tg, _row=None: True)
    monkeypatch.setattr(dashboard, "_switch_user_mode_runtime", switch_mock)

    with pytest.raises(HTTPException) as err:
        await dashboard.update_engine_mode(
            dashboard.EngineModePayload(trading_mode="scalping"),
            tg_id=106,
        )

    assert err.value.status_code == 503
    assert "runtime_dependency_missing:telegram" in str(err.value.detail)
    assert sessions[106]["trading_mode"] == "swing"
    switch_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_mode_switch_running_failure_does_not_persist_mode(monkeypatch):
    sessions = {
        107: {
            "telegram_id": 107,
            "trading_mode": "swing",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "active",
            "engine_active": True,
        }
    }
    fake = _FakeSupabase(sessions)
    switch_mock = AsyncMock(
        return_value={
            "success": False,
            "error_code": "runtime_switch_failed",
            "message": "unexpected runtime failure",
        }
    )

    monkeypatch.setattr(dashboard, "_client", lambda: fake)
    monkeypatch.setattr(dashboard, "_is_engine_runtime_running", lambda _tg, _row=None: True)
    monkeypatch.setattr(dashboard, "_switch_user_mode_runtime", switch_mock)

    with pytest.raises(HTTPException) as err:
        await dashboard.update_engine_mode(
            dashboard.EngineModePayload(trading_mode="scalping"),
            tg_id=107,
        )

    assert err.value.status_code == 500
    assert "unexpected runtime failure" in str(err.value.detail)
    assert sessions[107]["trading_mode"] == "swing"
    switch_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_switching_to_mixed_forces_auto_mode_off(monkeypatch):
    sessions = {
        104: {
            "telegram_id": 104,
            "trading_mode": "swing",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "stopped",
            "engine_active": False,
        }
    }
    fake = _FakeSupabase(sessions)
    monkeypatch.setattr(dashboard, "_client", lambda: fake)
    monkeypatch.setattr(dashboard, "_is_engine_runtime_running", lambda _tg, _row=None: False)

    result = await dashboard.update_engine_mode(
        dashboard.EngineModePayload(trading_mode="mixed"),
        tg_id=104,
    )

    assert result["engine"]["trading_mode"] == "mixed"
    assert result["engine"]["auto_mode_enabled"] is False
    assert result["engine"]["auto_mode_locked"] is True
    assert sessions[104]["auto_mode_enabled"] is False


@pytest.mark.asyncio
async def test_stackmentor_preference_toggle_persists(monkeypatch):
    sessions = {
        105: {
            "telegram_id": 105,
            "trading_mode": "swing",
            "auto_mode_enabled": True,
            "stackmentor_enabled": True,
            "status": "active",
            "engine_active": True,
        }
    }
    fake = _FakeSupabase(sessions)
    monkeypatch.setattr(dashboard, "_client", lambda: fake)

    result = await dashboard.update_engine_stackmentor(
        dashboard.EngineStackMentorPayload(enabled=False),
        tg_id=105,
    )

    assert result["success"] is True
    assert result["engine"]["stackmentor_enabled"] is False
    assert result["engine"]["stackmentor_active"] is False
    assert sessions[105]["stackmentor_enabled"] is False
