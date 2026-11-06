#!/usr/bin/env python3
"""Independent recomputation: rebuilds key numbers from the raw data of an evidence package (data/*.json) and compares them with results.json.

Usage: python tools/Verify-Package.py <package.zip | extracted folder> [--json]
Exit code 1 when a recomputed value or an invariant disagrees with the collector. Works on any package, including a customer's; it reads, it never writes."""
import json, re, sys, zipfile
from collections import Counter
from pathlib import Path


class Package:
    def __init__(self, path: Path):
        self.path = path
        if path.is_file():
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
        else:
            names = [str(p.relative_to(path)).replace("\\", "/") for p in path.rglob("*") if p.is_file()]
        marker = next((n for n in names if n.endswith("results.json")), None)
        if marker is None:
            raise SystemExit("[FAIL] results.json not found: not an evidence package")
        self.prefix = marker[: -len("results.json")]

    def get(self, name: str):
        rel = self.prefix + name
        try:
            if self.path.is_file():
                with zipfile.ZipFile(self.path) as z:
                    raw = z.read(rel)
            else:
                raw = (self.path / rel).read_bytes()
        except (KeyError, FileNotFoundError):
            return None
        return json.loads(raw.decode("utf-8-sig"))


def key(row: dict) -> tuple:
    name = row["machine"] if "machine" in row else row.get("name")
    return (str(row.get("resourceGroup", "")).lower(), str(name or "").lower())


def is_empty(value) -> bool:
    return value in (None, "", "[]", "null", "{}") or (isinstance(value, list) and not value)


def verify(pkg: Package) -> list[dict]:
    results = pkg.get("results.json") or {}
    by_id = {r["id"]: r for r in results.get("results", [])}
    machines = pkg.get("data/machines.json")
    extensions = pkg.get("data/extensions.json") or []
    gc = pkg.get("data/gcComp.json") or []
    defender = pkg.get("data/defender.json") or []
    rows: list[dict] = []

    def add(rule, check, expected, actual, ok, note=""):
        rows.append({"rule": rule, "check": check, "expected": expected, "actual": actual, "status": "PASS" if ok else "FAIL", "note": note})

    def skip(rule, check, why):
        rows.append({"rule": rule, "check": check, "expected": "-", "actual": "-", "status": "SKIP", "note": why})

    if machines is None:
        skip("V00", "all", "data/machines.json is missing; nothing to recompute")
        return rows
    total = (results.get("scope") or {}).get("machinesTotal")
    if total is not None:
        add("V01", "scope", len(machines), total, len(machines) == total, "machines in data/machines.json = machinesTotal in results.json")
    keys = [key(m) for m in machines]
    add("V02", "scope", len(keys), len(set(keys)), len(keys) == len(set(keys)), "machine key (resource group + name) is unique")

    if "CHK-21" in by_id:
        exp = sum(1 for m in machines if re.search(r"\d", str(m.get("incomingPorts") or "")))
        add("V10", "CHK-21", exp, by_id["CHK-21"]["found"], exp == by_id["CHK-21"]["found"], "machines with ports in incomingconnections.ports")
    if "CHK-23" in by_id:
        exp = sum(1 for m in machines if is_empty(m.get("extAllow")) and is_empty(m.get("extBlock")))
        add("V11", "CHK-23", exp, by_id["CHK-23"]["found"], exp == by_id["CHK-23"]["found"], "machines with neither allowlist nor blocklist")
    if "CHK-28" in by_id and extensions:
        exp = sum(1 for e in extensions if str(e.get("state")) != "Succeeded")
        add("V12", "CHK-28", exp, by_id["CHK-28"]["found"], exp == by_id["CHK-28"]["found"], "extensions not in Succeeded")
    if "CHK-37" in by_id:
        exp = sum(1 for m in machines if str(m.get("status")) != "Connected")
        add("V13", "CHK-37", exp, by_id["CHK-37"]["found"], exp == by_id["CHK-37"]["found"], "machines not Connected")
    if "CHK-39" in by_id and any(str(m.get("status")) == "Connected" for m in machines):
        ama = {key(e) for e in extensions if re.fullmatch(r"AzureMonitor(Windows|Linux)Agent", str(e.get("extType")))}
        exp = sum(1 for m in machines if str(m.get("status")) == "Connected" and key(m) not in ama)
        add("V14", "CHK-39", exp, by_id["CHK-39"]["found"], exp == by_id["CHK-39"]["found"], "connected machines without Azure Monitor Agent")
    if "CHK-29" in by_id:
        detail = str(by_id["CHK-29"].get("detail"))
        m = re.search(r"Distribution: (.*?)(?= Automatic| Whole|$)", detail)
        if m:
            shown = {}
            for part in m.group(1).split(";"):
                pair = re.fullmatch(r"\s*(\S+): (\d+)\.?\s*", part)
                if pair:
                    shown[pair.group(1)] = int(pair.group(2))
            real = Counter(".".join(str(x.get("agentVersion")).split(".")[:2]) for x in machines if x.get("agentVersion"))
            ok = all(real.get(k) == v for k, v in shown.items()) and sum(shown.values()) <= sum(real.values())
            add("V15", "CHK-29", dict(real), shown, ok, "agent version distribution in the detail matches data/machines.json")
    if "CHK-33" in by_id and defender:
        add("V20", "CHK-33", len(defender), by_id["CHK-33"]["found"], len(defender) == by_id["CHK-33"]["found"], "recommendation rows")
        most = max(int(d.get("machines") or 0) for d in defender)
        add("V21", "CHK-33", f"<= {len(machines)}", most, most <= len(machines),
            "no recommendation can affect more machines than exist in scope (nested resources counted as machines inflate it)")
    if "CHK-55" in by_id and gc:
        bad = {key(g) for g in gc if "baseline" in str(g.get("name", "")).lower() and str(g.get("complianceStatus")) == "NonCompliant"}
        found = by_id["CHK-55"]["found"]
        add("V22", "CHK-55", f">= {len(bad)}", found, found >= len(bad), "machines with a NonCompliant baseline are all counted")
    if "CHK-51" in by_id:
        now = str(results.get("generatedAt") or "")[:10] or "9999-12-31"
        legacy = 0
        for m in machines:
            sku = str(m.get("osSku"))
            if "2008" in sku:
                legacy += 1
            elif "2012" in sku and (now >= "2026-10-14" or str(m.get("esu")) != "Assigned"):
                legacy += 1
        add("V23", "CHK-51", legacy, by_id["CHK-51"]["found"], legacy == by_id["CHK-51"]["found"], "2008/2012 machines without security updates on the collection date")
    return rows


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    rows = verify(Package(Path(args[0])))
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(f"[{r['status']}] {r['rule']} {r['check']}: expected {r['expected']}, collector {r['actual']} - {r['note']}")
    failed = [r for r in rows if r["status"] == "FAIL"]
    print(f"[{'FAIL' if failed else 'PASS'}] independent recomputation: {sum(r['status'] == 'PASS' for r in rows)} agree, {len(failed)} disagree, {sum(r['status'] == 'SKIP' for r in rows)} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
