# Arc Posture Review v4.1.5 — pt-BR rendering fix patch candidate

**Status:** APPROVED_FOR_PUBLICATION — security review approved by Fabio Rodrigues Vieira Costa on 2026-11-06 (15/15). Tagging and publishing remain a separate, manual step.

## Fixed

- The Portuguese v4 report no longer rewrites text that is already Portuguese: "controle(s)" had become "contpapel(is)" in the executive summary and the PARTIAL coverage sentence (v4.1.4). A regression test guards it.
- README (EN-US/PT-BR), known issues and the pt-BR README screenshot refreshed.

## Preserved

- 64 checks (`CHK-01..CHK-64`) and 11 scenarios (`AS01..AS11`); scores and priorities unchanged.
- Canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.
- Single package with the pinned runtime kit.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
