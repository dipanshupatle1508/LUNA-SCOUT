#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements.txt
printf '%s\n' 'Open http://127.0.0.1:8000 in your browser. Keep this terminal open.'
exec .venv/bin/python run.py
