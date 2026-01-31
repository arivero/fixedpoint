from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from .ids import new_id

TEMPLATE_DIR = Path(__file__).parent / "templates"

def _now_date() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()

def _render(template_name: str, **kwargs: Any) -> str:
    tmpl = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    out = tmpl
    for k, v in kwargs.items():
        out = out.replace("{{" + k + "}}", "" if v is None else str(v))
    out = out.replace("{{", "").replace("}}", "")
    return out

def new_idea(repo_root: Path, *, title: str, doc_id: str, locator: str = "transcript.md") -> Path:
    iid = new_id("idea")
    path = repo_root / "ideas" / f"{iid}.md"
    content = _render("idea.md", id=iid, title=title, date=_now_date(), doc_id=doc_id, locator=locator)
    path.write_text(content, encoding="utf-8")
    return path

def new_project(repo_root: Path, *, title: str) -> Path:
    pid = new_id("proj")
    proj_dir = repo_root / "projects" / pid
    proj_dir.mkdir(parents=True, exist_ok=True)
    path = proj_dir / "project.md"
    content = _render("project.md", id=pid, title=title, date=_now_date())
    path.write_text(content, encoding="utf-8")
    return path

def new_notebook(repo_root: Path, *, title: str, project_id: str) -> Path:
    nbid = new_id("nb")
    path = repo_root / "lab" / "notebooks" / f"{nbid}.md"
    content = _render("notebook.md", id=nbid, title=title, date=_now_date(), project_id=project_id)
    path.write_text(content, encoding="utf-8")
    return path

def new_blackboard(repo_root: Path, *, title: str, topic: str) -> Path:
    bbid = new_id("bb")
    path = repo_root / "lab" / "blackboards" / f"{bbid}.md"
    content = _render("blackboard.md", id=bbid, title=title, date=_now_date(), topic=topic)
    path.write_text(content, encoding="utf-8")
    return path
