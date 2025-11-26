PRAGMA foreign_keys = ON;

-- schema version
PRAGMA user_version = 13;

CREATE TABLE IF NOT EXISTS profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  color TEXT,
  archived INTEGER NOT NULL DEFAULT 0,
  target_seconds INTEGER,
  company TEXT,
  contact_person TEXT,
  email TEXT,
  phone TEXT,
  business_address TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS time_entries (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
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


-- Services (catalog of billable services with hourly rate in cents)
CREATE TABLE IF NOT EXISTS services (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  rate_cents INTEGER NOT NULL,
  estimated_seconds INTEGER
);

-- Profile Services (instances of services added to profiles)
CREATE TABLE IF NOT EXISTS profile_services (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
  notes TEXT,
  created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_profile_services_profile ON profile_services(profile_id);

-- Profile Service Todos (todos for each service instance)
CREATE TABLE IF NOT EXISTS profile_service_todos (
  id INTEGER PRIMARY KEY,
  profile_service_id INTEGER NOT NULL REFERENCES profile_services(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  completed INTEGER NOT NULL DEFAULT 0,
  created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_profile_service_todos_service ON profile_service_todos(profile_service_id);

-- Projects (larger units of work for profiles)
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY,
  profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  estimated_seconds INTEGER,
  service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
  deadline_ts INTEGER,
  start_date_ts INTEGER,
  invoice_sent INTEGER NOT NULL DEFAULT 0,
  invoice_paid INTEGER NOT NULL DEFAULT 0,
  notes TEXT,
  created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_projects_profile ON projects(profile_id);

-- Project Todos
CREATE TABLE IF NOT EXISTS project_todos (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  completed INTEGER NOT NULL DEFAULT 0,
  created_ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_project_todos_project ON project_todos(project_id);


