from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path
from typing import Any

from .ids import new_id
from .ingest import _render_template, _now_date  # reuse templates

def archive_markdown_as_document(
    repo_root: Path,
    *,
    source_md: Path,
    title: str | None = None,
    license_status: str = "owned",
    url: str | None = None,
    doi: str | None = None,
    urn: str | None = None,
    doc_id: str | None = None,
    ingested_by: str = "archive",
) -> dict[str, str]:
    """Archive an internal Markdown artifact (notebook/blackboard) as a vault document.

    The source markdown is copied into:
      - vault/raw/<doc_id>/note.md
      - vault/owned/<doc_id>/transcript.md   (same content)
    and a doc.md metadata file is created.
    """
    source_md = source_md.expanduser()
    if not source_md.exists():
        raise FileNotFoundError(str(source_md))
    if license_status not in {"owned", "reference-only"}:
        raise ValueError("license_status must be owned or reference-only")

    if doc_id is None:
        doc_id = new_id("doc")

    if title is None:
        title = source_md.stem

    raw_dir = repo_root / "vault" / "raw" / doc_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "note.md"
    shutil.copy2(source_md, raw_path)

    if license_status == "owned":
        doc_dir = repo_root / "vault" / "owned" / doc_id
    else:
        doc_dir = repo_root / "vault" / "references" / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    doc_md_path = doc_dir / "doc.md"
    rendered = _render_template(
        "doc.md",
        id=doc_id,
        title=title,
        date=_now_date(),
        license_status=license_status,
        doi=doi or "",
        urn=urn or "",
        url=url or "",
        ingested_by=ingested_by,
        original_format="md",
        raw_path=str(raw_path.relative_to(repo_root)),
    )
    doc_md_path.write_text(rendered, encoding="utf-8")

    transcript_path = ""
    if license_status == "owned":
        transcript_md = doc_dir / "transcript.md"
        shutil.copy2(source_md, transcript_md)
        transcript_path = str(transcript_md.relative_to(repo_root))

    return {
        "doc_id": doc_id,
        "doc_md": str(doc_md_path.relative_to(repo_root)),
        "raw": str(raw_path.relative_to(repo_root)),
        "transcript": transcript_path,
    }
