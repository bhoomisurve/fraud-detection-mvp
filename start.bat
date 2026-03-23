@echo off
echo ========================================
echo   FRAUD SHIELD - Starting MVP
echo ========================================
echo.

echo Starting Backend Server...
start cmd /k "cd /d %~dp0backend && pip install -r requirements.txt && python run.py"

echo Waiting for backend to initialize...
timeout /t 10 /nobreak > nul

echo Starting Frontend Server...
start cmd /k "cd /d %~dp0frontend && npm install && npm start"

echo.
echo ========================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window...
pause > nul