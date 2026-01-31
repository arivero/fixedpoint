from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from .ids import new_id
from .llm import LLMClient
from .frontmatter import save_markdown, load_markdown

_JSON_ARRAY_RE = re.compile(r"(\[\s*\{.*?\}\s*\])", re.DOTALL)

def _today() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()

def _extract_json_array(text: str) -> list[dict[str, Any]]:
    # Prefer a clean JSON array, but fall back to regex extraction.
    t = text.strip()
    try:
        data = json.loads(t)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
    except Exception:
        pass
    m = _JSON_ARRAY_RE.search(text)
    if not m:
        raise ValueError("LLM did not return a JSON array")
    data = json.loads(m.group(1))
    if not isinstance(data, list):
        raise ValueError("Extracted JSON is not a list")
    return [x for x in data if isinstance(x, dict)]

def mine_ideas(repo_root: Path, *, doc_id: str, max_ideas: int = 12) -> list[Path]:
    transcript = repo_root / "vault" / "owned" / doc_id / "transcript.md"
    if not transcript.exists():
        raise FileNotFoundError(f"Owned transcript not found: {transcript}")

    text = transcript.read_text(encoding="utf-8")
    # Basic truncation safeguard (avoid gigantic prompts by default).
    max_chars = 60_000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[TRUNCATED]\n"

    system = """You are an expert research assistant extracting ATOMIC ideas from a technical note.
Return ONLY a JSON array (no markdown, no prose) where each element has:
- title: short, specific
- statement: a single atomic claim/definition/theorem/construction (no multi-idea bundles)
- tags: list of 0-6 short tags
- locator: best-effort locator string within the transcript (e.g. section name or heading)
- quote: OPTIONAL very short quote (<= 240 chars) if it helps; omit or empty if unnecessary

Rules:
- Prefer precise technical language.
- Do not invent facts not supported by the text.
- Keep ideas reusable and minimal.
"""

    user = f"""Document id: {doc_id}
Max ideas: {max_ideas}

Transcript:
{text}
"""

    client = LLMClient.from_env()
    resp = client.complete(system=system, user=user)
    items = _extract_json_array(resp)[:max_ideas]

    created_paths: list[Path] = []
    for it in items:
        iid = new_id("idea")
        title = str(it.get("title") or "(untitled idea)").strip()
        statement = str(it.get("statement") or "").strip()
        tags = it.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        tags = [str(t).strip() for t in tags if str(t).strip()]
        locator = str(it.get("locator") or "transcript.md").strip()
        quote = str(it.get("quote") or "").strip()
        if len(quote) > 240:
            quote = quote[:237] + "..."

        meta = {
            "id": iid,
            "title": title,
            "created": _today(),
            "updated": _today(),
            "status": "seed",
            "tags": tags,
            "sources": [
                {
                    "doc": doc_id,
                    "locator": locator,
                    "quote": quote,
                }
            ],
            "projects": [],
        }
        body = "Atomic idea statement:\n\n" + statement + "\n\n" + "Notes:\n"
        out_path = repo_root / "ideas" / f"{iid}.md"
        save_markdown(out_path, meta, body)
        created_paths.append(out_path)

    return created_paths
