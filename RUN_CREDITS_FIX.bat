@echo off
echo ========================================
echo FIX OPENCLAW CREDITS DATABASE
echo ========================================
echo.

cd Bismillah
python fix_openclaw_credits_sqlite.py

echo.
echo ========================================
echo DONE!
echo ========================================
pause
