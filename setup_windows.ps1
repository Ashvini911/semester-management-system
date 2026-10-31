$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = $PSScriptRoot
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$ExampleEnv = Join-Path $ProjectRoot ".env.example"
$LocalEnv = Join-Path $ProjectRoot ".env"
$VenvDirectory = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvDirectory "Scripts\python.exe"

function Stop-Setup($Message) {
    Write-Error "$Message`nSetup stopped. Resolve the issue above and run .\setup_windows.ps1 again."
    exit 1
}

function Test-PythonVersion($Command, $Arguments) {
    try {
        $Output = & $Command @Arguments -c "import sys; print('%d.%d' % sys.version_info[:2]); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Using Python $Output"
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

Write-Host "Preparing the Semester Management System in $ProjectRoot"

if (-not (Test-Path $Requirements -PathType Leaf)) {
    Stop-Setup "requirements.txt was not found beside this setup script."
}
if (-not (Test-Path $ExampleEnv -PathType Leaf)) {
    Stop-Setup ".env.example was not found beside this setup script."
}

$PythonCommand = $null
$PythonArguments = @()
$Launcher = Get-Command "py.exe" -ErrorAction SilentlyContinue
if (-not $Launcher) {
    $Launcher = Get-Command "py" -ErrorAction SilentlyContinue
}
if ($Launcher) {
    if (Test-PythonVersion $Launcher.Source @("-3")) {
        $PythonCommand = $Launcher.Source
        $PythonArguments = @("-3")
    }
}

if (-not $PythonCommand) {
    $Python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if (-not $Python) {
        $Python = Get-Command "python" -ErrorAction SilentlyContinue
    }
    if ($Python -and (Test-PythonVersion $Python.Source @())) {
        $PythonCommand = $Python.Source
    }
}

if (-not $PythonCommand) {
    Stop-Setup "Python 3.10 or later was not found. Install Python 3.10+ from https://www.python.org/downloads/windows/ (or the Microsoft Store), then reopen PowerShell. The Windows 'py' launcher is preferred when available."
}

if (Test-Path $VenvDirectory) {
    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        Stop-Setup "An existing .venv is not a Windows virtual environment. To preserve its contents, rename .venv manually, then rerun this script."
    }
    $VenvVersion = & $VenvPython -c "import sys; print('%d.%d' % sys.version_info[:2]); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
    if ($LASTEXITCODE -ne 0) {
        Stop-Setup "The existing .venv uses Python $VenvVersion, but Python 3.10 or later is required. Rename .venv manually and rerun setup."
    }
    Write-Host "Using existing Windows virtual environment (Python $VenvVersion)."
}
else {
    Write-Host "Creating .venv..."
    & $PythonCommand @PythonArguments -m venv $VenvDirectory
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython -PathType Leaf)) {
        Stop-Setup "Could not create .venv. Check that Python's venv component is available and that this folder is writable."
    }
}

Write-Host "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Stop-Setup "pip could not be upgraded. Check your internet connection and rerun setup."
}

Write-Host "Installing requirements.txt..."
& $VenvPython -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) {
    Stop-Setup "Dependency installation failed. Check your internet connection, then rerun setup."
}

& $VenvPython -c "import click, dotenv, flask, mysql.connector, werkzeug; from importlib.metadata import version; print('Critical imports OK; python-dotenv ' + version('python-dotenv'))"
if ($LASTEXITCODE -ne 0) {
    Stop-Setup "A required package import failed after installation. Review the pip output and rerun setup."
}

if (-not (Test-Path $LocalEnv -PathType Leaf)) {
    $EnvText = [System.IO.File]::ReadAllText($ExampleEnv)
    if ($EnvText -notmatch '(?m)^SECRET_KEY=') {
        Stop-Setup ".env.example must define SECRET_KEY before a local .env can be created."
    }
    $RandomBytes = New-Object byte[] 32
    $RandomGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $RandomGenerator.GetBytes($RandomBytes)
    }
    finally {
        $RandomGenerator.Dispose()
    }
    $SecretKey = [Convert]::ToBase64String($RandomBytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
    $EnvText = $EnvText -replace '(?m)^SECRET_KEY=.*$', "SECRET_KEY=$SecretKey"
    [System.IO.File]::WriteAllText($LocalEnv, $EnvText, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Created .env with a new random SECRET_KEY; existing .env files are never overwritten."
}
else {
    Write-Host "Keeping existing .env unchanged."
}

$EnvValues = @{}
foreach ($Line in [System.IO.File]::ReadAllLines($LocalEnv)) {
    if ($Line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
        $EnvValues[$Matches[1]] = $Matches[2].Trim('"').Trim("'")
    }
}
$RequiredVariables = @("SECRET_KEY", "DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME")
$MissingVariables = @($RequiredVariables | Where-Object { -not $EnvValues.ContainsKey($_) -or [string]::IsNullOrWhiteSpace($EnvValues[$_]) })
if ($MissingVariables.Count -gt 0) {
    Stop-Setup "The following required settings are missing or blank in .env: $($MissingVariables -join ', '). Add them without sharing the file."
}
if ($EnvValues["SECRET_KEY"] -eq "replace-with-a-secure-random-key") {
    Stop-Setup "SECRET_KEY in .env is still the template placeholder. Set a private random value and rerun setup."
}

$NeedsDatabaseConfig = $EnvValues["DB_PASS"] -eq "replace-with-your-database-password"
if ($NeedsDatabaseConfig) {
    Write-Warning "Set DB_PASS in .env to the password for the least-privilege semester_app MySQL account before launching."
}

$MySqlServices = @(Get-Service -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^MySQL' -or $_.DisplayName -match 'MySQL' })
if ($MySqlServices.Count -eq 0) {
    Write-Warning "No MySQL Windows service was detected. Install MySQL Server 8.0 and MySQL Workbench, then follow Database\README.md."
}
else {
    $RunningMySql = @($MySqlServices | Where-Object { $_.Status -eq "Running" })
    if ($RunningMySql.Count -eq 0) {
        Write-Warning "MySQL is installed but its service is stopped. Start it from Windows Services or MySQL Installer before checking the database."
    }
    else {
        Write-Host "MySQL service detected and running."
    }
}

Write-Host ""
Write-Host "Setup completed."
Write-Host "Python environment : $VenvDirectory"
Write-Host "Configuration file : $LocalEnv"
Write-Host "Next               : configure the database values, then run .\start_windows.ps1"
if ($NeedsDatabaseConfig) {
    Write-Host "Database setup     : follow Database\README.md before launching."
}
