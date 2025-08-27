# tests/test_routes.py
from __future__ import annotations
import json
import types

import app.services.games_service as gs  # we'll monkeypatch attributes on this module


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_games_requires_date_param(client):
    r = client.get("/games")
    assert r.status_code == 400
    assert "date is required" in r.get_json().get("error", "").lower()


def test_games_for_date_refresh_true(client, monkeypatch):
    called = {"list_games": 0}

    def fake_list_games(date_str: str):
        called["list_games"] += 1
        return [{"id": 123, "date": date_str, "home_team": {"id": 1}, "visitor_team": {"id": 2}}]

    # ensure cache-only path is not called when refresh=true
    def fake_list_games_cached(date_str: str):
        assert False, "list_games_cached should not be called when refresh=true"

    monkeypatch.setattr(gs, "list_games", fake_list_games)
    monkeypatch.setattr(gs, "list_games_cached", fake_list_games_cached)

    r = client.get("/games?date=2025-04-01&refresh=true")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list) and data[0]["id"] == 123
    assert called["list_games"] == 1


def test_games_for_date_refresh_false(client, monkeypatch):
    called = {"list_games_cached": 0}

    def fake_list_games_cached(date_str: str):
        called["list_games_cached"] += 1
        return [{"id": 456, "date": date_str}]

    # ensure hydrate path is not called when refresh=false
    def fake_list_games(date_str: str):
        assert False, "list_games should not be called when refresh=false"

    monkeypatch.setattr(gs, "list_games_cached", fake_list_games_cached)
    monkeypatch.setattr(gs, "list_games", fake_list_games)

    r = client.get("/games?date=2025-04-01&refresh=false")
    assert r.status_code == 200
    data = r.get_json()
    assert data[0]["id"] == 456
    assert called["list_games_cached"] == 1


def test_get_game_found(client, monkeypatch):
    def fake_get_game_details(game_id: int):
        return {"id": game_id, "home_team": {"id": 1}, "visitor_team": {"id": 2}}

    monkeypatch.setattr(gs, "get_game_details", fake_get_game_details)

    r = client.get("/games/9999")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == 9999


def test_get_game_not_found(client, monkeypatch):
    def fake_get_game_details(game_id: int):
        return None

    monkeypatch.setattr(gs, "get_game_details", fake_get_game_details)

    r = client.get("/games/424242")
    assert r.status_code == 404
    assert "not found" in r.get_json()["error"].lower()
