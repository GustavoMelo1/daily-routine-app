param(
    [string]$PythonPath = (Get-Command python -ErrorAction Stop).Source,
    [string]$Time = '20:00'
)
$ErrorActionPreference = 'Stop'
$taskName = 'DailyRoutineImageImport'
$runnerPath = (Resolve-Path (Join-Path $PSScriptRoot 'run_batch.ps1')).Path
$PythonPath = (Resolve-Path -LiteralPath $PythonPath).Path
$arguments = '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy RemoteSigned -File "{0}" -PythonPath "{1}"' -f $runnerPath, $PythonPath
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing -and $existing.Actions.Arguments -notlike ('*' + $runnerPath + '*')) {
    throw 'A different task already uses this name; it was not overwritten.'
}
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 55) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Import notebook images into Daily Routine; daily at 20h.' -Force | Out-Null
Get-ScheduledTaskInfo -TaskName $taskName
