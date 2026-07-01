# Archive -> collect -> git push -> Vercel (ASCII-safe for Windows PowerShell 5.1)

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
        "--step3-done", "--step4-done", "--step5-done", "--step6-done", "--step7-done", "--step8-done",
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

    if ($SkipTelegram) {
        Invoke-Cmd "build only" {
            Push-Location $Root
            python scripts/build_dashboard.py
            Pop-Location
        }
    } else {
        Invoke-Cmd "collect pipeline" {
            Push-Location $Root
            python scripts/collect_pipeline.py
            Pop-Location
        }
        $script:HadChanges = $true
    }

    if (-not $SkipPush) {
        Invoke-Cmd "git commit push" {
            Push-Location $ArchiveRoot
            git add Stock_Managment/public/data 2>&1
            git add Stock_Managment/data/column_index.json 2>&1
            git add Stock_Managment/src Stock_Managment/scripts 2>&1
            git add Progress_Report.html Results_Report.html 2>&1
            git add Progress_Report_*.html 2>&1
            Get-ChildItem -LiteralPath $ArchiveRoot -Directory | ForEach-Object {
                if ($_.Name -match "칼럼|브리핑") {
                    git add $_.FullName 2>&1
                }
            }
            $agentRoot = Join-Path $ArchiveRoot "0_주식_에이전트"
            if (Test-Path $agentRoot) {
                $signalDir = Join-Path $agentRoot "소수몽키_에이전트\03_신호_태그화\신호판"
                if (Test-Path $signalDir) { git add $signalDir 2>&1 }
            }
            $diff = git diff --staged --name-only 2>&1
            if ($diff) {
                $ts = Get-Date -Format "yyyy-MM-dd HH:mm"
                git commit -m "chore: auto-refresh dashboard $ts" 2>&1
                git pull --rebase origin main 2>&1
                git push origin main 2>&1
                if ($LASTEXITCODE -ne 0) {
                    Write-Log "WARN git push failed (exit $LASTEXITCODE)"
                } else {
                    Write-Log "git push ok"
                }
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
        Show-ReportFinal "Daily pipeline complete"
    } else {
        Show-Report "No changes" @("--step3-done", "--step4-done", "--no-open")
    }

} catch {
    Write-Log "FATAL: $_"
    $errArgs = @(
        $ReportScript, "--message", "Pipeline error",
        "--step3-done", "--step4-active", "--smart-open", "--meaningful"
    )
    & python @errArgs 2>&1 | ForEach-Object { Write-Log $_ }
    exit 1
}
