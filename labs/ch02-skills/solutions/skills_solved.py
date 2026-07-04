"""Skills: per-failure-class runbooks the model loads on demand.

Solved reference for Ch2 levels 3-4 (installed as budo/budo/tools/skills.py).
"""
from __future__ import annotations

import re
from pathlib import Path

from budo.core.loop import Tool

SKILLS_DIR = Path.home() / ".budo" / "skills"

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def _parse(path: Path) -> tuple[dict, str]:
    m = _FRONTMATTER.match(path.read_text())
    if not m:
        raise ValueError(f"{path.name}: missing frontmatter")
    fm_text, body = m.group(1), m.group(2).lstrip("\n")
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body


def list_skills() -> list[tuple[str, str]]:
    """(name, description) for every skill on disk. Feeds render_catalog()."""
    if not SKILLS_DIR.exists():
        return []
    out = []
    for p in sorted(SKILLS_DIR.glob("*.md")):
        try:
            fm, _ = _parse(p)
            if "name" in fm and "description" in fm:
                out.append((fm["name"], fm["description"]))
        except ValueError:
            continue  # skip malformed files; don't crash agent start
    return out


def read_skill(name: str) -> str:
    """Load a skill's body. The MODEL calls this — exposed as a tool."""
    # Only resolve names inside SKILLS_DIR. Never trust caller paths.
    safe = name.replace("/", "").replace("..", "")
    path = SKILLS_DIR / f"{safe}.md"
    if not path.is_file():
        available = ", ".join(n for n, _ in list_skills()) or "(none installed)"
        return f"error: no skill named {name!r}. Available: {available}"
    _, body = _parse(path)
    return body


SKILL_TOOLS: list[Tool] = [
    Tool(
        "read_skill",
        "Load the full procedure for a named skill (see the catalog in this system prompt). "
        "Use this when a symptom matches a skill's description. Returns markdown.",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        read_skill,
    ),
]
