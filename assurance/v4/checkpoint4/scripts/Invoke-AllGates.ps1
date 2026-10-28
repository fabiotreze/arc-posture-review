[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location $Root
try {
    & python ./checkpoint4-v4/scripts/Invoke-AllGates.py
    exit $LASTEXITCODE
}
finally { Pop-Location }
