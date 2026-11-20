@echo off
REM Fix SkillLens Schema Permissions

echo.
echo ========================================
echo   Fixing Schema Permissions
echo ========================================
echo.

REM Common PostgreSQL installation paths
set PG_PATH0=C:\Program Files\PostgreSQL\18\bin
set PG_PATH1=C:\Program Files\PostgreSQL\16\bin

if exist "%PG_PATH0%\psql.exe" (
    set PG_BIN=%PG_PATH0%
) else if exist "%PG_PATH1%\psql.exe" (
    set PG_BIN=%PG_PATH1%
) else (
    echo ERROR: PostgreSQL not found in common locations!
    set /p PG_BIN="PostgreSQL bin path: "
)

echo.
echo Please enter your 'postgres' master password when prompted.
echo.

"%PG_BIN%\psql.exe" -U postgres -d skilllens -c "GRANT ALL ON SCHEMA public TO skilllens;"

echo.
echo Permissions fixed.
pause
