# Checkpoint 5 — Canonical assessment-result.v4

Checkpoint 5 is additive to the read-only collector and Checkpoints 1–4.1. It converts collector schema-v3 evidence through the deterministic Checkpoint 4 Evaluation Engine into the canonical `assessment-result.v4.json` contract.

## Pipeline

`collector results.json/.zip → deterministic Evaluation Engine → assessment-result.v4.json`

The canonical result contains metadata and assurance, full Evidence → Observation → Claim traceability, exactly 64 control assessments, Zero Trust views, T0/T1/T2/Global views, 11 Security Scenarios, Prevent/Detect/Respond/Recover coverage, control and scenario residual risk, Action Cards, NOW/30d/90d roadmap and optional embedded before/after comparison.

## Commands from the repository root

```powershell
# All preserved and Checkpoint 5 gates; generated reports/caches are removed.
python tools/Invoke-V4Gates.py

# Collector package -> canonical result
python assurance/v4/checkpoint5/cli/arc_posture.py evaluate --evidence ./tests/fixtures/reviewed-lab-sanitized.zip --output ./assessment-result.v4.json

# Evaluate with an embedded before/after comparison
python assurance/v4/checkpoint5/cli/arc_posture.py evaluate --evidence ./current.zip --baseline ./before.zip --output ./assessment-result.v4.json

# Compare two canonical assessments
python assurance/v4/checkpoint5/cli/arc_posture.py compare --before ./before/assessment-result.v4.json --after ./after/assessment-result.v4.json --output ./assessment-comparison.v4.json
```

`evaluate` and `compare` are deterministic and perform no network call. The gates remove every generated `reports/`, `__pycache__`, `.pyc` and test cache before checking that the Git working tree is clean.
