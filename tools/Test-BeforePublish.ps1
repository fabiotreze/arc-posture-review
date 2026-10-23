<#
.SYNOPSIS
  Pre-publish check for Arc Posture Review. Run from the repository root before commit/tag.
.DESCRIPTION
  1. PSScriptAnalyzer with the same settings as the release gate (Error and Warning; fails on any finding).
  2. Version consistency: script ($ScriptVersion), CHANGELOG (newest section), CITATION.cff.
  3. Repository files: .nojekyll, index.html, both language pages.
  4. Commit e-mail: GitHub noreply (avoids GH007 push rejection).
  Exit code 0 = ready to publish; 1 = fix the items marked FAIL.
.EXAMPLE
  ./tools/Test-BeforePublish.ps1
#>
[CmdletBinding()]
param([string]$Root = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Stop'
$fail = 0
function Write-Check([bool]$Ok, [string]$Text) {
    if ($Ok) { Write-Host ('  PASS  ' + $Text) -ForegroundColor Green }
    else { Write-Host ('  FAIL  ' + $Text) -ForegroundColor Red; $script:fail++ }
}

Push-Location $Root
try {
    Write-Host 'PSScriptAnalyzer'
    if (-not (Get-Module -ListAvailable PSScriptAnalyzer)) {
        Install-Module PSScriptAnalyzer -Scope CurrentUser -Force -SkipPublisherCheck
    }
    $found = @(Invoke-ScriptAnalyzer -Path ./scripts -Recurse -Settings ./PSScriptAnalyzerSettings.psd1)
    if ($found.Count) { $found | Sort-Object Line | Format-Table Severity, RuleName, Line, Message -AutoSize -Wrap | Out-Host }
    Write-Check ($found.Count -eq 0) ('{0} finding(s) (Error/Warning)' -f $found.Count)

    Write-Host 'Version'
    $ps = Get-Content ./scripts/Invoke-ArcPostureReview.ps1 -Raw
    $sv = if ($ps -match "ScriptVersion = 'v([0-9]+\.[0-9]+\.[0-9]+)'") { $Matches[1] } else { '' }
    $cl = if ((Get-Content ./CHANGELOG.md -Raw) -match '(?m)^## \[([0-9]+\.[0-9]+\.[0-9]+)\]') { $Matches[1] } else { '' }
    $ci = if ((Get-Content ./CITATION.cff -Raw) -match '(?m)^version: "([0-9.]+)"') { $Matches[1] } else { '' }
    Write-Check ($sv -and $sv -eq $cl -and $sv -eq $ci) ("script v$sv · CHANGELOG $cl · CITATION $ci")
    $tags = @(git tag --list)
    Write-Check ($tags -notcontains "v$sv") ("tag v$sv not used yet")

    Write-Host 'Files'
    foreach ($f in '.nojekyll', 'index.html', 'arc-posture-review.pt-BR.html', 'arc-posture-review.en-US.html') { Write-Check (Test-Path $f) $f }
    foreach ($f in 'arc-posture-review.pt-BR.html', 'arc-posture-review.en-US.html') {
        Write-Check ((Get-Content $f -Raw) -match [regex]::Escape("v$sv")) ("$f shows v$sv")
    }

    Write-Host 'Git'
    $mail = [string](git config user.email)
    Write-Check ($mail -like '*@users.noreply.github.com') ("commit e-mail: $mail")
}
finally { Pop-Location }

if ($fail) { Write-Host ("NOT READY: {0} item(s) failed." -f $fail) -ForegroundColor Red; exit 1 }
Write-Host 'READY TO PUBLISH' -ForegroundColor Green
