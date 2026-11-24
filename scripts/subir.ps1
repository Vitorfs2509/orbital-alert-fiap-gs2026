[CmdletBinding()]
param([string]$EnvFile)

$ErrorActionPreference = 'Stop'
if ($EnvFile) { $EnvFile = (Resolve-Path -LiteralPath $EnvFile).Path }
$composeArgs = @()
if ($EnvFile) { $composeArgs += @('--env-file', $EnvFile) }

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    docker compose @composeArgs config --quiet
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    docker compose @composeArgs up --build -d --wait --wait-timeout 180 postgres schema backend frontend
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    docker compose @composeArgs port frontend 8080
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
