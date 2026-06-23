@echo off
setlocal enabledelayedexpansion

echo ═══════════════════════════════════════════════════════
echo     Safety Checker - Website Security Scanner
echo ═══════════════════════════════════════════════════════

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found

REM Check and install dependencies
echo.
echo Checking dependencies...
python -c "import requests, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -q -r requirements.txt
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies already installed
)

echo.
echo Starting Safety Checker...
echo.

if "%1"=="" (
    python safety_checker.py --menu
) else (
    python safety_checker.py %*
)

if errorlevel 1 (
    echo.
    echo ✗ Error occurred
    pause
)
