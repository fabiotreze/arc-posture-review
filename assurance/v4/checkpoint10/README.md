# Checkpoint 10 — release preparation (version-parametrised)

The target release is read from `assurance/v4/checkpoint10/manifest.json` (`release`). The gate validates `release/<release>/release-manifest.json`, `RELEASE-NOTES.md` and `SHA256SUMS`, the collector version, `CITATION.cff` and the CHANGELOG section.

- `PENDING_SECURITY_REVIEW` is valid only with `publishable: false` and without an `APPROVED` decision.
- `publishable: true` requires `APPROVED_FOR_PUBLICATION`, an `APPROVED` security review with reviewer and date, and no open blockers.
- `tools/Prepare-Release.py` regenerates `SHA256SUMS` and records approval only when the security-review record has no unchecked items.

`release/v4.0.0` is the published v4.0.0 record and is not modified. No gate publishes, tags or changes a remote repository.
