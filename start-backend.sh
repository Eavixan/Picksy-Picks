#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"
if [ ! -d .venv ]; then
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv
  else
    python -m venv .venv
  fi
fi
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
