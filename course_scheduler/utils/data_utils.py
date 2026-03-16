"""Data helpers."""
from __future__ import annotations

from typing import Dict, List


def flatten_courses(data: List[Dict[str, object]]) -> List[Dict[str, object]]:
    flat: List[Dict[str, object]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        sections = item.get("secciones")
        if isinstance(sections, list):
            for sec in sections:
                if not isinstance(sec, dict):
                    continue
                merged = dict(item)
                merged.update(sec)
                merged.pop("secciones", None)
                flat.append(merged)
        else:
            flat.append(item)
    return flat
