# Arc Posture Review v4.2.1 — pt-BR rule table fix patch candidate

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (9/9). Tagging and publishing remain a separate, manual step.

## Fixed

- The Portuguese v4 report now renders the CHK-21 (inbound ports) and CHK-29 (automatic upgrade) sentences in Portuguese; in v4.2.0 the rules were in the wrong place of the app file and the sentences stayed mostly in English.
- A regression test uses sentences from a real run and fails if they are not translated.

## Preserved

- 64 checks and 11 scenarios; canonical `assessment-result.v4` contract version `4.0.0`; collector schema version 3; collector logic unchanged; read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
