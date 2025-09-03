from flask import Flask
from .routes import bp as api_bp
from .repos.teams_repo import hydrate_teams_if_needed
from .config import BALLDONTLIE_API_KEY  # triggers validation at import time
from .exceptions import ConfigError

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)

    # Validate config (API key) at app startup
    try:
        _ = BALLDONTLIE_API_KEY  # Access forces load and validation
    except ConfigError as e:
        app.logger.critical(f"Startup failed due to config error: {e}")
        raise  # Let it crash and exit container

    # Warm team cache (idempotent)
    try:
        hydrate_teams_if_needed()
    except Exception as e:
        app.logger.warning(f"Could not hydrate teams cache at startup: {e}")

    return app
