from __future__ import annotations
from typing import List
from ..infra.db import get_con
from ..ingest.balldontlie import fetch_all_teams

# Simple in-process cache
_TEAMS_CACHE: dict[int, dict] = {}
_INDEX: dict[str, set[int]] = {}  # inverted index for quick lookup


def _index_team(t: dict):
    tid = int(t["id"])
    keys = set()

    def add(x: str | None):
        if not x:
            return
        s = x.strip()
        if not s:
            return
        keys.add(s.lower())

    add(str(tid))
    add(t.get("abbreviation"))
    add(t.get("name"))       # nickname (e.g., "Celtics")
    add(t.get("city"))       # city (e.g., "Boston")
    add(t.get("full_name"))  # "Boston Celtics"

    for k in keys:
        _INDEX.setdefault(k, set()).add(tid)


def hydrate_teams_if_needed() -> None:
    """
    Ensure teams table is populated and in-process cache is warm.
    Idempotent. Runs fast.
    """
    if _TEAMS_CACHE:  # already cached
        return

    con = get_con()
    # If table has rows, read them into cache. Else fetch from API and persist.
    df = con.execute("SELECT * FROM teams").df()
    rows = df.to_dict(orient="records") if not df.empty else []

    if not rows:
        api = fetch_all_teams()
        if api:
            # upsert to DB
            con.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_teams_id ON teams(id);")
            con.executemany("""
                INSERT INTO teams (id, abbreviation, city, conference, division, full_name, name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                  abbreviation=excluded.abbreviation,
                  city=excluded.city,
                  conference=excluded.conference,
                  division=excluded.division,
                  full_name=excluded.full_name,
                  name=excluded.name;
            """, [
                (int(t["id"]), t.get("abbreviation"), t.get("city"), t.get("conference"),
                 t.get("division"), t.get("full_name"), t.get("name")) for t in api
            ])
            rows = api

    # Build in-memory cache + index
    for t in rows:
        tid = int(t["id"])
        _TEAMS_CACHE[tid] = t
        _index_team(t)


def resolve_team_ids(q: str | None) -> List[int]:
    """
    Accepts id, abbreviation, name, full_name, city (partials OK).
    Returns a list of matching IDs (usually 1).
    """
    hydrate_teams_if_needed()
    if not q:
        return []

    ql = q.strip().lower()
    # direct ID?
    try:
        tid = int(q)
        return [tid] if tid in _TEAMS_CACHE else []
    except ValueError:
        pass

    # exact index hit first
    if ql in _INDEX:
        return sorted(_INDEX[ql])

    # partials across keys
    hits: set[int] = set()
    for key in list(_INDEX.keys()):
        if ql in key:
            hits.update(_INDEX[key])
            if len(hits) >= 8:
                break
    return sorted(hits)
