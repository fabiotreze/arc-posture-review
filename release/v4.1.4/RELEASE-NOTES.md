# Arc Posture Review v4.1.4 — wording and pt-BR report patch candidate

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (16/16). Tagging and publishing remain a separate, manual step.

## Fixed

- Verified-gap action cards no longer use incident-response wording: **Remediate** replaces *Contain and remediate*, with posture actions and closure criteria.
- The pt-BR v4 report shows engine, scenario, card, criterion and collector texts in Portuguese; the canonical JSON is unchanged.
- The Portuguese rules are shared between the app and the report (`criteria/v4/pt-br-detail-rules.json`, parity test); a rule-order bug that mixed languages is fixed.
- The collector traces the report step in `report/report.log`.

## Preserved

- 64 checks (`CHK-01..CHK-64`) and 11 scenarios (`AS01..AS11`); scores and priorities unchanged.
- Canonical `assessment-result.v4` contract version `4.0.0` and collector schema version 3.
- Read-only Azure access; evidence collection unchanged.
- Single package: the `.zip` carries `report/`; the runtime kit stays pinned by SHA-256 (now with two more data files).

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
