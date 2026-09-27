@echo off
chcp 65001 >nul
cd /d "%~dp0"
for %%I in ("%~dp0..") do set "ROOT=%%~fI"

echo 启动本地 PWA 服务（仅局域网访问）
echo 手机在同一 WiFi 下可访问
echo.

cd /d "%ROOT%"
python pwa\start_pwa.py
pause