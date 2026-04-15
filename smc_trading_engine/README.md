# SMC Trading Engine (Scaffold)

This module provides the isolated SMC decision/orchestration layer scaffold for phased integration.

## Scope
- Deterministic decision flow placeholders (`context_builder` -> `decision_engine`)
- Exchange adapter boundary (`exchange/bitunix_client.py`)
- Analytics-ready API routes for traces and decisions
- Local-first configuration via `.env.example`

## Run
```bash
cd smc_trading_engine
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Notes
- Execution endpoints are intentionally stubbed until endpoint signing/contract finalization.
- Existing production execution stack remains in `Bismillah` during phased rollout.
