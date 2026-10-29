#requires -Version 7.2
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$Assessment,
  [string]$OutputDirectory = (Join-Path $PWD 'report-v4'),
  [ValidateSet('both','en-US','pt-BR')][string]$Locale = 'both'
)
$ErrorActionPreference = 'Stop'
$Python = Get-Command python -ErrorAction SilentlyContinue
$PythonArgs = @()
if (-not $Python) { $Python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue; $PythonArgs = @('-3') }
if (-not $Python) { throw 'Python 3.10+ is required.' }
$Root = Split-Path -Parent $PSScriptRoot
$Renderer = Join-Path $Root 'assurance/v4/checkpoint6/report/render_v4.py'
$InputPath = (Resolve-Path $Assessment).Path
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Locales = if ($Locale -eq 'both') { @('en-US','pt-BR') } else { @($Locale) }
foreach ($CurrentLocale in $Locales) {
  $Output = Join-Path $OutputDirectory "arc-posture-review.v4.$CurrentLocale.html"
  & $Python.Source @PythonArgs $Renderer --input $InputPath --output $Output --locale $CurrentLocale
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Write-Host "[PASS] Arc Posture Review v4 report created in $OutputDirectory" -ForegroundColor Green
