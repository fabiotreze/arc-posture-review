# Arc Posture Review v4.0.0 — release preparation

This directory prepares, but does not publish, v4.0.0.

## Included

- Canonical render-only v4 report with 64-CHK traceability.
- Before/after visual and Verified Improvement.
- Five read-only DevSecOps workflows.
- v4 methodology, threat model and review checklists.
- Release manifest and SHA256SUMS validation.

## Publication status

**BLOCKED.** Eleven Dependabot alerts remain for the approved `pypdf==6.19.0`. The desired `6.21.2` patch is unavailable in the approved feed. Stable publication must not proceed until KI-V4-001 exit criteria are satisfied and the security review is repeated.
