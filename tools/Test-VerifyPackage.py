#!/usr/bin/env python3
"""The independent recomputation agrees with a consistent package and catches the three mistakes found in real runs."""
import importlib.util, json, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verify", ROOT / "tools/Verify-Package.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

M = lambda n, **kw: {"name": n, "resourceGroup": "rg", "status": "Connected", "osSku": "Windows Server 2022 Datacenter", "agentVersion": "1.68.1.1", "esu": "NotAssigned",
                     "incomingPorts": "[]", "extAllow": "[]", "extBlock": "[]", **kw}


def package(tmp: Path, *, found21=2, found23=3, defender_machines=3) -> Path:
    machines = [M("a", incomingPorts='["22"]', extAllow='[{"type":"x"}]'), M("b", incomingPorts='["6516","17426"]'), M("c"), M("d", status="Disconnected", osSku="Windows Server 2012 R2 Datacenter")]
    results = {"generatedAt": "2026-11-06T10:00:00+00:00", "scope": {"machinesTotal": 4}, "results": [
        {"id": "CHK-21", "found": found21, "detail": ""}, {"id": "CHK-23", "found": found23, "detail": ""},
        {"id": "CHK-37", "found": 1, "detail": ""}, {"id": "CHK-51", "found": 1, "detail": ""},
        {"id": "CHK-29", "found": 0, "detail": "Distribution: 1.68: 4. Automatic agent upgrade: disabled in Azure on 0 of 4."},
        {"id": "CHK-33", "found": 2, "detail": ""}]}
    files = {"results.json": results, "data/machines.json": machines, "data/extensions.json": [],
             "data/defender.json": [{"assessment": "x", "machines": defender_machines}, {"assessment": "y", "machines": 1}]}
    path = tmp / f"p{found21}{found23}{defender_machines}.zip"
    with zipfile.ZipFile(path, "w") as z:
        for name, value in files.items():
            z.writestr("run/" + name, json.dumps(value))
    return path


def real_run_package(tmp: Path) -> Path:
    """Shapes seen in real runs: capped sample of a larger scope, disconnected machines with a failing baseline, Windows Server 2016."""
    machines = [M("a", status="Disconnected"), M("b", osSku="Windows Server 2016 Standard"), M("c", osSku="Windows Server 2012 R2 Standard")]
    results = {"generatedAt": "2026-11-06T10:00:00+00:00", "scope": {"machinesTotal": 328, "maxMachines": 3}, "results": [
        {"id": "CHK-37", "found": 1, "detail": ""}, {"id": "CHK-51", "found": 2, "detail": ""}, {"id": "CHK-55", "found": 0, "detail": ""},
        {"id": "CHK-33", "found": 1, "detail": ""}]}
    files = {"results.json": results, "data/machines.json": machines, "data/extensions.json": [],
             "data/defender.json": [{"assessment": "x", "machines": 167}],
             "data/gcComp.json": [{"machine": "a", "resourceGroup": "rg", "name": "Windows security baseline", "complianceStatus": "NonCompliant"}]}
    path = tmp / "real.zip"
    with zipfile.ZipFile(path, "w") as z:
        for name, value in files.items():
            z.writestr("run/" + name, json.dumps(value))
    return path


def failing(path: Path) -> set[str]:
    return {r["rule"] for r in verify.verify(verify.Package(path)) if r["status"] == "FAIL"}


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        ok = failing(package(tmp))
        if ok:
            print(f"[FAIL] a consistent package was rejected: {sorted(ok)}")
            return 1
        cases = {"V10": package(tmp, found21=1), "V11": package(tmp, found23=2), "V21": package(tmp, defender_machines=9)}
        for rule, path in cases.items():
            got = failing(path)
            if rule not in got:
                print(f"[FAIL] {rule} was not detected (got {sorted(got)})")
                return 1
        got = failing(real_run_package(tmp))
        if got:
            print(f"[FAIL] a capped run, disconnected baseline or Windows Server 2016 was rejected: {sorted(got)}")
            return 1
    print("[PASS] verifier: consistent package accepted; port count, allowlist count and machine inflation are detected; capped runs, disconnected baselines and Windows Server 2016 are accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
