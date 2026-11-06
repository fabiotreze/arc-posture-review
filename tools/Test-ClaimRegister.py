#!/usr/bin/env python3
"""Claim register: every numeric threshold of the collector is registered with the state of its foundation.

Checks: schema; verified entries carry an official URL, evidence and a date; kit criteria carry a rationale; unverified entries say what to check;
every threshold literal found in the collector is covered by an entry and every registered token still exists (no stale entry)."""
import datetime, json, re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "criteria/v4/sources.json"
COLLECTOR = ROOT / "scripts/Invoke-ArcPostureReview.ps1"
STATUSES = {"VERIFIED_OFFICIAL", "VERIFIED_CVE", "KIT_CRITERION", "UNVERIFIED"}
OFFICIAL_HOSTS = {"learn.microsoft.com", "msrc.microsoft.com", "nvd.nist.gov", "azure.microsoft.com", "github.com"}
PATTERN = re.compile(
    r"(?<!Count )(-(?:lt|le|gt|ge|eq|ne)\s+-?\d+(?:\.\d+)?)|(AddMonths\(-?\d+\))|(AddDays\(-?\d+\))|(\[version\]'[\d.]+')|('\d{4}-\d{2}-\d{2}')"
    r"|(\b\d+ (?:days?|months?)\b)|(\$\w*(?:Floor|Target|Cutoff|Tol)\w*\s*=\s*[^\s;]+)|(\$P_\w+ = [\d.]+)")
TRIVIAL = re.compile(r"-(?:gt|ge|eq|ne|lt|le) [01]")


def collector_tokens() -> dict[str, list[int]]:
    lines = COLLECTOR.read_text(encoding="utf-8-sig").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("# Support tables"))
    end = next(i for i, l in enumerate(lines) if "Canonical v4 report" in l)
    found: dict[str, list[int]] = {}
    for i in range(start, end):
        for group in PATTERN.findall(lines[i]):
            for hit in group:
                if hit:
                    hit = re.sub(r"\s+", " ", hit)
                    if not TRIVIAL.fullmatch(hit):
                        found.setdefault(hit, []).append(i + 1)
    return found


def main() -> int:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    errors: list[str] = []
    ids = [e["id"] for e in data["entries"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate entry ids")
    covered: set[str] = set(data.get("ignoredTokens", []))
    today = datetime.date.today()
    counts: dict[str, int] = {}
    stale_review: list[str] = []
    for e in data["entries"]:
        label = e.get("id", "?")
        status = e.get("status")
        counts[status] = counts.get(status, 0) + 1
        if status not in STATUSES:
            errors.append(f"{label}: invalid status {status}")
            continue
        for lang in ("en-US", "pt-BR"):
            if not (e.get("claim", {}).get(lang) or "").strip():
                errors.append(f"{label}: claim.{lang} is empty")
        try:
            datetime.date.fromisoformat(e["verifiedOn"])
        except (KeyError, ValueError):
            errors.append(f"{label}: verifiedOn must be an ISO date")
        for s in e.get("sources", []):
            host = urlparse(s.get("url", "")).hostname
            if host not in OFFICIAL_HOSTS:
                errors.append(f"{label}: source host not allowed: {s.get('url')}")
        if status in ("VERIFIED_OFFICIAL", "VERIFIED_CVE"):
            if not e.get("sources"):
                errors.append(f"{label}: a verified entry needs a source URL")
            if not (e.get("evidence") or "").strip():
                errors.append(f"{label}: a verified entry needs the evidence (quote or finding)")
            if status == "VERIFIED_CVE" and not any("nvd.nist.gov" in s["url"] or "msrc.microsoft.com" in s["url"] for s in e.get("sources", [])):
                errors.append(f"{label}: a CVE entry needs an NVD or MSRC URL")
            if status == "VERIFIED_OFFICIAL" and not any(urlparse(s["url"]).hostname in ("learn.microsoft.com", "azure.microsoft.com") for s in e.get("sources", [])):
                errors.append(f"{label}: an official entry needs a Microsoft Learn or Azure URL")
        if status == "KIT_CRITERION" and not (e.get("rationale") or "").strip():
            errors.append(f"{label}: a kit criterion needs a rationale")
        if status == "UNVERIFIED" and not (e.get("todo") or "").strip():
            errors.append(f"{label}: an unverified entry needs a todo")
        if e.get("reviewBy") and datetime.date.fromisoformat(e["reviewBy"]) < today:
            stale_review.append(label)
        target = ROOT / e["file"] if e.get("file") else COLLECTOR
        text = target.read_text(encoding="utf-8-sig") if target.exists() else ""
        if e.get("file") and not target.exists():
            errors.append(f"{label}: file not found: {e['file']}")
        for token in e.get("tokens", []):
            if token not in text:
                errors.append(f"{label}: token no longer in {target.name}: {token}")
            if not e.get("file"):
                covered.add(token)

    for token, where in sorted(collector_tokens().items()):
        if token not in covered:
            errors.append(f"threshold without a register entry: {token} (collector line {where[0]})")

    if errors:
        print(f"[FAIL] claim register: {len(errors)} problem(s)")
        for error in errors:
            print(" - " + error)
        return 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    print(f"[PASS] claim register: {len(ids)} entries ({summary}); every collector threshold is registered")
    if stale_review:
        print("[WARN] review date passed: " + ", ".join(stale_review))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
