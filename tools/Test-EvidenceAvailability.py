#!/usr/bin/env python3
"""Negative test: evidence availability must come from package members, not from declared sources."""
import importlib.util, os, sys, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENG = os.path.join(ROOT, "assurance", "v4", "checkpoint4", "engine")
sys.path.insert(0, ENG)
spec = importlib.util.spec_from_file_location("deterministic_engine", os.path.join(ENG, "deterministic_engine.py"))
mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
C = next(v for v in vars(mod).values() if isinstance(v, type) and hasattr(v, "_evidence_record"))
class D(dict):
    def __missing__(self, key): return ""
model = D(id="CHK-99", severity="High", resultCriteria="test", sourceRefs=D(datasets=["roles"]),
          claim=D(evidenceRequired=["scope", "timestamp", "source", "roles"], claimType="configuration"))
def evidence(members):
    loaded = types.SimpleNamespace(members=tuple(members), integrity="VERIFIED",
                                   document={"scope": {"s": 1}, "startedAt": "2026-10-30T00:00:00Z"})
    raw = {"status": "PASS", "evidenceCoverage": "FULL", "evidenceSources": "data/roles.json"}
    return C._evidence_record(C, model, raw, loaded), raw
errors = []
declared_only, raw = evidence(["manifest.json"])
if "roles" not in declared_only["missingFields"]:
    errors.append("declared-only source counted as available evidence")
packaged, _ = evidence(["manifest.json", "data/roles.json"])
if packaged["missingFields"]:
    errors.append("packaged dataset reported missing: " + ",".join(packaged["missingFields"]))
obs = C._observation(model, raw, declared_only)
claim = C._claim_evaluation(model, obs, declared_only)
if claim.get("verdict") == "SUPPORTED" or claim.get("confidence") == "HIGH":
    errors.append("PASS with missing required evidence escaped the evidence gate")
if "MISSING_REQUIRED_EVIDENCE" not in obs.get("falsePositiveGuards", []):
    errors.append("MISSING_REQUIRED_EVIDENCE guard not raised")
print(("FAIL" if errors else "PASS") + " evidence availability: " + ("; ".join(errors) if errors else "declared-only source not trusted; packaged dataset accepted; PASS gate holds"))
sys.exit(1 if errors else 0)
