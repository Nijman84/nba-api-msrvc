# src/app/infra/http_client.py
from __future__ import annotations
import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

BALLDONTLIE_BASE = os.getenv("BALLDONTLIE_BASE", "https://api.balldontlie.io/v1")
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY", "")

def _headers():
    h = {}
    if BALLDONTLIE_API_KEY:
        # BallDontLie uses a simple Authorization header for API keys
        h["Authorization"] = BALLDONTLIE_API_KEY
    return h

def _should_retry(exc: Exception) -> bool:
    # Retry only on connection issues / 5xx – not on 4xx like your 403
    if isinstance(exc, httpx.HTTPStatusError):
        return 500 <= exc.response.status_code < 600
    return isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout))

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception(_should_retry),
    reraise=True,
)
def get(path: str, params: dict | None = None) -> dict:
    url = f"{BALLDONTLIE_BASE.rstrip('/')}/{path.lstrip('/')}"
    with httpx.Client(timeout=10.0) as client:
        r = client.get(url, headers=_headers(), params=params or {})
        r.raise_for_status()
        return r.json()
