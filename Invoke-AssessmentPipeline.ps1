#requires -Version 7.2
[CmdletBinding()]
param(
  [Parameter(Mandatory)] [string]$CollectorOutput,
  [string]$Baseline,
  [string]$Output = (Join-Path $PWD 'assessment-result.v4.json')
)
$Parameters = @{
  Command = 'evaluate'
  Evidence = (Resolve-Path $CollectorOutput).Path
  Output = $Output
}
if ($Baseline) { $Parameters.Baseline = (Resolve-Path $Baseline).Path }
& (Join-Path $PSScriptRoot 'arc-posture.ps1') @Parameters
exit $LASTEXITCODE
