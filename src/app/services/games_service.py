from __future__ import annotations

from ..ingest.balldontlie import (
    fetch_games_by_date,
    fetch_game_by_id,
)
from ..repos.games_repo import (
    upsert_games,
    get_games_by_date,
    get_game,
)


def list_games(date_str: str) -> list[dict]:
    """
    Return games for a date.
    - Check local cache; if empty, hydrate from API, store, and re-read.
    """
    rows = get_games_by_date(date_str)
    if rows:
        return rows

    api_rows = fetch_games_by_date(date_str)
    if not api_rows:
        return []

    upsert_games(api_rows)
    return get_games_by_date(date_str)


def get_game_details(game_id: int) -> dict | None:
    """Return a single game from cache, hydrating from API if necessary."""
    g = get_game(game_id)
    if g:
        return g

    api_g = fetch_game_by_id(game_id)
    if not api_g:
        return None

    upsert_games([api_g])
    return get_game(game_id)


def list_games_cached(date_str: str) -> list[dict]:
    """Return games from local cache only (no API calls)."""
    return get_games_by_date(date_str)
