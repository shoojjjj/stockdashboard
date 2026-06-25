# Windows Task Scheduler - daily 06:00
# Run in PowerShell (admin optional)

$TaskName = "StockManagment_DailyDeploy"
$Script = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_deploy.ps1"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`" -SkipTelegram"
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

$RefreshScript = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_refresh.ps1"
$Action2 = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$RefreshScript`""
Register-ScheduledTask -TaskName "StockManagment_DailyRefresh" -Action $Action2 -Trigger $Trigger -Settings $Settings -Force

Write-Host "OK: StockManagment_DailyDeploy  (build+push+vercel @ 06:00)"
Write-Host "OK: StockManagment_DailyRefresh (data refresh + report @ 06:00)"
