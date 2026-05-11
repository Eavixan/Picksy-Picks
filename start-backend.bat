@echo off
setlocal
set ROOT=%~dp0
cd /d "%ROOT%backend"

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING"') do (
  set PID8000=%%P
  goto :check_existing_backend
)
goto :setup_backend

:check_existing_backend
echo Port 8000 is in use (PID %PID8000%). Checking existing backend health...
powershell -NoProfile -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' | Out-Null; exit 0 } catch { exit 1 }"
if %errorlevel%==0 (
  echo Existing backend is already running on http://127.0.0.1:8000
  goto :eof
)

echo Port 8000 is occupied by a non-responsive process.
echo Stop that process manually, then rerun start-backend.bat.
exit /b 1

:setup_backend

if not exist .venv (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -m venv .venv
  ) else (
    python -m venv .venv
  )
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\uvicorn.exe" app.main:app --reload --host 127.0.0.1 --port 8000
