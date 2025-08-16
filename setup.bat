@echo off
echo Setting up IPO Readiness PDF Analyzer...
echo.

echo Installing Backend Dependencies...
cd backend
if not exist ".venv" (
    echo Creating virtual environment...
    uv venv
)
echo Installing Python packages...
uv sync
echo Backend setup complete!
echo.

echo Installing Frontend Dependencies...
cd ..\frontend
echo Installing Node.js packages...
npm install
echo Frontend setup complete!
echo.

cd ..
echo.
echo Setup Complete!
echo.
echo Next steps:
echo 1. Copy backend\env.example to backend\.env
echo 2. Add your Gemini API key to backend\.env
echo 3. Run start-dev.bat to start both servers
echo.
pause