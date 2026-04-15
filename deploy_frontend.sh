#!/bin/bash
# Atomic frontend deploy for VPS with stale-bundle verification.
# Usage: ./deploy_frontend.sh [source_dir]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SOURCE_DIR="${1:-.}"
SOURCE_DIST="$SOURCE_DIR/dist"
CANONICAL_BASE="/var/www/cryptomentor"
RELEASES_DIR="$CANONICAL_BASE/releases"
CURRENT_LINK="$CANONICAL_BASE/current"
RELEASE_ID="$(date +%Y%m%d_%H%M%S)"
NEW_RELEASE_DIR="$RELEASES_DIR/$RELEASE_ID"
LIVE_URL="https://cryptomentor.id"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}🚀 ATOMIC FRONTEND DEPLOY (CRYPTOMENTOR)${NC}"
echo -e "${BLUE}============================================${NC}"
echo

if [ ! -d "$SOURCE_DIST" ]; then
  echo -e "${RED}✗ Missing build output: $SOURCE_DIST${NC}"
  exit 1
fi

echo -e "${YELLOW}Source dist:${NC} $SOURCE_DIST"
echo -e "${YELLOW}Canonical root:${NC} $CURRENT_LINK"
echo

mkdir -p "$RELEASES_DIR"
mkdir -p "$NEW_RELEASE_DIR"

echo -e "${YELLOW}📤 Uploading to new release directory...${NC}"
rsync -a --delete "$SOURCE_DIST/" "$NEW_RELEASE_DIR/"

if [ ! -f "$NEW_RELEASE_DIR/index.html" ]; then
  echo -e "${RED}✗ Release is invalid: missing index.html${NC}"
  exit 1
fi

ASSET_COUNT="$(find "$NEW_RELEASE_DIR/assets" -type f 2>/dev/null | wc -l || true)"
if [ "$ASSET_COUNT" -eq 0 ]; then
  echo -e "${RED}✗ Release is invalid: no hashed assets found in assets/${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Release prepared: $NEW_RELEASE_DIR${NC}"
echo -e "${GREEN}✓ Asset files: $ASSET_COUNT${NC}"
echo

echo -e "${YELLOW}🔗 Switching symlink atomically...${NC}"
ln -sfn "$NEW_RELEASE_DIR" "$CURRENT_LINK"

echo -e "${YELLOW}🔄 Validating and reloading nginx...${NC}"
nginx -t
systemctl reload nginx

LOCAL_INDEX_SHA="$(sha256sum "$NEW_RELEASE_DIR/index.html" | awk '{print $1}')"
REMOTE_INDEX_SHA="$(curl -fsSL "$LIVE_URL/" | sha256sum | awk '{print $1}')"
echo -e "${YELLOW}🔍 index.html sha (local):${NC}  $LOCAL_INDEX_SHA"
echo -e "${YELLOW}🔍 index.html sha (remote):${NC} $REMOTE_INDEX_SHA"

if [ "$LOCAL_INDEX_SHA" != "$REMOTE_INDEX_SHA" ]; then
  echo -e "${RED}✗ Stale bundle detected: live index does not match deployed release${NC}"
  exit 1
fi

echo
echo -e "${YELLOW}🧪 Cache header sanity check (index should be no-cache/no-store)${NC}"
curl -sI "$LIVE_URL/" | grep -iE 'cache-control|etag|last-modified' || true

echo
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✅ DEPLOY COMPLETED${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Release:${NC} $NEW_RELEASE_DIR"
echo -e "${BLUE}Live root:${NC} $CURRENT_LINK"
echo -e "${BLUE}URL:${NC} $LIVE_URL"
echo
