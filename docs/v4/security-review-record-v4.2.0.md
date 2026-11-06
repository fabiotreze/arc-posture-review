# Arc Posture Review v4.2.0 — foundations of the claims review record

## Scope

- Claim register `criteria/v4/sources.json` and its pages `docs/sources.{en-US,pt-BR}.md` (`tools/Sync-Sources.py`); `tools/Test-ClaimRegister.py` enforces that every collector threshold is registered.
- `tools/Verify-Package.py` and `tools/Test-VerifyPackage.py`: independent, read-only recomputation of key numbers from a package.
- Collector: CHK-21 classification limited to documented channels (22, 6516) with an AdminCenter extension cross-check; CHK-29 CVE ranges per NVD, automatic upgrade detail (eligibility, last attempt, local block limit); two read-only projections added to the machines query (`agentUpgrade.lastAttemptStatus`, `agentUpgrade.desiredVersion`); agent 1.69 in the release calendar.
- App text: the kit index is described as inspired by, not equal to, the Defender for Cloud Secure Score.
- Version alignment for v4.2.0.

## Preserved boundaries

- 64 checks and 11 scenarios; `assessment-result.v4` contract version `4.0.0`; collector schema version 3.
- The collector stays read-only; the new Resource Graph projections only read properties of the machine resource.
- No environment evidence or customer reports in the source/release test package.

## Validation state

- Decision: see the line at the end. The approval is recorded by the assistant on the reviewer's instruction, after the release gate (`tools/Invoke-V4FinalGates.py --profile release`) and PSScriptAnalyzer pass.

## Publication security review

- [x] The register is static data; verified entries cite only Microsoft Learn, Azure, MSRC or NVD pages and carry the quoted evidence and the date.
- [x] Entries that are not confirmed are marked UNVERIFIED with a to-do, and kit criteria are marked as such; nothing unconfirmed is presented as official.
- [x] `tools/Verify-Package.py` only reads the package and writes nothing; it parses JSON with the standard library and executes nothing from the package.
- [x] `tools/Test-CollectorChecks.py` executes the CHK-21 and CHK-29 rules of the collector with synthetic data (ports, AdminCenter cross-check, CVE ranges, automatic upgrade detail).
- [x] The two new Resource Graph projections are read-only and add no permission.
- [x] CHK-21 labels only documented channels; the result stays WARN and states that an allowed port is not evidence of exposure.
- [x] CHK-29 CVE ranges match the NVD records of CVE-2026-26117, CVE-2025-55316 and CVE-2025-49692; CVE-2025-26627 is not mapped per machine.
- [x] The kit still equals the pinned SHA-256 (`tools/Build-Kit.py --check`).
- [x] The collector performs no Azure write and the `az` command allow-list is unchanged.
- [x] `assessment-result.v4.json` passes JSON Schema and semantic validation; CHK-01..CHK-64 occur exactly once.
- [x] Security Scenarios preserve `attackConfirmation=NOT_ASSERTED`.
- [x] The pt-BR rules for the changed sentences are in the app table and in `criteria/v4/pt-br-detail-rules.json` (`tools/Test-PtBrContent.py`).
- [x] README, guide, CHANGELOG, collector, HTML pages and release notes state v4.2.0 (`tools/Test-GuideVersion.py`).
- [x] PSScriptAnalyzer reports no Error/Warning for the collector and the BOM is intact.
- [x] The embedded collector, criteria and CSS in the pages match their sources (`tools/Sync-ReportAssets.py --check`).
- [x] The five CP8 workflows parse; the release workflow runs the new tests before uploading the script and kit.
- [x] The gate entrypoint leaves the working tree exactly as found.
- [x] Release manifest and `SHA256SUMS` validate.

**Decision:** APPROVED — Fabio Rodrigues Vieira Costa, 2026-11-06 (17/17)
