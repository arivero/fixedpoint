from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Iterable

import yaml

from .frontmatter import load_markdown
from .text import md_table


def _now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _is_entity_file(path: Path) -> bool:
    name = path.name.lower()
    if name in {"readme.md", "index.md"}:
        return False
    if name.endswith(".md") is False:
        return False
    return True


def _collect_md_files(dirpath: Path) -> list[Path]:
    if not dirpath.exists():
        return []
    return [p for p in dirpath.rglob("*.md") if p.is_file() and _is_entity_file(p)]


def _safe_get(d: dict[str, Any], *keys: str, default: Any = "") -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def scan_documents(repo_root: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for base in [repo_root / "vault" / "owned", repo_root / "vault" / "references"]:
        for doc_md in base.glob("*/doc.md"):
            meta, body = load_markdown(doc_md)
            if not meta:
                continue
            docs.append(
                {
                    "id": meta.get("id", ""),
                    "title": meta.get("title", ""),
                    "created": meta.get("created", ""),
                    "updated": meta.get("updated", ""),
                    "license_status": _safe_get(meta, "license", "status", default=""),
                    "identifiers": meta.get("identifiers", {}) or {},
                    "tags": meta.get("tags", []) or [],
                    "path": str(doc_md.relative_to(repo_root)),
                }
            )
    docs.sort(key=lambda x: x.get("id", ""))
    return docs


def scan_ideas(repo_root: Path) -> list[dict[str, Any]]:
    ideas_dir = repo_root / "ideas"
    out: list[dict[str, Any]] = []
    for p in ideas_dir.glob("*.md"):
        if not _is_entity_file(p):
            continue
        meta, body = load_markdown(p)
        if not meta:
            continue
        out.append(
            {
                "id": meta.get("id", ""),
                "title": meta.get("title", ""),
                "created": meta.get("created", ""),
                "updated": meta.get("updated", ""),
                "status": meta.get("status", ""),
                "tags": meta.get("tags", []) or [],
                "sources": meta.get("sources", []) or [],
                "projects": meta.get("projects", []) or meta.get("project_ids", []) or [],
                "path": str(p.relative_to(repo_root)),
            }
        )
    out.sort(key=lambda x: x.get("id", ""))
    return out


def scan_projects(repo_root: Path) -> list[dict[str, Any]]:
    projects_dir = repo_root / "projects"
    out: list[dict[str, Any]] = []
    for proj_md in projects_dir.glob("*/project.md"):
        meta, body = load_markdown(proj_md)
        if not meta:
            continue
        out.append(
            {
                "id": meta.get("id", ""),
                "title": meta.get("title", ""),
                "created": meta.get("created", ""),
                "updated": meta.get("updated", ""),
                "status": meta.get("status", ""),
                "tags": meta.get("tags", []) or [],
                "idea_ids": meta.get("idea_ids", []) or [],
                "issues": meta.get("issues", []) or [],
                "path": str(proj_md.relative_to(repo_root)),
            }
        )
    out.sort(key=lambda x: x.get("id", ""))
    return out


def scan_posts(repo_root: Path) -> list[dict[str, Any]]:
    posts_dir = repo_root / "site" / "_posts"
    out: list[dict[str, Any]] = []
    if not posts_dir.exists():
        return out
    for p in posts_dir.glob("*.md"):
        meta, body = load_markdown(p)
        if not meta:
            continue
        out.append(
            {
                "path": str(p.relative_to(repo_root)),
                "title": meta.get("title", ""),
                "date": meta.get("date", ""),
                "idea_ids": meta.get("idea_ids", []) or meta.get("ideas", []) or [],
                "doc_ids": meta.get("doc_ids", []) or meta.get("documents", []) or [],
                "tags": meta.get("tags", []) or [],
            }
        )
    return out


def build_xref(documents: list[dict[str, Any]], ideas: list[dict[str, Any]], projects: list[dict[str, Any]], posts: list[dict[str, Any]]) -> dict[str, Any]:
    doc_to_ideas: dict[str, list[str]] = {}
    idea_to_docs: dict[str, list[str]] = {}
    for idea in ideas:
        iid = idea.get("id", "")
        srcs = idea.get("sources", []) or []
        doc_ids: list[str] = []
        for s in srcs:
            if isinstance(s, dict) and s.get("doc"):
                doc_ids.append(str(s["doc"]))
        idea_to_docs[iid] = sorted(set(doc_ids))
        for did in doc_ids:
            doc_to_ideas.setdefault(did, []).append(iid)

    for did, lst in doc_to_ideas.items():
        doc_to_ideas[did] = sorted(set(lst))

    project_to_ideas: dict[str, list[str]] = {}
    idea_to_projects: dict[str, list[str]] = {}
    for proj in projects:
        pid = proj.get("id", "")
        iids = [str(x) for x in (proj.get("idea_ids", []) or [])]
        project_to_ideas[pid] = sorted(set(iids))
        for iid in iids:
            idea_to_projects.setdefault(iid, []).append(pid)
    for iid, lst in idea_to_projects.items():
        idea_to_projects[iid] = sorted(set(lst))

    idea_to_posts: dict[str, list[str]] = {}
    doc_to_posts: dict[str, list[str]] = {}
    for post in posts:
        ppath = post.get("path", "")
        for iid in post.get("idea_ids", []) or []:
            idea_to_posts.setdefault(str(iid), []).append(ppath)
        for did in post.get("doc_ids", []) or []:
            doc_to_posts.setdefault(str(did), []).append(ppath)
    for iid, lst in idea_to_posts.items():
        idea_to_posts[iid] = sorted(set(lst))
    for did, lst in doc_to_posts.items():
        doc_to_posts[did] = sorted(set(lst))

    return {
        "generated_at": _now_iso(),
        "doc_to_ideas": doc_to_ideas,
        "idea_to_docs": idea_to_docs,
        "project_to_ideas": project_to_ideas,
        "idea_to_projects": idea_to_projects,
        "idea_to_posts": idea_to_posts,
        "doc_to_posts": doc_to_posts,
    }


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_documents_md(path: Path, documents: list[dict[str, Any]]) -> None:
    rows = []
    for d in documents:
        ids = d.get("identifiers", {}) or {}
        ident = ", ".join([f"doi:{ids.get('doi')}" if ids.get("doi") else "", f"urn:{ids.get('urn')}" if ids.get("urn") else "", f"url:{ids.get('url')}" if ids.get("url") else ""])
        ident = ", ".join([x for x in ident.split(", ") if x])
        rows.append([d.get("id", ""), d.get("title", ""), d.get("license_status", ""), ident, ", ".join(d.get("tags", []) or []), d.get("path", "")])
    table = md_table(["id", "title", "license", "identifiers", "tags", "path"], rows)
    path.write_text("# Documents\n\n" + table, encoding="utf-8")


def write_ideas_md(path: Path, ideas: list[dict[str, Any]], xref: dict[str, Any]) -> None:
    idea_to_posts = xref.get("idea_to_posts", {}) if xref else {}
    rows = []
    for i in ideas:
        iid = i.get("id", "")
        docs = [s.get("doc", "") for s in (i.get("sources", []) or []) if isinstance(s, dict)]
        docs = [d for d in docs if d]
        posts = idea_to_posts.get(iid, [])
        rows.append([iid, i.get("title", ""), i.get("status", ""), ", ".join(i.get("tags", []) or []), ", ".join(sorted(set(docs))), ", ".join(posts), i.get("path", "")])
    table = md_table(["id", "title", "status", "tags", "source_docs", "blog_posts", "path"], rows)
    path.write_text("# Ideas\n\n" + table, encoding="utf-8")


def write_projects_md(path: Path, projects: list[dict[str, Any]]) -> None:
    rows = []
    for p in projects:
        rows.append([p.get("id", ""), p.get("title", ""), p.get("status", ""), str(len(p.get("idea_ids", []) or [])), ", ".join(p.get("tags", []) or []), p.get("path", "")])
    table = md_table(["id", "title", "status", "#ideas", "tags", "path"], rows)
    path.write_text("# Projects\n\n" + table, encoding="utf-8")




def write_kanban_md(path: Path, projects: list[dict[str, Any]]) -> None:
    """Write a simple Markdown kanban board derived from project.status."""
    buckets: dict[str, list[dict[str, Any]]] = {"backlog": [], "active": [], "paused": [], "done": []}
    for p in projects:
        st = str(p.get("status", "backlog") or "backlog")
        buckets.setdefault(st, []).append(p)

    def section(title: str, items: list[dict[str, Any]]) -> str:
        lines = [f"## {title}", ""]
        if not items:
            lines.append("- (none)")
            lines.append("")
            return "\n".join(lines)
        for it in items:
            pid = it.get("id", "")
            t = it.get("title", "")
            lines.append(f"- **{pid}** — {t}  ")
        lines.append("")
        return "\n".join(lines)

    content = "# Kanban\n\n" \
        + section("Backlog", buckets.get("backlog", [])) \
        + section("Active", buckets.get("active", [])) \
        + section("Paused", buckets.get("paused", [])) \
        + section("Done", buckets.get("done", []))

    path.write_text(content, encoding="utf-8")
def write_unused_ideas_md(path: Path, ideas: list[dict[str, Any]], xref: dict[str, Any]) -> None:
    idea_to_posts = xref.get("idea_to_posts", {}) if xref else {}
    unused = []
    for i in ideas:
        iid = i.get("id", "")
        if idea_to_posts.get(iid):
            continue
        if i.get("status") in {"published", "used"}:
            # Explicit status beats crossref.
            continue
        unused.append(i)
    rows = []
    for i in unused:
        docs = [s.get("doc", "") for s in (i.get("sources", []) or []) if isinstance(s, dict)]
        docs = [d for d in docs if d]
        rows.append([i.get("id", ""), i.get("title", ""), i.get("status", ""), ", ".join(sorted(set(docs))), ", ".join(i.get("tags", []) or []), i.get("path", "")])
    table = md_table(["id", "title", "status", "source_docs", "tags", "path"], rows)
    path.write_text("# Unused ideas (computed)\n\n" + table, encoding="utf-8")


def run(repo_root: Path) -> None:
    documents = scan_documents(repo_root)
    ideas = scan_ideas(repo_root)
    projects = scan_projects(repo_root)
    posts = scan_posts(repo_root)

    xref = build_xref(documents, ideas, projects, posts)

    # YAML indexes
    write_yaml(repo_root / "catalog" / "documents.yml", {"generated_at": _now_iso(), "documents": documents})
    write_yaml(repo_root / "catalog" / "ideas.yml", {"generated_at": _now_iso(), "ideas": ideas})
    write_yaml(repo_root / "catalog" / "projects.yml", {"generated_at": _now_iso(), "projects": projects})
    write_yaml(repo_root / "catalog" / "xref.yml", xref)

    # Markdown tables
    write_documents_md(repo_root / "catalog" / "documents.md", documents)
    write_ideas_md(repo_root / "catalog" / "ideas.md", ideas, xref)
    write_projects_md(repo_root / "catalog" / "projects.md", projects)
    write_kanban_md(repo_root / "catalog" / "kanban.md", projects)
    write_unused_ideas_md(repo_root / "catalog" / "unused-ideas.md", ideas, xref)
