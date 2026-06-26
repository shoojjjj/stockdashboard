# Windows Task Scheduler
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Daily 06:00 full deploy with telegram collect
$Deploy = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_deploy.ps1"
Register-ScheduledTask -TaskName "StockManagment_DailyDeploy" `
    -Action (New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Deploy`"") `
    -Trigger (New-ScheduledTaskTrigger -Daily -At "06:00") `
    -Settings $Settings -Force

# Daily 06:00 data refresh
$Refresh = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\auto_refresh.ps1"
Register-ScheduledTask -TaskName "StockManagment_DailyRefresh" `
    -Action (New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Refresh`"") `
    -Trigger (New-ScheduledTaskTrigger -Daily -At "06:00") `
    -Settings $Settings -Force

# Hourly health + report (smart-open, max 1 popup/hour)
$Hourly = "C:\Users\JEON\Desktop\아카이브\Stock_Managment\scripts\hourly_check.ps1"
Register-ScheduledTask -TaskName "StockManagment_HourlyCheck" `
    -Action (New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Hourly`"") `
    -Trigger (New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)) `
    -Settings $Settings -Force

Write-Host "OK: DailyDeploy, DailyRefresh @ 06:00"
Write-Host "OK: HourlyCheck every 1 hour (report throttle)"
