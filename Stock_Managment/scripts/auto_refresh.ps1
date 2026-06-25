# 매일 아카이브 데이터를 대시보드 JSON으로 갱신
# Windows 작업 스케줄러에 등록: 매일 06:00 실행

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ArchiveRoot = Split-Path -Parent $Root
$LogDir = Join-Path $Root "logs"
$LogFile = Join-Path $LogDir "refresh_$(Get-Date -Format 'yyyy-MM-dd').log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

try {
    Write-Log "=== 대시보드 데이터 갱신 시작 ==="

    # 1) 텔레그램 수집 (선택 — .env 있을 때만)
    $TelegramScript = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\telegram_api_collect.py"
    $TelegramEnv = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\.env"
    if ((Test-Path $TelegramScript) -and (Test-Path $TelegramEnv)) {
        Write-Log "텔레그램 수집 실행..."
        Push-Location (Split-Path $TelegramScript)
        python telegram_api_collect.py --days 1 2>&1 | ForEach-Object { Write-Log $_ }
        Pop-Location
    } else {
        Write-Log "텔레그램 수집 스킵 (.env 또는 스크립트 없음)"
    }

    # 2) 대시보드 JSON 빌드
    Write-Log "dashboard.json 빌드..."
    Push-Location $Root
    python scripts/build_dashboard.py 2>&1 | ForEach-Object { Write-Log $_ }
    Pop-Location

    Write-Log "=== 완료 ==="
} catch {
    Write-Log "ERROR: $_"
    exit 1
}
