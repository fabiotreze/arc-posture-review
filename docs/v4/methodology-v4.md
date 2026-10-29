# Arc Posture Review v4 methodology

**Candidate:** v4.0.0-rc.1  
**Canonical result:** `assessment-result.v4.json`  
**Evidence layer:** exactly `CHK-01` through `CHK-64`

## Purpose and assurance boundary

Arc Posture Review v4 evaluates read-only collector evidence with a deterministic Evaluation Engine. The engine, not the HTML report, decides claim verdicts, control outcomes, residual risk, priority, Security Scenario state, Defense Coverage, Action Cards, roadmap placement and comparison deltas. The report is a projection of the canonical contract and must not infer compromise, exploitation or causality.

## Pipeline

1. The preserved collector produces schema-v3 evidence.
2. Input integrity and required fields are validated.
3. Evidence is normalized into 64 evidence records.
4. Evidence → Observation → Claim → Control traceability is evaluated.
5. The engine evaluates Zero Trust mappings, Tier scope, Security Scenarios and Prevent/Detect/Respond/Recover coverage.
6. The engine emits `assessment-result.v4.json` with a stable digest.
7. CP6 renders EN-US/PT-BR HTML; CP7 renders canonical before/after data.

## Control and evidence semantics

Every CHK appears exactly once in `traceability.evidence`, `traceability.observations`, `traceability.claims` and `controlAssessments`. Missing evidence never yields an effective outcome. Evidence coverage and control outcome are independent: partial coverage can coexist with a conclusive outcome when available evidence is sufficient, while missing required evidence remains unresolved.

## Security Scenarios

Scenarios retain the ordered security model `IDENTITY → MANAGEMENT → HOST → DEFENSE`. Evidence maturity is represented as `HYPOTHESIS`, `POTENTIAL_RELEVANCE`, `PROVIDER_IDENTIFIED` or `VALIDATED`. These are posture-validation states; none confirms an attack. `attackConfirmation` remains `NOT_ASSERTED` unless a future, separately governed incident source changes the contract.

## Defense Coverage

For each scenario, the engine emits Prevent, Detect, Respond and Recover status plus supporting CHK IDs. The report displays these values as supplied. A gap is a posture finding, not proof that a threat actor used the path.

## Risk, priority and roadmap

Residual-risk scores, levels, priorities and NOW/30d/90d placement are deterministic engine outputs. The rendering layer cannot recompute, reorder or override them. Action Cards include owners, actions, closure evidence and rollback text as canonical data.

## Before/after and Verified Improvement

When no baseline is supplied, `comparison` is `null` and the report explicitly states that no trend is asserted. With a baseline, the engine emits control and scenario deltas. CP7 labels only canonical `IMPROVED` rows as **Verified Improvement**; it does not derive improvement from displayed scores.

## Reproducibility and quality gates

The same evidence, model and engine produce byte-stable canonical output. Repository gates cover JSON contracts, determinism, false-positive guards, bilingual parity, responsive Playwright checks and clean PDF output. DevSecOps workflows have read-only repository permissions and do not publish releases.

## Known release constraint

The approved dependency remains `pypdf==6.19.0`. Eleven Dependabot alerts are open; `6.21.2` is not available in the approved feed. This blocks stable v4.0.0 publication until remediated or formally accepted through the security process. See [Known issues](known-issues.md).
