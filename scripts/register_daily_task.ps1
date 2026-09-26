# 注册每日自动生成任务
$TaskName   = "ArtForge_Daily"
$ProjectDir = "E:\SD_OpenVINO\ArtForge"
$Python     = "$ProjectDir\venv\Scripts\python.exe"
$Script     = "$ProjectDir\skills\daily_pipeline\skill.py"

$Action  = New-ScheduledTaskAction -Execute $Python -Argument "$Script --count 6 --vary-preset" -WorkingDirectory $ProjectDir
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force
Write-Host "✅ 已注册每日 08:00 自动任务" -ForegroundColor Green