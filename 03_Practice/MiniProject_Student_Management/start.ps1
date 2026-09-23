$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$FrontendRoot = Join-Path $ProjectRoot "frontend\student-management-ui"
$BackendPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $BackendPython)) {
    $BackendPython = Join-Path $ProjectRoot "..\..\.venv\Scripts\python.exe"
}

if (-not (Test-Path $BackendPython)) {
    $BackendPython = "python"
}

if (-not (Test-Path (Join-Path $ProjectRoot "app.py"))) {
    throw "Backend entry point was not found: $ProjectRoot\app.py"
}

if (-not (Test-Path (Join-Path $FrontendRoot "package.json"))) {
    throw "Frontend package.json was not found: $FrontendRoot\package.json"
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js, then run this script again."
}

if (-not (Test-Path (Join-Path $FrontendRoot "node_modules"))) {
    Write-Host "Frontend dependencies are missing. Running npm install..."
    Push-Location $FrontendRoot
    try {
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

Start-Process powershell.exe -WorkingDirectory $ProjectRoot -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "& '$BackendPython' app.py"
)

Write-Host "Waiting for FastAPI startup and database readiness..."
$BackendReady = $false
for ($Attempt = 1; $Attempt -le 30; $Attempt++) {
    try {
        $HealthResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing -TimeoutSec 2
        if ($HealthResponse.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $BackendReady) {
    throw "FastAPI did not become ready within 60 seconds. Check the backend window for startup or database errors."
}

Write-Host "FastAPI is ready. Starting the React frontend..."
Start-Process powershell.exe -WorkingDirectory $FrontendRoot -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "npm run dev -- --host localhost"
)

Write-Host "Backend starting at http://localhost:8000/docs"
Write-Host "Frontend starting at http://localhost:5173"
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"