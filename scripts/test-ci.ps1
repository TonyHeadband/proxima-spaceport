Param()

Write-Host "Running tests using docker-compose.test.yml"

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path (Join-Path $root "..")

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "docker-compose not found. Please install Docker Compose or use 'docker compose' CLI." -ForegroundColor Yellow
}

Write-Host "Building and running backend-test service"
docker-compose -f docker-compose.test.yml build --pull --no-cache
docker-compose -f docker-compose.test.yml run --rm backend-test

Write-Host "Done"
