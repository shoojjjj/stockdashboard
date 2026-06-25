@echo off
REM 풀 파이프라인: 수집 → 빌드 → git push → Vercel
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_deploy.ps1" %*
