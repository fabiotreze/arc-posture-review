#requires -Version 7.2
[CmdletBinding()]
param(
  [Parameter(Mandatory, Position = 0)]
  [ValidateSet('evaluate', 'compare')]
  [string]$Command,
  [string]$Evidence,
  [string]$Baseline,
  [string]$Before,
  [string]$After,
  [string]$Output
)
$ErrorActionPreference = 'Stop'
$Python = Get-Command python -ErrorAction SilentlyContinue
$PythonArgs = @()
if (-not $Python) { $Python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue; $PythonArgs = @('-3') }
if (-not $Python) { throw 'Python 3.10+ is required.' }
$Cli = Join-Path $PSScriptRoot 'assurance/v4/checkpoint5/cli/arc_posture.py'
if ($Command -eq 'evaluate') {
  if (-not $Evidence) { throw '-Evidence is required for evaluate.' }
  if (-not $Output) { $Output = Join-Path $PWD 'assessment-result.v4.json' }
  $CliArgs = @('evaluate', '--evidence', $Evidence, '--output', $Output)
  if ($Baseline) { $CliArgs += @('--baseline', $Baseline) }
}
else {
  if (-not $Before -or -not $After) { throw '-Before and -After are required for compare.' }
  if (-not $Output) { $Output = Join-Path $PWD 'assessment-comparison.v4.json' }
  $CliArgs = @('compare', '--before', $Before, '--after', $After, '--output', $Output)
}
& $Python.Source @PythonArgs $Cli @CliArgs
exit $LASTEXITCODE
