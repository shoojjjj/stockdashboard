# Hourly health check — report browser opens at most once per hour
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
python scripts/health_check.py
python scripts/generate_progress_report.py --message "Hourly health check" --step3-done --step4-done --vercel-password-set --smart-open
Pop-Location
