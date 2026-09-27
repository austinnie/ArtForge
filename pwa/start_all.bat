@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ============================================================
REM  ArtForge - 一键启动 PWA + Tunnel
REM  会打开两个新窗口
REM ============================================================

echo.
echo ============================================================
echo   ArtForge - All-in-One Launcher
echo ============================================================
echo.
echo This will open TWO windows:
echo   [1] PWA service   (port 8000, local)
echo   [2] Cloudflare Tunnel  (public URL)
echo.
echo Close them individually to stop services.
echo.
pause

REM -------- 窗口 1: PWA --------
start "ArtForge PWA" cmd /k "%~dp0start_pwa.bat"

REM -------- 等 4 秒让 PWA 先起 --------
echo Waiting 4s for PWA service to start...
timeout /t 4 /nobreak >nul

REM -------- 窗口 2: Tunnel --------
start "ArtForge Tunnel" cmd /k "%~dp0start_tunnel.bat"

echo.
echo Both windows launched.
echo.
echo Tip: In the Tunnel window, copy the https://xxx.trycloudflare.com URL.
echo.
pause