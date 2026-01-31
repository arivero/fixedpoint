from __future__ import annotations

import re
from typing import Iterable, Sequence

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")

def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()

def md_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    h = "| " + " | ".join(headers) + " |\n"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |\n"
    body = "".join("| " + " | ".join(md_escape(str(c)) for c in r) + " |\n" for r in rows)
    return h + sep + body
