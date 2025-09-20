Param(
    [string]$Job = "all"
)

Write-Host "CI-local runner - job: $Job"

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path (Join-Path $root "..")

function Run-Mypy {
    Write-Host "Running mypy (static-checks)..."
    Push-Location -Path backend
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtualenv .venv"
        python -m venv .venv
    }
    Write-Host "Activating venv"
    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -e .[dev]
    Write-Host "Invoking mypy"
    & python -m mypy --config-file mypy.ini app tests
    $mypyExit = $LASTEXITCODE
    if ($mypyExit -ne 0) {
        Write-Host "mypy failed with exit code $mypyExit" -ForegroundColor Red
        Pop-Location
        exit $mypyExit
    }
    Pop-Location
}

function Run-Tests {
    Write-Host "Running tests via docker-compose.test.yml"
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Host "docker-compose not found. Please install Docker Compose or use 'docker compose' CLI." -ForegroundColor Yellow
    }
    docker-compose -f docker-compose.test.yml build --pull --no-cache
    docker-compose -f docker-compose.test.yml run --rm backend-test
}

switch ($Job.ToLower()) {
    'all' {
        Run-Mypy
        Run-Tests
    }
    'mypy' {
        Run-Mypy
    }
    'static-checks' {
        Run-Mypy
    }
    'tests' {
        Run-Tests
    }
    'backend-tests' {
        Run-Tests
    }
    default {
        Write-Host "Unknown job: $Job" -ForegroundColor Red
        Write-Host "Valid values: all, mypy, tests" -ForegroundColor Yellow
        exit 2
    }
}

Write-Host "Done"
