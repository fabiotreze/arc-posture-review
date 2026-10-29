[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$Script = Join-Path $PSScriptRoot 'Invoke-AllGates.py'

& python $Script

exit $LASTEXITCODE
