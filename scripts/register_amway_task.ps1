# 注册安利产品每日推送任务
$TaskName   = "Amway_Daily_Push"
$ProjectDir = "E:\SD_OpenVINO\ArtForge"

# ✅ 使用你系统里真实的 Python 路径
$Python     = "C:\Python314\python.exe" 
$Script     = "$ProjectDir\scripts\amway_daily.py"

# 删除旧任务（如果存在）
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 创建新动作
$Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`"" -WorkingDirectory $ProjectDir

# 触发器：每天 08:00 (你可以根据需要修改时间，比如 "12:00" 或 "20:00")
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"

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
    -Description "安利产品每日自动推送 (single_products_sharebar)" `
    -Force

Write-Host ""
Write-Host "✅ 计划任务已注册成功！" -ForegroundColor Green
Write-Host "   任务名   : $TaskName"
Write-Host "   执行脚本 : $Script"
Write-Host "   执行时间 : 每天 08:00"
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "   - 277个文件，每天发1篇，预计需要 9 个多月发完。"
Write-Host "   - 进度会自动保存在 data/amway_queue_sharebar.json 中。"
Write-Host "   - 立即手动测试一次：Start-ScheduledTask -TaskName $TaskName"