$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$LocalEnv = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $VenvPython -PathType Leaf)) {
    Write-Error "The Windows Python environment was not found. From the project folder, run .\setup_windows.ps1 first."
    exit 1
}
if (-not (Test-Path $LocalEnv -PathType Leaf)) {
    Write-Error ".env is missing. Run .\setup_windows.ps1 to create it from .env.example, then configure the database settings."
    exit 1
}

& $VenvPython -c "import click, dotenv, flask, mysql.connector, werkzeug"
if ($LASTEXITCODE -ne 0) {
    Write-Error "One or more required Python packages are missing. Run .\setup_windows.ps1 to install them."
    exit 1
}

Write-Host "Starting the Semester Management System at http://127.0.0.1:5000"
Write-Host "Press Ctrl+C to stop the server."
Push-Location $ProjectRoot
try {
    & $VenvPython (Join-Path $ProjectRoot "run.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "The Flask application exited with code $LASTEXITCODE. Check .env and the application error above."
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
