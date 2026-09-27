@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ============================================================
REM  ArtForge - Cloudflare Tunnel
REM  作用：把本地 127.0.0.1:8000 暴露到公网
REM  前置：PWA 服务必须先启动（另一个窗口）
REM ============================================================

set "CLOUDFLARED=%~dp0cloudflared.exe"
set "LOCAL_PORT=8000"
set "LOCAL_URL=http://127.0.0.1:%LOCAL_PORT%"

echo.
echo ============================================================
echo   ArtForge - Cloudflare Tunnel
echo ============================================================
echo.

REM -------- 检查 cloudflared.exe --------
if not exist "%CLOUDFLARED%" (
    echo [ERROR] cloudflared.exe not found
    echo.
    echo Expected location:
    echo   %CLOUDFLARED%
    echo.
    echo Download from:
    echo   https://github.com/cloudflare/cloudflared/releases/latest
    echo   Choose: cloudflared-windows-amd64.exe
    echo   Rename to: cloudflared.exe
    echo   Put it in this folder.
    echo.
    pause
    exit /b 1
)

REM -------- 检查 8000 端口是否被占用（即 PWA 是否在跑）--------
netstat -ano | findstr ":%LOCAL_PORT%" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo [WARN] Port %LOCAL_PORT% is not listening.
    echo        PWA service may not be running.
    echo.
    echo Hint: run "start_pwa.bat" in another window first.
    echo.
    echo Continue anyway? Tunnel will return 502 until PWA starts.
    echo Press any key to continue, or Ctrl+C to cancel.
    pause >nul
) else (
    echo [OK] Port %LOCAL_PORT% is listening.
)

echo.
echo Starting tunnel to %LOCAL_URL% ...
echo.
echo IMPORTANT:
echo   - Keep this window OPEN
echo   - Copy the https://xxxx.trycloudflare.com URL below
echo   - Open it on your phone (4G) to verify
echo.

REM -------- 启动 tunnel --------
"%CLOUDFLARED%" tunnel --url %LOCAL_URL%

REM cloudflared 退出（Ctrl+C 或错误）后走到这里
echo.
echo Tunnel stopped.
pause