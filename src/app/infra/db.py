# src/app/infra/db.py
from __future__ import annotations
import os
import duckdb
from threading import Lock

_DB_DIR = os.getenv("DB_DIR", "/app/data")
_DUCK_PATH = os.path.join(_DB_DIR, "nba.duckdb")

_con: duckdb.DuckDBPyConnection | None = None
_lock = Lock()

DDL_GAMES = """
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,         -- balldontlie g["id"]
    date DATE,                      -- balldontlie g["date"]
    season INTEGER,
    period INTEGER,
    status TEXT,
    postseason BOOLEAN,
    home_team_id INTEGER,
    home_team_name TEXT,
    home_team_score INTEGER,
    visitor_team_id INTEGER,
    visitor_team_name TEXT,
    visitor_team_score INTEGER
);
"""

DDL_TEAMS = """
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,        -- was team_id
    abbreviation TEXT,
    city TEXT,
    name TEXT,
    full_name TEXT,
    conference TEXT,
    division TEXT
);
"""


DDL_PLAYER_STATS = """
CREATE TABLE IF NOT EXISTS player_stats (
    player_id INTEGER,
    game_id INTEGER,
    team_id INTEGER,
    min TEXT,
    pts INTEGER,
    reb INTEGER,
    ast INTEGER,
    stl INTEGER,
    blk INTEGER,
    tov INTEGER,
    pf INTEGER,
    fgm INTEGER,
    fga INTEGER,
    fg3m INTEGER,
    ftm INTEGER,
    fta INTEGER,
    PRIMARY KEY (player_id, game_id)
);
"""

def _init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(DDL_GAMES)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_games_date ON games(date);")
    conn.execute(DDL_TEAMS)
    conn.execute(DDL_PLAYER_STATS)

def get_con() -> duckdb.DuckDBPyConnection:
    global _con
    if _con is not None:
        return _con
    with _lock:
        if _con is not None:
            return _con
        os.makedirs(_DB_DIR, exist_ok=True)
        _con = duckdb.connect(_DUCK_PATH)
        _init_schema(_con)
        return _con
