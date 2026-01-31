from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

from .frontmatter import load_markdown, save_markdown
from .llm import LLMClient
from .text import slugify

IDEA_ID_RE = re.compile(r"\bidea_\d{8}_[0-9a-f]{8}\b")
DOC_ID_RE = re.compile(r"\bdoc_\d{8}_[0-9a-f]{8}\b")

def _today() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()

def _collect_ids(text: str, regex: re.Pattern[str]) -> list[str]:
    return sorted(set(regex.findall(text or "")))

def draft_post(
    repo_root: Path,
    *,
    issue_title: str,
    issue_body: str,
    issue_number: int | None = None,
    idea_ids: list[str] | None = None,
    doc_ids: list[str] | None = None,
) -> Path:
    # Auto-extract if not provided.
    if idea_ids is None:
        idea_ids = _collect_ids(issue_body + "\n" + issue_title, IDEA_ID_RE)
    if doc_ids is None:
        doc_ids = _collect_ids(issue_body + "\n" + issue_title, DOC_ID_RE)

    # Load idea content for context.
    idea_blobs: list[str] = []
    for iid in idea_ids:
        p = repo_root / "ideas" / f"{iid}.md"
        if not p.exists():
            continue
        meta, body = load_markdown(p)
        title = (meta or {}).get("title", "")
        sources = (meta or {}).get("sources", [])
        idea_blobs.append(f"IDEA {iid}: {title}\nSOURCES: {sources}\n{body}")

    # Load doc metadata for context.
    doc_blobs: list[str] = []
    for did in doc_ids:
        candidates = [
            repo_root / "vault" / "owned" / did / "doc.md",
            repo_root / "vault" / "references" / did / "doc.md",
        ]
        for c in candidates:
            if c.exists():
                meta, body = load_markdown(c)
                title = (meta or {}).get("title", "")
                identifiers = (meta or {}).get("identifiers", {})
                lic = (meta or {}).get("license", {})
                doc_blobs.append(f"DOC {did}: {title}\nidentifiers={identifiers}\nlicense={lic}\nnotes={body}")
                break

    system = """You are a technical writer. Draft a GitHub Pages blog post in Markdown (Jekyll compatible).
Output ONLY the post body markdown (no code fences). Do not include YAML frontmatter; it will be added separately.

Requirements:
- The post must clearly state the thesis and scope.
- Use precise technical language, but provide intuition.
- Cite sources by referencing idea IDs and doc IDs inline, e.g. (idea_YYYYMMDD_xxxxxxxx, doc_YYYYMMDD_xxxxxxxx).
- Do NOT include long verbatim excerpts from reference-only sources. Prefer paraphrase + citation.
- Include a short 'Further reading' section listing doc IDs/DOIs/URLs.
"""

    user = f"""Issue: {issue_title}
Issue number: {issue_number}

Issue body:
{issue_body}

Selected ideas:
{chr(10).join(idea_blobs) if idea_blobs else '(none provided)'}

Selected documents:
{chr(10).join(doc_blobs) if doc_blobs else '(none provided)'}
"""

    client = LLMClient.from_env()
    post_body = client.complete(system=system, user=user).strip() + "\n"

    date = _today()
    slug = slugify(issue_title.replace("[publish]", ""))
    if not slug:
        slug = "post"
    filename = f"{date}-{slug}.md"
    out_path = repo_root / "docs" / "_posts" / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)

    meta = {
        "layout": "post",
        "title": issue_title.replace("[publish]", "").strip(),
        "date": date,
        "tags": [],
        "idea_ids": idea_ids,
        "doc_ids": doc_ids,
        "issue": issue_number,
    }
    save_markdown(out_path, meta, post_body)
    return out_path
