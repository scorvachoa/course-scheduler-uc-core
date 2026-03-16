"""HTTP client for the academic API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import os
import time

import requests


@dataclass
class ApiClient:
    base_url: str
    timeout: int = 30
    retries: int = 3
    cookie: Optional[str] = None
    token: Optional[str] = None

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        headers: Dict[str, str] = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        cookie = (self.cookie or os.environ.get("API_COOKIE", "")).strip()
        if cookie:
            headers["Cookie"] = cookie
        token = (self.token or os.environ.get("API_TOKEN", "")).strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        last_error: Optional[Exception] = None
        for attempt in range(self.retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                if response.status_code >= 500:
                    raise requests.HTTPError(
                        f"{response.status_code} Server Error: {response.text}",
                        response=response,
                    )
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise last_error
