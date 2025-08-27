from __future__ import annotations
import app.services.games_service as gs


def test_list_games_hydrates_then_reads(monkeypatch):
    # Arrange: first call sees empty cache -> fetch -> upsert -> return
    calls = {"fetch": 0, "upsert": 0, "get_by_date": []}

    def fake_get_games_by_date(date_str: str):
        # return empty first time, then return the "persisted" rows
        calls["get_by_date"].append(date_str)
        if len(calls["get_by_date"]) == 1:
            return []
        return [{"id": 1001, "date": date_str}]

    def fake_fetch_games_by_date(date_str: str):
        calls["fetch"] += 1
        return [{"id": 1001, "date": date_str}]

    def fake_upsert_games(rows):
        calls["upsert"] += 1
        assert rows and rows[0]["id"] == 1001

    monkeypatch.setattr(gs, "get_games_by_date", fake_get_games_by_date)
    monkeypatch.setattr(gs, "fetch_games_by_date", fake_fetch_games_by_date)
    monkeypatch.setattr(gs, "upsert_games", fake_upsert_games)

    # Act
    out = gs.list_games("2025-04-01")

    # Assert
    assert out == [{"id": 1001, "date": "2025-04-01"}]
    assert calls["fetch"] == 1
    assert calls["upsert"] == 1
    # get_by_date called twice (once pre-hydrate, once post-upsert)
    assert calls["get_by_date"] == ["2025-04-01", "2025-04-01"]


def test_get_game_details_cache_miss_hydrates(monkeypatch):
    calls = {"get": 0, "fetch": 0, "upsert": 0}

    def fake_get_game(game_id: int):
        calls["get"] += 1
        # miss on first get, then hit after upsert
        return {"id": game_id} if calls["upsert"] else None

    def fake_fetch_game_by_id(game_id: int):
        calls["fetch"] += 1
        return {"id": game_id, "home_team": {"id": 1}, "visitor_team": {"id": 2}}

    def fake_upsert_games(rows):
        calls["upsert"] += 1
        assert rows and rows[0]["id"]

    monkeypatch.setattr(gs, "get_game", fake_get_game)
    monkeypatch.setattr(gs, "fetch_game_by_id", fake_fetch_game_by_id)
    monkeypatch.setattr(gs, "upsert_games", fake_upsert_games)

    out = gs.get_game_details(777)
    assert out["id"] == 777
    assert calls["fetch"] == 1
    assert calls["upsert"] == 1
    # get() called twice: before and after upsert
    assert calls["get"] == 2


def test_list_games_cached(monkeypatch):
    def fake_get_games_by_date(date_str: str):
        return [{"id": 42, "date": date_str}]

    monkeypatch.setattr(gs, "get_games_by_date", fake_get_games_by_date)
    out = gs.list_games_cached("2025-04-01")
    assert out == [{"id": 42, "date": "2025-04-01"}]
