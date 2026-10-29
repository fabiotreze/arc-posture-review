# Arc Posture Review v4 threat model

## Scope

This model covers the read-only collector package, evidence ZIP, deterministic Evaluation Engine, canonical `assessment-result.v4.json`, static reports, repository gates and CI workflows.

## Security objectives

- Preserve evidence integrity and traceability.
- Prevent missing or malformed evidence from becoming a positive result.
- Prevent the report layer from calculating or overstating security conclusions.
- Keep credentials, tenant identifiers and raw evidence out of committed fixtures and logs.
- Make release readiness reproducible and reviewable.

## Assets

| Asset | Security property |
|---|---|
| Collector and criteria | Integrity, least privilege |
| Evidence package | Confidentiality, integrity, provenance |
| Canonical assessment | Integrity, deterministic reproducibility |
| 64-CHK traceability | Completeness, non-repudiation of derivation |
| Security Scenario model | Correct boundaries, no attack overclaim |
| HTML/PDF reports | Faithful rendering, offline safety |
| Workflows and release metadata | Supply-chain integrity, read-only permissions |

## Trust boundaries

1. Operator workstation → Azure control plane.
2. Collector output → Evaluation Engine input.
3. Evaluation Engine → canonical contract.
4. Canonical contract → HTML/PDF renderer.
5. Repository → GitHub-hosted runner and approved package feed.

## Threats and controls

| Threat | Example | Required control |
|---|---|---|
| Evidence tampering | ZIP content changed after collection | Package/input digest and integrity state |
| Schema confusion | Unexpected fields or cardinality | Draft 2020-12 schemas and semantic validators |
| Missing-evidence optimism | Absent data interpreted as healthy | Missing evidence never PASS; unresolved claim |
| False positive | Proxy signal treated as direct proof | Claim criteria, evidence coverage, guard tests and reviewer checklist |
| Attack overclaim | Posture weakness presented as compromise | `attackConfirmation=NOT_ASSERTED` and scenario guardrail |
| Renderer drift | HTML recomputes score or priority | Render-purity gate and embedded canonical parity |
| Script injection | Evidence rendered as executable content | HTML escaping, restrictive CSP, no contract parsing in browser JavaScript |
| Secret disclosure | Tenant data in fixture or CI artifact | Sanitized fixture and content review |
| Workflow privilege expansion | Write token used by quality gate | `permissions: contents: read` and workflow validator |
| Dependency exposure | Vulnerable PDF parser version | Pinned approved version, Dependabot tracking and stable-release blocker |

## Abuse cases

- A contributor changes JavaScript to derive a lower score: rejected by render-purity and report-contract gates.
- A scenario skips MANAGEMENT: rejected by scenario transition tests.
- A check disappears from Evidence: rejected by exact 64-CHK cardinality gates.
- A pull request adds a mutating command to a v4 workflow: rejected by CP8 workflow policy.
- A stable release is prepared while the pypdf alerts remain: rejected by CP9/CP10 blocker gates.

## Residual risks

- The review is limited to collected scope and point-in-time evidence.
- Read-only collection cannot validate every host-local or incident-response condition.
- Approved-feed lag can prevent immediate dependency remediation.
- A correct posture report does not replace incident investigation, penetration testing or change approval.
