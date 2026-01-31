from __future__ import annotations

import datetime as dt
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .ids import new_id

TEMPLATE_DIR = Path(__file__).parent / "templates"

def _now_date() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()

def _render_template(template_name: str, **kwargs: Any) -> str:
    tmpl = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    out = tmpl
    for k, v in kwargs.items():
        out = out.replace("{{" + k + "}}", "" if v is None else str(v))
    # Remove unreplaced placeholders
    out = out.replace("{{", "").replace("}}", "")
    return out

def _pandoc_exists() -> bool:
    return shutil.which("pandoc") is not None

def _run_pandoc_to_md(src: Path, dst: Path) -> tuple[bool, str]:
    if not _pandoc_exists():
        return False, "pandoc not found"
    try:
        subprocess.run(
            ["pandoc", str(src), "-t", "gfm", "-o", str(dst)],
            check=True,
            text=True,
            capture_output=True,
        )
        return True, "ok"
    except subprocess.CalledProcessError as e:
        return False, (e.stderr or e.stdout or "pandoc failed")

def ingest(
    repo_root: Path,
    source_file: Path,
    *,
    license_status: str,
    title: str | None = None,
    url: str | None = None,
    doi: str | None = None,
    urn: str | None = None,
    doc_id: str | None = None,
    ingested_by: str = "manual",
) -> dict[str, str]:
    """Ingest a document into vault/.

    Policy:
    - owned: raw is committed under vault/raw/<doc_id>/original.<ext>; transcript.md is created.
    - reference-only: raw is copied into vault/private/raw/<doc_id>/original.<ext> (gitignored) and
      vault/raw/<doc_id>/README.md is created as a pointer. No transcript is created.

    Returns paths and created doc_id.
    """
    source_file = source_file.expanduser().resolve()
    if not source_file.exists():
        raise FileNotFoundError(str(source_file))

    if license_status not in {"owned", "reference-only"}:
        raise ValueError("license_status must be 'owned' or 'reference-only'")

    if doc_id is None:
        doc_id = new_id("doc")
    if title is None:
        title = source_file.stem

    # Raw handling
    raw_public_dir = repo_root / "vault" / "raw" / doc_id
    raw_public_dir.mkdir(parents=True, exist_ok=True)

    raw_public_path: Path
    raw_private_path: Path | None = None

    if license_status == "owned":
        raw_public_path = raw_public_dir / ("original" + source_file.suffix.lower())
        shutil.copy2(source_file, raw_public_path)
    else:
        # Keep the raw file out of git; store a pointer in vault/raw.
        private_dir = repo_root / "vault" / "private" / "raw" / doc_id
        private_dir.mkdir(parents=True, exist_ok=True)
        raw_private_path = private_dir / ("original" + source_file.suffix.lower())
        shutil.copy2(source_file, raw_private_path)

        raw_public_path = raw_public_dir / "README.md"
        raw_public_path.write_text(
            "# Raw file pointer (reference-only)\n\n"
            "The raw file is stored under `vault/private/` (gitignored).\n\n"
            f"- Canonical URL: {url or '(unknown)'}\n"
            f"- Local private path: `{raw_private_path.relative_to(repo_root)}`\n",
            encoding="utf-8",
        )

    # Document directory
    doc_dir = (
        repo_root / "vault" / ("owned" if license_status == "owned" else "references") / doc_id
    )
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
        original_format=source_file.suffix.lower().lstrip("."),
        raw_path=str(raw_public_path.relative_to(repo_root)),
    )
    doc_md_path.write_text(rendered, encoding="utf-8")

    transcript_path = ""
    transcript_status = ""
    if license_status == "owned":
        transcript_md = doc_dir / "transcript.md"
        ok, msg = _run_pandoc_to_md(raw_public_path, transcript_md)
        transcript_status = msg
        if not ok:
            transcript_md.write_text(
                "# Transcript (placeholder)\n\nPandoc conversion was not run or failed.\n\n"
                + f"Source: `{raw_public_path.relative_to(repo_root)}`\n",
                encoding="utf-8",
            )
        transcript_path = str(transcript_md.relative_to(repo_root))

    return {
        "doc_id": doc_id,
        "doc_md": str(doc_md_path.relative_to(repo_root)),
        "raw": str(raw_public_path.relative_to(repo_root)),
        "transcript": transcript_path,
        "transcript_status": transcript_status,
        "raw_private": str(raw_private_path.relative_to(repo_root)) if raw_private_path else "",
    }
