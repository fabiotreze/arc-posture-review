# Arc Posture Review v4 — query and evidence matrix

This matrix is the review baseline for the read-only collector. The generated evidence package is authoritative for a run: `data/query-evidence.json` preserves the normalized query or CLI command, its SHA-256, official source, row/page counts, scope attempts, failures, and collection timestamp; `manifest.json` protects every saved dataset with SHA-256.

## Global execution contract

- Azure Resource Graph queries are paged with `--first 1000` and the returned skip token. A still-present token at the 500-page safety limit rejects the dataset as incomplete; it is never scored as an empty result.
- Per-subscription commands record attempted, successful, and failed scopes. If every scope fails, the dataset is `null` and dependent checks become `ERROR`. Partial scope failures reduce evidence coverage through the permission and collection ledgers.
- Empty data is interpreted by the check, not globally. A valid absence can be `PASS` only when an explicit non-zero target was evaluated. No applicable target is `N/A`; an explicit zero-target `PASS` is rejected again by the v4 Evaluation Engine.
- Resource IDs, subscriptions, resource groups, and machine names are normalized only for matching. Original evidence rows remain in `data/*.json`.
- The collector is read-only. Its command allowlist admits Azure Resource Graph, read/list CLI operations, and four bounded ARM GET patterns only.

