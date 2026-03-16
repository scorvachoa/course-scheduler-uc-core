"""Schedule model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Schedule:
    day: str
    start: str
    end: str
    modality: str

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Schedule":
        day = str(data.get("dia") or data.get("day") or "")
        start = str(data.get("inicio") or data.get("start") or "")
        end = str(data.get("fin") or data.get("end") or "")
        modality = str(data.get("modalidad") or data.get("modality") or "")
        return cls(day=day, start=start, end=end, modality=modality)
