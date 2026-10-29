#!/usr/bin/env python3
from validation_lib import *

RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def main() -> int:
    report = load(); errors = []
    for control in report["controlAssessments"]:
        score = control["residualRisk"]["score"]
        require(control["priority"] == priority_for(score), f"{control['checkId']}: priority formula drift", errors)
    for scenario in report["securityScenarios"]:
        score = scenario["residualRisk"]["score"]
        require(scenario["priority"] == priority_for(score), f"{scenario['scenarioId']}: priority formula drift", errors)
    cards = {row["id"]: row for row in report["actionCards"]}
    seen = []
    for horizon in ("NOW", "30d", "90d"):
        rows = report["roadmap"][horizon]
        expected_order = sorted(rows, key=lambda row: (RANK[row["priority"]], -row["priorityScore"], row["riskId"]))
        require(rows == expected_order, f"{horizon}: unstable roadmap ordering", errors)
        for item in rows:
            seen.append(item["actionCardId"])
            card = cards[item["actionCardId"]]
            require(card["horizon"] == horizon == horizon_for(card["priority"]), f"{card['id']}: horizon formula drift", errors)
            require(item["priorityScore"] == card["priorityScore"], f"{card['id']}: score drift into roadmap", errors)
    require(len(seen) == len(set(seen)) == len(cards), "Action Cards must occur exactly once in roadmap", errors)
    require(set(seen) == set(cards), "Action Card/roadmap coverage mismatch", errors)
    return finish(errors, "deterministic priority and NOW/30d/90d roadmap")


if __name__ == "__main__":
    raise SystemExit(main())
