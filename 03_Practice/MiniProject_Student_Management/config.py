"""
Configuration Module — Day 019 Exercise 2: Pydantic Settings.

This module defines a single `Settings` class that reads all application
configuration from environment variables (and the .env file via python-dotenv).

Why Pydantic Settings?
----------------------
1. Automatic .env loading  : python-dotenv reads the .env file; Pydantic maps
                             each key to a typed Python attribute automatically.
2. Type safety             : Every setting is declared with a Python type. If
                             you put LOG_LEVEL=OOPS in .env, you get a clear
                             validation error at startup instead of a silent bug.
3. IDE auto-complete       : settings.jwt_secret_key is a real attribute — your
                             editor knows its type without any special magic.
4. Single source of truth  : One import (from config import settings) gives any
                             module access to all configuration — no scattered
                             os.getenv() calls across the codebase.

Usage:
    from config import settings

    secret = settings.jwt_secret_key
    db_host = settings.db_host
"""

import logging
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# ──────────────────────────────────────────────────────────────────────────────
# Day 019 Exercise 2: Settings class — reads .env automatically via BaseSettings
# ──────────────────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    """
    Application-wide configuration loaded from environment variables / .env file.

    Pydantic Settings reads each field name (case-insensitive) from:
      1. The process environment (os.environ)  ← highest priority
      2. The .env file in the project root     ← fallback for local dev
      3. The default values declared below     ← last resort

    Field names are lowercase by convention; env var names are uppercase.
    Example: `db_host` reads from `DB_HOST` in the environment.
    """

    # ── Application ─────────────────────────────────────────────────────────
    # Day 019 Exercise 3: App name and version read from config (not hardcoded)
    app_name: str
    app_version: str
    debug: bool = False

    # ── Security (JWT) ───────────────────────────────────────────────────────
    # Day 019 Exercise 4: JWT secret moved out of jwt_utils.py hardcode
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # ── Database ─────────────────────────────────────────────────────────────
    # Day 019 Exercise 5: Database connection settings sourced from .env
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: SecretStr

    # ── Logging ──────────────────────────────────────────────────────────────
    # Day 019 Exercise 6: Console log level controlled via LOG_LEVEL env var
    log_level: str = "INFO" #default value is given as INFO in case if it's not mentioned in .env file

    # ── Pydantic Settings configuration ──────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",           # Load from .env in the working directory
        env_file_encoding="utf-8",
        case_sensitive=False,      # DB_HOST and db_host both work
        extra="ignore",            # Silently ignore unknown env vars
    )



# ──────────────────────────────────────────────────────────────────────────────
# Singleton: imported by all other modules as `from config import settings`
# ──────────────────────────────────────────────────────────────────────────────

settings = Settings()
