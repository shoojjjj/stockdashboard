# 매일 아카이브 → 대시보드 → GitHub → Vercel 전체 파이프라인
# Report popup: only on meaningful completion (smart-open, max 1/hour)

param(
    [switch]$SkipTelegram,
    [switch]$SkipPush,
    [switch]$SkipVercel
)

$Root = Split-Path -Parent $PSScriptRoot
$ArchiveRoot = Split-Path -Parent $Root
$LogDir = Join-Path $Root "logs"
$LogFile = Join-Path $LogDir "refresh_$(Get-Date -Format 'yyyy-MM-dd').log"
$ReportScript = Join-Path $PSScriptRoot "generate_progress_report.py"
$HadChanges = $false

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

function Show-Report($message, [string[]]$extraArgs) {
    $allArgs = @($ReportScript, "--message", $message, "--no-open") + $extraArgs
    $out = & python @allArgs 2>&1
    foreach ($line in $out) { Write-Log $line }
}

function Show-ReportFinal($message) {
    $allArgs = @(
        $ReportScript, "--message", $message,
        "--step3-done", "--step4-done",
        "--smart-open", "--meaningful"
    )
    $out = & python @allArgs 2>&1
    foreach ($line in $out) { Write-Log $line }
}

function Invoke-Cmd($label, [scriptblock]$Block) {
    Write-Log "--- $label ---"
    try {
        & $Block *>&1 | ForEach-Object { Write-Log "$_" }
    } catch {
        Write-Log "WARN [$label]: $_"
    }
}

try {
    Show-Report "pipeline start" @("--step3-done", "--step4-active")
    Write-Log "=== pipeline start ==="

    if (-not $SkipTelegram) {
        $TelegramScript = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\telegram_api_collect.py"
        $TelegramEnv = Join-Path $ArchiveRoot "0_주식_에이전트\소수몽키_에이전트\01_텔레그램_원천파서\.env"
        if ((Test-Path $TelegramScript) -and (Test-Path $TelegramEnv)) {
            Invoke-Cmd "telegram collect" {
                Push-Location (Split-Path $TelegramScript)
                python telegram_api_collect.py --limit 200
                Pop-Location
            }
            $script:HadChanges = $true
        } else {
            Write-Log "telegram skip - no .env"
        }
    }

    Invoke-Cmd "build dashboard.json" {
        Push-Location $Root
        python scripts/build_dashboard.py
        Pop-Location
    }

    if (-not $SkipPush) {
        Invoke-Cmd "git commit push" {
            Push-Location $ArchiveRoot
            git add Stock_Managment/public/data/dashboard.json Progress_Report.html 2>&1
            git add Progress_Report_*.html Stock_Managment/public/data/health.json 2>&1
            $diff = git diff --staged --name-only 2>&1
            if ($diff) {
                git commit -m "chore: auto-refresh dashboard $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>&1
                git push origin main 2>&1
                Write-Log "git push ok"
                $script:HadChanges = $true
            } else {
                Write-Log "git no changes - skip"
            }
            Pop-Location
        }
    }

    if (-not $SkipVercel) {
        Invoke-Cmd "vercel deploy" {
            Push-Location $Root
            npx vercel deploy --prod --yes
            Pop-Location
        }
        $script:HadChanges = $true
    }

    Write-Log "=== pipeline done ==="
    if ($HadChanges) {
        Show-ReportFinal "Daily pipeline complete (meaningful update)"
    } else {
        Show-Report "No changes - report file only" @("--step3-done", "--step4-done", "--no-open")
    }

} catch {
    Write-Log "FATAL: $_"
    $allArgs = @($ReportScript, "--message", "Pipeline error", "--step3-done", "--step4-active", "--smart-open", "--meaningful")
    & python @allArgs 2>&1 | ForEach-Object { Write-Log $_ }
    exit 1
}
