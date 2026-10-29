# False-positive review record — v4.0.0-rc.1

| Review area | Expected result | RC.1 gate |
|---|---|---|
| Missing evidence | Never effective | Automated negative test |
| Unsupported N/A | Rejected | Automated negative test |
| Informational control | Does not score compliance | Engine contract |
| Partial failure | Coverage and outcome remain separate | Engine contract |
| Attack overclaim | `NOT_ASSERTED` retained | Scenario contract |
| Tampered evidence | Integrity validation fails | Automated negative test |
| Verified Improvement | Only canonical IMPROVED rows receive the label | CP7 contract/visual gate |

Final human review remains required using `security-review-checklist.md`.
