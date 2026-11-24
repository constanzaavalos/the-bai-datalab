#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

find_python() {
  for p in python3.12 python3.11 python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
      if "$p" -c 'import sys; raise SystemExit(0 if (3,11) <= sys.version_info[:2] < (3,13) else 1)' >/dev/null 2>&1; then
        echo "$p"
        return 0
      fi
    fi
  done
  return 1
}

PY="$(find_python || true)"
if [ -z "$PY" ]; then
  echo "The B-AI DataLab requires Python 3.11 or 3.12."
  echo "Install Python 3.12 from https://www.python.org/downloads/ and run this file again."
  read -r -p "Press Enter to close..."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "First-time setup: creating a local environment..."
  "$PY" -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r the-bai-datalab-streamlit/requirements.txt
  .venv/bin/python -m pip install -e ./the-bai-datalab-core
fi

echo "Starting The B-AI DataLab v0.17.0..."
cd the-bai-datalab-streamlit
exec ../.venv/bin/python -m streamlit run app.py
