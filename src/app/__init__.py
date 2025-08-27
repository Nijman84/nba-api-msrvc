from flask import Flask
from .routes import bp as api_bp
from .repos.teams_repo import hydrate_teams_if_needed

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    # warm team cache (idempotent)
    try:
        hydrate_teams_if_needed()
    except Exception as e:
        app.logger.warning(f"could not hydrate teams cache at startup: {e}")
    return app


from .routes import bp as api_bp
from .repos.teams_repo import hydrate_teams_if_needed

