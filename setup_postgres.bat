@echo off
REM Add PostgreSQL to PATH and setup database

echo.
echo ========================================
echo   PostgreSQL PATH Setup
echo ========================================
echo.

REM Common PostgreSQL installation paths
set PG_PATH1=C:\Program Files\PostgreSQL\16\bin
set PG_PATH2=C:\Program Files\PostgreSQL\15\bin
set PG_PATH3=C:\Program Files\PostgreSQL\14\bin
set PG_PATH4=C:\PostgreSQL\16\bin

REM Try to find PostgreSQL
if exist "%PG_PATH1%\psql.exe" (
    set PG_BIN=%PG_PATH1%
    echo Found PostgreSQL 16 at: %PG_PATH1%
) else if exist "%PG_PATH2%\psql.exe" (
    set PG_BIN=%PG_PATH2%
    echo Found PostgreSQL 15 at: %PG_PATH2%
) else if exist "%PG_PATH3%\psql.exe" (
    set PG_BIN=%PG_PATH3%
    echo Found PostgreSQL 14 at: %PG_PATH3%
) else if exist "%PG_PATH4%\psql.exe" (
    set PG_BIN=%PG_PATH4%
    echo Found PostgreSQL at: %PG_PATH4%
) else (
    echo ERROR: PostgreSQL not found in common locations!
    echo Please enter the full path to PostgreSQL bin directory:
    echo Example: C:\Program Files\PostgreSQL\16\bin
    set /p PG_BIN="PostgreSQL bin path: "
)

REM Add to PATH for this session
set PATH=%PG_BIN%;%PATH%

REM Verify psql works
echo.
echo Verifying PostgreSQL installation...
"%PG_BIN%\psql.exe" --version
if %errorlevel% neq 0 (
    echo ERROR: Could not run psql!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Creating Database
echo ========================================
echo.
echo You will be prompted for the PostgreSQL 'postgres' user password.
echo This is the password you set during PostgreSQL installation.
echo.
pause

REM Create database
echo Creating database 'skilllens'...
"%PG_BIN%\psql.exe" -U postgres -c "CREATE DATABASE skilllens;"
if %errorlevel% equ 0 (
    echo OK: Database created
) else (
    echo NOTE: Database might already exist (this is OK)
)

echo.
echo Creating user 'skilllens'...
"%PG_BIN%\psql.exe" -U postgres -c "CREATE USER skilllens WITH PASSWORD 'skilllens';"
if %errorlevel% equ 0 (
    echo OK: User created
) else (
    echo NOTE: User might already exist (this is OK)
)

echo.
echo Granting privileges...
"%PG_BIN%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;"
if %errorlevel% equ 0 (
    echo OK: Privileges granted
) else (
    echo ERROR: Could not grant privileges
)

echo.
echo ========================================
echo   Database Setup Complete!
echo ========================================
echo.
echo PostgreSQL bin path: %PG_BIN%
echo Database: skilllens
echo User: skilllens
echo Password: skilllens
echo.
echo IMPORTANT: Add PostgreSQL to your system PATH permanently:
echo 1. Search for "Environment Variables" in Windows
echo 2. Click "Environment Variables"
echo 3. Under "System variables", find "Path"
echo 4. Click "Edit"
echo 5. Click "New"
echo 6. Add: %PG_BIN%
echo 7. Click "OK" on all windows
echo.
echo Or run this in PowerShell as Administrator:
echo [Environment]::SetEnvironmentVariable("Path", $env:Path + ";%PG_BIN%", "Machine")
echo.
pause
