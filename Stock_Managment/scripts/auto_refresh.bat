@echo off
REM 더블클릭 또는 작업 스케줄러에서 실행
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_refresh.ps1"
pause
