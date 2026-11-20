@echo off
REM Run SkillLens Test Suite

echo.
echo ========================================
echo   Running SkillLens Tests
echo ========================================
echo.

cd backend

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run tests
python test_migration.py

echo.
pause
