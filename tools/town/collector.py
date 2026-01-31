from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .llm import LLMClient

def _load_catalog(repo_root: Path) -> dict[str, Any]:
    cat = repo_root / "catalog"
    ideas = {}
    docs = {}
    try:
        ideas_y = yaml.safe_load((cat / "ideas.yml").read_text(encoding="utf-8")) or {}
        for it in ideas_y.get("ideas", []) or []:
            ideas[it.get("id")] = {"title": it.get("title"), "tags": it.get("tags", [])}
    except Exception:
        pass
    try:
        docs_y = yaml.safe_load((cat / "documents.yml").read_text(encoding="utf-8")) or {}
        for it in docs_y.get("documents", []) or []:
            docs[it.get("id")] = {"title": it.get("title"), "tags": it.get("tags", []), "identifiers": it.get("identifiers", {})}
    except Exception:
        pass
    return {"ideas": ideas, "documents": docs}

def collect(repo_root: Path, *, issue_title: str, issue_body: str) -> str:
    catalog = _load_catalog(repo_root)
    system = """You are the collector agent for a research blog issue.

Produce a single Markdown comment with these sections:
1) Suggested IDs
   - idea_ids: [...]
   - doc_ids: [...]
2) Outline (H2 sections with 1-2 bullet goals each)
3) Missing inputs (what to ingest or mine next)
4) Next command (one of: /mine-ideas <doc_id>, /new-project <title>, /draft-post ...)

Rules:
- Prefer reusing existing idea/doc IDs when possible.
- Do not invent IDs. Only suggest IDs that exist in the provided catalog.
- If the catalog is empty or insufficient, say so and focus on missing inputs.
- Keep the comment concise and actionable.
"""
    user = f"""Issue title:
{issue_title}

Issue body:
{issue_body}

Catalog snapshot (ids -> title/tags):
{json.dumps(catalog, indent=2)}
"""
    client = LLMClient.from_env()
    return client.complete(system=system, user=user).strip() + "\n"
