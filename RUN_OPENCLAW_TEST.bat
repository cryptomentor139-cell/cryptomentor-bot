@echo off
echo ========================================
echo OpenClaw Quick Test
echo ========================================
echo.

cd /d "%~dp0"
python quick_test_openclaw.py

echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Next: Add handlers to bot.py
echo See OPENCLAW_READY.md for details
echo.
pause
