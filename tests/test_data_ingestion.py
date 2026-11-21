"""Unit tests for SQLite database schema and StatsBomb ingestion."""

import sqlite3
import pytest
from pathlib import Path
from src.data.db_schema import init_db, get_db_connection

TEST_DB_PATH = "data/processed/test_gptinho.db"


@pytest.fixture(scope="module")
def db_conn():
    Path(TEST_DB_PATH).unlink(missing_ok=True)
    conn = init_db(TEST_DB_PATH)
    yield conn
    conn.close()
    Path(TEST_DB_PATH).unlink(missing_ok=True)


def test_schema_tables_exist(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cur.fetchall()}
    assert "teams" in tables
    assert "players" in tables
    assert "matches" in tables
    assert "events" in tables


def test_schema_indexes_exist(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = {row[0] for row in cur.fetchall()}
    assert "idx_events_match" in indexes
    assert "idx_events_team_type" in indexes
    assert "idx_events_player_pressure" in indexes
    assert "idx_matches_date" in indexes


def test_foreign_key_enforcement(db_conn):
    cur = db_conn.cursor()
    # Inserting player with non-existent team_id must fail when FK is enabled
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO players (player_id, player_name, team_id) VALUES (?, ?, ?);",
            (99999, "Ghost Player", 88888),
        )


def test_team_and_player_insertion(db_conn):
    cur = db_conn.cursor()
    cur.execute("INSERT INTO teams (team_id, team_name, country) VALUES (1, 'Liverpool', 'England');")
    cur.execute("INSERT INTO players (player_id, player_name, team_id, position) VALUES (10, 'Philippe Coutinho', 1, 'Attacking Midfield');")
    db_conn.commit()

    cur.execute("SELECT p.player_name, t.team_name FROM players p JOIN teams t ON p.team_id = t.team_id WHERE p.player_id = 10;")
    row = cur.fetchone()
    assert row[0] == "Philippe Coutinho"
    assert row[1] == "Liverpool"
