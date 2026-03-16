"""Time parsing helpers."""
from __future__ import annotations


def to_minutes(value: str, *, default: int = 0) -> int:
    parts = value.split(":")
    if len(parts) != 2:
        return default
    try:
        hours, minutes = parts
        return int(hours) * 60 + int(minutes)
    except ValueError:
        return default


def format_minutes(value: int) -> str:
    hours = value // 60
    minutes = value % 60
    return f"{hours:02d}:{minutes:02d}"
