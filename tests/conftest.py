# tests/conftest.py
from __future__ import annotations
import os
import pytest
from flask import Flask

# Ensure required env vars exist BEFORE importing app.routes
os.environ.setdefault("BALLDONTLIE_API_KEY", "test-key")
# add any others your app reads at import time, e.g.:
# os.environ.setdefault("DUCKDB_PATH", ":memory:")
# os.environ.setdefault("APP_ENV", "test")

from app.routes import bp as api_bp  # safe now

@pytest.fixture(scope="session")
def app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(api_bp)
    return flask_app

@pytest.fixture()
def client(app):
    return app.test_client()
