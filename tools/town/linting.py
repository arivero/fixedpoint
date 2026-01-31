from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .frontmatter import load_markdown, FrontmatterError
from .indexer import scan_documents, scan_ideas, scan_projects, scan_posts

REQUIRED_DOC_FIELDS = ["id", "title", "created", "updated"]
REQUIRED_IDEA_FIELDS = ["id", "title", "created", "updated", "status", "sources"]
REQUIRED_PROJECT_FIELDS = ["id", "title", "created", "updated", "status", "idea_ids"]

ALLOWED_IDEA_STATUS = {"seed", "validated", "used", "published"}
ALLOWED_PROJECT_STATUS = {"backlog", "active", "paused", "done"}

def _err(path: str, msg: str) -> str:
    return f"{path}: {msg}"

def lint(repo_root: Path) -> list[str]:
    errors: list[str] = []

    documents = scan_documents(repo_root)
    ideas = scan_ideas(repo_root)
    projects = scan_projects(repo_root)
    posts = scan_posts(repo_root)

    # Duplicate IDs
    def check_duplicates(items: list[dict[str, Any]], kind: str) -> None:
        seen: dict[str, str] = {}
        for it in items:
            iid = str(it.get("id", ""))
            p = it.get("path", "")
            if not iid:
                errors.append(_err(p, f"missing id for {kind}"))
                continue
            if iid in seen:
                errors.append(_err(p, f"duplicate id {iid} (also in {seen[iid]})"))
            else:
                seen[iid] = p

    check_duplicates(documents, "document")
    check_duplicates(ideas, "idea")
    check_duplicates(projects, "project")

    doc_ids = {d.get("id") for d in documents}
    idea_ids = {i.get("id") for i in ideas}
    proj_ids = {p.get("id") for p in projects}

    # Validate document frontmatter fields
    for d in documents:
        p = d.get("path", "")
        for f in REQUIRED_DOC_FIELDS:
            if not d.get(f):
                errors.append(_err(p, f"missing required field {f}"))

        ls = d.get("license_status", "")
        if ls not in {"owned", "reference-only"}:
            errors.append(_err(p, "license.status must be owned or reference-only"))

    # Validate ideas
    for i in ideas:
        p = i.get("path", "")
        for f in REQUIRED_IDEA_FIELDS:
            if i.get(f) in (None, "", []):
                errors.append(_err(p, f"missing required field {f}"))
        st = i.get("status", "")
        if st and st not in ALLOWED_IDEA_STATUS:
            errors.append(_err(p, f"invalid status {st} (allowed: {sorted(ALLOWED_IDEA_STATUS)})"))

        # Validate sources doc IDs
        srcs = i.get("sources", []) or []
        if not isinstance(srcs, list):
            errors.append(_err(p, "sources must be a list"))
            continue
        for s in srcs:
            if not isinstance(s, dict):
                errors.append(_err(p, "each source must be a mapping with keys {doc, locator, quote?}"))
                continue
            did = s.get("doc")
            if not did:
                errors.append(_err(p, "source missing doc"))

            elif did not in doc_ids:
                errors.append(_err(p, f"source doc id not found: {did}"))

    # Validate projects
    for pr in projects:
        p = pr.get("path", "")
        for f in REQUIRED_PROJECT_FIELDS:
            if pr.get(f) in (None, "", []):
                errors.append(_err(p, f"missing required field {f}"))
        st = pr.get("status", "")
        if st and st not in ALLOWED_PROJECT_STATUS:
            errors.append(_err(p, f"invalid status {st} (allowed: {sorted(ALLOWED_PROJECT_STATUS)})"))

        iids = pr.get("idea_ids", []) or []
        if not isinstance(iids, list):
            errors.append(_err(p, "idea_ids must be a list"))
            continue
        for iid in iids:
            if iid not in idea_ids:
                errors.append(_err(p, f"idea_id not found: {iid}"))

    # Validate posts
    for post in posts:
        p = post.get("path", "")
        for iid in post.get("idea_ids", []) or []:
            if iid not in idea_ids:
                errors.append(_err(p, f"post references unknown idea id: {iid}"))
        for did in post.get("doc_ids", []) or []:
            if did not in doc_ids:
                errors.append(_err(p, f"post references unknown doc id: {did}"))

    return errors
