# 매일 아카이브 데이터를 대시보드 JSON으로 갱신 (+ 레포트)
# Windows 작업 스케줄러: 매일 06:00

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
    Write-Log "=== 일일 갱신 시작 ==="
    python $ReportScript --message "일일 자동 갱신 시작" --step3-done --step4-active 2>&1 | Out-Null

    $TelegramScript = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\telegram_api_collect.py"
    $TelegramEnv = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\.env"
    if ((Test-Path $TelegramScript) -and (Test-Path $TelegramEnv)) {
        Write-Log "텔레그램 수집..."
        Push-Location (Split-Path $TelegramScript)
        python telegram_api_collect.py --limit 200 2>&1 | ForEach-Object { Write-Log $_ }
        Pop-Location
    }

    Write-Log "dashboard.json 빌드..."
    Push-Location $Root
    python scripts/build_dashboard.py 2>&1 | ForEach-Object { Write-Log $_ }
    Pop-Location

    Write-Log "=== 일일 갱신 완료 ==="
    python $ReportScript --message "일일 갱신 완료 (06:00 스케줄)" --step3-done --step4-done 2>&1 | Out-Null
} catch {
    Write-Log "ERROR: $_"
    python $ReportScript --message "일일 갱신 오류: $_" --step3-done --step4-active 2>&1 | Out-Null
    exit 1
}
