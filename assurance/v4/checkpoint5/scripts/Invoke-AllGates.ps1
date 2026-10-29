#requires -Version 7.2
[CmdletBinding()]
param()
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
& (Join-Path $Root 'Invoke-AllGates.ps1') @args
exit $LASTEXITCODE
