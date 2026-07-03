#!/usr/bin/env python3
"""Cheat codes for Ch2 — the sensei writes a level's code into the live tree.

Usage:  just ch2 solve <level>        (or: python3 checks/solve.py <level>)

    1,2   findings — installs solutions/k8s_solved.py (Ch1 tools + all findings)
    3,4   skills + router — the above, plus tools/skills.py, the router
          __main__.py, and env-typo.md into ~/.budo/skills/
    5     the above, plus crashloop.md (the level-5 answer key) into ~/.budo/skills/

⚠️ Coarser than Ch1's solver: Ch2 has you CREATE files, so solving installs
complete solved versions of tools/k8s.py and __main__.py — including the Ch1
solutions — replacing your edits to those files. Backups land in
~/.budo/solve-backups/ first; diff or restore any time:
    git diff budo/ && git checkout -- budo/
(git checkout won't remove tools/skills.py — delete it by hand if you want
the pre-skills state back.)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
REPO = LAB.parents[1]
SOL = LAB / "solutions"
SKILLS_SRC = LAB / "skills"
BUDO = REPO / "budo/budo"
SKILLS_DST = Path.home() / ".budo" / "skills"
BACKUPS = Path.home() / ".budo" / "solve-backups"

GREEN, DIM, RESET = "\033[32m", "\033[2m", "\033[0m"


def install(src: Path, dst: Path) -> None:
    if dst.exists():
        BACKUPS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, BACKUPS / f"{time.strftime('%Y%m%d-%H%M%S')}-{dst.name}")
    shutil.copy2(src, dst)
    print(f"{GREEN}✓{RESET} installed {src.relative_to(LAB)} → {dst.relative_to(REPO) if dst.is_relative_to(REPO) else dst}")


def install_skill(name: str) -> None:
    SKILLS_DST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILLS_SRC / f"{name}.md", SKILLS_DST / f"{name}.md")
    print(f"{GREEN}✓{RESET} skill installed: ~/.budo/skills/{name}.md")


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg not in ("1", "2", "3", "4", "5"):
        print(__doc__)
        sys.exit(64)
    n = int(arg)

    # Ch2 presumes a working Ch1 loop — transplant it first if it's still a skeleton.
    ch1_solve = LAB.parent / "ch01-naked-loop/checks/solve.py"
    subprocess.run([sys.executable, str(ch1_solve), "1", "--apply-only"], check=True)

    install(SOL / "k8s_solved.py", BUDO / "tools/k8s.py")
    if n >= 3:
        install(SOL / "skills_solved.py", BUDO / "tools/skills.py")
        install(SOL / "main_solved.py", BUDO / "__main__.py")
        install_skill("env-typo")
    if n >= 5:
        install_skill("crashloop")
        print(f"{DIM}  (crashloop.md is the level-5 answer key — you were going to write "
              f"this one yourself. No judgment. Some.){RESET}")

    print(f"{DIM}  backups in {BACKUPS} · restore: git checkout -- budo/ "
          f"(and rm budo/budo/tools/skills.py if unwanted){RESET}")

    if n <= 4:
        print(f"\nrunning the checkpoint: just ch2 check {n}\n")
        sys.exit(subprocess.run([sys.executable, str(HERE / "check.py"), str(n)]).returncode)
    print(f"\n{DIM}no offline check for level 5 — restart the agent and run the "
          f"crashloop chaos from the chapter.{RESET}")


if __name__ == "__main__":
    main()
