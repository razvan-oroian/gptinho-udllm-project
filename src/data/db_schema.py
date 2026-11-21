"""Database schema and SQLite initialization for GPTinho."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    country TEXT
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL,
    player_nickname TEXT,
    team_id INTEGER,
    position TEXT,
    FOREIGN KEY(team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    competition_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    season_name TEXT NOT NULL,
    match_date TEXT NOT NULL,
    match_week INTEGER,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    stadium TEXT,
    referee TEXT,
    FOREIGN KEY(home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY(away_team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    match_id INTEGER NOT NULL,
    index_num INTEGER,
    period INTEGER,
    timestamp TEXT,
    minute INTEGER NOT NULL,
    second INTEGER,
    event_type TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER,
    position TEXT,
    play_pattern TEXT,
    under_pressure INTEGER DEFAULT 0,
    counterpress INTEGER DEFAULT 0,
    location_x REAL,
    location_y REAL,
    end_location_x REAL,
    end_location_y REAL,
    pass_recipient_id INTEGER,
    pass_recipient_name TEXT,
    pass_length REAL,
    pass_angle REAL,
    pass_height TEXT,
    pass_body_part TEXT,
    outcome TEXT,
    duration REAL,
    FOREIGN KEY(match_id) REFERENCES matches(match_id),
    FOREIGN KEY(team_id) REFERENCES teams(team_id),
    FOREIGN KEY(player_id) REFERENCES players(player_id)
);

-- Optimized indexes for Text-to-SQL performance
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_home ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away ON matches(away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_week ON matches(match_week);

CREATE INDEX IF NOT EXISTS idx_events_match ON events(match_id);
CREATE INDEX IF NOT EXISTS idx_events_team_type ON events(team_id, event_type);
CREATE INDEX IF NOT EXISTS idx_events_player_type ON events(player_id, event_type);
CREATE INDEX IF NOT EXISTS idx_events_player_pressure ON events(player_id, under_pressure, event_type);
CREATE INDEX IF NOT EXISTS idx_events_pattern ON events(play_pattern);
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);
"""


def get_db_connection(db_path: Path | str) -> sqlite3.Connection:
    """Connect to SQLite database with optimized pragmas."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str) -> sqlite3.Connection:
    """Initialize database tables and indexes."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn
