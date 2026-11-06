#!/usr/bin/env python3
"""The collector's v4 report step: report generated from a run folder, kit download verified by SHA-256."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "Invoke-ArcPostureReview.ps1"
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
PWSH = shutil.which("pwsh") or shutil.which("powershell")

HARNESS = r"""
param([string]$Path, [string]$Case, [string]$RunDir, [string]$KitRoot, [string]$KitZip, [string]$Sha)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errs = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errs)
$wanted = 'Get-PythonCommand', 'Test-PythonVersion', 'Invoke-Python', 'Resolve-KitRoot', 'Invoke-V4Report', 'Save-Text'
$funcs = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $wanted -contains $n.Name }, $true)
if ($funcs.Count -ne $wanted.Count) { Write-Output ('MISSING_FUNCTIONS ' + $funcs.Count); exit 2 }
foreach ($f in $funcs) { . ([scriptblock]::Create($f.Extent.Text)) }
$Utf8 = New-Object System.Text.UTF8Encoding $false; $KitSha256 = '0' * 64; $ScriptVersion = 'vTEST'; $KitUrl = ''
try {
  if ($Case -eq 'repo') {
    Invoke-V4Report $RunDir $KitRoot ''
    Write-Output ('OK ' + ((Get-ChildItem (Join-Path $RunDir 'report') | Sort-Object Name | ForEach-Object Name) -join ','))
  }
  elseif ($Case -eq 'download') {
    $work = Join-Path ([IO.Path]::GetTempPath()) ('kt-' + [guid]::NewGuid().ToString('N')); New-Item -ItemType Directory -Force $work | Out-Null
    $r = Resolve-KitRoot $KitZip $Sha 'vTEST' $work
    Write-Output ('OK ' + (Test-Path (Join-Path $r 'assurance/v4/checkpoint5/cli/arc_posture.py')))
  }
}
catch { Write-Output ('ERR ' + $_.Exception.Message) }
"""


def run(case, **kw):
    with tempfile.TemporaryDirectory() as d:
        h = Path(d) / "harness.ps1"
        h.write_text(HARNESS, encoding="utf-8")
        args = [PWSH, "-NoProfile", "-NonInteractive", "-File", str(h), "-Path", str(SCRIPT), "-Case", case]
        for key, value in kw.items():
            args += [f"-{key}", str(value)]
        r = subprocess.run(args, capture_output=True, text=True)
        lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
        return (lines[-1].strip() if lines else r.stderr.strip()[:200])


if not PWSH:
    print("FAIL v4 report step: PowerShell not found"); sys.exit(1)
errors = []
tmp = Path(tempfile.mkdtemp())
try:
    with zipfile.ZipFile(FIXTURE) as z:
        z.extractall(tmp / "run")
    run_dir = next(p.parent for p in (tmp / "run").rglob("results.json"))
    got = run("repo", RunDir=run_dir, KitRoot=ROOT)
    expected = "OK arc-posture-review.v4.en-US.html,arc-posture-review.v4.pt-BR.html,assessment.v4.json,report.log"
    if got != expected:
        errors.append(f"report step returned {got!r}")
    else:
        html = (run_dir / "report" / "arc-posture-review.v4.pt-BR.html").read_text(encoding="utf-8")
        if 'id="executive-narrative"' not in html or "Zero Trust" not in html:
            errors.append("generated report is missing the executive summary or the Zero Trust view")
        json.loads((run_dir / "report" / "assessment.v4.json").read_text(encoding="utf-8"))
    kit = tmp / "arc-posture-kit.zip"
    subprocess.run([sys.executable, str(ROOT / "tools" / "Build-Kit.py"), "--output", str(kit)], check=True, capture_output=True)
    sha = subprocess.run([sys.executable, str(ROOT / "tools" / "Build-Kit.py")], capture_output=True, text=True, check=True).stdout.strip()
    if run("download", KitZip=kit, Sha=sha) != "OK True":
        errors.append("a kit with the pinned SHA-256 was not accepted")
    bad = run("download", KitZip=kit, Sha="F" * 64)
    if not bad.startswith("ERR") or "does not match" not in bad:
        errors.append(f"a kit with a different SHA-256 was not rejected: {bad!r}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(("FAIL" if errors else "PASS") + " v4 report step: " + ("; ".join(errors) if errors else
      "report generated into report/ from a run folder; a downloaded kit is accepted only with the pinned SHA-256"))
sys.exit(1 if errors else 0)
