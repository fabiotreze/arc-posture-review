#!/usr/bin/env python3
"""Regression: absence of configuration or evidence must not be reported as a conclusive FAIL.

Runs the collector's check blocks against stubbed data and asserts the control result.
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "Invoke-ArcPostureReview.ps1")
PWSH = shutil.which("pwsh") or shutil.which("powershell")

HARNESS = r"""
param([string]$Path, [string]$CheckId, [string]$Case)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errs = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errs)
$target = '$Eval[' + "'" + $CheckId + "'" + ']'
$node = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.AssignmentStatementAst] -and $n.Left.Extent.Text -eq $target }, $true) | Select-Object -First 1
if (-not $node) { Write-Output 'NOT_FOUND'; exit 2 }
$win = @(1..2 | ForEach-Object { [pscustomobject]@{ name = "w$_"; resourceGroup = 'rg'; subscriptionId = 's1'; osType = 'windows'; status = 'Connected'; osSku = 'x'
  extensionsEnabled = 'true'; extAllow = '[]'; extBlock = '[]'; configMode = 'full'; incomingPorts = '[]' } })
$script:DS = @{ gcComp = @(); pricing = @(); machines = $win; defender = @(); related = @(); diag = @(); govAssign = @() }
$script:Subs = @([pscustomobject]@{ subscriptionId = 's1'; name = 'sub1' })
$script:QueryEvidence = New-Object System.Collections.Generic.List[object]
$script:ImplicitScope = $false
$script:cur = [ordered]@{ status = 'NONE'; detail = '' }
if ($Case -eq 'implicit-empty') { $script:DS.machines = @(); $script:ImplicitScope = $true }
if ($Case -eq 'pricing-free') { $script:DS.pricing = @([pscustomobject]@{ name = 'VirtualMachines'; subscriptionId = 's1'; pricingTier = 'Free'; subPlan = '' }) }
if ($Case -eq 'noncompliant') { $script:DS.gcComp = @([pscustomobject]@{ name = 'AzureWindowsBaseline'; resourceGroup = 'rg'; machine = 'w1'; complianceStatus = 'NonCompliant'; lastChecked = '2026-11-06T00:00:00Z' }) }
function Get-ArcMachine { return @($script:DS.machines) }
function Get-ArcConnected { return @($script:DS.machines | Where-Object { $_.status -eq 'Connected' }) }
function Get-MachineKey($rg, $name) { return (([string]$rg) + '/' + ([string]$name)).ToLower() }
function Test-EmptyList($v) { $s = [string]$v; return ([string]::IsNullOrWhiteSpace($s) -or $s -eq '[]' -or $s -eq 'null') }
function Write-Result { param($Status, $Found, $Detail, $Rows, $Coverage) $script:status = $Status }
$script:status = 'NONE'
$block = & ([scriptblock]::Create($node.Right.Extent.Text))
& $block
Write-Output $script:status
"""


def run(check, case):
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "harness.ps1")
        with open(h, "w", encoding="utf-8") as f:
            f.write(HARNESS)
        r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", h, "-Path", SCRIPT,
                            "-CheckId", check, "-Case", case], capture_output=True, text=True)
        lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
        return (lines[-1].strip() if lines else ""), r


CASES = [
    ("CHK-23", "default", "WARN", "no allowlist is a hardening opportunity, not a FAIL"),
    ("CHK-55", "noncompliant", "FAIL", "explicit NonCompliant stays a FAIL"),
    ("CHK-56", "default", "WARN", "a missing local-administrators audit is a visibility gap, not a FAIL"),
    ("CHK-31", "default", "PARTIAL", "an unread Defender plan is unknown, not Free"),
    ("CHK-31", "pricing-free", "FAIL", "an explicit Free tier stays a FAIL"),
    ("CHK-01", "implicit-empty", "PARTIAL", "zero machines under the implicit default scope is not a conclusion"),
]

if not PWSH:
    print("FAIL posture wording: PowerShell not found"); sys.exit(1)
errors = []
for check, case, expected, why in CASES:
    got, r = run(check, case)
    if got != expected:
        errors.append(f"{check}/{case} returned {got or r.stderr.strip()[:120]} (expected {expected}: {why})")
print(("FAIL" if errors else "PASS") + " posture wording: " + ("; ".join(errors) if errors else
      "absence of configuration or evidence is WARN/PARTIAL; explicit adverse evidence stays FAIL"))
sys.exit(1 if errors else 0)
