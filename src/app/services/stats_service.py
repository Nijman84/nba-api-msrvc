from __future__ import annotations

import csv
from io import StringIO
from statistics import median
from typing import Iterator

from ..repos.teams_repo import resolve_team_ids, hydrate_teams_if_needed, _TEAMS_CACHE
from ..ingest.balldontlie import fetch_games_for_team_range


def _aggregate_team(team_id: int, start: str, end: str, split: bool) -> dict:
    games = fetch_games_for_team_range(team_id, start, end)

    scores, wins = [], []
    h_scores, h_wins, a_scores, a_wins = [], [], [], []

    for g in games:
        is_home = g["home_team"]["id"] == team_id
        my = g["home_team_score"] if is_home else g["visitor_team_score"]
        opp = g["visitor_team_score"] if is_home else g["home_team_score"]
        won = 1 if my > opp else 0

        scores.append(my)
        wins.append(won)

        if split:
            if is_home:
                h_scores.append(my); h_wins.append(won)
            else:
                a_scores.append(my); a_wins.append(won)

    def _med(xs): return float(median(xs)) if xs else None
    def _avg(xs): return float(sum(xs)) / len(xs) if xs else None

    out = {
        "median_score": _med(scores),
        "win_pct": _avg(wins),
        "games_played": len(scores),
    }
    if split:
        out.update({
            "home_median_score": _med(h_scores),
            "home_win_pct": _avg(h_wins),
            "home_games": len(h_scores),
            "away_median_score": _med(a_scores),
            "away_win_pct": _avg(a_wins),
            "away_games": len(a_scores),
        })
    return out


def iter_team_stats_csv(start: str, end: str, team_query: str | None, split: bool) -> Iterator[str]:
    """Stream a CSV of aggregate stats for matching teams."""
    hydrate_teams_if_needed()
    team_ids = resolve_team_ids(team_query)

    header = ["team_name", "team_id", "median_score", "win_pct", "games_played"]
    if split:
        header += [
            "home_median_score", "home_win_pct", "home_games",
            "away_median_score", "away_win_pct", "away_games",
        ]

    # Always emit header first
    sio = StringIO()
    csv.writer(sio).writerow(header)
    yield sio.getvalue()

    for tid in team_ids:
        t = _TEAMS_CACHE.get(tid, {})
        team_name = t.get("full_name") or t.get("name") or str(tid)

        agg = _aggregate_team(tid, start, end, split)
        row = [team_name, tid, agg["median_score"], agg["win_pct"], agg["games_played"]]
        if split:
            row += [
                agg["home_median_score"], agg["home_win_pct"], agg["home_games"],
                agg["away_median_score"], agg["away_win_pct"], agg["away_games"],
            ]

        sio = StringIO()
        csv.writer(sio).writerow(row)
        yield sio.getvalue()