Official foundations: [Resource Graph overview](https://learn.microsoft.com/azure/governance/resource-graph/overview), [pagination guidance](https://learn.microsoft.com/azure/governance/resource-graph/concepts/paging-results), [Azure Arc sample queries](https://learn.microsoft.com/azure/azure-arc/servers/resource-graph-samples), [Azure Policy sample queries](https://learn.microsoft.com/azure/governance/policy/samples/resource-graph-samples), and [Defender for Cloud sample queries](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples).

## Dataset-by-dataset validation

| Dataset | Source and purpose | Scope/join key | Zero-row meaning | Official reference |
|---|---|---|---|---|
| `subs` | `resourcecontainers`; resolves the accessible subscription population | `subscriptionId` | Fatal: no accessible scope | [Resource Graph query language](https://learn.microsoft.com/azure/governance/resource-graph/concepts/query-language) |
| `permissions` | ARM `Microsoft.Authorization/permissions` GET per subscription | `subscriptionId` | `UNKNOWN`; dependent evidence cannot be assumed complete | [Permissions - List for subscription](https://learn.microsoft.com/rest/api/authorization/permissions/list-for-subscription) |
| `machines` | `resources` / `microsoft.hybridcompute/machines`; canonical Arc inventory and configuration | lower-case `subscriptionId/resourceGroup/name` | No Arc target; machine controls are `N/A`, not `PASS` | [Arc Resource Graph samples](https://learn.microsoft.com/azure/azure-arc/servers/resource-graph-samples) |
| `extensions` | `resources` / Arc machine extensions; state, type, publisher, version, auto-upgrade | `resourceGroup/machine` | Extension-specific checks are `N/A`; machine hardening checks keep the machine target | [Extension resource reference](https://learn.microsoft.com/azure/templates/microsoft.hybridcompute/machines/extensions) |
| `gcAssign`, `gcComp` | `guestconfigurationresources`; assignments and compliance | `subscriptionId/resourceGroup/machine` | Unknown coverage unless non-applicability is independently established | [Machine Configuration overview](https://learn.microsoft.com/azure/governance/machine-configuration/overview) |
| `related` | Bounded `resources` inventory for PLS, gateway, DNS, resolver, DCR/DCE, Key Vault, workspace, Automation, licenses, Sentinel solutions | resource ID plus Arc subscription/RG scope | Per-resource applicability; never a global healthy conclusion | [Resource Graph overview](https://learn.microsoft.com/azure/governance/resource-graph/overview) |
| `dcra` | `insightsresources`; DCR associations attached to Arc machines | `resourceGroup/machine` → `dcrId` | If AMA exists, zero association is a gap; without AMA, assessment is blocked | [DCR associations](https://learn.microsoft.com/azure/azure-monitor/data-collection/data-collection-rule-associations) |
| `roles` | `authorizationresources`; role assignments left-joined to definitions; published built-in IDs are fallback names | `principalId`, normalized assignment `scope`, `roleId` | Valid zero assignment only against a non-zero machine/subscription target | [RBAC Resource Graph samples](https://learn.microsoft.com/azure/role-based-access-control/resource-graph-samples) |
| `policyAssignments` | `policyresources`; assignments and enforcement mode | assignment `scope` reaches Arc subscription/RG | Zero relevant assignment is a gap, not success | [Policy Resource Graph samples](https://learn.microsoft.com/azure/governance/policy/samples/resource-graph-samples) |
| `policyStates` | `policyresources`; non-compliant states for Arc machines | normalized `resourceId` | PASS only if query succeeded and Arc machine target is non-zero | [Get policy compliance data](https://learn.microsoft.com/azure/governance/policy/how-to/get-compliance-data) |
| `defender` | `securityresources`; unhealthy/exempt assessments summarized by recommendation | `properties.resourceDetails.Id` → Arc machine | Empty unhealthy set is PASS only with successful collection, permissions, and non-zero machine target | [Defender Resource Graph samples](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `govAssign` | Defender governance assignments; due/overdue ownership coverage | assigned Arc resource ID | Supplemental coverage; does not erase an unhealthy recommendation | [Governance rules](https://learn.microsoft.com/azure/defender-for-cloud/governance-rules) |
| `alerts` | Active/InProgress Defender alerts that reference Arc machines | resource identifiers → machine | Absence is not proof of endpoint health; used with plan/MDE coverage | [Defender Resource Graph samples](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `vulns` | Unhealthy Defender subassessments rooted at Arc machines | parent Arc machine ID | Zero findings without plan/MDE coverage remains `PARTIAL` | [Defender Resource Graph samples](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `secscore` | Subscription Secure Score | `subscriptionId` | Informational; score includes non-Arc resources | [Secure Score Resource Graph](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `patch` | Arc patch assessment results | `resourceGroup/machine` | No current assessment is unknown/partial, not zero pending patches | [Azure Update Manager queries](https://learn.microsoft.com/azure/update-manager/query-logs) |
| `advisor` | Arc-impacting Advisor recommendations | impacted machine | Informational cross-check for status/version controls | [Advisor Resource Graph](https://learn.microsoft.com/azure/advisor/advisor-azure-resource-graph) |
| `providers` | `az provider list` per subscription | `subscriptionId/namespace` | Missing required provider is a finding; command failure is dataset failure | [Azure CLI provider](https://learn.microsoft.com/cli/azure/provider) |
| `pricing` | Defender pricing at subscription scope | `subscriptionId/name` | Missing `VirtualMachines` row is not Standard | [Azure CLI security pricing](https://learn.microsoft.com/cli/azure/security/pricing) |
| `pricingRes` | Bounded ARM GET for `Microsoft.Security/pricings/VirtualMachines` per Arc machine | `resourceGroup/machine` | Failed reads are retained per machine and cannot become Free/Standard by assumption | [Defender pricing GET](https://learn.microsoft.com/rest/api/defenderforcloud/pricings/get) |
| `refVersions` | Hybrid Compute Agent Version List and Extension Metadata List | OS globally; region/publisher/type for extensions | Fallback tables must be disclosed; live-query failure lowers freshness confidence | [Agent Version - List](https://learn.microsoft.com/rest/api/hybridcompute/agent-version/list?view=rest-hybridcompute-2025-01-13) |
| `diag` | Subscription Activity Log diagnostic settings | `subscriptionId` | Zero setting is a gap for Activity Log export | [Diagnostic settings CLI](https://learn.microsoft.com/cli/azure/monitor/diagnostic-settings/subscription) |
| `activity` | Hybrid Compute Activity Log events for the requested period | `subscriptionId/resourceId`, `correlationId` | Valid zero event count is an observation, not proof no attack occurred | [Activity Log CLI](https://learn.microsoft.com/cli/azure/monitor/activity-log) |

## Cross-information rules

1. **Machine identity ↔ RBAC:** `machines.identityPrincipalId` joins `roles.principalId`. A machine without `identity.principalId` is a failed validation target, not a clean identity.
2. **Machine ↔ extension:** use normalized `resourceGroup/machine`; subscription remains part of scope validation. Extension absence is interpreted according to the service being measured.
3. **AMA ↔ DCRA ↔ DCR ↔ workspace:** an installed agent alone does not prove data flow. CHK-39 validates deployment; CHK-40 validates association; CHK-41/45 use DCR destinations and workspace/Sentinel evidence.
4. **Defender plan ↔ recommendation/alert/vulnerability:** zero findings are not healthy without plan and sensor/assessment coverage. Subscription Secure Score remains contextual.
5. **Policy assignment ↔ policy state:** assignment reach and enforcement mode are separate from evaluated compliance. Both are retained.
6. **Sample ↔ whole estate:** `MaxMachines` is a risk-prioritized discovery sample. Whole-estate status/version summaries are computed before sampling, and the report labels the denominator explicitly.

## Release evidence

A v4.0.2 package is acceptable only when:

- all 64 checks are present exactly once;
- all 45 automatic checks have an explicit target contract;
- `PASS` with `applicableCount = 0` is absent;
- every query has a ledger row and every saved dataset is covered by the manifest;
- EN-US and PT-BR reports embed the identical canonical JSON and show target, coverage, query reference, and source status;
- deterministic, schema, traceability, visual, localization, security, and release gates pass.
