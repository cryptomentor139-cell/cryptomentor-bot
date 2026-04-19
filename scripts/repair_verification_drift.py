#!/usr/bin/env python3
"""
Repair verification drift between user_verifications and autotrade_sessions.

Default mode is dry-run (no writes). Use --apply to persist repairs.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple


def _bootstrap_import_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bismillah_root = repo_root / "Bismillah"
    if str(bismillah_root) not in sys.path:
        sys.path.insert(0, str(bismillah_root))


def _map_legacy_status(raw_status: str) -> Optional[str]:
    status = str(raw_status or "").strip().lower()
    if status in {"uid_verified", "active"}:
        return "approved"
    if status == "uid_rejected":
        return "rejected"
    return None


def _iter_pending_rows(s, limit: Optional[int], page_size: int = 500) -> List[Dict]:
    rows: List[Dict] = []
    start = 0
    while True:
        end = start + page_size - 1
        res = (
            s.table("user_verifications")
            .select("telegram_id, status, bitunix_uid, reviewed_at")
            .eq("status", "pending")
            .range(start, end)
            .execute()
        )
        batch = res.data or []
        if not batch:
            break
        rows.extend(batch)
        if limit is not None and len(rows) >= limit:
            return rows[:limit]
        if len(batch) < page_size:
            break
        start += page_size
    return rows


def _get_legacy_session(s, telegram_id: int) -> Tuple[Optional[str], Optional[str]]:
    res = (
        s.table("autotrade_sessions")
        .select("status, bitunix_uid")
        .eq("telegram_id", int(telegram_id))
        .limit(1)
        .execute()
    )
    row = (res.data or [None])[0]
    if not row:
        return None, None
    return row.get("status"), row.get("bitunix_uid")


def run(apply: bool, limit: Optional[int]) -> int:
    _bootstrap_import_path()
    from app.supabase_repo import _client

    s = _client()
    now_iso = datetime.now(timezone.utc).isoformat()

    scanned = 0
    eligible = 0
    updated = 0
    unchanged = 0
    errors = 0
    candidates: List[Dict] = []

    pending_rows = _iter_pending_rows(s, limit=limit)

    for row in pending_rows:
        scanned += 1
        telegram_id = int(row.get("telegram_id"))
        uv_uid = row.get("bitunix_uid")
        legacy_status, legacy_uid = _get_legacy_session(s, telegram_id)
        target_status = _map_legacy_status(legacy_status or "")

        if not target_status:
            unchanged += 1
            continue

        eligible += 1
        candidate = {
            "telegram_id": telegram_id,
            "from_status": "pending",
            "to_status": target_status,
            "legacy_status": legacy_status,
            "uv_uid": uv_uid,
            "legacy_uid": legacy_uid,
        }
        candidates.append(candidate)

        if not apply:
            unchanged += 1
            continue

        try:
            payload = {
                "status": target_status,
                "updated_at": now_iso,
            }
            if not uv_uid and legacy_uid:
                payload["bitunix_uid"] = legacy_uid
            if row.get("reviewed_at") is None:
                payload["reviewed_at"] = now_iso
            (
                s.table("user_verifications")
                .update(payload)
                .eq("telegram_id", telegram_id)
                .eq("status", "pending")
                .execute()
            )
            updated += 1
        except Exception as exc:
            errors += 1
            print(f"[ERROR] telegram_id={telegram_id} failed update: {exc}")

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== Verification Drift Repair ({mode}) ===")
    print(f"scanned={scanned}")
    print(f"eligible={eligible}")
    print(f"updated={updated}")
    print(f"unchanged={unchanged}")
    print(f"errors={errors}")

    if candidates:
        print("\nEligible candidates:")
        for c in candidates:
            print(
                f"- telegram_id={c['telegram_id']} from={c['from_status']} "
                f"to={c['to_status']} legacy={c['legacy_status']} "
                f"uv_uid={c['uv_uid'] or '-'} legacy_uid={c['legacy_uid'] or '-'}"
            )
    else:
        print("\nNo eligible drift rows found.")

    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair pending user_verifications rows that already have terminal legacy autotrade status."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist updates. Omit this flag for dry-run mode.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of pending verification rows to scan.",
    )
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        print("--limit must be > 0")
        return 2

    return run(apply=bool(args.apply), limit=args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
