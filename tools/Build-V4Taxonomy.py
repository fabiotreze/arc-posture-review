#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "taxonomy" / "v4"
OUT.mkdir(parents=True, exist_ok=True)

def write(name: str, obj: dict) -> None:
    path = OUT / name
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

write("zero-trust-principles.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "principles": [
        {
            "id": "VERIFY_EXPLICITLY",
            "name": "Verify explicitly"
        },
        {
            "id": "USE_LEAST_PRIVILEGE",
            "name": "Use least privilege"
        },
        {
            "id": "ASSUME_BREACH",
            "name": "Assume breach"
        }
    ]
})

write("zero-trust-pillars.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "pillars": [
        {"id": "ID", "name": "Identities"},
        {"id": "EP", "name": "Endpoints"},
        {"id": "DT", "name": "Data"},
        {"id": "AP", "name": "Applications"},
        {"id": "IN", "name": "Infrastructure"},
        {"id": "NW", "name": "Network"},
        {"id": "SO", "name": "SecOps"}
    ]
})

write("tiers.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "tiers": [
        {
            "id": "T0",
            "name": "Control Plane",
            "privilegeWeight": 100
        },
        {
            "id": "T1",
            "name": "Workload and Server Management",
            "privilegeWeight": 70
        },
        {
            "id": "T2",
            "name": "User Access",
            "privilegeWeight": 35
        },
        {
            "id": "GLOBAL",
            "name": "Global Governance",
            "privilegeWeight": None
        },
        {
            "id": "UNKNOWN",
            "name": "Not established",
            "privilegeWeight": None
        }
    ],
    "rules": {
        "tierIsNotBusinessCriticality": True,
        "effectiveTierRule": "Highest privileged plane reachable or controllable",
        "inferredTierRequiresValidation": True
    }
})

write("risk-families.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "riskFamilies": [
        {"id": "R01", "name": "Asset Visibility and Ownership"},
        {"id": "R02", "name": "Architecture and Governance"},
        {"id": "R03", "name": "Identity and Privileged Access"},
        {"id": "R04", "name": "Network Exposure and Lateral Movement"},
        {"id": "R05", "name": "Arc Agent, Extensions and Remote Execution"},
        {"id": "R06", "name": "Protection, Baseline and Vulnerabilities"},
        {"id": "R07", "name": "Telemetry, Detection and Response"},
        {"id": "R08", "name": "Patching and Lifecycle"},
        {"id": "R09", "name": "Operational and Change Risk"},
        {"id": "R10", "name": "Data Protection and Residency"},
        {"id": "R11", "name": "Licensing, Entitlement and Cost"}
    ]
})

write("attack-surfaces.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "attackSurfaces": [
        {"id": "AS01", "name": "Identity Control Plane"},
        {"id": "AS02", "name": "Azure Resource Management Plane"},
        {"id": "AS03", "name": "Azure Arc Agent"},
        {"id": "AS04", "name": "Arc Extensions"},
        {"id": "AS05", "name": "Remote Operations"},
        {"id": "AS06", "name": "Local OS Privilege"},
        {"id": "AS07", "name": "Network Connectivity"},
        {"id": "AS08", "name": "Monitoring and Telemetry"},
        {"id": "AS09", "name": "Patch and Software Supply"},
        {"id": "AS10", "name": "SQL Management Plane"},
        {"id": "AS11", "name": "Secrets and Credentials"}
    ]
})

write("security-boundaries.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "boundaries": [
        {
            "id": "SB01",
            "name": "Identity to Azure Control Plane"
        },
        {
            "id": "SB02",
            "name": "Azure Control Plane to Arc Resource"
        },
        {
            "id": "SB03",
            "name": "Arc Resource to Connected Machine Agent"
        },
        {
            "id": "SB04",
            "name": "Connected Machine Agent to Local Host"
        },
        {
            "id": "SB05",
            "name": "Extension to Local Privileged Context"
        },
        {
            "id": "SB06",
            "name": "Workload to Workload"
        },
        {
            "id": "SB07",
            "name": "Tier to Higher Privileged Tier"
        }
    ]
})

write("severity.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "technicalSeverity": [
        {"id": "CRITICAL", "score": 100},
        {"id": "HIGH", "score": 80},
        {"id": "MEDIUM", "score": 55},
        {"id": "LOW", "score": 25},
        {"id": "INFORMATIONAL", "score": 0}
    ],
    "riskBands": [
        {"id": "CRITICAL", "min": 80, "max": 100},
        {"id": "HIGH", "min": 60, "max": 79},
        {"id": "MEDIUM", "min": 40, "max": 59},
        {"id": "LOW", "min": 20, "max": 39},
        {"id": "INFORMATIONAL", "min": 0, "max": 19},
        {"id": "NOT_EVALUATED", "min": None, "max": None}
    ]
})

write("assurance.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "coverage": ["FULL", "PARTIAL", "NONE", "ERROR"],
    "confidence": ["HIGH", "MEDIUM", "LOW", "UNKNOWN"],
    "freshness": ["CURRENT", "STALE", "UNKNOWN"],
    "rule": "Evidence assurance never reduces observed risk solely because evidence is incomplete"
})

write("control-effectiveness.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "states": [
        "NOT_ASSESSED",
        "CONFIGURED",
        "OBSERVED",
        "VALIDATED",
        "DEGRADED",
        "INEFFECTIVE"
    ],
    "rules": [
        "CONFIGURED does not imply VALIDATED",
        "OBSERVED does not imply end-to-end effectiveness"
    ]
})

