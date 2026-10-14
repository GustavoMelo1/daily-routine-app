param(
    [Parameter(Mandatory=$true)][string]$PythonPath,
    [string]$ImageFolder = (Join-Path $PSScriptRoot '..\images')
)
$ErrorActionPreference = 'Stop'
$backendPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ownedServer = $null
$exitCode = 1
Set-Location -LiteralPath $backendPath
New-Item -ItemType Directory -Path (Join-Path $backendPath 'logs') -Force | Out-Null
function Test-Api {
    try {
        $response = Invoke-RestMethod 'http://localhost:8000/image-imports/health' -TimeoutSec 3
        return $response.status -eq 'ready'
    } catch { return $false }
}
try {
    if (-not (Test-Api)) {
        # Never stop or replace an existing server on this port.
        if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
            throw 'API on port 8000 is not ready. Check migrations and restart it.'
        }
        $ownedServer = Start-Process -FilePath $PythonPath -ArgumentList '-m uvicorn app.main:app --host 127.0.0.1 --port 8000' -WorkingDirectory $backendPath -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $backendPath 'logs/api-scheduler.log') -RedirectStandardError (Join-Path $backendPath 'logs/api-scheduler-error.log')
        $ready = $false
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            if ($ownedServer.HasExited) { throw 'Scheduled API failed to start. Check logs/api-scheduler-error.log.' }
            if (Test-Api) { $ready = $true; break }
            Start-Sleep -Seconds 1
        }
        if (-not $ready) { throw 'API did not become ready.' }
    }
    & $PythonPath -m pipeline.batch --folder $ImageFolder
    $exitCode = $LASTEXITCODE
} catch {
    $_ | Out-String | Add-Content -LiteralPath (Join-Path $backendPath 'logs/scheduler-error.log')
} finally {
    if ($null -ne $ownedServer -and -not $ownedServer.HasExited) {
        Stop-Process -Id $ownedServer.Id
    }
}
exit $exitCode
