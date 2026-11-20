@echo off
REM Reset PostgreSQL user password

echo.
echo ========================================
echo   Reset skilllens User Password
echo ========================================
echo.

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
echo.
pause

echo.
echo Resetting password for user 'skilllens'...
"%PG_PATH%\psql.exe" -U postgres -c "ALTER USER skilllens WITH PASSWORD 'skilllens';"

if %errorlevel% equ 0 (
    echo ✓ Password reset successfully
) else (
    echo ✗ Failed to reset password
    pause
    exit /b 1
)

echo.
echo Granting all permissions...
"%PG_PATH%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;"
"%PG_PATH%\psql.exe" -U postgres -d skilllens -c "GRANT ALL ON SCHEMA public TO skilllens;"
"%PG_PATH%\psql.exe" -U postgres -d skilllens -c "ALTER DATABASE skilllens OWNER TO skilllens;"

echo.
echo Testing connection (password: skilllens)...
"%PG_PATH%\psql.exe" -U skilllens -d skilllens -c "SELECT 'Connection successful!' as status;"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✓ Password Reset Complete!
    echo ========================================
    echo.
    echo Database: skilllens
    echo User: skilllens
    echo Password: skilllens
    echo.
    echo You can now run: python init_db_simple.py
    echo.
) else (
    echo.
    echo ========================================
    echo   ✗ Connection Still Failed
    echo ========================================
    echo.
    echo The password might not be 'skilllens'.
    echo Check your .env file and update DATABASE_URL if needed.
    echo.
)

pause
