"""Unit tests for PDF extraction, chunking, and ChromaDB vector store."""

import pytest
from pathlib import Path
from src.rag import (
    load_all_scouting_pdfs,
    chunk_all_reports,
    recursive_character_split,
    ScoutingVectorStore,
)

TEST_CHROMA_DIR = "data/test_chromadb"


@pytest.fixture(scope="module")
def vector_store():
    vs = ScoutingVectorStore(persist_dir=TEST_CHROMA_DIR, collection_name="test_reports")
    yield vs
    vs.reset()


def test_recursive_character_split():
    text = "Paragraph one explaining tactics.\n\nParagraph two focusing on build-up.\n\nParagraph three on defensive line."
    splits = recursive_character_split(text, chunk_size=80, chunk_overlap=10)
    assert len(splits) >= 2
    assert all(len(s) <= 80 for s in splits)


def test_pdf_extraction_and_chunking():
    reports = load_all_scouting_pdfs("data/raw/scouting_reports")
    assert len(reports) >= 6, "Expected at least 6 generated scouting reports"

    liverpool = next(r for r in reports if r.team == "Liverpool")
    assert liverpool.opponent == "Chelsea"
    assert "Emre Can" in liverpool.full_text

    chunks = chunk_all_reports(reports)
    assert len(chunks) > 0
    assert any("bypass the midfield pivot" in c.text for c in chunks)


def test_vector_store_indexing_and_metadata_prefilter(vector_store):
    reports = load_all_scouting_pdfs("data/raw/scouting_reports")
    chunks = chunk_all_reports(reports)
    count = vector_store.add_chunks(chunks)
    assert count == len(chunks)

    # Search with Liverpool metadata filter
    results = vector_store.search(
        query="bypass the midfield pivot with long passes",
        n_results=2,
        metadata_filter={"team": "Liverpool"},
    )
    assert len(results) > 0
    assert results[0]["metadata"]["team"] == "Liverpool"
    assert "Liverpool" in results[0]["document"]

    # Search with Leicester filter should return Leicester documents
    leicester_res = vector_store.search(
        query="counter attack Mahrez Vardy through balls",
        n_results=2,
        metadata_filter={"team": "Leicester City"},
    )
    assert len(leicester_res) > 0
    assert all(r["metadata"]["team"] == "Leicester City" for r in leicester_res)
    assert any("Mahrez" in r["document"] for r in leicester_res)
