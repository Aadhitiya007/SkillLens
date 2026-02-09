@echo off
REM Fix SkillLens Database Password

echo.
echo ========================================
echo   Fixing Database Password
echo ========================================
echo.

REM Common PostgreSQL installation paths
set PG_PATH0=C:\Program Files\PostgreSQL\18\bin
set PG_PATH1=C:\Program Files\PostgreSQL\16\bin
set PG_PATH2=C:\Program Files\PostgreSQL\15\bin
set PG_PATH3=C:\Program Files\PostgreSQL\14\bin
set PG_PATH4=C:\PostgreSQL\16\bin

REM Try to find PostgreSQL
if exist "%PG_PATH0%\psql.exe" (
    set PG_BIN=%PG_PATH0%
    echo Found PostgreSQL 18 at: %PG_PATH0%
) else if exist "%PG_PATH1%\psql.exe" (
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
    set /p PG_BIN="PostgreSQL bin path: "
)

echo.
echo Please enter your 'postgres' master password when prompted.
echo.

"%PG_BIN%\psql.exe" -U postgres -c "ALTER USER skilllens WITH PASSWORD 'skilllens';"
"%PG_BIN%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skilllens TO skilllens;"

echo.
echo Password reset complete.
pause
