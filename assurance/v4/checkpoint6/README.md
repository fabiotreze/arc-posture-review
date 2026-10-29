# Arc Posture Review v4.2.0 — Checkpoint 6

Checkpoint 6 adds a static, bilingual renderer for the canonical `assessment-result.v4.json` emitted by the Evaluation Engine. The report does not calculate risk, priority, scenario state, Defense Coverage or roadmap placement in HTML/JavaScript. Browser JavaScript is limited to navigation, expand/collapse and print.

## PowerShell

```powershell
./arc-posture.ps1 evaluate -Evidence ./collector.zip -Output ./assessment-result.v4.json
./tools/New-V4Report.ps1 -Assessment ./assessment-result.v4.json -OutputDirectory ./report
python ./tools/Invoke-V4FinalGates.py --profile report-quality
```

`New-V4Report.ps1` creates EN-US and PT-BR HTML reports. `comparison: null` is rendered as an explicit no-baseline disclosure. The 64 CHKs remain visible in Checks and in the Evidence → Observation → Claim traceability table.

## Gates

The repository-level `tools/Invoke-V4Gates.py` runs in an isolated copy and verifies the original working tree has exactly the same content after completion. It includes preserved Checkpoints 1–5.1, legacy v3.9.6 report contract/Playwright/localization/PDF gates, and the Checkpoint 6 canonical renderer gates.
