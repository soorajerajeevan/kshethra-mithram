#!/usr/bin/env python3
"""Compute PEP 440 compatible app versions for CI and server deploys."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


def compute_ci_version(base_version: str) -> str:
    run_number = os.getenv("GITHUB_RUN_NUMBER", "0")
    short_sha = os.getenv("GITHUB_SHA", "local")[:7]
    return f"{base_version}.post{run_number}+g{short_sha}"


def compute_deploy_version(base_version: str, commit_sha: str) -> str:
    unix_ts = int(time.time())
    short_sha = commit_sha[:7]
    return f"{base_version}.post{unix_ts}+g{short_sha}"


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

    if args.mode == "deploy":
        version = compute_deploy_version(base_version, args.commit_sha)
    else:
        version = compute_ci_version(base_version)
    print(version)


if __name__ == "__main__":
    main()
