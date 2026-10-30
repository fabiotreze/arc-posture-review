# Arc Posture Review v4.0.4 - release preparation

Patch release on top of v4.0.3 (`f0803c9`).

## Changes

- CHK-32 (MDE extension deployed through Arc) and CHK-39 (Azure Monitor Agent) no longer return PASS when the Arc inventory has machines but none is Connected. Both now return N/A with an explicit reason and point to CHK-37 (disconnected or expired machines).
- New negative test `tools/Test-ZeroConnectedEstate.py` (fails on v4.0.3, passes on v4.0.4).

## Unchanged

- Canonical contract, scoring and report rendering. Results are unchanged whenever at least one Arc machine is Connected.

## Deferred to v4.1.0

- Unchanged from v4.0.3: CHK-42/55/57/63 inconclusive-evidence handling, F2, F3, F4, F5, F6.

## Verification

- `python tools/Invoke-V4FinalGates.py --profile release` and `--profile all`.
- `release/v4.0.4/SHA256SUMS`: SHA-256 of LF-normalised content.

Publication remains blocked until the v4.0.4 security review is approved.
