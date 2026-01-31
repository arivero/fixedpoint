from __future__ import annotations

from pathlib import Path

MARKER = "<!-- AUTO-GENERATED. DO NOT EDIT. -->"

def _inject(page_path: Path, new_body: str) -> None:
    text = page_path.read_text(encoding="utf-8")
    if MARKER not in text:
        raise ValueError(f"Marker not found in {page_path}")
    head, _ = text.split(MARKER, 1)
    out = head + MARKER + "\n\n" + new_body.strip() + "\n"
    page_path.write_text(out, encoding="utf-8")

def _strip_heading(md: str) -> str:
    # Drop a leading '# Title' heading if present.
    lines = md.splitlines()
    if lines and lines[0].startswith("# "):
        # remove first heading and following blank line(s)
        i = 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        return "\n".join(lines[i:]).strip()
    return md.strip()

def run(repo_root: Path) -> None:
    catalog = repo_root / "catalog"
    site = repo_root / "docs"

    ideas_md = _strip_heading((catalog / "ideas.md").read_text(encoding="utf-8")) if (catalog / "ideas.md").exists() else "(No ideas yet.)"
    docs_md = _strip_heading((catalog / "documents.md").read_text(encoding="utf-8")) if (catalog / "documents.md").exists() else "(No documents yet.)"
    projects_md = _strip_heading((catalog / "projects.md").read_text(encoding="utf-8")) if (catalog / "projects.md").exists() else "(No projects yet.)"

    _inject(site / "ideas.md", ideas_md)
    _inject(site / "documents.md", docs_md)
    _inject(site / "projects.md", projects_md)
    kanban_md = _strip_heading((catalog / "kanban.md").read_text(encoding="utf-8")) if (catalog / "kanban.md").exists() else "(No projects yet.)"

    _inject(site / "kanban.md", kanban_md)
