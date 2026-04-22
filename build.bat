@echo off
echo ========================================
echo  Claude Code Installer — Build Script
echo ========================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.9+ first.
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
pip install pyinstaller

echo [3/3] Building executable...
pyinstaller --clean main.spec

echo.
echo Build complete! Output: dist\ClaudeCodeInstaller.exe
pause
