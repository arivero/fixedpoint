from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

import yaml


FRONTMATTER_DELIM = "---"


class FrontmatterError(Exception):
    pass


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Return (meta, body). If no YAML frontmatter, meta is None.

    Frontmatter must be at file start, delimited by lines containing exactly '---'.
    """
    if not text.startswith(FRONTMATTER_DELIM + "\n") and text.strip() != FRONTMATTER_DELIM:
        return None, text

    lines = text.splitlines(keepends=False)
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None, text

    # Find closing delimiter.
    try:
        end_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == FRONTMATTER_DELIM)
    except StopIteration:
        raise FrontmatterError("Frontmatter starts with --- but no closing --- found")

    fm_lines = lines[1:end_idx]
    body_lines = lines[end_idx + 1 :]

    fm_text = "\n".join(fm_lines).strip()
    body_text = "\n".join(body_lines)
    if body_text and not body_text.endswith("\n"):
        body_text += "\n"

    meta: dict[str, Any] = {}
    if fm_text:
        try:
            meta = yaml.safe_load(fm_text) or {}
        except Exception as e:
            raise FrontmatterError(f"Invalid YAML frontmatter: {e}") from e
        if not isinstance(meta, dict):
            raise FrontmatterError("YAML frontmatter must parse to a mapping (dict)")
    return meta, body_text


def load_markdown(path: Path) -> tuple[dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    return split_frontmatter(text)


def dump_markdown(meta: dict[str, Any] | None, body: str) -> str:
    if meta is None:
        return body
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    out = FRONTMATTER_DELIM + "\n" + fm + "\n" + FRONTMATTER_DELIM + "\n\n" + body.lstrip("\n")
    if not out.endswith("\n"):
        out += "\n"
    return out


def save_markdown(path: Path, meta: dict[str, Any] | None, body: str) -> None:
    path.write_text(dump_markdown(meta, body), encoding="utf-8")
