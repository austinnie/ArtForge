# 注册每日自动生成任务（ArtForge 智能调度版）
$TaskName   = "ArtForge_Daily"
$ProjectDir = "E:\SD_OpenVINO\ArtForge"
$Python     = "$ProjectDir\venv\Scripts\python.exe"
$Script     = "$ProjectDir\skills\artforge_daily\skill.py"

# ✅ 关键参数：--smart 启用智能调度（白名单+权重+防重复）
#             --week-plan 启用主题周计划（按星期几决定主题）
#             --count 6 生成 6 张图
#             --theme terracotta 使用赤陶排版主题
#             --footer-image 文末二维码
$Arguments = "-m skills.artforge_daily.skill --smart --week-plan --count 6 --theme terracotta --footer-image `"assets/qr/公众号结束处.png`""

$Action  = New-ScheduledTaskAction -Execute $Python -Argument $Arguments -WorkingDirectory $ProjectDir

# ✅ 改成 05:00
$Trigger = New-ScheduledTaskTrigger -Daily -At "05:00"

# ✅ 关键设置：
#    -StartWhenAvailable : 错过时间后（比如电脑没开），开机后立刻补跑
#    -ExecutionTimeLimit : 最长跑 1 小时，防止卡死
#    -AllowStartIfOnBatteries : 笔记本用电池也能跑
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# 删除旧任务（如果存在）
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 注册新任务
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "ArtForge 每日智能日更（5:00 AM，智能调度+周计划）" `
    -Force

Write-Host ""
Write-Host "✅ 已注册每日 05:00 自动任务" -ForegroundColor Green
Write-Host "   任务名: $TaskName"
Write-Host "   脚本  : $Script"
Write-Host "   参数  : $Arguments"
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "   - 如果 5 点时电脑关机，开机后会立刻补跑（-StartWhenAvailable）"
Write-Host "   - 查看任务：Get-ScheduledTask -TaskName $TaskName"
Write-Host "   - 立即测试：Start-ScheduledTask -TaskName $TaskName"
Write-Host "   - 删除任务：Unregister-ScheduledTask -TaskName $TaskName"