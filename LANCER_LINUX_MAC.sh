#!/usr/bin/env sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 launch.py
elif command -v python >/dev/null 2>&1; then
  python launch.py
else
  echo "Python 3.11-3.13 est nécessaire. Installez Python puis relancez." >&2
  exit 1
fi
