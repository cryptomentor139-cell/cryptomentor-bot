@echo off
REM ========================================
REM CryptoMentor Bot - Run Script
REM Windows Batch File
REM ========================================

echo.
echo ========================================
echo   CryptoMentor Bot - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Pastikan Python sudah terinstall dan ada di PATH
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist main.py (
    echo [ERROR] main.py tidak ditemukan!
    echo Pastikan Anda berada di folder Bismillah
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file tidak ditemukan!
    echo Bot mungkin tidak berfungsi tanpa konfigurasi
    echo.
    pause
)

echo [INFO] Starting CryptoMentor Bot...
echo [INFO] Press Ctrl+C to stop
echo.
echo ========================================
echo.

REM Start bot
python main.py

REM If bot exits, pause to see error
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Bot stopped with error!
    echo ========================================
    pause
)
