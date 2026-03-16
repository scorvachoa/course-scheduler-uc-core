"""Fetch sections (NRC) for a course."""
from __future__ import annotations

from typing import Dict, List

from .api_client import ApiClient


def get_sections(client: ApiClient, term: str, subject: str, course: str) -> List[Dict[str, str]]:
    data = client.get(
        "/academicoffercourse",
        params={"term": term, "subject": subject, "course": course},
    )
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]
