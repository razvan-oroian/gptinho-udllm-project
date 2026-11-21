"""Test suite verifying the Golden Dataset against SQLite and ChromaDB."""

import pytest
from src.data.validate_golden_dataset import run_golden_dataset_validation


def test_golden_dataset_execution_and_retrieval():
    report = run_golden_dataset_validation(
        dataset_path="data/golden_dataset/golden_dataset.jsonl",
        db_path="data/processed/gptinho.db",
        chroma_dir="data/chromadb",
    )

    assert report["total_items"] == 20
    assert report["sql_accuracy"] == 1.0, f"Expected 100% SQL Execution Accuracy, got {report['sql_accuracy']}"
    assert report["vector_accuracy"] == 1.0, f"Expected 100% Vector Retrieval Accuracy, got {report['vector_accuracy']}"
    assert all(d["passed"] for d in report["details"]), f"Some items failed: {[d for d in report['details'] if not d['passed']]}"