write("defense-coverage.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "functions": [
        "PREVENT",
        "DETECT",
        "RESPOND",
        "RECOVER"
    ],
    "states": [
        "MISSING",
        "PARTIAL",
        "CONFIGURED",
        "OBSERVED",
        "VALIDATED",
        "NOT_ASSESSED",
        "NOT_APPLICABLE"
    ]
})

write("threat-scenarios.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "scenarioStates": [
        "HYPOTHESIS",
        "POTENTIAL_RELEVANCE",
        "PROVIDER_IDENTIFIED",
        "VALIDATED"
    ],
    "stages": [
        {
            "id": "TS01",
            "name": "Initial compromise"
        },
        {
            "id": "TS02",
            "name": "Identity or account expansion"
        },
        {
            "id": "TS03",
            "name": "Privilege escalation"
        },
        {
            "id": "TS04",
            "name": "Persistence or expansion"
        },
        {
            "id": "TS05",
            "name": "Containment and response"
        }
    ],
    "rules": [
        "Threat hypothesis is not an observed attack",
        "Potential relevance is not a validated attack path",
        "Attack paths require provider-identified or independently validated evidence"
    ]
})

write("priority-rules.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "weights": {
        "technicalSeverity": 0.25,
        "tierPrivilege": 0.25,
        "exposure": 0.15,
        "attackPath": 0.15,
        "businessCriticality": 0.10,
        "blastRadius": 0.10
    },
    "rules": {
        "evidenceCoverageChangesRisk": False,
        "missingEvidenceDefault": "UNKNOWN",
        "configuredMeansValidated": False,
        "hypothesisMeansAttackPath": False
    },
    "overrides": [
        {
            "id": "PR-001",
            "description": "Failed privileged-execution control affecting Tier 0",
            "effectiveTier": "T0",
            "privilegedExecution": True,
            "postureStatus": "FAIL",
            "minimumPriority": "CRITICAL"
        },
        {
            "id": "PR-002",
            "description": "Validated or provider-identified path reaching Tier 0",
            "attackPathToTier0": True,
            "minimumPriority": "CRITICAL"
        },
        {
            "id": "PR-003",
            "description": "Unsupported production component",
            "supportedLifecycle": False,
            "environment": "Production",
            "minimumPriority": "HIGH"
        }
    ]
})

write("roadmap-policy.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "lanes": [
        {
            "id": "NOW",
            "description": "Critical risk or immediate override"
        },
        {
            "id": "DAYS_30",
            "description": "High risk or prerequisite for Critical remediation"
        },
        {
            "id": "DAYS_90",
            "description": "Medium risk or maturity improvement"
        },
        {
            "id": "BACKLOG",
            "description": "Low risk"
        },
        {
            "id": "DECISION_REQUIRED",
            "description": "Architecture or governance decision required"
        },
        {
            "id": "ASSURANCE_REQUIRED",
            "description": "Evidence gap prevents reliable conclusion"
        }
    ],
    "rule": "Roadmap position includes risk, dependency ordering, lifecycle deadlines and assurance requirements"
})

write("action-cards.json", {
    "schemaVersion": "1.0",
    "taxonomyVersion": "4.0.0",
    "actionCards": [
        {"id":"AC01","name":"Inventory, tags and Arc map","riskFamilies":["R01"]},
        {"id":"AC02","name":"Arc architecture and landing zone","riskFamilies":["R02"]},
        {"id":"AC03","name":"Tiering and remote operations","riskFamilies":["R03","R05"]},
        {"id":"AC04","name":"Region and residency","riskFamilies":["R10"]},
        {"id":"AC05","name":"Providers, Policy and compliance","riskFamilies":["R02","R06"]},
        {"id":"AC06","name":"RBAC, PIM, MFA and OS access","riskFamilies":["R03"]},
        {"id":"AC07","name":"Secrets and Key Vault","riskFamilies":["R03","R10"]},
        {"id":"AC08","name":"Local administrators and LAPS","riskFamilies":["R03"]},
        {"id":"AC09","name":"Connectivity, Private Link and DNS","riskFamilies":["R04"]},
        {"id":"AC10","name":"Arc local surface and extension guardrails","riskFamilies":["R05"]},
        {"id":"AC11","name":"Machine Configuration, baseline and encryption","riskFamilies":["R06","R10"]},
        {"id":"AC12","name":"Agent and extension lifecycle","riskFamilies":["R05","R08"]},
        {"id":"AC13","name":"Defender for Servers and MDE","riskFamilies":["R06"]},
        {"id":"AC14","name":"Recommendations, threats and vulnerabilities","riskFamilies":["R06"]},
        {"id":"AC15","name":"SQL security and least privilege","riskFamilies":["R03","R06"]},
        {"id":"AC16","name":"Local collection and assurance","riskFamilies":["R09"]},
        {"id":"AC17","name":"Disconnected and expired machines","riskFamilies":["R09"]},
        {"id":"AC18","name":"Advisor, cost and benefits","riskFamilies":["R11"]},
        {"id":"AC19","name":"AMA, DCR, Sentinel and telemetry","riskFamilies":["R07"]},
        {"id":"AC20","name":"Patch authority and update posture","riskFamilies":["R08"]},
        {"id":"AC21","name":"Activity Log and sensitive operations","riskFamilies":["R07"]},
        {"id":"AC22","name":"Pilot, rollout and automation","riskFamilies":["R09"]},
        {"id":"AC23","name":"Removal and hygiene","riskFamilies":["R01"]},
        {"id":"AC24","name":"KPI and periodic review","riskFamilies":["R07"]},
        {"id":"AC25","name":"Legacy, EOS, ESU and exit plan","riskFamilies":["R08"]},
        {"id":"AC26","name":"SQL licensing and usage upload","riskFamilies":["R11"]}
    ]
})

print(f"Generated taxonomy in {OUT}")
