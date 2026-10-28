from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CP5 = REPO_ROOT / "assurance" / "v4" / "checkpoint5"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "reviewed-lab-sanitized.zip"
sys.path.insert(0, str(CP5))

from engine.canonical_v4 import (
    LoadedEvidence, build_assessment, build_comparison, comparison_payload,
    digest, evaluate, evaluate_path, load_evidence,
)


def fixture():
    return load_evidence(FIXTURE)


def canonical():
    return evaluate_path(FIXTURE)


def mutated(loaded: LoadedEvidence, mutator) -> LoadedEvidence:
    document = deepcopy(loaded.document)
    mutator(document)
    return replace(loaded, document=document, source_name="mutated-results.json", integrity="NOT_PROVIDED", package_digest="0" * 64)


def row(document, check_id):
    return next(item for item in document["results"] if item["id"] == check_id)


def canonical_text(document):
    return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
