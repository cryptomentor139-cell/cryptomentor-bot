@echo off
REM ========================================
REM CryptoMentor Bot - Stop Script
REM Windows Batch File
REM ========================================

echo.
echo ========================================
echo   CryptoMentor Bot - Stop Script
echo ========================================
echo.

echo [INFO] Mencari proses bot yang sedang berjalan...
echo.

REM Kill existing Python processes running main.py
set FOUND=0
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    echo [INFO] Menghentikan proses Python (PID: %%i)...
    taskkill /F /PID %%i >nul 2>&1
    set FOUND=1
)

if %FOUND%==1 (
    echo.
    echo [SUCCESS] Bot berhasil dihentikan!
) else (
    echo [INFO] Tidak ada proses bot yang berjalan
)

echo.
echo ========================================
pause
