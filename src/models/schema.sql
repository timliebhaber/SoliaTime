PRAGMA foreign_keys = ON;

-- schema version
PRAGMA user_version = 2;

CREATE TABLE IF NOT EXISTS profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  color TEXT,
  archived INTEGER NOT NULL DEFAULT 0,
  target_seconds INTEGER
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


