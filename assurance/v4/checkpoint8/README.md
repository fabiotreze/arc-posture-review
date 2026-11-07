# Checkpoint 8 — Repository DevSecOps

> **Historical (checkpoint 8, v4.0.x).** Since v4.2.3 the repository runs two v4 workflows (`v4-pr-quality` and `v4-security-regression`) besides `psscriptanalyzer` and `release`; see `docs/v4.2.3-cleanup.md`.

Checkpoint 8 adds five read-only GitHub Actions quality gates for the real repository: PR quality, v4 methodology, security regression, report quality and release readiness. Workflows use read-only repository permissions and do not perform source-control or release mutations. Infrastructure deployment and operational emergency procedures are outside this checkpoint.
