#!/usr/bin/env python3
"""Cheat codes for Ch1 — the sensei writes a level's code into the live tree.

Usage:  just ch1 solve <level>        (or: python3 checks/solve.py <level>)

    1   Tool.spec() + the full Agent.run()   (note: run() includes level 4's armor)
    2   get_events / describe / delete_pod   (+ everything from 1)
    3   logs                                 (+ everything from 1-2)
    4   alias of 1 — the armor ships with the loop
    5   prints the Harden-it clamp, ready to paste (it can't guess where
        your run() wants it)

Solving is CUMULATIVE (solve 3 ⇒ levels 1-3 applied) and SURGICAL: only the
named functions are replaced, lifted straight from starter/*_hint.py via AST —
the rest of your file is left alone. The old file is backed up to
~/.budo/solve-backups/ first. Restore skeletons any time:
    git checkout -- budo/budo/core/loop.py budo/budo/tools/k8s.py

Use it to skip ahead, unbrick a broken attempt, or see the demo early.
The belt only counts if your fingers eventually write it.
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
REPO = LAB.parents[1]
LIVE = {"loop": REPO / "budo/budo/core/loop.py", "k8s": REPO / "budo/budo/tools/k8s.py"}
HINT = {"loop": LAB / "starter/loop_hint.py", "k8s": LAB / "starter/k8s_hint.py"}
BACKUPS = Path.home() / ".budo" / "solve-backups"

GREEN, DIM, RESET = "\033[32m", "\033[2m", "\033[0m"

# (file, class-or-None, function) per level; solve n applies levels 1..n
COMPONENTS = {
    1: [("loop", "Tool", "spec"), ("loop", "Agent", "run"), ("loop", "Agent", "_execute")],
    2: [("k8s", None, "get_events"), ("k8s", None, "describe"), ("k8s", None, "delete_pod")],
    3: [("k8s", None, "logs")],
}

CLAMP_SNIPPET = '''\
# Paste into the Agent class in budo/budo/core/loop.py, then wrap every tool
# result before appending:  result = self._clamp(result)

MAX_RESULT_CHARS = 8_000  # ~2k tokens; tune per model

    def _clamp(self, result: str) -> str:
        if len(result) <= MAX_RESULT_CHARS:
            return result
        omitted = result.count("\\n") - 40
        return (result[:6_000] + f"\\n[... ~{omitted} lines omitted — "
                "request a narrower slice (grep/since/tail) ...]" + result[-2_000:])
'''


def die(msg: str) -> None:
    print(f"solve: {msg}", file=sys.stderr)
    sys.exit(1)


def _find(tree: ast.Module, cls: str | None, name: str):
    for node in tree.body:
        if cls is None and isinstance(node, ast.FunctionDef) and node.name == name:
            return node, None
        if cls and isinstance(node, ast.ClassDef) and node.name == cls:
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == name:
                    return sub, node
            return None, node  # class exists, method doesn't → insert
    return None, None


def transplant(key: str, targets: list[tuple[str | None, str]]) -> list[str]:
    live_path, hint_path = LIVE[key], HINT[key]
    hint_src, live_src = hint_path.read_text(), live_path.read_text()
    hint_lines, live_lines = hint_src.splitlines(), live_src.splitlines()
    hint_tree = ast.parse(hint_src)
    try:
        live_tree = ast.parse(live_src)
    except SyntaxError as e:
        die(f"{live_path.relative_to(REPO)} doesn't parse (line {e.lineno}: {e.msg}).\n"
            f"       Fix it — or reset: git checkout -- {live_path.relative_to(REPO)}")

    ops, applied = [], []  # ops: (start, end, new_lines) on live_lines[start:end]
    for cls, name in targets:
        h, _ = _find(hint_tree, cls, name)
        if h is None:
            die(f"reference for {name}() not found in {hint_path.name} — course bug, please report")
        seg = hint_lines[h.lineno - 1:h.end_lineno]
        l, parent = _find(live_tree, cls, name)
        label = f"{cls}.{name}" if cls else name
        if l is not None:
            ops.append((l.lineno - 1, l.end_lineno, seg))
        elif parent is not None:  # method missing → append at end of class
            ops.append((parent.end_lineno, parent.end_lineno, ["", *seg]))
        else:
            die(f"can't find {label} (or its class) in {live_path.name} — reset the file and retry")
        applied.append(label)

    for start, end, seg in sorted(ops, key=lambda o: o[0], reverse=True):
        live_lines[start:end] = seg
    live_path.write_text("\n".join(live_lines) + "\n")
    return applied


def backup(paths: set[Path]) -> None:
    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for p in paths:
        shutil.copy2(p, BACKUPS / f"{stamp}-{p.name}")


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    apply_only = "--apply-only" in sys.argv[2:]
    if arg not in ("1", "2", "3", "4", "5"):
        print(__doc__)
        sys.exit(64)
    n = int(arg)

    upto = min(n if n != 5 else 4, 4)
    levels = [lv for lv in sorted(COMPONENTS) if lv <= upto]
    touched = {LIVE[f] for lv in levels for f, _, _ in COMPONENTS[lv]}
    backup(touched)

    for lv in levels:
        by_file: dict[str, list[tuple[str | None, str]]] = {}
        for f, cls, fn in COMPONENTS[lv]:
            by_file.setdefault(f, []).append((cls, fn))
        for f, targets in by_file.items():
            applied = transplant(f, targets)
            print(f"{GREEN}✓{RESET} level {lv}: wrote {', '.join(applied)} "
                  f"→ {LIVE[f].relative_to(REPO)}")

    print(f"{DIM}  backups in {BACKUPS} · reset skeletons: "
          f"git checkout -- budo/budo/core/loop.py budo/budo/tools/k8s.py{RESET}")

    if n == 1:
        print(f"{DIM}  heads-up: the reference run() already includes level 4's armor.{RESET}")
    if n == 5:
        print(f"\nThe clamp can't be auto-placed (it belongs inside YOUR run()). Paste this:\n")
        print(CLAMP_SNIPPET)
        print(f"{DIM}then: just ch1 check 5{RESET}")
        return
    if apply_only:
        return

    check = min(n, 4)
    print(f"\nrunning the checkpoint: just ch1 check {check}\n")
    sys.exit(subprocess.run([sys.executable, str(HERE / "check.py"), str(check)]).returncode)


if __name__ == "__main__":
    main()
