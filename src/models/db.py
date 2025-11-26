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
        elif version == 2:
            # Migrate to v3: add contact fields
            conn.execute("ALTER TABLE profiles ADD COLUMN company TEXT;")
            conn.execute("ALTER TABLE profiles ADD COLUMN contact_person TEXT;")
            conn.execute("ALTER TABLE profiles ADD COLUMN email TEXT;")
            conn.execute("ALTER TABLE profiles ADD COLUMN phone TEXT;")
            conn.execute("PRAGMA user_version = 3;")
        elif version == 3:
            # Migrate to v4: create profile_todos
            conn.execute(
                "CREATE TABLE IF NOT EXISTS profile_todos (id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, text TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now')));"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todos_profile ON profile_todos(profile_id);")
            conn.execute("PRAGMA user_version = 4;")
        elif version == 4:
            # Migrate to v5: add notes column to profiles
            try:
                conn.execute("ALTER TABLE profiles ADD COLUMN notes TEXT;")
            except Exception:
                # Column may already exist
                pass
            conn.execute("PRAGMA user_version = 5;")
        elif version == 5:
            # Migrate to v6: create services table
            conn.execute(
                "CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, rate_cents INTEGER NOT NULL);"
            )
            conn.execute("PRAGMA user_version = 6;")
        elif version == 6:
            # Migrate to v7: add estimated_seconds to services
            try:
                conn.execute("ALTER TABLE services ADD COLUMN estimated_seconds INTEGER;")
            except Exception:
                pass
            conn.execute("PRAGMA user_version = 7;")
        elif version == 7:
            # Migrate to v8: create profile_services and profile_service_todos
            conn.execute(
                """CREATE TABLE IF NOT EXISTS profile_services (
                    id INTEGER PRIMARY KEY,
                    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
                    notes TEXT,
                    created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
                );"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_profile_services_profile ON profile_services(profile_id);")
            conn.execute(
                """CREATE TABLE IF NOT EXISTS profile_service_todos (
                    id INTEGER PRIMARY KEY,
                    profile_service_id INTEGER NOT NULL REFERENCES profile_services(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
                );"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_profile_service_todos_service ON profile_service_todos(profile_service_id);")
            conn.execute("PRAGMA user_version = 8;")
        elif version == 8:
            # Migrate to v9: create projects and project_todos tables
            conn.execute(
                """CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    estimated_seconds INTEGER,
                    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
                    deadline_ts INTEGER,
                    notes TEXT,
                    created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
                );"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_profile ON projects(profile_id);")
            conn.execute(
                """CREATE TABLE IF NOT EXISTS project_todos (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
                );"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_todos_project ON project_todos(project_id);")
            conn.execute("PRAGMA user_version = 9;")
        elif version == 9:
            # Migrate to v10: add project_id to time_entries
            try:
                conn.execute("ALTER TABLE time_entries ADD COLUMN project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL;")
            except Exception:
                # Column may already exist
                pass
            conn.execute("PRAGMA user_version = 10;")
        elif version == 10:
            # Migrate to v11: clear all profile time estimates (target_seconds)
            # Time estimates are now only on projects and services
            conn.execute("UPDATE profiles SET target_seconds = NULL;")
            conn.execute("PRAGMA user_version = 11;")
        elif version == 11:
            # Migrate to v12: add business_address to profiles
            try:
                conn.execute("ALTER TABLE profiles ADD COLUMN business_address TEXT;")
            except Exception:
                # Column may already exist
                pass
            conn.execute("PRAGMA user_version = 12;")
        elif version == 12:
            # Migrate to v13: add start_date_ts, invoice_sent, invoice_paid to projects
            try:
                conn.execute("ALTER TABLE projects ADD COLUMN start_date_ts INTEGER;")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE projects ADD COLUMN invoice_sent INTEGER NOT NULL DEFAULT 0;")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE projects ADD COLUMN invoice_paid INTEGER NOT NULL DEFAULT 0;")
            except Exception:
                pass
            conn.execute("PRAGMA user_version = 13;")


