[CmdletBinding()]
param([string]$EnvFile)

$ErrorActionPreference = 'Stop'
if ($EnvFile) { $EnvFile = (Resolve-Path -LiteralPath $EnvFile).Path }
$composeArgs = @()
if ($EnvFile) { $composeArgs += @('--env-file', $EnvFile) }

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    # Keep operational data, the Data Lake and the optional Oracle volume.
    docker compose @composeArgs --profile oracle --profile jobs down
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
