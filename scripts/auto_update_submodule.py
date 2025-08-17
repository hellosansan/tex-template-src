from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from typing import List

SUBMODULE_PATH: str = "src"  # Submodule directory inside each repo


def run(cmd: str, cwd: str) -> str:
    """Execute *cmd* in *cwd*; terminate on non-zero exit.

    Args:
        cmd: Shell command to invoke.
        cwd: Working directory for the command.

    Returns:
        The command's standard output as a stripped string.

    Raises:
        SystemExit: If the command returns a non-zero status.
    """
    proc = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[ERROR] ({cwd}) {cmd}\n{proc.stderr.strip()}")
        sys.exit(proc.returncode)
    return proc.stdout.strip()


def run_safe(cmd: str, cwd: str) -> int:
    """Execute *cmd* in *cwd*; return exit code without terminating."""
    proc = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    return proc.returncode


def is_semver(tag: str) -> bool:
    """Return ``True`` when *tag* matches ``v<major>.<minor>.<patch>``."""
    return bool(re.fullmatch(r"v\d+\.\d+\.\d+", tag))


def git_tag_and_push(tag: str, repo: str) -> None:
    """Create *tag* on HEAD and push commits plus tag.

    Args:
        tag: Semantic version tag beginning with ``v``.
        repo: Path to the Git repository.
    """
    print(f"▶ Tagging {repo} with {tag}")
    run(f"git tag {tag}", repo)
    run("git push", repo)
    run(f"git push origin {tag}", repo)


def update_sibling_repos(repos: List[str], tag: str | None) -> None:
    """Synchronize each repository listed in *repos*.

    Steps
    -----
    1. ``git pull``
    2. ``git submodule update --remote --recursive``
       (brings submodule to the latest commit on its tracking branch)
    3. ``git add <SUBMODULE_PATH>``
    4. Commit if changes are staged.

    Args:
        repos: List of repository names to update.
        tag: Tag that triggered the sync; ``None`` when running
             in "no-arg" mode.
    """
    parent_dir = os.path.dirname(os.getcwd())

    for name in repos:
        repo_path = os.path.join(parent_dir, name)
        if not os.path.isdir(repo_path):
            print(f"[WARN] Skipping missing repo: {repo_path}")
            continue

        print(f"\n=== Updating {name} ===")

        # Check for uncommitted changes and stash if needed
        stash_created = False
        if (
            run_safe("git diff --cached --quiet", repo_path) != 0
            or run_safe("git diff --quiet", repo_path) != 0
            or run("git status --porcelain", repo_path).strip()
        ):
            print(" ↳ stashing uncommitted changes")
            run("git stash push -u", repo_path)
            stash_created = True

        try:
            run("git pull", repo_path)
            run("git submodule update --remote --recursive", repo_path)
            run(f"git add {SUBMODULE_PATH}", repo_path)

            has_change = (
                subprocess.run(
                    "git diff --cached --quiet", cwd=repo_path, shell=True
                ).returncode
                != 0
            )

            if has_change:
                message = (
                    f"chore: 自动更新至模版 {tag}"
                    if tag
                    else "chore: 自动更新至最新模版"
                )
                run(f'git commit -m "{message}"', repo_path)
                print(" ↳ committed changes")
            else:
                print(" ↳ no changes")

        finally:
            # Restore stashed changes if we created a stash
            if stash_created:
                print(" ↳ restoring stashed changes")
                run("git stash pop", repo_path)


def main() -> None:
    """CLI dispatcher."""
    parser = argparse.ArgumentParser(
        description="Tag push & multi-repository synchronization tool"
    )

    parser.add_argument("repos", help="Repository names to update (comma-separated)")

    parser.add_argument(
        "-v",
        "--version",
        help=(
            "Optional tag (format vX.Y.Z). "
            "If omitted, only pull & sync when a newer remote v-tag exists."
        ),
    )

    args = parser.parse_args()

    # Parse comma-separated repos
    repo_list = [r.strip() for r in args.repos.split(",") if r.strip()]

    current_repo = os.getcwd()

    # Case A: explicit tag provided
    if args.version:
        if not is_semver(args.version):
            print(
                f"[ERROR] Illegal tag: {args.version} (expected v<major>.<minor>.<patch>)"
            )
            sys.exit(2)

        git_tag_and_push(args.version, current_repo)
        update_sibling_repos(repo_list, args.version)
        return

    # Case B: no tag provided (sync if remote tag advanced)
    print("No tag specified — pulling latest commits …")
    run("git pull", current_repo)
    run("git fetch --tags", current_repo)

    fetched_tags = run("git tag", current_repo).splitlines()
    v_tags = [t for t in fetched_tags if is_semver(t)]

    if not v_tags:
        print("No v-style tags found — exiting.")
        return

    # Sort semver-aware
    v_tags.sort(key=lambda s: list(map(int, s.lstrip("v").split("."))))
    newest_tag = v_tags[-1]

    head_tags = run("git tag --points-at HEAD", current_repo).splitlines()

    if newest_tag in head_tags:
        print("Already on the latest tag — still updating sibling repos ...")
        update_sibling_repos(repo_list, newest_tag)
        return

    print(f"Newer tag detected: {newest_tag} — checking out …")
    run(f"git checkout {newest_tag}", current_repo)
    update_sibling_repos(repo_list, newest_tag)


if __name__ == "__main__":
    main()
