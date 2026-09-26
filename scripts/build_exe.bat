@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

rem ============================================================
rem ArtForge 打包脚本（PyInstaller）
rem 用法：双击本文件，或在项目根目录运行 scripts\build_exe.bat
rem ============================================================

cd /d "%~dp0\.."

echo.
echo ============================================================
echo   ArtForge 打包工具
echo ============================================================
echo.

:: ---------- 1. 检查 Python ----------
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo ✅ Python 已安装
python --version

:: ---------- 2. 检查 PyInstaller ----------
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo.
    echo ⚠️ 未安装 PyInstaller，正在安装...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller 安装失败
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller 已安装

:: ---------- 3. 清理旧构建 ----------
echo.
echo 🧹 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ArtForge.spec del /q ArtForge.spec

:: ---------- 4. 打包 ----------
echo.
echo 📦 开始打包（约 1-3 分钟）...
echo.

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name ArtForge ^
    --add-data "assets;assets" ^
    --add-data "presets;presets" ^
    --add-data "layers;layers" ^
    --add-data "core;core" ^
    --add-data "services;services" ^
    --add-data "api_engines;api_engines" ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=dotenv ^
    --hidden-import=requests ^
    --collect-all=PIL ^
    --noconfirm ^
    run_gui_tk.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败
    pause
    exit /b 1
)

:: ---------- 5. 附带配置 ----------
echo.
echo 📋 复制配置样例...

if exist ".env.sample" (
    copy ".env.sample" "dist\.env.sample" >nul
    echo    ✅ .env.sample
)
if exist "README.md" (
    copy "README.md" "dist\README.md" >nul
    echo    ✅ README.md
)

:: 创建 output 目录
if not exist "dist\output" mkdir "dist\output"
echo    ✅ output/ 目录

:: 创建 .env（如果项目根有）
if exist ".env" (
    copy ".env" "dist\.env" >nul
    echo    ⚠️ .env 已复制（含 API Key，注意安全）
)

:: ---------- 6. 完成 ----------
echo.
echo ============================================================
echo   ✅ 打包完成
echo ============================================================
echo.
echo 📁 输出目录: dist\
echo 📦 可执行文件: dist\ArtForge.exe
echo.
echo 💡 分发方式：
echo    把 dist\ 整个目录打包给对方（含 .env 和 output\）
echo    或只发 ArtForge.exe（对方需自行配置 .env）
echo.

:: 计算文件大小
for %%F in ("dist\ArtForge.exe") do (
    set /a size_mb=%%~zF/1048576
    echo 📏 大小: !size_mb! MB
)

echo.
pause
endlocal