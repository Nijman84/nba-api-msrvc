from __future__ import annotations
from datetime import date, timedelta
from ..infra.http_client import get

def fetch_games_for_team_range(team_id: int, start_date: str, end_date: str) -> list[dict]:
    """
    Fetch all games for a team between [start_date, end_date] inclusive,
    using BDL's range params (single paginated call).
    """
    params = {
        "team_ids[]": team_id,
        "start_date": start_date,
        "end_date": end_date,
        "per_page": 100,
        "page": 1,
    }
    out: list[dict] = []
    while True:
        payload = get("/games", params=params)
        data = payload.get("data", []) if isinstance(payload, dict) else []
        out.extend(data)
        meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
        total_pages = int(meta.get("total_pages", 1) or 1)
        if params["page"] >= total_pages:
            break
        params["page"] += 1
    return out


def fetch_all_teams() -> list[dict]:
    # BDL teams is small and unpaginated
    payload = get("/teams")
    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    return data or []


def fetch_games_for_team_on_date(team_id: int, yyyy_mm_dd: str) -> list[dict]:
    # Use BDL's date filter (no TZ work), plus team filter
    params = {"dates[]": yyyy_mm_dd, "team_ids[]": team_id, "per_page": 100, "page": 1}
    out = []
    while True:
        payload = get("/games", params=params)
        data = payload.get("data", []) if isinstance(payload, dict) else []
        out.extend(data)
        meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
        if not meta or params["page"] >= meta.get("total_pages", 1):
            break
        params["page"] += 1
    return out


def iter_dates_inclusive(start: str, end: str):
    d0 = date.fromisoformat(start)
    d1 = date.fromisoformat(end)
    step = timedelta(days=1)
    d = d0
    while d <= d1:
        yield d.isoformat()
        d += step


def fetch_games_by_date(date_str: str) -> list[dict]:
    data, page = [], 1
    while True:
        payload = get("/games", params={"dates[]": date_str, "per_page": 100, "page": page})
        data.extend(payload.get("data", []))
        meta = payload.get("meta", {}) or {}
        if page >= meta.get("total_pages", 1):
            break
        page += 1
    return data


def fetch_game_by_id(game_id: int) -> dict | None:
    """Return a single BDL game object or None if missing/invalid."""
    payload = get(f"/games/{game_id}")

    # Some gateways/clients wrap responses under "data"
    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
        payload = payload["data"]

    # Validate minimal shape needed by upsert_games
    if not isinstance(payload, dict):
        return None
    required = ["id", "home_team", "visitor_team"]
    if any(k not in payload for k in required):
        return None
    return payload


def fetch_player_stats_for_game(game_id: int) -> list[dict]:
    """/stats supports filtering with game_ids[] and paginates."""
    data, page = [], 1
    while True:
        payload = get("/stats", params={"game_ids[]": game_id, "per_page": 100, "page": page})
        data.extend(payload.get("data", []))
        meta = payload.get("meta", {}) or {}
        if page >= meta.get("total_pages", 1):
            break
        page += 1
    return data
