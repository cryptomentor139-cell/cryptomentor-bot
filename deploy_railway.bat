@echo off
echo ========================================
echo Railway Deploy Script
echo ========================================
echo.

echo Step 1: Login to Railway...
echo (Browser will open for login)
railway login
if errorlevel 1 (
    echo ERROR: Login failed!
    pause
    exit /b 1
)
echo.

echo Step 2: Link to project...
echo (Select: industrious-dream / production)
railway link
if errorlevel 1 (
    echo ERROR: Link failed!
    pause
    exit /b 1
)
echo.

echo Step 3: Deploy to Railway...
railway up
if errorlevel 1 (
    echo ERROR: Deploy failed!
    pause
    exit /b 1
)
echo.

echo ========================================
echo Deploy SUCCESS!
echo ========================================
echo.
echo Now checking logs...
echo.
railway logs
echo.
echo ========================================
echo Test bot in Telegram: /start
echo ========================================
pause
