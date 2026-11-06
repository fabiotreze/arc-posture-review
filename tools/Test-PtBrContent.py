#!/usr/bin/env python3
"""pt-BR v4 report: engine and static texts are Portuguese, display-only (canonical JSON identical), and the rules mirror the app."""
import html, importlib.util, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
CLI = ROOT / "assurance/v4/checkpoint5/cli/arc_posture.py"
RENDER = ROOT / "assurance/v4/checkpoint6/report/render_v4.py"
RULES = ROOT / "criteria/v4/pt-br-detail-rules.json"
APP_PT = ROOT / "arc-posture-review.pt-BR.html"
ENGINE = ROOT / "assurance/v4/checkpoint4/engine/deterministic_engine.py"


def fail(message: str) -> None:
    print("[FAIL] " + message)
    raise SystemExit(1)


def visible_text(page: str) -> list[str]:
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    return [html.unescape(x).strip() for x in re.findall(r">([^<>]+)<", page)]


def app_rules() -> list[list[str]]:
    text = APP_PT.read_text(encoding="utf-8")
    block = re.search(r"var PT_DETAIL_RULES = \[\r?\n(.*?)\r?\n  \];", text, re.S).group(1)
    rows = []
    for line in block.splitlines():
        match = re.match(r'^\s*\[/(.*)/([gimsuy]*),\s*("(?:[^"\\]|\\.)*")\],?\s*$', line)
        if match:
            rows.append([match.group(1), match.group(2), json.loads(match.group(3))])
    return rows


def golden_sentences() -> list[str]:
    """Sentences produced by the collector in a real run (v4.2.0): each must be rendered in Portuguese, with no English left from the rule table."""
    spec = importlib.util.spec_from_file_location("render_v4", RENDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases = [
        ("6 machine(s) with inbound ports configured on the agent: 2 with SSH (22) or Windows Admin Center (6516), 5 with ports this check does not classify (see unclassifiedPorts); 2 with port 6516 allowed but no AdminCenter extension. The list defines which local ports the Azure Arc connectivity channel may reach, it is not evidence of exposure: confirm the purpose of each port, the need and RBAC.",
         "6 máquina(s) com portas de entrada configuradas no agente"),
        ("Automatic agent upgrade: disabled in Azure on 0 of 7 machine(s); agent below 1.67 (not eligible) on 0; last attempt failed on 0. A local block (automaticupgrade.blocklocally = true) takes precedence over the Azure setting and cannot be read through Azure: check a sample with 'azcmagent config get automaticupgrade.blocklocally' (CHK-36).",
         "Upgrade automático do agente: desabilitado no Azure em 0 de 7"),
        ("228 Defender recommendation(s) affect Arc machines; High severity: 13; Critical/High risk: 0; open 90+ days: 0; attack paths: 0; exemptions: 0.",
         "228 Recomendações do Defender afetam máquinas Arc"),
        ("6 machine(s) with inbound ports configured on the agent: 2 with SSH (22) or Windows Admin Center (6516), 5 with ports this check does not classify (see unclassifiedPorts); 2 with port 6516 allowed but no AdminCenter extension…",
         "6 máquina(s) com portas de entrada configuradas no agente"),
    ]
    problems = []
    for english, expected in cases:
        shown = module._pt_text(english)
        if expected not in shown:
            problems.append(f"not translated: {english[:70]}...")
        elif re.search(r"\b(machine\(s\)|with ports|not eligible|takes precedence)\b", shown):
            problems.append(f"English left in: {shown[:90]}...")
    return problems


def main() -> int:
    data = json.loads(RULES.read_text(encoding="utf-8"))
    leftovers_golden = golden_sentences()
    if leftovers_golden:
        fail("golden sentences: " + "; ".join(leftovers_golden))
    if data["rules"] != app_rules():
        fail("criteria/v4/pt-br-detail-rules.json differs from PT_DETAIL_RULES in arc-posture-review.pt-BR.html; regenerate it from the app table")
    for pattern, flags, _ in [*data["rules"], *data["narrative"]]:
        re.compile(pattern, re.I if "i" in flags else 0)
    order = [p for p, _, _ in data["rules"]]
    if order.index(r"connected machine\(s\)") > order.index(r"machine\(s\)"):
        fail("rule order: 'connected machine(s)' must precede 'machine(s)'")

    with tempfile.TemporaryDirectory() as tmp:
        assessment = Path(tmp) / "assessment.v4.json"
        subprocess.run([sys.executable, str(CLI), "evaluate", "--evidence", str(FIXTURE), "--output", str(assessment)], check=True, capture_output=True)
        pages = {}
        for loc in ("en-US", "pt-BR"):
            out = Path(tmp) / f"{loc}.html"
            subprocess.run([sys.executable, str(RENDER), "--input", str(assessment), "--locale", loc, "--output", str(out)], check=True, capture_output=True)
            pages[loc] = out.read_text(encoding="utf-8")

    canonical = lambda page: re.search(r'<script type="application/json" id="canonical-assessment">(.*?)</script>', page, re.S).group(1)
    if canonical(pages["en-US"]) != canonical(pages["pt-BR"]):
        fail("pt-BR localization must be display-only: the embedded canonical JSON differs")

    texts = visible_text(pages["pt-BR"])
    joined = "\n".join(texts)
    model = ROOT / "assurance/v4/checkpoint3/data"
    english = set()
    taxonomies = json.loads((model / "taxonomies.json").read_text(encoding="utf-8"))
    english.update(row["name"] for row in taxonomies["risks"])
    english.update(row["name"] for row in taxonomies["securityBoundaries"])
    for row in json.loads((model / "security-scenarios.json").read_text(encoding="utf-8")):
        english.update((row["name"], row["hypothesis"]))
    source = ENGINE.read_text(encoding="utf-8")
    for block in re.findall(r"BASIS_(?:ACTIONS|CLOSURE) = \{(.*?)\n\}", source, re.S):
        english.update(re.findall(r'^\s+"(.+)",$', block, re.M))
    english.add("A posture weakness is not evidence of exploitation or compromise.")
    leftovers = sorted(x for x in english if x in joined)
    if leftovers:
        fail("English engine/static text still visible in the pt-BR report: " + "; ".join(leftovers[:5]))
    for marker in ("Contain and remediate", "Contain the exposed boundary", "preserve timestamped evidence"):
        if marker.lower() in pages["en-US"].lower() or marker.lower() in joined.lower():
            fail("incident-response wording in a posture report: " + marker)
    if "Corrigir:" not in joined and "Melhorar a postura:" not in joined:
        fail("action card titles were not localized")
    if "contpapel" in joined or not re.search(r"\d+ controle\(s\) não verificado\(s\)", joined):
        fail("a rule rewrote text that was already Portuguese (controle(s) -> contpapel(is))")
    print("[PASS] pt-BR v4 report: rules mirror the app, static and engine texts are Portuguese, canonical JSON untouched, no incident wording")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
