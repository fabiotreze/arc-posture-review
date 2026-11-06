#!/usr/bin/env python3
"""Static quality gate: pyflakes rules through ruff (unused imports and variables, undefined names; configuration in ruff.toml) and orphan detection.

A script under tools/ or assurance/ that no other file mentions (gate, workflow, documentation or import) is dead weight: it is not run by anything and silently rots."""
import re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_REFERENCE_SOURCES = ("SHA256SUMS", "release/", "CHANGELOG.md", "docs/v4/security-review-record", "docs/v4/security-review-addendum")
TEXT_SUFFIXES = (".py", ".ps1", ".json", ".md", ".yml", ".yaml", ".txt", ".html", ".toml", ".psd1", ".cff")
CODE_DIRS = ("tools/", "assurance/")
EXEMPT = {"__init__.py"}
IGNORED_PARTS = {".git", "__pycache__", "build", "reports", ".ruff_cache"}


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return [f for f in result.stdout.splitlines() if f]
    return [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and not IGNORED_PARTS & set(p.relative_to(ROOT).parts)]


def ruff() -> list[str]:
    command = [sys.executable, "-m", "ruff", "check", "--output-format", "concise", "."]
    if shutil.which("ruff") is None and subprocess.run([sys.executable, "-m", "ruff", "--version"], capture_output=True).returncode != 0:
        return ["ruff is not installed: python -m pip install -r requirements-dev.txt"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode == 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip() and not line.startswith(("Found ", "[*]"))] or [result.stderr.strip()]


def orphans(files: list[str]) -> list[str]:
    texts: dict[str, str] = {}
    for f in files:
        if f.endswith(TEXT_SUFFIXES) and not any(s in f for s in SKIP_REFERENCE_SOURCES):
            try:
                texts[f] = (ROOT / f).read_text(encoding="utf-8-sig", errors="ignore")
            except OSError:
                pass
    found = []
    for f in files:
        path = Path(f)
        if not f.startswith(CODE_DIRS) or path.suffix not in (".py", ".ps1") or path.name in EXEMPT:
            continue
        stem = re.escape(path.stem)
        module_import = re.compile(r"\b(?:from|import)\s+" + stem + r"\b")
        if not any(g != f and (path.name in t or module_import.search(t)) for g, t in texts.items()):
            found.append(f)
    return found


def main() -> int:
    problems = ruff()
    dead = orphans(tracked_files())
    if problems or dead:
        print("[FAIL] code quality")
        for line in problems:
            print(" - ruff: " + line)
        for f in dead:
            print(f" - orphan (nothing runs or mentions it): {f}")
        return 1
    print("[PASS] code quality: ruff (pyflakes rules) is clean and no script under tools/ or assurance/ is orphaned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
