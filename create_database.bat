@echo off
REM Create PostgreSQL database for SkillLens

echo.
echo ========================================
echo   Creating PostgreSQL Database
echo ========================================
echo.

REM Find PostgreSQL
set PG_PATH=C:\Program Files\PostgreSQL\18\bin
if not exist "%PG_PATH%\psql.exe" (
    set PG_PATH=C:\Program Files\PostgreSQL\17\bin
)
if not exist "%PG_PATH%\psql.exe" (
    set PG_PATH=C:\Program Files\PostgreSQL\16\bin
)

echo PostgreSQL bin: %PG_PATH%
echo.
echo You will be prompted for the PostgreSQL 'postgres' user password.
echo This is the password you set during PostgreSQL installation.
echo.
pause

echo.
echo Creating database...
"%PG_PATH%\psql.exe" -U postgres -c "CREATE DATABASE skilllens;"
if %errorlevel% equ 0 (
    echo ✓ Database 'skilllens' created
) else (
    echo Note: Database might already exist
)

echo.
echo Creating user...
"%PG_PATH%\psql.exe" -U postgres -c "CREATE USER skilllens WITH PASSWORD 'skilllens';"
if %errorlevel% equ 0 (
    echo ✓ User 'skilllens' created
) else (
    echo Note: User might already exist
)

echo.
echo Granting privileges...
"%PG_PATH%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;"
"%PG_PATH%\psql.exe" -U postgres -d skilllens -c "GRANT ALL ON SCHEMA public TO skilllens;"
"%PG_PATH%\psql.exe" -U postgres -d skilllens -c "ALTER DATABASE skilllens OWNER TO skilllens;"

echo.
echo Testing connection...
"%PG_PATH%\psql.exe" -U skilllens -d skilllens -c "SELECT version();"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✓ Database Setup Complete!
    echo ========================================
    echo.
    echo Database: skilllens
    echo User: skilllens
    echo Password: skilllens
    echo Host: localhost
    echo Port: 5432
    echo.
) else (
    echo.
    echo ========================================
    echo   ✗ Connection Test Failed
    echo ========================================
    echo.
    echo Please check:
    echo 1. PostgreSQL service is running
    echo 2. Password is correct
    echo 3. User has proper permissions
    echo.
)

pause
