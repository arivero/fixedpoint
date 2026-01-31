from __future__ import annotations

import datetime as _dt
import secrets as _secrets
from dataclasses import dataclass

ALLOWED_KINDS = {"doc", "idea", "proj", "nb", "bb"}

def new_id(kind: str, now: _dt.datetime | None = None) -> str:
    """Generate a stable, filesystem-safe ID.

    Format: <kind>_YYYYMMDD_<8hex>
    Example: doc_20260131_a1b2c3d4
    """
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"Unknown kind {kind!r}. Allowed: {sorted(ALLOWED_KINDS)}")
    if now is None:
        now = _dt.datetime.utcnow()
    ymd = now.strftime("%Y%m%d")
    suffix = _secrets.token_hex(4)  # 8 hex chars
    return f"{kind}_{ymd}_{suffix}"
