# -*- coding: utf-8 -*-
# 每日从 QQ空间日志推送一篇到微信公众号草稿箱
# 由 Windows 任务计划程序调用

$ErrorActionPreference = "Continue"

# ---- 路径配置 ----
$PROJECT_ROOT = "E:\SD_OpenVINO\ArtForge"
$PY_SCRIPT    = Join-Path $PROJECT_ROOT "scripts\daily_push.py"
$LOG_DIR      = Join-Path $PROJECT_ROOT "output\logs"
$LOG_FILE     = Join-Path $LOG_DIR ("daily_push_{0:yyyyMMdd}.log" -f (Get-Date))

# ---- 找 python.exe（优先用 where.exe 结果，找不到用兜底）----
$PY_EXE = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PY_EXE) {
    # 兜底：常见安装路径
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $PY_EXE = $c; break }
    }
}

if (-not $PY_EXE -or -not (Test-Path $PY_EXE)) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ❌ 找不到 python.exe"
    exit 1
}

if (-not (Test-Path $PY_SCRIPT)) {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ❌ 找不到脚本: $PY_SCRIPT"
    exit 2
}

# ---- 建日志目录 ----
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# ---- 切到项目目录 ----
Set-Location $PROJECT_ROOT

# ---- 执行，输出同时打到控制台和日志 ----
$startTime = Get-Date
"============================================================" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"[$($startTime.ToString('yyyy-MM-dd HH:mm:ss'))] 开始执行 daily_push" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"python: $PY_EXE" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"script: $PY_SCRIPT" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"cwd   : $PROJECT_ROOT" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"============================================================" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

$output = & $PY_EXE $PY_SCRIPT 2>&1
$exitCode = $LASTEXITCODE

# 输出到控制台
$output | Write-Host
# 输出到日志
$output | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds
"[$($endTime.ToString('yyyy-MM-dd HH:mm:ss'))] 执行结束，exitCode=$exitCode，耗时 ${duration}s" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
"" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8

exit $exitCode