[CmdletBinding()]
param([string]$EnvFile)

$ErrorActionPreference = 'Stop'
if (!$EnvFile) { $EnvFile = Join-Path (Split-Path -Parent $PSScriptRoot) '.env' }
$EnvFile = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($EnvFile)
if (!(Test-Path -LiteralPath $EnvFile)) {
    Copy-Item -LiteralPath (Join-Path (Split-Path -Parent $PSScriptRoot) '.env.example') -Destination $EnvFile
}
$lines = @(Get-Content -LiteralPath $EnvFile)
$modified = $false
foreach ($key in 'POSTGRES_PASSWORD','ORBITAL_ADMIN_TOKEN','ORBITAL_INGEST_TOKEN') {
    $index = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^$key=") { $index = $i }
    }
    if ($index -ge 0 -and ($lines[$index] -replace "^$key=", '').Trim()) { continue }
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $value = "$key=" + ([BitConverter]::ToString($bytes) -replace '-','')
    if ($index -ge 0) { $lines[$index] = $value } else { $lines += $value }
    $modified = $true
}
if ($modified) { [IO.File]::WriteAllLines($EnvFile, [string[]]$lines, (New-Object Text.UTF8Encoding($false))) }
