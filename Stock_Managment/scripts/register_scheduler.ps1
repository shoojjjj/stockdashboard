# Windows 작업 스케줄러 등록 (관리자 PowerShell)
# 매일 오전 6시 자동 갱신

$TaskName = "StockManagment_DailyRefresh"
$Script = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_refresh.ps1"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`""
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

Write-Host "등록 완료: $TaskName (매일 06:00)"
Write-Host "확인: Get-ScheduledTask -TaskName $TaskName"
