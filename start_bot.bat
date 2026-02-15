@echo off
REM Script untuk menjalankan CryptoMentor AI Bot di Windows

echo ========================================
echo   CryptoMentor AI Bot - Starter
echo ========================================
echo.

REM Cek apakah di folder yang benar
if not exist "main.py" (
    echo ERROR: File main.py tidak ditemukan!
    echo Pastikan Anda menjalankan script ini dari folder Bismillah
    pause
    exit /b 1
)

REM Cek apakah .env ada
if not exist ".env" (
    echo WARNING: File .env tidak ditemukan!
    echo Bot mungkin tidak bisa jalan tanpa konfigurasi.
    echo.
)

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Install Python terlebih dahulu dari python.org
    pause
    exit /b 1
)

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Ada masalah saat install dependencies
    echo Bot mungkin tidak berfungsi dengan baik
    echo.
)

echo.
echo [3/3] Starting bot...
echo.
echo ========================================
echo   Bot is starting...
echo   Press Ctrl+C to stop
echo ========================================
echo.

python main.py

echo.
echo ========================================
echo   Bot stopped
echo ========================================
pause
