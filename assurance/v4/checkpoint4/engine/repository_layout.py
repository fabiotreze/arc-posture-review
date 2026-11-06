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
# One copy of the contract schemas (checkpoint 5). Checkpoint 4 keeps only the two schemas that differ: its reviewed-lab fixture comes from an older
# collector, so it is validated with the older collector-results-v3 and scenario-evaluation schemas.
SCHEMAS = REPO_ROOT / "assurance" / "v4" / "checkpoint5" / "schemas"
CP4_SCHEMAS = CP4_ROOT / "schemas"
CP4_REPORTS = CP4_ROOT / "reports"

FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures"

REVIEWED_LAB_FIXTURE = (
    FIXTURE_ROOT / "reviewed-lab-sanitized.zip"
)

REVIEWED_LAB_REPORT = (
    CP4_REPORTS / "reviewed-lab-evaluation.json"
)


def schema_paths() -> dict[str, Path]:
    """Checkpoint 5 schemas, overridden by the few checkpoint 4 schemas that differ."""
    paths = {p.name: p for p in sorted(SCHEMAS.glob("*.json"))}
    paths.update({p.name: p for p in sorted(CP4_SCHEMAS.glob("*.json"))})
    return paths
