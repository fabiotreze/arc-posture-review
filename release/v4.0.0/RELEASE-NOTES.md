# Arc Posture Review v4.0.0 — release preparation

This directory prepares, but does not publish, v4.0.0.

## Included

- Canonical render-only v4 report with 64-CHK traceability.
- Before/after visual and Verified Improvement.
- Five read-only DevSecOps workflows.
- v4 methodology, threat model and review checklists.
- Release manifest and SHA256SUMS validation.

## Publication status

**BLOCKED — pending security review.** KI-V4-001 is resolved: `pypdf` moved from `6.19.0` to `6.21.2`, closing the eleven Dependabot alerts per requirements file. Stable publication must not proceed until the security-review checklist is repeated and approved.

## Security review

The v4.0.0 security review was repeated after KI-V4-001 and **APPROVED** on 2026-10-29 by Fabio Rodrigues Vieira Costa (29/29 checklist items).
The release manifest status is `APPROVED_FOR_PUBLICATION` with `publishable: true`. Publication (tag and GitHub release) is a separate manual step.
