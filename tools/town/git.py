from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

def _run(cmd: Sequence[str], cwd: Path | None = None) -> str:
    res = subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, text=True, capture_output=True)
    return res.stdout.strip()

def has_changes(cwd: Path | None = None) -> bool:
    out = _run(["git", "status", "--porcelain"], cwd=cwd)
    return bool(out.strip())

def commit_all(message: str, cwd: Path | None = None, author: str | None = None) -> None:
    _run(["git", "add", "-A"], cwd=cwd)
    cmd = ["git", "commit", "-m", message]
    if author:
        cmd.extend(["--author", author])
    # If nothing to commit, git returns non-zero; avoid raising.
    res = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if res.returncode != 0:
        if "nothing to commit" in (res.stdout + res.stderr).lower():
            return
        raise subprocess.CalledProcessError(res.returncode, cmd, res.stdout, res.stderr)

def current_head_message(cwd: Path | None = None) -> str:
    try:
        return _run(["git", "log", "-1", "--pretty=%B"], cwd=cwd)
    except Exception:
        return ""
