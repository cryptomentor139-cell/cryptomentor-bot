@echo off
REM ========================================
REM CryptoMentor Bot - Status Check
REM Windows Batch File
REM ========================================

echo.
echo ========================================
echo   CryptoMentor Bot - Status Check
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

echo [INFO] Checking bot status...
echo.

REM Check for running Python processes
set FOUND=0
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    echo [RUNNING] Bot process found (PID: %%i)
    set FOUND=1
)

if %FOUND%==1 (
    echo.
    echo [STATUS] Bot is RUNNING
) else (
    echo [STATUS] Bot is NOT running
)

echo.
echo ========================================
echo.

REM Check configuration
if exist .env (
    echo [CONFIG] .env file: EXISTS
) else (
    echo [CONFIG] .env file: MISSING
)

if exist main.py (
    echo [CONFIG] main.py: EXISTS
) else (
    echo [CONFIG] main.py: MISSING
)

if exist bot.py (
    echo [CONFIG] bot.py: EXISTS
) else (
    echo [CONFIG] bot.py: MISSING
)

echo.
echo ========================================
pause
