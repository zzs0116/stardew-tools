#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# 建议本地安装 http-server（只需第一次）
if ! npx --yes --quiet http-server --version >/dev/null 2>&1; then
  echo "Installing http-server locally..."
  npm i -D http-server
fi

echo
echo "Starting static server at http://127.0.0.1:5500"
echo "Root: $(pwd)/public"
echo
npx http-server public -p 5500