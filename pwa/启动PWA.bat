@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   ArtForge PWA qi dong
echo ============================================
echo.
echo   Dang qian mu lu: %CD%
echo.

REM 找项目根目录（pwa 的上一级）
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
echo   Xiang mu gen mu lu: %ROOT%
echo.

REM 检查文件
if not exist "%ROOT%\pwa\start_pwa.py" (
    echo [ERROR] missing %ROOT%\pwa\start_pwa.py
    pause
    exit /b 1
)
if not exist "%~dp0cloudflared.exe" (
    echo [ERROR] missing %~dp0cloudflared.exe
    pause
    exit /b 1
)

echo   Wen jian jian cha tong guo
echo.
echo   Zheng zai qi dong liang ge chuang kou...
echo.

REM 启动窗口 1：PWA 后端
start "ArtForge PWA" cmd /k "cd /d %ROOT% && python pwa\start_pwa.py"

REM 等 3 秒
timeout /t 3 /nobreak >nul

REM 启动窗口 2：Cloudflare Tunnel
start "ArtForge Tunnel" cmd /k "cd /d %~dp0 && cloudflared.exe tunnel --url http://127.0.0.1:8000"

echo   Liang ge chuang kou yi fa qi
echo.
echo   Qing kan di 2 ge chuang kou da yin de URL
echo   https://xxxx-xxxx.trycloudflare.com
echo.
echo   Shou ji 4G da kai zhe ge di zhi
echo.
pause