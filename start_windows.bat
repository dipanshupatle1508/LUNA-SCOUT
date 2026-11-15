@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  if errorlevel 1 goto :fail
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fail
echo Open http://127.0.0.1:8000 in your browser. Keep this window open.
.venv\Scripts\python.exe run.py
if errorlevel 1 goto :fail
exit /b 0
:fail
echo Setup or server failed. See the error above. Python 3.11 or 3.12 64-bit is recommended.
pause
exit /b 1
