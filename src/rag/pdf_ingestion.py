"""PDF text extraction and metadata parser for tactical scouting reports."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractedReport:
    source_file: str
    team: str
    opponent: str
    match_date: str
    fixture: str
    scout: str
    full_text: str
    raw_metadata: dict[str, Any]


def extract_metadata_from_text(text: str) -> dict[str, str]:
    """Parse header metadata from report text."""
    meta = {
        "team": "Unknown",
        "opponent": "Unknown",
        "match_date": "2015-08-08",
        "fixture": "Unknown",
        "scout": "Staff",
    }

    team_match = re.search(r"Tactical Scouting Dossier:\s*(.*?)(?=\s*Fixture:|$)", text)
    if team_match:
        meta["team"] = team_match.group(1).strip()

    fixture_match = re.search(r"Fixture:\s*(.*?)(?=\s*Match Date:|$)", text)
    if fixture_match:
        meta["fixture"] = fixture_match.group(1).strip()

    date_match = re.search(r"Match Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
    if date_match:
        meta["match_date"] = date_match.group(1).strip()

    opp_match = re.search(r"Opposition:\s*(.*?)(?=\s*Lead Analyst:|$)", text)
    if opp_match:
        meta["opponent"] = opp_match.group(1).strip()

    scout_match = re.search(r"Lead Analyst:\s*(.*?)(?=\s*\||\s*Classification:|$)", text)
    if scout_match:
        meta["scout"] = scout_match.group(1).strip()

    return meta


def load_pdf_report(pdf_path: Path | str) -> ExtractedReport:
    """Read and extract all pages of a PDF scouting report."""
    path = Path(pdf_path)
    reader = PdfReader(str(path))
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        # Normalize soft line breaks while preserving paragraph boundaries
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        pages_text.append(text)

    full_text = "\n".join(pages_text).strip()
    meta = extract_metadata_from_text(full_text)

    return ExtractedReport(
        source_file=path.name,
        team=meta["team"],
        opponent=meta["opponent"],
        match_date=meta["match_date"],
        fixture=meta["fixture"],
        scout=meta["scout"],
        full_text=full_text,
        raw_metadata=meta,
    )


def load_all_scouting_pdfs(directory: Path | str = "data/raw/scouting_reports") -> list[ExtractedReport]:
    """Load all PDF scouting reports from directory."""
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.warning("Directory %s does not exist", directory)
        return []

    reports = []
    for file_path in sorted(dir_path.glob("*.pdf")):
        try:
            report = load_pdf_report(file_path)
            reports.append(report)
        except Exception as exc:
            logger.error("Failed to parse PDF %s: %s", file_path, exc)

    logger.info("Successfully extracted %d PDF reports from %s", len(reports), dir_path)
    return reports
