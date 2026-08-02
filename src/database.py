"""Database initialization and connection utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "sasadiakopi.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "01_create_schema.sql"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database() -> None:
    """Create the database schema if it does not already exist."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    connection = get_connection()

    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()
