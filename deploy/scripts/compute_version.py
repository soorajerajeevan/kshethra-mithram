#!/usr/bin/env python3
"""Compute PEP 440 compatible app versions for CI and server deploys."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path


def short_commit_id(commit_sha: str, length: int = 7) -> str:
    return commit_sha[:length]


def resolve_commit_sha(repo_root: Path, fallback: str = "local") -> str:
    env_sha = os.getenv("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip()
        if sha:
            return sha
    except Exception:
        pass
    return fallback


def compute_ci_version(base_version: str, commit_sha: str) -> str:
    run_number = os.getenv("GITHUB_RUN_NUMBER", "0")
    return f"{base_version}.post{run_number}+{short_commit_id(commit_sha)}"


def compute_deploy_version(base_version: str, commit_sha: str) -> str:
    unix_ts = int(time.time())
    return f"{base_version}.post{unix_ts}+{short_commit_id(commit_sha)}"


def find_repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "VERSION").exists():
            return path
    raise FileNotFoundError("Could not locate VERSION file in parent paths")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["ci", "deploy"],
        default="ci",
        help="ci: GitHub run-number based version, deploy: unix-timestamp based version",
    )
    parser.add_argument(
        "--commit-sha",
        default=os.getenv("GITHUB_SHA", "local"),
        help="Commit SHA used for --mode deploy",
    )
    args = parser.parse_args()

    repo_root = find_repo_root(Path(__file__).resolve().parent)
    base_version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    commit_sha = args.commit_sha if args.commit_sha != "local" else resolve_commit_sha(repo_root)

    if args.mode == "deploy":
        version = compute_deploy_version(base_version, commit_sha)
    else:
        version = compute_ci_version(base_version, commit_sha)
    print(version)


if __name__ == "__main__":
    main()
