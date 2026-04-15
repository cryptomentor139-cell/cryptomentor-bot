#!/bin/bash
# Verify deployed frontend release contents and live references.
# Usage: verify_frontend_release.sh [dist_dir] [site_url]

set -euo pipefail

DIST_DIR="${1:-/root/cryptomentor-bot/website-frontend/dist}"
SITE_URL="${2:-https://cryptomentor.id}"

if [ ! -f "$DIST_DIR/index.html" ]; then
  echo "✗ index.html not found in $DIST_DIR"
  exit 1
fi
if [ ! -f "$DIST_DIR/release-meta.json" ]; then
  echo "✗ release-meta.json not found in $DIST_DIR"
  exit 1
fi

echo "✓ local index.html + release-meta.json found"

mapfile -t assets < <(grep -Eo 'assets/[^"'"'"']+\.(js|css)' "$DIST_DIR/index.html" | sort -u)
if [ "${#assets[@]}" -eq 0 ]; then
  echo "✗ no hashed assets referenced by index.html"
  exit 1
fi

for asset in "${assets[@]}"; do
  if [ ! -f "$DIST_DIR/$asset" ]; then
    echo "✗ missing asset: $DIST_DIR/$asset"
    exit 1
  fi
done
echo "✓ local hashed assets exist (${#assets[@]} files)"

if command -v curl >/dev/null 2>&1; then
  live_index="$(curl -fsSL --max-time 20 "$SITE_URL/" || true)"
  live_meta="$(curl -fsSL --max-time 20 "$SITE_URL/release-meta.json" || true)"
  if [ -n "$live_index" ]; then
    for asset in "${assets[@]}"; do
      if ! printf '%s' "$live_index" | grep -Fq "$asset"; then
        echo "✗ live index mismatch, missing asset reference: $asset"
        exit 1
      fi
    done
    echo "✓ live index references current hashed assets"
  else
    echo "⚠ unable to fetch live index from $SITE_URL"
  fi
  if [ -n "$live_meta" ]; then
    local_marker="$(grep -Eo '"build_marker"\s*:\s*"[^"]+"' "$DIST_DIR/release-meta.json" | head -n1 | cut -d'"' -f4)"
    live_marker="$(printf '%s' "$live_meta" | grep -Eo '"build_marker"\s*:\s*"[^"]+"' | head -n1 | cut -d'"' -f4)"
    if [ -n "$local_marker" ] && [ -n "$live_marker" ] && [ "$local_marker" != "$live_marker" ]; then
      echo "✗ live release marker mismatch: local=$local_marker live=$live_marker"
      exit 1
    fi
    echo "✓ live release marker matches local build"
  else
    echo "⚠ unable to fetch live release-meta.json from $SITE_URL/release-meta.json"
  fi
fi

echo "✓ frontend release verification passed"
