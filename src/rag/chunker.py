"""Recursive character text chunker tailored for tactical scouting reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .pdf_ingestion import ExtractedReport


@dataclass
class TacticalChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]


def recursive_character_split(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    separators: list[str] | None = None,
) -> list[str]:
    """Recursively split text prioritizing natural paragraph breaks."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    separator = separators[-1]
    new_separators = []
    for i, sep in enumerate(separators):
        if sep == "":
            separator = ""
            break
        if sep in text:
            separator = sep
            new_separators = separators[i + 1:]
            break

    splits = text.split(separator) if separator else list(text)

    good_splits = []
    for s in splits:
        if s.strip():
            good_splits.append(s)

    docs = []
    current_doc: list[str] = []
    total = 0

    for piece in good_splits:
        piece_len = len(piece) + (len(separator) if current_doc else 0)
        if total + piece_len > chunk_size and current_doc:
            doc_str = separator.join(current_doc).strip()
            if doc_str:
                docs.append(doc_str)
            # Retain overlap
            while total > chunk_overlap and len(current_doc) > 1:
                removed = current_doc.pop(0)
                total -= len(removed) + len(separator)
        current_doc.append(piece)
        total += piece_len

    if current_doc:
        doc_str = separator.join(current_doc).strip()
        if doc_str:
            docs.append(doc_str)

    # If any chunk is still larger than chunk_size and we have deeper separators
    final_chunks = []
    for d in docs:
        if len(d) > chunk_size and new_separators:
            sub_chunks = recursive_character_split(
                d,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=new_separators,
            )
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(d)

    return final_chunks


def chunk_extracted_report(
    report: ExtractedReport,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[TacticalChunk]:
    """Split an extracted report into chunks with enriched metadata."""
    raw_chunks = recursive_character_split(
        report.full_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = []
    for idx, text in enumerate(raw_chunks):
        chunk_id = f"{report.source_file}#chunk-{idx}"
        meta = {
            "source": report.source_file,
            "chunk_index": idx,
            "team": report.team,
            "opponent": report.opponent,
            "match_date": report.match_date,
            "fixture": report.fixture,
            "scout": report.scout,
        }
        chunks.append(TacticalChunk(chunk_id=chunk_id, text=text, metadata=meta))

    return chunks


def chunk_all_reports(
    reports: list[ExtractedReport],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[TacticalChunk]:
    """Chunk a list of extracted scouting reports."""
    all_chunks = []
    for rep in reports:
        chunks = chunk_extracted_report(rep, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)
    return all_chunks
