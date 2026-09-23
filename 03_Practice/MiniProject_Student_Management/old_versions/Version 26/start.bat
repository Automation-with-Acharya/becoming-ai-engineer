@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "FRONTEND_ROOT=%PROJECT_ROOT%frontend\student-management-ui"
set "BACKEND_PYTHON=%PROJECT_ROOT%.venv\Scripts\python.exe"

if not exist "%BACKEND_PYTHON%" set "BACKEND_PYTHON=%PROJECT_ROOT%..\..\.venv\Scripts\python.exe"
if not exist "%BACKEND_PYTHON%" set "BACKEND_PYTHON=python"

if not exist "%PROJECT_ROOT%app.py" (
    echo Backend entry point was not found: "%PROJECT_ROOT%app.py"
    exit /b 1
)

if not exist "%FRONTEND_ROOT%\package.json" (
    echo Frontend package.json was not found: "%FRONTEND_ROOT%\package.json"
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo npm was not found. Install Node.js, then run this file again.
    exit /b 1
)

if not exist "%FRONTEND_ROOT%\node_modules" (
    echo Frontend dependencies are missing. Running npm install...
    pushd "%FRONTEND_ROOT%"
    call npm install
    if errorlevel 1 (
        popd
        echo npm install failed.
        exit /b 1
    )
    popd
)

start "FastAPI Backend" powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%PROJECT_ROOT%'; & '%BACKEND_PYTHON%' app.py"

echo Waiting for FastAPI startup and database readiness...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ready = $false; for ($attempt = 1; $attempt -le 30; $attempt++) { try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 2; if ($response.StatusCode -eq 200) { $ready = $true; break } } catch { Start-Sleep -Seconds 2 } }; if (-not $ready) { exit 1 }"
if errorlevel 1 (
    echo FastAPI did not become ready within 60 seconds. Check the backend window for startup or database errors.
    exit /b 1
)

echo FastAPI is ready. Starting the React frontend...
start "React Frontend" powershell.exe -NoExit -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%FRONTEND_ROOT%'; npm run dev -- --host localhost"

echo Backend ready at http://localhost:8000/docs
echo Frontend starting at http://localhost:5173
timeout /t 2 /nobreak >nul
start "" http://localhost:5173

endlocal