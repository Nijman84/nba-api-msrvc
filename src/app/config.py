import os
from .exceptions import ConfigError

def get_env_var(key: str) -> str:
    value = os.getenv(key)
    if not value or not value.strip():
        raise ConfigError(f"Missing required environment variable: {key}")
    return value

# Validate essential config at import time
BALLDONTLIE_API_KEY = get_env_var("BALLDONTLIE_API_KEY")
