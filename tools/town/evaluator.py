from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .frontmatter import load_markdown

IDEA_ID_RE = re.compile(r"\bidea_\d{8}_[0-9a-f]{8}\b")
DOC_ID_RE = re.compile(r"\bdoc_\d{8}_[0-9a-f]{8}\b")

def evaluate_post(repo_root: Path, post_relpath: str) -> tuple[bool, list[str]]:
    """Deterministic checks for a blog post."""
    p = repo_root / post_relpath
    if not p.exists():
        return False, [f"Post not found: {post_relpath}"]

    meta, body = load_markdown(p)
    if meta is None:
        return False, ["Missing YAML frontmatter."]

    findings: list[str] = []
    ok = True

    idea_ids = meta.get("idea_ids", []) or []
    doc_ids = meta.get("doc_ids", []) or []

    # Existence checks
    for iid in idea_ids:
        if not (repo_root / "ideas" / f"{iid}.md").exists():
            ok = False
            findings.append(f"Frontmatter references missing idea file: {iid}")
    for did in doc_ids:
        if not (repo_root / "vault" / "owned" / did / "doc.md").exists() and not (repo_root / "vault" / "references" / did / "doc.md").exists():
            ok = False
            findings.append(f"Frontmatter references missing doc record: {did}")

    # Citation presence (weak heuristic)
    cited_ideas = set(IDEA_ID_RE.findall(body))
    cited_docs = set(DOC_ID_RE.findall(body))

    missing_cites = [iid for iid in idea_ids if iid not in cited_ideas]
    if missing_cites:
        ok = False
        findings.append(f"Missing inline citations for idea_ids: {', '.join(missing_cites)}")

    missing_doc_cites = [did for did in doc_ids if did not in cited_docs]
    if missing_doc_cites:
        findings.append(f"No inline doc_id mentions for: {', '.join(missing_doc_cites)} (recommended)")

    # Basic structure checks
    if "Further reading" not in body and "Further Reading" not in body:
        findings.append("No 'Further reading' section found (recommended).")

    return ok, findings
