"""Data models for course offers loaded from JSON."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .schedule import Schedule


@dataclass
class Course:
    name: str
    subject: str
    course: str
    credits: int
    nrc: str
    teacher: str
    block: str
    schedules: List[Schedule]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Course":
        subject = str(data.get("subject") or "")
        course = str(data.get("course") or "")
        name = str(
            data.get("curso")
            or data.get("name")
            or data.get("nameCourse")
            or data.get("name_course")
            or ""
        )
        if not name:
            name = f"{subject}-{course}".strip("-")
        credits = int(data.get("credits") or 0)
        nrc = str(data.get("nrc") or "")
        teacher = str(data.get("teacher") or "")
        block = str(data.get("seccion") or data.get("block") or "")

        raw_schedules = data.get("horarios") or data.get("schedules") or []
        schedules: List[Schedule] = []
        if isinstance(raw_schedules, list):
            for item in raw_schedules:
                if isinstance(item, dict):
                    schedules.append(Schedule.from_dict(item))

        return cls(
            name=name,
            subject=subject,
            course=course,
            credits=credits,
            nrc=nrc,
            teacher=teacher,
            block=block,
            schedules=schedules,
        )

    def course_key(self) -> str:
        return f"{self.subject}:{self.course}"

    def block_letter(self) -> str:
        block = (self.block or "").strip()
        if block.endswith("A"):
            return "A"
        if block.endswith("B"):
            return "B"
        return ""
