"""Evaluator and verification suite for the GPTinho Golden Dataset."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.data.db_schema import get_db_connection
from src.rag.vector_store import ScoutingVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_sql_query(
    conn,
    expected_sql: str,
    expected_rows: list[dict[str, Any]] | None = None,
) -> tuple[bool, Any, str | None]:
    """Execute SQL query and compare returned rows with expected output."""
    try:
        cur = conn.cursor()
        cur.execute(expected_sql)
        rows = [dict(row) for row in cur.fetchall()]
        if expected_rows is None:
            return True, rows, None

        # Compare row content ignoring order if list
        matches = True
        if len(rows) != len(expected_rows):
            matches = False
        else:
            for exp, actual in zip(expected_rows, rows):
                for k, v in exp.items():
                    if k not in actual or str(actual[k]) != str(v):
                        matches = False
                        break
        return matches, rows, None
    except Exception as exc:
        return False, [], str(exc)


def evaluate_vector_retrieval(
    vector_store: ScoutingVectorStore,
    prompt: str,
    target_team: str,
    expected_snippet: str | None = None,
) -> tuple[bool, list[dict[str, Any]], str | None]:
    """Query ChromaDB with team metadata filter and verify if relevant snippet is retrieved."""
    try:
        results = vector_store.search(
            query=prompt,
            n_results=3,
            metadata_filter={"team": target_team} if target_team else None,
        )
        if not results:
            return False, [], "No chunks retrieved"

        if expected_snippet:
            norm_exp = " ".join(expected_snippet.split()).lower()
            found = any(norm_exp in " ".join(r["document"].split()).lower() for r in results)
            return found, results, None if found else "Expected snippet not found in top-3 chunks"

        return True, results, None
    except Exception as exc:
        return False, [], str(exc)


def run_golden_dataset_validation(
    dataset_path: Path | str = "data/golden_dataset/golden_dataset.jsonl",
    db_path: Path | str = "data/processed/gptinho.db",
    chroma_dir: Path | str = "data/chromadb",
) -> dict[str, Any]:
    """Evaluate all entries in the Golden Dataset."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Golden dataset file not found at {path}")

    conn = get_db_connection(db_path)
    vector_store = ScoutingVectorStore(persist_dir=chroma_dir)

    total = 0
    sql_passed = 0
    vector_passed = 0
    details = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            total += 1
            item_id = item.get("id", f"item-{total}")
            tier = item.get("tier", "quantitative")

            sql_ok = True
            vec_ok = True
            error_msg = None

            # 1. SQL evaluation (for quantitative and hybrid)
            if tier in ("quantitative", "hybrid") and item.get("expected_sql"):
                matched, actual_rows, err = evaluate_sql_query(
                    conn,
                    item["expected_sql"],
                    item.get("expected_sql_rows"),
                )
                if matched:
                    sql_passed += 1
                else:
                    sql_ok = False
                    error_msg = err or f"Rows did not match. Actual: {actual_rows}"

            # 2. Vector retrieval evaluation (for qualitative and hybrid)
            if tier in ("qualitative", "hybrid") and item.get("expected_doc_snippet"):
                matched, retrieved, err = evaluate_vector_retrieval(
                    vector_store,
                    item["prompt"],
                    item.get("target_team", ""),
                    item.get("expected_doc_snippet"),
                )
                if matched:
                    vector_passed += 1
                else:
                    vec_ok = False
                    error_msg = (error_msg + "; " if error_msg else "") + (err or "Vector retrieval mismatch")

            details.append({
                "id": item_id,
                "tier": tier,
                "sql_ok": sql_ok,
                "vector_ok": vec_ok,
                "passed": sql_ok and vec_ok,
                "error": error_msg,
            })

    conn.close()
    quant_hybrid_count = sum(1 for d in details if d["tier"] in ("quantitative", "hybrid"))
    qual_hybrid_count = sum(1 for d in details if d["tier"] in ("qualitative", "hybrid"))

    return {
        "total_items": total,
        "sql_evaluated": quant_hybrid_count,
        "sql_passed": sql_passed,
        "sql_accuracy": (sql_passed / quant_hybrid_count) if quant_hybrid_count else 1.0,
        "vector_evaluated": qual_hybrid_count,
        "vector_passed": vector_passed,
        "vector_accuracy": (vector_passed / qual_hybrid_count) if qual_hybrid_count else 1.0,
        "details": details,
    }


if __name__ == "__main__":
    report = run_golden_dataset_validation()
    print("Golden Dataset Validation Report:")
    print(json.dumps(report, indent=2))
