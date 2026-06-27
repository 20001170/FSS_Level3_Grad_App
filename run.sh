#!/usr/bin/env bash
# macOS / Linux launcher
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
  echo "First run: creating virtual environment and installing dependencies..."
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet -r requirements.txt
fi
exec ./.venv/bin/python app.py
