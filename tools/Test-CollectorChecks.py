#!/usr/bin/env python3
"""Executes the CHK-21 and CHK-29 rules of the collector with synthetic data (the other static tests only read the script text)."""
import json, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/Invoke-ArcPostureReview.ps1"
PWSH = shutil.which("pwsh") or shutil.which("powershell")

HARNESS = r"""
param([string]$Path, [string]$DataFile)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errs = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errs)
$wanted = 'Get-MachineKey', 'Test-EmptyList', 'Get-ExtIndex'
$funcs = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $wanted -contains $n.Name }, $true)
if ($funcs.Count -ne $wanted.Count) { Write-Output ('MISSING_FUNCTIONS ' + $funcs.Count); exit 2 }
foreach ($f in $funcs) { . ([scriptblock]::Create($f.Extent.Text)) }
$text = [IO.File]::ReadAllText($Path)
function Get-Section([string]$From, [string]$To) { $i = $text.IndexOf($From); $j = $text.IndexOf($To, $i + 1); return $text.Substring($i, $j - $i) }
$tables = Get-Section '$AgentReleases = @{' "`$Eval['CHK-01']"
$chk21 = Get-Section "`$Eval['CHK-21'] = {" "`$Eval['CHK-22']"
$chk29 = Get-Section "`$Eval['CHK-29'] = {" "`$Eval['CHK-30']"
$data = Get-Content -Raw $DataFile | ConvertFrom-Json
$DS = @{ extensions = @($data.extensions); estate = @() }
$Start = Get-Date; $AgentLatestLive = 0; $ExtLatest = @{}; $Eval = @{}
$script:machines = @($data.machines)
function Get-ArcMachine { return $script:machines }
function Write-Result($Status, $Found, $Detail, $Rows) { $script:res = [pscustomobject]@{ status = $Status; found = $Found; detail = $Detail; rows = @($Rows) } }
. ([scriptblock]::Create($tables))
. ([scriptblock]::Create($chk21))
. ([scriptblock]::Create($chk29))
$out = @{}
foreach ($id in 'CHK-21', 'CHK-29') { $script:res = $null; & $Eval[$id]; $out[$id] = $script:res }
$out | ConvertTo-Json -Depth 6
"""


def run(machines, extensions):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "h.ps1").write_text(HARNESS, encoding="utf-8")
        (Path(d) / "d.json").write_text(json.dumps({"machines": machines, "extensions": extensions}), encoding="utf-8")
        r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(Path(d) / "h.ps1"), "-Path", str(SCRIPT), "-DataFile", str(Path(d) / "d.json")], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip().startswith("{"):
        raise SystemExit("[FAIL] harness error: " + (r.stdout + r.stderr)[:600])
    return json.loads(r.stdout)


def machine(name, ports="[]", version="1.68.03532.3282", au="true", status="Connected", attempt=""):
    return {"name": name, "resourceGroup": "rg", "subscriptionId": "s", "status": status, "incomingPorts": ports, "agentVersion": version,
            "agentAutoUpgrade": au, "agentUpgradeStatus": attempt}


def main() -> int:
    if not PWSH:
        print("[FAIL] PowerShell not found")
        return 1
    ms = [machine("ssh", '["22"]'), machine("wac", '["6516","17426"]'), machine("odd", '["17426"]'), machine("none"),
          machine("v148", version="1.48.1.1"), machine("v155", version="1.55.1.1"), machine("v160", version="1.60.1.1", au="false"),
          machine("v166", version="1.66.1.1", attempt="failed")]
    res = run(ms, [{"machine": "ssh", "resourceGroup": "rg", "extType": "AdminCenter", "state": "Succeeded"}])
    errors = []
    c21 = res["CHK-21"]
    if c21["status"] != "WARN" or c21["found"] != 3:
        errors.append(f"CHK-21 expected WARN with 3 machines, got {c21['status']} {c21['found']}")
    for needle in ("2 with SSH (22) or Windows Admin Center (6516)", "2 with ports this check does not classify", "1 with port 6516 allowed but no AdminCenter extension", "not evidence of exposure"):
        if needle not in c21["detail"]:
            errors.append("CHK-21 detail lacks: " + needle)
    if "RDP" in c21["detail"]:
        errors.append("CHK-21 still names RDP")
    rows = {r["name"]: r for r in c21["rows"]}
    if rows["odd"]["documentedChannels"] or rows["odd"]["unclassifiedPorts"] != "17426":
        errors.append("CHK-21 classification of port 17426 is wrong")
    if rows["ssh"]["adminCenterExtension"] != "yes" or rows["wac"]["adminCenterExtension"] != "no":
        errors.append("CHK-21 AdminCenter cross-check is wrong")
    c29 = res["CHK-29"]
    for needle in ("disabled in Azure on 1 of 8", "agent below 1.67 (not eligible) on 4", "last attempt failed on 1", "automaticupgrade.blocklocally", "azcmagent config get automaticupgrade.blocklocally"):
        if needle not in c29["detail"]:
            errors.append("CHK-29 detail lacks: " + needle)
    cves = {r["name"]: r["cves"] for r in c29["rows"]}
    expected = {"v148": "CVE-2025-49692, CVE-2025-55316, CVE-2026-26117", "v155": "CVE-2025-55316, CVE-2026-26117", "v160": "CVE-2026-26117"}
    for name, want in expected.items():
        if cves.get(name) != want:
            errors.append(f"CHK-29 CVEs for {name}: expected '{want}', got '{cves.get(name)}'")
    if "CVE-2025-26627" in json.dumps(c29["rows"]):
        errors.append("CHK-29 still maps CVE-2025-26627 per machine")
    if errors:
        print("[FAIL] collector rules:\n - " + "\n - ".join(errors))
        return 1
    print("[PASS] collector rules executed: CHK-21 ports and AdminCenter cross-check, CHK-29 CVE ranges and automatic upgrade detail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
