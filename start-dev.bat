@echo off
echo Starting IPO Readiness PDF Analyzer in Development Mode...
echo.

echo Starting Backend Server...
cd backend
start cmd /k "uv run python run.py"

echo Waiting for backend to start...
timeout /t 5

echo Starting Frontend Server...
cd ..\frontend
start cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to exit...
pause