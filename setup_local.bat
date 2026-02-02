@echo off
REM Complete SkillLens Setup with PostgreSQL PATH handling

echo.
echo ========================================
echo   SkillLens Complete Setup
echo ========================================
echo.

REM Find PostgreSQL
set PG_PATH1=C:\Program Files\PostgreSQL\18\bin
set PG_PATH2=C:\Program Files\PostgreSQL\17\bin
set PG_PATH3=C:\Program Files\PostgreSQL\16\bin
set PG_PATH4=C:\Program Files\PostgreSQL\15\bin
set PG_PATH5=C:\Program Files\PostgreSQL\14\bin
set PG_PATH6=C:\PostgreSQL\18\bin

if exist "%PG_PATH1%\psql.exe" (
    set PG_BIN=%PG_PATH1%
) else if exist "%PG_PATH2%\psql.exe" (
    set PG_BIN=%PG_PATH2%
) else if exist "%PG_PATH3%\psql.exe" (
    set PG_BIN=%PG_PATH3%
) else if exist "%PG_PATH4%\psql.exe" (
    set PG_BIN=%PG_PATH4%
) else if exist "%PG_PATH5%\psql.exe" (
    set PG_BIN=%PG_PATH5%
) else if exist "%PG_PATH6%\psql.exe" (
    set PG_BIN=%PG_PATH6%
) else (
    echo PostgreSQL not found in common locations.
    set /p PG_BIN="Enter PostgreSQL bin path (e.g., C:\Program Files\PostgreSQL\18\bin): "
)

REM Add to PATH for this session
set PATH=%PG_BIN%;%PATH%

echo [1/6] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo OK
echo.

echo [2/6] Checking PostgreSQL...
"%PG_BIN%\psql.exe" --version
if %errorlevel% neq 0 (
    echo ERROR: PostgreSQL not found!
    pause
    exit /b 1
)
echo OK
echo.

echo [3/6] Creating Python virtual environment...
if not exist "backend\venv" (
    cd backend
    python -m venv venv
    cd ..
    echo OK: Created
) else (
    echo OK: Already exists
)
echo.

echo [4/6] Installing dependencies...
cd backend
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK
cd ..
echo.

echo [5/6] Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo OK: .env created
) else (
    echo OK: .env exists
)
echo.

echo [6/6] Creating database...
echo You will be prompted for PostgreSQL password.
pause
"%PG_BIN%\psql.exe" -U postgres -c "CREATE DATABASE skilllens;" 2>nul
"%PG_BIN%\psql.exe" -U postgres -c "CREATE USER skilllens WITH PASSWORD 'skilllens';" 2>nul
"%PG_BIN%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;" 2>nul
echo OK
echo.

echo Initializing database schema...
cd backend
call venv\Scripts\activate.bat
set PATH=%PG_BIN%;%PATH%
python scripts\init_db.py --seed
if %errorlevel% neq 0 (
    echo ERROR: Database initialization failed
    echo Check your .env file DATABASE_URL setting
    pause
    exit /b 1
)
cd ..
echo.

echo ========================================
echo   Setup Complete! ✓
echo ========================================
echo.
echo Next steps:
echo   1. Run: start_backend.bat
echo   2. Open: http://localhost:8000/docs
echo   3. Run tests: run_tests.bat
echo.
echo PostgreSQL bin: %PG_BIN%
echo.
pause
