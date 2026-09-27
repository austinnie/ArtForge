# 注册每日自动生成任务（直接调用 smart_daily.py）
$TaskName   = "ArtForge_Daily"
$ProjectDir = "E:\SD_OpenVINO\ArtForge"

# ✅ 修正 1：使用你系统里真实的 Python 路径（根据你之前的日志）
$Python     = "C:\Python314\python.exe" 

# ✅ 修正 2：直接指向 smart_daily.py
$Script     = "$ProjectDir\scripts\smart_daily.py"

# smart_daily.py 内部已经写好了 --smart --week-plan --count 6 等参数
# 所以这里不需要再传参数，直接跑脚本即可
$Arguments = "`"$Script`""

# 删除旧任务（如果存在）
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 创建新动作
$Action = New-ScheduledTaskAction -Execute $Python -Argument $Arguments -WorkingDirectory $ProjectDir

# 触发器：每天 05:00
$Trigger = New-ScheduledTaskTrigger -Daily -At "05:00"

# 设置：允许电池运行、错过补跑、1小时超时
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# 注册任务
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "ArtForge 智能日更 (05:00 AM) - 直接调用 smart_daily.py" `
    -Force

Write-Host ""
Write-Host "✅ 计划任务已重新注册！" -ForegroundColor Green
Write-Host "   任务名   : $TaskName"
Write-Host "   Python   : $Python"
Write-Host "   执行脚本 : $Script"
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "   - 以后想改参数（比如换主题、换张数），直接改 smart_daily.py 即可，不用动计划任务！"
Write-Host "   - 立即测试：Start-ScheduledTask -TaskName $TaskName"