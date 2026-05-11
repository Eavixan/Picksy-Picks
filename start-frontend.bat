@echo off
setlocal
set ROOT=%~dp0

powershell -NoProfile -Command "$connections = Get-NetTCPConnection -State Listen -LocalPort 4173 -ErrorAction SilentlyContinue; foreach ($conn in $connections) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }"

cd /d "%ROOT%frontend"

call npm install
call npm run start
