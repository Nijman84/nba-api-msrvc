from ..infra.db import get_con

def _init_schema():
    con = get_con()
    con.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,     -- balldontlie g["id"]
        date DATE,                  -- balldontlie g["date"]
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
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_games_date ON games(date);")



def upsert_games(games: list[dict]):
    con = get_con()
    con.executemany("""
        INSERT OR REPLACE INTO games (
            id, date, season, period, status, postseason,
            home_team_id, home_team_name, home_team_score,
            visitor_team_id, visitor_team_name, visitor_team_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            int(g["id"]),
            g.get("date"),
            g.get("season"),
            g.get("period"),
            g.get("status"),
            g.get("postseason", False),
            g["home_team"]["id"],
            g["home_team"]["full_name"],
            g.get("home_team_score"),
            g["visitor_team"]["id"],
            g["visitor_team"]["full_name"],
            g.get("visitor_team_score"),
        )
        for g in games
    ])


def get_games_by_date(date_str: str) -> list[dict]:
    con = get_con()
    cur = con.execute("""
        SELECT
            id AS game_id,
            date,
            season,
            period,
            status,
            postseason,
            home_team_id,
            home_team_name,
            home_team_score,
            visitor_team_id,
            visitor_team_name,
            visitor_team_score
        FROM games
        WHERE date = ?
        ORDER BY id ASC
    """, [date_str])
    rows = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
    return rows


def get_game(game_id: int) -> dict | None:
    con = get_con()
    cur = con.execute("""
        SELECT
            id AS game_id,
            date,
            season,
            period,
            status,
            postseason,
            home_team_id,
            home_team_name,
            home_team_score,
            visitor_team_id,
            visitor_team_name,
            visitor_team_score
        FROM games
        WHERE id = ?
    """, [game_id])
    row = cur.fetchone()
    if not row:
        return None
    return dict(zip([c[0] for c in cur.description], row))
