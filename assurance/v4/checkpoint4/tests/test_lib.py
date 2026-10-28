from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

CP4 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CP4))

from engine.repository_layout import (
    REPO_ROOT,
    REVIEWED_LAB_FIXTURE,
)

from engine.deterministic_engine import (
    DeterministicEvaluationEngine,
    LoadedEvidence,
    load_evidence,
)

ROOT = REPO_ROOT
FIXTURE = REVIEWED_LAB_FIXTURE


def engine():
    return DeterministicEvaluationEngine(REPO_ROOT)


def fixture():
    return load_evidence(FIXTURE)


def mutated(loaded: LoadedEvidence, mutator) -> LoadedEvidence:
    document = deepcopy(loaded.document)
    mutator(document)
    return replace(loaded, document=document, source_name="mutated-results.json", integrity="NOT_PROVIDED", package_digest="0" * 64)


def row(document, check_id):
    return next(item for item in document["results"] if item["id"] == check_id)


def control(report, check_id):
    return next(item for item in report["controlAssessments"] if item["checkId"] == check_id)


def claim(report, check_id):
    return next(item for item in report["claims"] if item["checkId"] == check_id)


def observation(report, check_id):
    return next(item for item in report["observations"] if item["checkId"] == check_id)
