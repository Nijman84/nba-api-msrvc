# tests/conftest.py
from __future__ import annotations
import os
import pytest
from flask import Flask

# Import the blueprint directly (this imports games_service, but we'll monkeypatch its functions in tests)
from app.routes import bp as api_bp


@pytest.fixture(scope="session")
def app():
    # Keep the app tiny: just register your API blueprint
    flask_app = Flask(__name__)
    flask_app.register_blueprint(api_bp)
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()
