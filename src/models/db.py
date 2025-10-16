from __future__ import annotations

import sqlite3
from pathlib import Path

from src.services.settings import get_data_dir


DB_FILENAME = "solia.db"


def _db_path() -> Path:
    return get_data_dir() / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    # Simple migration: ensure tables exist; set user_version if empty
    with conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.execute("PRAGMA user_version;")
        version = cur.fetchone()[0]
        if version == 0:
            schema_path = Path(__file__).with_name("schema.sql")
            if schema_path.exists():
                schema_text = schema_path.read_text(encoding="utf-8")
            else:
                schema_text = (
                    "PRAGMA foreign_keys=ON;\n"
                    "CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, color TEXT, archived INTEGER NOT NULL DEFAULT 0, target_seconds INTEGER);\n"
                    "CREATE TABLE IF NOT EXISTS time_entries (id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, start_ts INTEGER NOT NULL, end_ts INTEGER, note TEXT, tags TEXT);\n"
                    "CREATE INDEX IF NOT EXISTS idx_entries_profile_start ON time_entries(profile_id, start_ts);\n"
                    "CREATE INDEX IF NOT EXISTS idx_entries_end ON time_entries(end_ts);\n"
                )
            conn.executescript(schema_text)
            conn.execute("PRAGMA user_version = 2;")
        elif version == 1:
            # Migrate to v2: add target_seconds to profiles
            conn.execute("ALTER TABLE profiles ADD COLUMN target_seconds INTEGER;")
            conn.execute("PRAGMA user_version = 2;")


