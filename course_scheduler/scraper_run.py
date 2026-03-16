"""Scrape courses and write data/cursos.json."""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from tqdm import tqdm

from course_scheduler.scraper.api_client import ApiClient
from course_scheduler.scraper.get_courses import get_courses
from course_scheduler.scraper.get_sections import get_sections
from course_scheduler.scraper.get_schedule import get_schedule


BASE_URL = "https://estudiantes.continental.edu.pe/api/academic"
DEFAULT_TERM = "202610"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "cursos.json")


def _merge_schedules(*schedule_groups: List[Dict[str, str]]) -> List[Dict[str, str]]:
    merged: List[Dict[str, str]] = []
    seen = set()
    for group in schedule_groups:
        for item in group:
            key = (
                str(item.get("dia") or ""),
                str(item.get("inicio") or ""),
                str(item.get("fin") or ""),
                str(item.get("modalidad") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged




def _nearby_nrc_values(base_values: List[str]) -> List[str]:
    neighbors: List[str] = []
    seen = set()
    for value in base_values:
        if not value.isdigit():
            continue
        width = len(value)
        number = int(value)
        candidate = number - 1
        if candidate <= 0:
            continue
        normalized = str(candidate).zfill(width)
        if normalized in seen:
            continue
        seen.add(normalized)
        neighbors.append(normalized)
    return neighbors

def _candidate_nrc_values(section: Dict[str, object], nrc: str, nrcpadre: str) -> List[str]:
    raw_values = [
        nrcpadre,
        nrc,
        section.get("nrcpadre"),
        section.get("nrcPadre"),
        section.get("nrc_parent"),
        section.get("parentNrc"),
        section.get("nrc"),
        section.get("nrcchild"),
        section.get("nrcChild"),
    ]
    candidates: List[str] = []
    seen = set()
    for value in raw_values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(normalized)

    # academicoffercourse suele traer NRC virtual; el presencial relacionado
    # se consulta como NRC - 1 según la regla indicada.
    for neighbor in _nearby_nrc_values(candidates):
        if neighbor in seen:
            continue
        seen.add(neighbor)
        candidates.append(neighbor)

    return candidates


def _fetch_section_schedules(
    client: ApiClient,
    *,
    term: str,
    subject: str,
    course_code: str,
    nrc: str,
    nrcpadre: str,
    idseccion: str,
    section: Dict[str, object],
) -> List[Dict[str, str]]:
    schedule_groups: List[List[Dict[str, str]]] = []
    for query_nrc in _candidate_nrc_values(section, nrc, nrcpadre):
        schedule_groups.append(
            get_schedule(
                client,
                term=term,
                subject=subject,
                course=course_code,
                nrcpadre=query_nrc,
                idseccion=idseccion,
            )
        )

    return _merge_schedules(*schedule_groups)


def build_records(term: str, *, cookie: Optional[str] = None, token: Optional[str] = None) -> Dict[str, object]:
    client = ApiClient(base_url=BASE_URL, cookie=cookie, token=token)

    courses = get_courses(client)
    records: List[Dict[str, object]] = []
    sections_found = 0
    horarios_processed = 0

    for course in tqdm(courses, desc="Cursos", unit="curso"):
        subject = str(course.get("subject") or "")
        course_code = str(course.get("course") or "")
        sections = get_sections(client, term, subject, course_code)
        sections_found += len(sections)

        secciones: List[Dict[str, object]] = []
        for section in sections:
            nrc = str(section.get("nrc") or "")
            nrcpadre = str(section.get("nrcpadre") or "")
            idseccion = str(section.get("idseccion") or "")

            horarios = _fetch_section_schedules(
                client,
                term=term,
                subject=subject,
                course_code=course_code,
                nrc=nrc,
                nrcpadre=nrcpadre,
                idseccion=idseccion,
                section=section,
            )
            if not horarios:
                continue

            horarios_processed += len(horarios)
            secciones.append(
                {
                    "nrc": nrc,
                    "teacher": section.get("teacher", ""),
                    "seccion": idseccion,
                    "horarios": horarios,
                }
            )

        if not secciones:
            continue

        name = course.get("name") or course.get("nameCourse") or ""
        records.append(
            {
                "curso": name,
                "subject": subject,
                "course": course_code,
                "credits": int(course.get("credits", 0) or 0),
                "secciones": secciones,
            }
        )

    return {
        "courses_found": len(courses),
        "sections_found": sections_found,
        "horarios_processed": horarios_processed,
        "records": records,
    }


def main() -> None:
    term = os.environ.get("TERM_CODE", DEFAULT_TERM)
    result = build_records(term)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result["records"], f, ensure_ascii=False, indent=2)

    print(f"Cursos encontrados: {result['courses_found']}")
    print(f"Secciones encontradas: {result['sections_found']}")
    print(f"Horarios procesados: {result['horarios_processed']}")
    print(f"Archivo generado: {os.path.basename(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()
