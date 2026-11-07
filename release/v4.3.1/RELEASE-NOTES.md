# Arc Posture Review v4.3.1 — download guidance and tooling

**Status:** APPROVED_FOR_PUBLICATION — 11/11 checklist items verified by the release gates and recorded at the request of the maintainer (Fabio Rodrigues Vieira Costa) on 2026-11-06. This is the project's own checklist, not an independent audit. Tagging and publishing remain a separate, manual step.

## Changed

- **Download guidance (EN-US and pt-BR):** the README and `DISCLAIMER.md` say how to get a working offline copy of the app: use *Download raw file* (or the `raw.githubusercontent.com` link) and compare the SHA-256 with `SHA256SUMS.txt`. *Save as* on the GitHub page saves the GitHub web page, not the app, and it cannot load a `.zip`.
- **Development dependencies:** `requirements-dev.txt` updated (playwright, beautifulsoup4, jsonschema, referencing, PyYAML, ruff), superseding the Dependabot update.

## Preserved

- App, collector logic, results, 64 checks and 11 scenarios, canonical `assessment-result.v4` contract version `4.0.0`, collector schema version 3, read-only Azure access.

## Distribution status

This package contains no collected environment data or customer reports. Tagging and publishing remain a separate, manual step.
