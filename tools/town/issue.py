from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict

_HEADING_RE = re.compile(r"^###\s+(.*)\s*$")

def parse_issue_template(body: str) -> dict[str, str]:
    """Parse a GitHub issue form rendered as Markdown headings.

    GitHub Issue Forms (YAML) are rendered into Markdown blocks like:

        ### Field name
        value

    This parser turns that into {"Field name": "value"}.
    """
    lines = body.splitlines()
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            current = m.group(1).strip()
            fields.setdefault(current, [])
            continue
        if current is not None:
            fields[current].append(line)

    out: dict[str, str] = {}
    for k, vlines in fields.items():
        # Trim surrounding blank lines
        while vlines and vlines[0].strip() == "":
            vlines.pop(0)
        while vlines and vlines[-1].strip() == "":
            vlines.pop()
        out[k] = "\n".join(vlines).strip()
    return out

def first_nonempty(*values: str | None) -> str:
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return ""
