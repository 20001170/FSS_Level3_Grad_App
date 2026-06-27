@echo off
REM Windows launcher
cd /d "%~dp0"
if not exist ".venv" (
  echo First run: creating virtual environment and installing dependencies...
  python -m venv .venv
  .venv\Scripts\pip install --quiet -r requirements.txt
)
.venv\Scripts\python app.py
