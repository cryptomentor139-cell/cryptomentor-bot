#!/bin/bash
# Atomic frontend deploy for VPS.
# Usage: ./deploy_frontend.sh [source_dir] [site_url]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SOURCE_DIR="${1:-.}"
SITE_URL="${2:-https://cryptomentor.id}"
APP_ROOT="/root/cryptomentor-bot/website-frontend"
RELEASES_DIR="$APP_ROOT/releases"
ARCHIVE_DIR="$APP_ROOT/releases_archive"
CURRENT_LINK="$APP_ROOT/dist"
KEEP_RELEASES="${KEEP_RELEASES:-5}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_SCRIPT="$SCRIPT_DIR/tools/verify_frontend_release.sh"

if [ ! -d "$SOURCE_DIR/dist" ]; then
  echo -e "${RED}✗ Missing dist directory: $SOURCE_DIR/dist${NC}"
  exit 1
fi

BUILD_TAG="$(date +%Y%m%d_%H%M%S)"
if command -v git >/dev/null 2>&1; then
  GIT_SHA="$(git -C "$SOURCE_DIR" rev-parse --short HEAD 2>/dev/null || true)"
else
  GIT_SHA=""
fi
RELEASE_ID="${BUILD_TAG}${GIT_SHA:+_${GIT_SHA}}"
STAGE_DIR="$RELEASES_DIR/$RELEASE_ID"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Atomic Frontend Deploy${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${YELLOW}Source: $SOURCE_DIR/dist${NC}"
echo -e "${YELLOW}Release: $STAGE_DIR${NC}"
echo ""

mkdir -p "$RELEASES_DIR" "$ARCHIVE_DIR"

echo -e "${YELLOW}1) Stage release artifacts...${NC}"
mkdir -p "$STAGE_DIR"
rsync -a --delete "$SOURCE_DIR/dist/" "$STAGE_DIR/"

if [ ! -f "$STAGE_DIR/index.html" ]; then
  echo -e "${RED}✗ index.html missing in staged release${NC}"
  exit 1
fi
if [ ! -f "$STAGE_DIR/release-meta.json" ]; then
  echo -e "${RED}✗ release-meta.json missing in staged release${NC}"
  exit 1
fi

echo -e "${YELLOW}2) Promote release atomically...${NC}"
if [ -e "$CURRENT_LINK" ] && [ ! -L "$CURRENT_LINK" ]; then
  LEGACY_BACKUP="$ARCHIVE_DIR/dist_legacy_${BUILD_TAG}"
  mv "$CURRENT_LINK" "$LEGACY_BACKUP"
  echo -e "${YELLOW}  archived legacy dist -> $LEGACY_BACKUP${NC}"
fi
ln -sfn "$STAGE_DIR" "$CURRENT_LINK"

echo -e "${YELLOW}3) Archive stale releases...${NC}"
mapfile -t release_paths < <(find "$RELEASES_DIR" -mindepth 1 -maxdepth 1 -type d | sort -r)
if [ "${#release_paths[@]}" -gt "$KEEP_RELEASES" ]; then
  for old_release in "${release_paths[@]:$KEEP_RELEASES}"; do
    target="$ARCHIVE_DIR/$(basename "$old_release")"
    mv "$old_release" "$target"
    echo -e "${YELLOW}  archived stale release: $target${NC}"
  done
fi

echo -e "${YELLOW}4) Reload nginx...${NC}"
if sudo systemctl reload nginx; then
  echo -e "${GREEN}✓ nginx reload ok${NC}"
else
  echo -e "${RED}✗ nginx reload failed${NC}"
  exit 1
fi

echo -e "${YELLOW}5) Post-deploy verification...${NC}"
if [ -x "$VERIFY_SCRIPT" ]; then
  "$VERIFY_SCRIPT" "$CURRENT_LINK" "$SITE_URL"
else
  echo -e "${YELLOW}⚠ verify script missing/executable: $VERIFY_SCRIPT${NC}"
fi

FILE_COUNT="$(find "$CURRENT_LINK" -type f | wc -l | tr -d ' ')"
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✓ Deploy completed${NC}"
echo -e "${BLUE}URL: $SITE_URL${NC}"
echo -e "${BLUE}Release: $RELEASE_ID${NC}"
echo -e "${BLUE}Files: $FILE_COUNT${NC}"
echo -e "${BLUE}Current symlink: $CURRENT_LINK -> $(readlink -f "$CURRENT_LINK")${NC}"
echo -e "${BLUE}============================================${NC}"
