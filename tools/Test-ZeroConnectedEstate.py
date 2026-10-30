#!/usr/bin/env python3
"""Negative test: CHK-32 and CHK-39 must not return PASS when Arc machines exist but none is Connected."""
import os, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "Invoke-ArcPostureReview.ps1")
PWSH = shutil.which("pwsh") or shutil.which("powershell")
HARNESS = r"""
param([string]$Path, [string]$CheckId, [int]$Connected)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errs = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errs)
$target = '$Eval[' + "'" + $CheckId + "'" + ']'
$node = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.AssignmentStatementAst] -and $n.Left.Extent.Text -eq $target }, $true) | Select-Object -First 1
if (-not $node) { Write-Output 'NOT_FOUND'; exit 2 }
$script:all = @(1..3 | ForEach-Object { [pscustomobject]@{ name = "m$_"; resourceGroup = 'rg'; status = 'Disconnected'; osSku = 'x' } })
$script:conn = @($script:all | Select-Object -First $Connected | ForEach-Object { $_.status = 'Connected'; $_ })
function Get-ArcMachine { return @($script:all) }
function Get-ArcConnected { return @($script:conn) }
function Get-MachineKey([string]$rg, [string]$n) { return ($rg + '/' + $n).ToLower() }
function Get-ExtIndex([string]$p) { $h = @{}; foreach ($m in $script:conn) { $h[(Get-MachineKey $m.resourceGroup $m.name)] = $true }; return $h }
function Write-Result { param($Status, $Found, $Detail, $Rows, $Coverage) $script:status = $Status }
$script:status = 'NONE'
$block = & ([scriptblock]::Create($node.Right.Extent.Text))
& $block
Write-Output $script:status
"""

def run(check, connected):
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "harness.ps1")
        with open(h, "w", encoding="utf-8") as f:
            f.write(HARNESS)
        r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", h, "-Path", SCRIPT,
                            "-CheckId", check, "-Connected", str(connected)], capture_output=True, text=True)
        lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
        return (lines[-1].strip() if lines else ""), r

if not PWSH:
    print("FAIL zero-connected estate: PowerShell not found"); sys.exit(1)
errors = []
for chk in ("CHK-32", "CHK-39"):
    s0, r0 = run(chk, 0)
    if s0 != "N/A":
        errors.append(f"{chk} with 3 machines and 0 connected returned {s0 or r0.stderr.strip()[:120]} (expected N/A)")
    s1, r1 = run(chk, 2)
    if s1 != "PASS":
        errors.append(f"{chk} with 2 connected machines covered returned {s1 or r1.stderr.strip()[:120]} (expected PASS)")
print(("FAIL" if errors else "PASS") + " zero-connected estate: " + ("; ".join(errors) if errors else
      "CHK-32/CHK-39 return N/A when no Arc machine is Connected; PASS preserved for covered connected machines"))
sys.exit(1 if errors else 0)
