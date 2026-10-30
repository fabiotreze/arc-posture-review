# Arc Posture Review v4.0.5 - release preparation

Patch release on top of v4.0.4 (`7a04552`).

## Changes

- The version markers of the guide embedded in `index.html`, `arc-posture-review.en-US.html` and `arc-posture-review.pt-BR.html` now match the collector version. In v4.0.4 they showed v4.0.1 (index and EN-US) and v3.9.5 (PT-BR).
- New test `tools/Test-GuideVersion.py`, registered in checkpoint 4: the guide markers in the three HTML files and in `docs/guide.*.md` must equal `$ScriptVersion`.

## Unchanged

- Collection, scoring, canonical contract (`assessment-result.v4`, contract 4.0.0) and report rendering.

## Deferred to v4.1.0

- Unchanged from v4.0.4: CHK-42/55/57/63 inconclusive-evidence handling, F2, F3, F4, F5, F6.

## Verification

- `python tools/Invoke-V4FinalGates.py --profile release` and `--profile all`.
- `release/v4.0.5/SHA256SUMS`: SHA-256 of LF-normalised content.

Publication remains blocked until the v4.0.5 security review is approved.
