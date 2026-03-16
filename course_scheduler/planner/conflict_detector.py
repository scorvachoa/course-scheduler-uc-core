"""Detect schedule conflicts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from course_scheduler.models.course import Course
from course_scheduler.models.schedule import Schedule
from course_scheduler.utils.time_utils import to_minutes


@dataclass
class Conflict:
    course_a: Course
    course_b: Course
    schedule_a: Schedule
    schedule_b: Schedule
    kind: str


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def _conflict_kind(mod_a: str, mod_b: str) -> str:
    a = mod_a.lower()
    b = mod_b.lower()
    if a == "presencial" and b == "presencial":
        return "conflicto fuerte"
    if "presencial" in (a, b):
        return "advertencia"
    return "advertencia leve"


def detect_conflicts(courses: List[Course]) -> List[Conflict]:
    conflicts: List[Conflict] = []
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            a_course = courses[i]
            b_course = courses[j]
            a_block = a_course.block_letter()
            b_block = b_course.block_letter()
            if a_block and b_block and a_block != b_block:
                continue

            for a_sched in a_course.schedules:
                for b_sched in b_course.schedules:
                    if not a_sched.day or not b_sched.day:
                        continue
                    if a_sched.day != b_sched.day:
                        continue
                    a_start = to_minutes(a_sched.start)
                    a_end = to_minutes(a_sched.end)
                    b_start = to_minutes(b_sched.start)
                    b_end = to_minutes(b_sched.end)
                    if _overlap(a_start, a_end, b_start, b_end):
                        conflicts.append(
                            Conflict(
                                course_a=a_course,
                                course_b=b_course,
                                schedule_a=a_sched,
                                schedule_b=b_sched,
                                kind=_conflict_kind(a_sched.modality, b_sched.modality),
                            )
                        )
    return conflicts


def has_conflict(courses: List[Course]) -> bool:
    return len(detect_conflicts(courses)) > 0
