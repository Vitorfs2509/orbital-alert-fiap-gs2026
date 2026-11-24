[CmdletBinding()]
param(
    [string]$EnvFile,
    [string]$Resultado,
    [switch]$Oracle,
    [switch]$SemRecomendacao,
    [switch]$Mineracao
)

$ErrorActionPreference = 'Stop'
if ($EnvFile) { $EnvFile = (Resolve-Path -LiteralPath $EnvFile).Path }
if ($Resultado) { $Resultado = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Resultado) }
$composeArgs = @()
if ($EnvFile) { $composeArgs += @('--env-file', $EnvFile) }
$demoArgs = @()
if ($SemRecomendacao) { $demoArgs += '--skip-recommendation' }
if ($Mineracao) { $demoArgs += '--process-sample' }

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    # The default demo expects the stack started by subir.ps1.
    docker compose @composeArgs build etl
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $runArgs = @('run', '--rm', '--no-deps', '-T', 'etl', 'python', 'scripts/demo_fase7.py')
    if ($Resultado) {
        $result = docker compose @composeArgs @runArgs @demoArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Set-Content -LiteralPath $Resultado -Value $result -Encoding utf8
        $result
    } else {
        docker compose @composeArgs @runArgs @demoArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    if ($Oracle) {
        docker compose @composeArgs --profile oracle up -d --wait --wait-timeout 480 oracle
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        docker compose @composeArgs --profile oracle run --build --rm --no-deps -T oracle-sync
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    exit 0
} finally {
    Pop-Location
}
