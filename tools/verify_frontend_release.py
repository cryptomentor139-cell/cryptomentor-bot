#!/usr/bin/env python3
"""
Post-deploy verification for frontend release integrity.

Checks:
1) local index hash == live index hash
2) at least one hashed JS/CSS asset from local index is accessible on live URL
3) cache-control headers are visible for index and assets
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_asset_paths(index_html: str) -> list[str]:
    # Vite build outputs hashed files under /assets/*.js|css
    return sorted(set(re.findall(r'(/assets/[^"\']+\.(?:js|css))', index_html)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", default="website-frontend/dist", help="Local dist directory")
    parser.add_argument("--url", default="https://cryptomentor.id/", help="Live site URL")
    args = parser.parse_args()

    dist = Path(args.dist)
    index_path = dist / "index.html"
    if not index_path.exists():
        print(f"FAIL: missing local index file: {index_path}")
        return 1

    local_index = index_path.read_text(encoding="utf-8")
    local_sha = sha256_text(local_index)

    live_resp = requests.get(args.url, timeout=15)
    live_resp.raise_for_status()
    live_index = live_resp.text
    live_sha = sha256_text(live_index)

    print(f"local index sha256: {local_sha}")
    print(f"live  index sha256: {live_sha}")
    if local_sha != live_sha:
        print("FAIL: stale bundle detected (live index mismatch)")
        return 2

    assets = extract_asset_paths(local_index)
    if not assets:
        print("FAIL: no hashed assets found in local index")
        return 3

    probe_assets = assets[:2]
    for asset_path in probe_assets:
        asset_url = urljoin(args.url, asset_path)
        asset_resp = requests.get(asset_url, timeout=15)
        asset_resp.raise_for_status()
        cache_control = asset_resp.headers.get("Cache-Control", "")
        print(f"asset ok: {asset_path} | cache-control={cache_control or '<none>'}")

    index_cache_control = live_resp.headers.get("Cache-Control", "")
    print(f"index cache-control={index_cache_control or '<none>'}")
    print("PASS: frontend release verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
