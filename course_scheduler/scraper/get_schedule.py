"""Fetch schedule for a section (NRC)."""
from __future__ import annotations

from typing import Dict, List

from .api_client import ApiClient


VIRTUAL_ATTR_CODES = {
    "AREM",
}

PRESENTIAL_ATTR_CODES = {
    "AFIS",
}


def derive_codliga(idseccion: str) -> str:
    return (idseccion or "")[:2]


def _is_virtual_room(room: str) -> bool:
    return any(keyword in room for keyword in ("meet", "zoom", "teams", "virtual"))


def _infer_modalidad(attr_code: str, classroom: str) -> str:
    code = (attr_code or "").strip().upper()
    room = (classroom or "").strip().lower()

    # Regla principal: si hay aula explícita, prima sobre attrCode.
    # Esto evita marcar como virtual cursos presenciales con attrCode inconsistente.
    if room:
        if _is_virtual_room(room):
            return "virtual"
        return "presencial"

    # Sin aula informada, usamos attrCode como señal secundaria.
    if code in VIRTUAL_ATTR_CODES:
        return "virtual"
    if code in PRESENTIAL_ATTR_CODES:
        return "presencial"

    # Fallback defensivo para no perder bloques horarios válidos.
    return "presencial"


def get_schedule(
    client: ApiClient,
    term: str,
    subject: str,
    course: str,
    nrcpadre: str,
    idseccion: str,
) -> List[Dict[str, str]]:
    codliga = derive_codliga(idseccion)
    data = client.get(
        "/scheduleoffercourse",
        params={
            "nrcpadre": nrcpadre,
            "term": term,
            "subject": subject,
            "course": course,
            "codliga": codliga,
        },
    )
    if not isinstance(data, list):
        return []

    horarios: List[Dict[str, str]] = []
    for day_block in data:
        if not isinstance(day_block, dict):
            continue
        dia = day_block.get("day")
        courses = day_block.get("courses")
        if not dia or not isinstance(courses, list) or len(courses) == 0:
            continue
        for item in courses:
            if not isinstance(item, dict):
                continue
            modalidad = _infer_modalidad(item.get("attrCode", ""), item.get("classroom", ""))
            horarios.append(
                {
                    "dia": dia,
                    "inicio": item.get("start", ""),
                    "fin": item.get("end", ""),
                    "modalidad": modalidad,
                }
            )
    return horarios
