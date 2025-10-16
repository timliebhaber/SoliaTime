PRAGMA foreign_keys = ON;

-- schema version
PRAGMA user_version = 4;

CREATE TABLE IF NOT EXISTS profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  color TEXT,
  archived INTEGER NOT NULL DEFAULT 0,
  target_seconds INTEGER,
  company TEXT,
  contact_person TEXT,
  email TEXT,
  phone TEXT
);

CREATE TABLE IF NOT EXISTS time_entries (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  start_ts INTEGER NOT NULL,
  end_ts INTEGER,
  note TEXT,
  tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_profile_start ON time_entries(profile_id, start_ts);
CREATE INDEX IF NOT EXISTS idx_entries_end ON time_entries(end_ts);

-- Per-profile todos
CREATE TABLE IF NOT EXISTS profile_todos (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  completed INTEGER NOT NULL DEFAULT 0,
  created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_todos_profile ON profile_todos(profile_id);


