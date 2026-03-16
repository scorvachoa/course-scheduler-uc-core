"""Fetch and filter offered courses."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .api_client import ApiClient


def _extract_list(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("data", "items", "results", "courses", "value"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _extract_offer_list(data: Any) -> List[Dict[str, Any]]:
    # Current API returns a list of term blocks with `offertAcademic` list inside.
    blocks = _extract_list(data)
    for block in blocks:
        offer = block.get("offertAcademic")
        if isinstance(offer, list):
            return [item for item in offer if isinstance(item, dict)]
    return []


def get_courses(client: ApiClient) -> List[Dict[str, Any]]:
    data = client.get("/coursesoffered")

    if os.environ.get("DUMP_RAW", ""):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        output_path = os.path.join(base_dir, "data", "coursesoffered_raw.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    courses = _extract_offer_list(data)
    return [
        item
        for item in courses
        if isinstance(item, dict) and item.get("recommended") == "Y"
    ]
