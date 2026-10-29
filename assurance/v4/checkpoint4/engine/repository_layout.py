from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()

    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (
            (candidate / "assurance" / "v4" / "checkpoint3").is_dir()
            and
            (candidate / "assurance" / "v4" / "checkpoint4").is_dir()
            and
            (candidate / "tests" / "fixtures").is_dir()
        ):
            return candidate

    raise RuntimeError(
        "APR repository root could not be resolved from integrated layout"
    )


REPO_ROOT = find_repo_root()

CP3_ROOT = REPO_ROOT / "assurance" / "v4" / "checkpoint3"
CP4_ROOT = REPO_ROOT / "assurance" / "v4" / "checkpoint4"

CP3_DATA = CP3_ROOT / "data"
CP4_REPORTS = CP4_ROOT / "reports"

FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures"

REVIEWED_LAB_FIXTURE = (
    FIXTURE_ROOT / "reviewed-lab-sanitized.zip"
)

REVIEWED_LAB_REPORT = (
    CP4_REPORTS / "reviewed-lab-evaluation.json"
)


def validate_layout() -> None:
    required = [
        CP3_ROOT,
        CP4_ROOT,
        CP3_DATA / "checks.enriched.json",
        CP3_DATA / "control-assessments.json",
        CP3_DATA / "defense-coverage.json",
        CP3_DATA / "security-scenarios.json",
        CP4_ROOT / "engine" / "deterministic_engine.py",
        REVIEWED_LAB_FIXTURE,
    ]

    missing = [
        str(path)
        for path in required
        if not path.exists()
    ]

    if missing:
        raise RuntimeError(
            "APR integrated layout is incomplete:\n"
            + "\n".join(missing)
        )
