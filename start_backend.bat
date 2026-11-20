@echo off
REM Start SkillLens Backend with PostgreSQL PATH

REM Find PostgreSQL
set PG_PATH1=C:\Program Files\PostgreSQL\18\bin
set PG_PATH2=C:\Program Files\PostgreSQL\17\bin
set PG_PATH3=C:\Program Files\PostgreSQL\16\bin
set PG_PATH4=C:\Program Files\PostgreSQL\15\bin

if exist "%PG_PATH1%\psql.exe" (
    set PATH=%PG_PATH1%;%PATH%
) else if exist "%PG_PATH2%\psql.exe" (
    set PATH=%PG_PATH2%;%PATH%
) else if exist "%PG_PATH3%\psql.exe" (
    set PATH=%PG_PATH3%;%PATH%
) else if exist "%PG_PATH4%\psql.exe" (
    set PATH=%PG_PATH4%;%PATH%
)

echo.
echo ========================================
echo   Starting SkillLens Backend
echo ========================================
echo.

cd backend
call venv\Scripts\activate.bat

echo Starting server on http://localhost:8000
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press CTRL+C to stop
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
