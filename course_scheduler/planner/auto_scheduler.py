"""Automatic schedule generator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from course_scheduler.models.course import Course
from course_scheduler.utils.time_utils import to_minutes


def _day_key(value: str) -> str:
    text = (value or "").strip().lower()
    if not text:
        return ""
    # Normalize accents to plain ascii
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
    }
    normalized = "".join(replacements.get(ch, ch) for ch in text)
    normalized = "".join(ch for ch in normalized if ch.isalpha())
    mapping = {
        "lunes": "lunes",
        "martes": "martes",
        "miercoles": "miercoles",
        "jueves": "jueves",
        "viernes": "viernes",
        "sabado": "sabado",
        "domingo": "domingo",
        "l": "lunes",
        "m": "martes",
        "x": "miercoles",
        "j": "jueves",
        "v": "viernes",
        "s": "sabado",
        "d": "domingo",
    }
    return mapping.get(normalized, normalized)


def _allowed_days_set(days: Iterable[str]) -> Set[str]:
    cleaned = {_day_key(day) for day in days if day}
    return {d for d in cleaned if d}


def _section_in_allowed_days(section: Course, allowed_days: Set[str]) -> bool:
    if not allowed_days:
        return True
    for sched in section.schedules:
        day = _day_key(sched.day)
        if not day or day not in allowed_days:
            return False
    return True


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def _has_conflict(candidate: Course, selected: Sequence[Course]) -> bool:
    for a in candidate.schedules:
        day_a = _day_key(a.day)
        if not day_a:
            continue
        a_start = to_minutes(a.start)
        a_end = to_minutes(a.end)
        if a_end <= a_start:
            continue
        for course in selected:
            for b in course.schedules:
                day_b = _day_key(b.day)
                if day_a != day_b:
                    continue
                b_start = to_minutes(b.start)
                b_end = to_minutes(b.end)
                if b_end <= b_start:
                    continue
                if _overlap(a_start, a_end, b_start, b_end):
                    return True
    return False


@dataclass
class _CourseGroup:
    key: str
    credits: int
    sections: List[Course]


def _group_courses(courses: Iterable[Course], selected_keys: Set[str], block: str) -> List[_CourseGroup]:
    grouped: Dict[str, _CourseGroup] = {}
    for course in courses:
        key = course.course_key() or course.name
        if selected_keys and key not in selected_keys:
            continue
        if course.block_letter() != block:
            continue
        group = grouped.get(key)
        if group is None:
            grouped[key] = _CourseGroup(key=key, credits=course.credits, sections=[course])
        else:
            group.sections.append(course)
    return list(grouped.values())


def _solve_block(
    courses: Iterable[Course],
    *,
    selected_keys: Set[str],
    allowed_days: Set[str],
    target_credits: int,
    allow_less: bool,
    block: str,
) -> Tuple[List[Course], int]:
    groups = _group_courses(courses, selected_keys, block)
    groups.sort(key=lambda g: g.credits, reverse=True)

    remaining_credits = [0] * (len(groups) + 1)
    for i in range(len(groups) - 1, -1, -1):
        remaining_credits[i] = remaining_credits[i + 1] + max(0, groups[i].credits)

    best: List[Course] = []
    best_credits = -1

    def dfs(idx: int, chosen: List[Course], credits: int) -> None:
        nonlocal best, best_credits
        if credits > target_credits:
            return
        if credits > best_credits:
            best_credits = credits
            best = list(chosen)
            if best_credits == target_credits:
                return
        if idx >= len(groups):
            return
        if credits + remaining_credits[idx] < best_credits:
            return

        group = groups[idx]
        dfs(idx + 1, chosen, credits)

        for section in group.sections:
            if not _section_in_allowed_days(section, allowed_days):
                continue
            if _has_conflict(section, chosen):
                continue
            chosen.append(section)
            dfs(idx + 1, chosen, credits + group.credits)
            chosen.pop()

    dfs(0, [], 0)

    if not allow_less and best_credits != target_credits:
        return [], 0
    return best, max(0, best_credits)


def generate_auto_schedule(
    courses: Iterable[Course],
    *,
    selected_course_keys: Iterable[str],
    allowed_days: Iterable[str],
    target_credits: int = 12,
    allow_less: bool = True,
) -> Dict[str, Dict[str, object]]:
    """Generate an automatic schedule for blocks A and B."""
    selected_keys = set(selected_course_keys)
    allowed_days_set = _allowed_days_set(allowed_days)

    selected_a, credits_a = _solve_block(
        courses,
        selected_keys=selected_keys,
        allowed_days=allowed_days_set,
        target_credits=target_credits,
        allow_less=allow_less,
        block="A",
    )
    selected_b, credits_b = _solve_block(
        courses,
        selected_keys=selected_keys,
        allowed_days=allowed_days_set,
        target_credits=target_credits,
        allow_less=allow_less,
        block="B",
    )

    return {
        "bloque_a": {"courses": selected_a, "credits": credits_a},
        "bloque_b": {"courses": selected_b, "credits": credits_b},
    }
