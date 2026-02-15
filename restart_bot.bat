@echo off
REM ========================================
REM CryptoMentor Bot - Restart Script
REM Windows Batch File
REM ========================================

echo.
echo ========================================
echo   CryptoMentor Bot - Restart Script
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

echo [1/4] Mencari proses bot yang sedang berjalan...
echo.

REM Kill existing Python processes running main.py
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    echo Menghentikan proses Python (PID: %%i)...
    taskkill /F /PID %%i >nul 2>&1
)

echo.
echo [2/4] Proses bot dihentikan
echo.
timeout /t 2 /nobreak >nul

echo [3/4] Membersihkan cache...
if exist __pycache__ rmdir /s /q __pycache__ >nul 2>&1
if exist app\__pycache__ rmdir /s /q app\__pycache__ >nul 2>&1
echo Cache dibersihkan
echo.

echo [4/4] Memulai bot...
echo.
echo ========================================
echo   Bot Starting...
echo   Press Ctrl+C to stop
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
