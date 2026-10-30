# Arc Posture Review v4.0.2 - release preparation

Patch release on top of v4.0.1.

## Fixed

A real Azure Arc collection with zero `Microsoft.HybridCompute/machines`
resources exposed an empty-set evaluation issue: selected machine-dependent
controls could return PASS because no non-compliant machine was found.

The following controls are protected by the zero-target guard:

- CHK-12
- CHK-21
- CHK-23
- CHK-24
- CHK-27
- CHK-28
- CHK-32
- CHK-37
- CHK-39
- CHK-51

When the successfully collected Azure Arc machine inventory is empty, these
controls now return:

- Control Result: INFO
- Evidence Coverage: FULL
- found: 0
- explicit disclosure that the control was not evaluated and must not be
  interpreted as PASS

FULL means that collection conclusively established zero targets. It does not
represent an effective control outcome.

## Compatibility

No change to:

- the 64-control catalog
- `assessment-result.v4`
- the scoring model
- security scenarios
- attack confirmation semantics
- legacy v3.9.6 compatibility

## Publication status

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-10-30 (34/34). Tagging and publishing remain a separate, manual step.

Publication remains blocked until the v4.0.2 security review is completed and
approved.
