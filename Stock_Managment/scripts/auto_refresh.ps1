# Daily data refresh — report popup only if meaningful (smart-open)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ArchiveRoot = Split-Path -Parent $Root
$LogDir = Join-Path $Root "logs"
$LogFile = Join-Path $LogDir "refresh_$(Get-Date -Format 'yyyy-MM-dd').log"
$ReportScript = Join-Path $PSScriptRoot "generate_progress_report.py"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

try {
    Write-Log "=== daily refresh start ==="

    $TelegramScript = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\telegram_api_collect.py"
    $TelegramEnv = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\.env"
    if ((Test-Path $TelegramScript) -and (Test-Path $TelegramEnv)) {
        Write-Log "telegram collect..."
        Push-Location (Split-Path $TelegramScript)
        python telegram_api_collect.py --limit 200 2>&1 | ForEach-Object { Write-Log $_ }
        Pop-Location
    }

    Push-Location $Root
    python scripts/build_dashboard.py 2>&1 | ForEach-Object { Write-Log $_ }
    python scripts/health_check.py 2>&1 | ForEach-Object { Write-Log $_ }
    Pop-Location

    Write-Log "=== daily refresh done ==="
    & python $ReportScript --message "Daily refresh done" --step3-done --step4-done --step5-done --step6-done --smart-open --meaningful 2>&1 | ForEach-Object { Write-Log $_ }

} catch {
    Write-Log "ERROR: $_"
    & python $ReportScript --message "Refresh error" --smart-open --meaningful 2>&1 | Out-Null
    exit 1
}
