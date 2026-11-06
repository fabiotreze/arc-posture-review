## What and why

<!-- One or two sentences. -->

## Checklist

- [ ] No collected data (`.zip`, `results.json`, `findings/*.csv`, real names, IDs or e-mails) in the diff, the description or screenshots.
- [ ] The collector stays read-only; BOM and line endings of `scripts/Invoke-ArcPostureReview.ps1` are intact.
- [ ] Posture vocabulary kept (verified gap / improvement opportunity / not verified); EN-US and PT-BR both updated.
- [ ] `python tools/Invoke-V4FinalGates.py --profile release` passes (after `Build-Kit.py --write-hash`, `Sync-ReportAssets.py` and `Prepare-Release.py checksums` when applicable).
- [ ] README, guide and CHANGELOG updated when behaviour changes.
