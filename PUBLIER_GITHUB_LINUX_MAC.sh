#!/usr/bin/env sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 PUBLIER_GITHUB.py
else
  python PUBLIER_GITHUB.py
fi
