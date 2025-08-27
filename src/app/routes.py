from __future__ import annotations

from flask import Blueprint, request, jsonify, Response
from .services import games_service
from .services import stats_service

bp = Blueprint("api", __name__)

@bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@bp.get("/games")
def games_for_date():
    """
    GET /games?date=YYYY-MM-DD[&refresh=true|false]
    - refresh=true  (default): hydrate from BDL, upsert, then return from DuckDB
    - refresh=false: return from local cache only
    """
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date is required (YYYY-MM-DD)"}), 400

    refresh = request.args.get("refresh", "true").lower() != "false"
    try:
        rows = (
            games_service.list_games(date)
            if refresh else games_service.list_games_cached(date)
        )
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/games/<int:game_id>")
def get_game(game_id: int):
    """
    GET /games/<game_id>
    Returns a single game's details (no player stats).
    """
    try:
        game = games_service.get_game_details(game_id)
        if not game:
            return jsonify({"error": f"game {game_id} not found"}), 404
        return jsonify(game), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.get("/stats/teams.csv")
def teams_csv():
    """
    GET /stats/teams.csv?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&team=<query>[&split=home_away]
    """
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    team = request.args.get("team")
    split = request.args.get("split") == "home_away"

    if not start or not end:
        return jsonify({"error": "start_date and end_date are required"}), 400

    def generate():
        for chunk in stats_service.iter_team_stats_csv(start, end, team, split):
            yield chunk

    filename = f"teams_{start}_to_{end}.csv"
    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )

