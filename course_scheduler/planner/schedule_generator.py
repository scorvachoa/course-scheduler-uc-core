"""Generate conflict-free schedules."""
from __future__ import annotations

from typing import Dict, List

from course_scheduler.models.course import Course
from course_scheduler.planner.conflict_detector import has_conflict


def _course_key(item: Course) -> str:
    return item.course_key() or item.name


def group_by_course(records: List[Course]) -> Dict[str, List[Course]]:
    grouped: Dict[str, List[Course]] = {}
    for item in records:
        key = _course_key(item)
        grouped.setdefault(key, []).append(item)
    return grouped


def generate_schedules(selected_courses: List[Course], limit: int = 20) -> List[List[Course]]:
    grouped = list(group_by_course(selected_courses).values())
    results: List[List[Course]] = []

    def backtrack(idx: int, chosen: List[Course]) -> None:
        if len(results) >= limit:
            return
        if idx >= len(grouped):
            results.append(list(chosen))
            return

        for section in grouped[idx]:
            candidate = chosen + [section]
            if has_conflict(candidate):
                continue
            backtrack(idx + 1, candidate)

    backtrack(0, [])
    return results
