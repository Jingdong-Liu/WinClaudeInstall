@echo off
echo ========================================
echo  Claude Code Installer — Build Script
echo ========================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.9+ first.
    pause
    exit /b 1
)

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [3/4] Cleaning previous builds...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec.bak del /q *.spec.bak

echo [4/4] Building executable...
pyinstaller --clean main.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build complete! Output: dist\ClaudeCodeInstaller\
echo ========================================
pause
