"""Audit trail. If you can't replay it, it didn't happen. (Rule of the dojo.)"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

AUDIT_DIR = Path(os.environ.get("BUDO_AUDIT_DIR", Path.home() / ".budo" / "audit"))


class Audit:
    def __init__(self, command: str):
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        self.path = AUDIT_DIR / f"{int(time.time())}-{command}.jsonl"

    def log(self, kind: str, **payload) -> None:
        rec = {"ts": time.time(), "kind": kind, **payload}
        with self.path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
