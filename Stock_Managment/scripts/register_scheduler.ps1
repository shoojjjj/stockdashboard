# Windows 작업 스케줄러 — 매일 06:00 풀 파이프라인
# 관리자 PowerShell에서 실행

$TaskName = "StockManagment_DailyDeploy"
$Script = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_deploy.ps1"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`" -SkipTelegram"
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

# 기존 refresh 태스크도 유지 (가벼운 갱신용)
$RefreshScript = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_refresh.ps1"
$Action2 = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$RefreshScript`""
Register-ScheduledTask -TaskName "StockManagment_DailyRefresh" -Action $Action2 -Trigger $Trigger -Settings $Settings -Force

Write-Host "등록 완료:"
Write-Host "  StockManagment_DailyDeploy  — 06:00 빌드+push+Vercel"
Write-Host "  StockManagment_DailyRefresh — 06:00 데이터 갱신+레포트"
