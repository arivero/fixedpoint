from __future__ import annotations

import datetime as dt
import tempfile
from pathlib import Path
from typing import Any

import requests

from .frontmatter import load_markdown, save_markdown
from .ingest import ingest

def _today() -> str:
    return dt.datetime.utcnow().date().isoformat()

def _is_request_file(p: Path) -> bool:
    name = p.name.lower()
    if not name.endswith('.md'):
        return False
    if name in {'readme.md', 'request-template.md'}:
        return False
    return True

def process_librarian_queue(repo_root: Path) -> list[dict[str, Any]]:
    qdir = repo_root / 'queue' / 'librarian'
    done_dir = qdir / 'done'
    done_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for req in sorted(qdir.glob('*.md')):
        if not _is_request_file(req):
            continue
        meta, body = load_markdown(req)
        if meta is None:
            continue
        if str(meta.get('type', '')).strip() not in {'librarian.ingest', 'ingest'}:
            continue
        status = str(meta.get('status', '')).strip().lower()
        if status in {'done', 'completed'}:
            continue

        license_status = str(meta.get('license_status', '') or meta.get('license', '') or 'reference-only').strip()
        title = str(meta.get('title', '')).strip() or None
        identifiers = meta.get('identifiers', {}) or {}
        doi = identifiers.get('doi') or None
        urn = identifiers.get('urn') or None

        source = meta.get('source', {}) or {}
        url = str(source.get('url', '')).strip() or None
        local_path = str(source.get('local_path', '')).strip() or None

        if not url and not local_path:
            results.append({'request': str(req), 'error': 'missing source.url or source.local_path'})
            continue

        # Get source file.
        tmp_path: Path | None = None
        if url:
            with tempfile.TemporaryDirectory() as td:
                tdpath = Path(td)
                # Infer extension (very naive)
                ext = '.bin'
                if '.' in url.split('/')[-1]:
                    ext = '.' + url.split('/')[-1].split('.')[-1].split('?')[0].lower()
                    if len(ext) > 8:
                        ext = '.bin'
                tmp_path = tdpath / ('download' + ext)
                r = requests.get(url, timeout=120)
                r.raise_for_status()
                tmp_path.write_bytes(r.content)
                info = ingest(
                    repo_root,
                    tmp_path,
                    license_status=license_status,
                    title=title,
                    url=url,
                    doi=doi,
                    urn=urn,
                    ingested_by='queue:librarian',
                )
        else:
            src = (repo_root / local_path) if not Path(local_path).is_absolute() else Path(local_path)
            info = ingest(
                repo_root,
                src,
                license_status=license_status,
                title=title,
                url=url,
                doi=doi,
                urn=urn,
                ingested_by='queue:librarian',
            )

        # Mark request as done and move.
        meta['status'] = 'done'
        meta['completed_at'] = _today()
        meta['doc_id'] = info.get('doc_id')
        save_markdown(req, meta, body)

        new_path = done_dir / req.name
        req.replace(new_path)
        results.append({'request': str(new_path.relative_to(repo_root)), **info})

    return results
