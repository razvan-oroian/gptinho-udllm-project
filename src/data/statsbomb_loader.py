"""StatsBomb open-data downloader and SQLite database ETL pipeline."""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests

from .db_schema import get_db_connection, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


class StatsBombLoader:
    def __init__(
        self,
        raw_dir: Path | str = "data/raw/statsbomb",
        db_path: Path | str = "data/processed/gptinho.db",
    ):
        self.raw_dir = Path(raw_dir)
        self.matches_dir = self.raw_dir / "matches"
        self.events_dir = self.raw_dir / "events"
        self.db_path = Path(db_path)

        self.matches_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def fetch_matches(self, competition_id: int = 2, season_id: int = 27) -> list[dict[str, Any]]:
        """Fetch match list for a competition/season, caching locally."""
        cache_file = self.matches_dir / f"{competition_id}_{season_id}.json"
        if cache_file.exists():
            logger.info("Loading cached matches from %s", cache_file)
            return json.loads(cache_file.read_text(encoding="utf-8"))

        url = f"{BASE_URL}/matches/{competition_id}/{season_id}.json"
        logger.info("Fetching matches from %s", url)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Saved %d matches to %s", len(data), cache_file)
        return data

    def fetch_event_file(self, match_id: int, session: requests.Session | None = None) -> tuple[int, list[dict[str, Any]]]:
        """Fetch events for a single match, caching on disk."""
        cache_file = self.events_dir / f"{match_id}.json"
        if cache_file.exists():
            return match_id, json.loads(cache_file.read_text(encoding="utf-8"))

        url = f"{BASE_URL}/events/{match_id}.json"
        s = session or requests.Session()
        resp = s.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        cache_file.write_text(json.dumps(data), encoding="utf-8")
        return match_id, data

    def download_all_events(
        self,
        match_ids: list[int],
        max_workers: int = 12,
    ) -> dict[int, Path]:
        """Download match event files concurrently."""
        to_download = [mid for mid in match_ids if not (self.events_dir / f"{mid}.json").exists()]
        logger.info("Matches to download: %d (Already cached: %d)", len(to_download), len(match_ids) - len(to_download))

        if not to_download:
            return {mid: self.events_dir / f"{mid}.json" for mid in match_ids}

        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.fetch_event_file, mid, session): mid
                    for mid in to_download
                }
                completed = 0
                for fut in as_completed(futures):
                    mid = futures[fut]
                    try:
                        fut.result()
                        completed += 1
                        if completed % 25 == 0 or completed == len(to_download):
                            logger.info("Downloaded %d/%d event files", completed, len(to_download))
                    except Exception as exc:
                        logger.error("Failed downloading match %d: %s", mid, exc)

        return {mid: self.events_dir / f"{mid}.json" for mid in match_ids}

    def load_season_into_db(
        self,
        competition_id: int = 2,
        season_id: int = 27,
        match_limit: int | None = None,
    ) -> dict[str, int]:
        """Full ETL pipeline: fetches matches, events, flattens records and writes to SQLite."""
        init_db(self.db_path)
        conn = get_db_connection(self.db_path)

        matches_data = self.fetch_matches(competition_id, season_id)
        if match_limit:
            matches_data = matches_data[:match_limit]

        match_ids = [m["match_id"] for m in matches_data]
        self.download_all_events(match_ids)

        teams_dict: dict[int, tuple[str, str]] = {}
        players_dict: dict[int, tuple[str, str | None, int, str | None]] = {}
        matches_rows: list[tuple] = []
        events_rows: list[tuple] = []

        # Process matches metadata
        for m in matches_data:
            c_name = m.get("competition", {}).get("country_name", "England")
            home_t = m["home_team"]
            away_t = m["away_team"]
            teams_dict[home_t["home_team_id"]] = (home_t["home_team_name"], c_name)
            teams_dict[away_t["away_team_id"]] = (away_t["away_team_name"], c_name)

            matches_rows.append((
                m["match_id"],
                competition_id,
                season_id,
                m.get("season", {}).get("season_name", "2015/2016"),
                m["match_date"],
                m.get("match_week", 1),
                home_t["home_team_id"],
                away_t["away_team_id"],
                m.get("home_score", 0),
                m.get("away_score", 0),
                (m.get("stadium") or {}).get("name"),
                (m.get("referee") or {}).get("name"),
            ))

        # Insert teams and matches first
        with conn:
            conn.executemany(
                "INSERT OR REPLACE INTO teams (team_id, team_name, country) VALUES (?, ?, ?);",
                [(tid, name, country) for tid, (name, country) in teams_dict.items()],
            )
            conn.executemany(
                """INSERT OR REPLACE INTO matches (
                    match_id, competition_id, season_id, season_name,
                    match_date, match_week, home_team_id, away_team_id,
                    home_score, away_score, stadium, referee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                matches_rows,
            )

        logger.info("Saved %d teams and %d matches", len(teams_dict), len(matches_rows))

        # Process events for each match
        for idx, mid in enumerate(match_ids, start=1):
            event_file = self.events_dir / f"{mid}.json"
            if not event_file.exists():
                continue
            with open(event_file, encoding="utf-8") as f:
                events = json.load(f)

            for e in events:
                e_type = e.get("type", {}).get("name", "Unknown")
                team_info = e.get("team")
                if not team_info:
                    continue
                team_id = team_info["id"]
                team_name = team_info.get("name", "Unknown")
                if team_id not in teams_dict:
                    teams_dict[team_id] = (team_name, "England")

                player_info = e.get("player")
                player_id = None
                position_name = None
                if player_info:
                    player_id = player_info["id"]
                    player_name = player_info.get("name", "Unknown")
                    position_name = (e.get("position") or {}).get("name")
                    if player_id not in players_dict:
                        players_dict[player_id] = (player_name, None, team_id, position_name)

                under_pressure = 1 if e.get("under_pressure") else 0
                counterpress = 1 if e.get("counterpress") else 0

                loc = e.get("location")
                loc_x = loc[0] if loc and len(loc) > 0 else None
                loc_y = loc[1] if loc and len(loc) > 1 else None

                end_loc_x = None
                end_loc_y = None
                pass_recip_id = None
                pass_recip_name = None
                pass_length = None
                pass_angle = None
                pass_height = None
                pass_body_part = None
                outcome = None

                if "pass" in e:
                    p = e["pass"]
                    pass_length = p.get("length")
                    pass_angle = p.get("angle")
                    pass_height = (p.get("height") or {}).get("name")
                    pass_body_part = (p.get("body_part") or {}).get("name")
                    recipient = p.get("recipient")
                    if recipient:
                        pass_recip_id = recipient.get("id")
                        pass_recip_name = recipient.get("name")
                    end_loc = p.get("end_location")
                    if end_loc and len(end_loc) >= 2:
                        end_loc_x, end_loc_y = end_loc[0], end_loc[1]
                    outcome = (p.get("outcome") or {}).get("name", "Complete")
                elif "shot" in e:
                    s = e["shot"]
                    end_loc = s.get("end_location")
                    if end_loc and len(end_loc) >= 2:
                        end_loc_x, end_loc_y = end_loc[0], end_loc[1]
                    outcome = (s.get("outcome") or {}).get("name")
                elif "duel" in e:
                    outcome = (e["duel"].get("outcome") or {}).get("name")
                elif "interception" in e:
                    outcome = (e["interception"].get("outcome") or {}).get("name")

                events_rows.append((
                    e["id"],
                    mid,
                    e.get("index"),
                    e.get("period"),
                    e.get("timestamp"),
                    e.get("minute", 0),
                    e.get("second", 0),
                    e_type,
                    team_id,
                    player_id,
                    position_name,
                    (e.get("play_pattern") or {}).get("name"),
                    under_pressure,
                    counterpress,
                    loc_x,
                    loc_y,
                    end_loc_x,
                    end_loc_y,
                    pass_recip_id,
                    pass_recip_name,
                    pass_length,
                    pass_angle,
                    pass_height,
                    pass_body_part,
                    outcome,
                    e.get("duration"),
                ))

            if idx % 50 == 0 or idx == len(match_ids):
                logger.info("Processed %d/%d matches (%d events accumulated)", idx, len(match_ids), len(events_rows))

        # Bulk insert players and events
        logger.info("Inserting %d players into database...", len(players_dict))
        with conn:
            conn.executemany(
                """INSERT OR REPLACE INTO players (player_id, player_name, player_nickname, team_id, position)
                   VALUES (?, ?, ?, ?, ?);""",
                [(pid, name, nick, tid, pos) for pid, (name, nick, tid, pos) in players_dict.items()],
            )

        logger.info("Inserting %d events into database...", len(events_rows))
        # Batch insert events to prevent memory spikes
        batch_size = 20000
        with conn:
            for i in range(0, len(events_rows), batch_size):
                batch = events_rows[i:i + batch_size]
                conn.executemany(
                    """INSERT OR REPLACE INTO events (
                        event_id, match_id, index_num, period, timestamp,
                        minute, second, event_type, team_id, player_id,
                        position, play_pattern, under_pressure, counterpress,
                        location_x, location_y, end_location_x, end_location_y,
                        pass_recipient_id, pass_recipient_name, pass_length,
                        pass_angle, pass_height, pass_body_part, outcome, duration
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                    batch,
                )

        conn.close()
        logger.info("ETL completed successfully.")
        return {
            "teams": len(teams_dict),
            "matches": len(matches_rows),
            "players": len(players_dict),
            "events": len(events_rows),
        }


if __name__ == "__main__":
    loader = StatsBombLoader()
    # Download and load all 380 matches for 2015/2016 Premier League
    counts = loader.load_season_into_db(competition_id=2, season_id=27)
    print("Database populated with:", counts)
